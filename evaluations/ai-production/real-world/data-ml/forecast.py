"""Fit and replay a bounded calendar/available-lag demand forecast, standard library only."""
import argparse
import csv
from datetime import date, datetime, time as clocktime, timedelta
import json
import math
from pathlib import Path
import statistics
import time
from zoneinfo import ZoneInfo
from common import atomic_json, load_json, observed_resources, private_root, require, sha_file

ZONE = ZoneInfo('America/New_York')
ORIGIN = date(2011, 1, 1)
ALPHAS = (0.1, 1.0, 10.0)
FEATURES = ['intercept', 'elapsed_years', 'annual_sin', 'annual_cos', 'holiday'] + [
    'weekday_' + str(i) for i in range(7)] + ['lag2', 'lag7', 'mean7_through_lag2']


def midnight(day):
    return datetime.combine(day, clocktime(), ZONE)


def load_days(path):
    with Path(path).open(newline='') as stream:
        source = list(csv.DictReader(stream))
    required = {'dteday', 'cnt', 'holiday'}
    require(source and required <= source[0].keys(), 'daily source schema drift')
    rows = {}
    for row in source:
        day = date.fromisoformat(row['dteday'])
        count = int(row['cnt'])
        require(day not in rows and count >= 0, 'duplicate date/negative target')
        rows[day] = {'date': day, 'cnt': count, 'holiday': int(row['holiday']),
                     'available_at': midnight(day + timedelta(days=2))}
    return rows


def features(day, rows):
    required = [day - timedelta(days=i) for i in range(2, 9)]
    cutoff = midnight(day)
    if any(key not in rows for key in required):
        return None, 'insufficient_history'
    require(all(rows[key]['available_at'] <= cutoff for key in required), 'future/delayed label leaked into feature')
    angle = 2 * math.pi * day.timetuple().tm_yday / 365.25
    values = [1.0, (day - ORIGIN).days / 365.25, math.sin(angle), math.cos(angle),
              float(rows.get(day, {}).get('holiday', 0))]
    values += [float(day.weekday() == i) for i in range(7)]
    values += [float(rows[day - timedelta(days=2)]['cnt']), float(rows[day - timedelta(days=7)]['cnt']),
               statistics.mean(rows[key]['cnt'] for key in required)]
    return values, None


def solve(matrix, target):
    size = len(target)
    augmented = [row[:] + [value] for row, value in zip(matrix, target)]
    for column in range(size):
        pivot = max(range(column, size), key=lambda i: abs(augmented[i][column]))
        require(abs(augmented[pivot][column]) > 1e-12, 'singular bounded regression system')
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        divisor = augmented[column][column]
        augmented[column] = [x / divisor for x in augmented[column]]
        for i in range(size):
            if i != column:
                scale = augmented[i][column]
                augmented[i] = [a - scale * b for a, b in zip(augmented[i], augmented[column])]
    return [row[-1] for row in augmented]


def fit(rows, cutoff, alpha):
    training = []
    for day, row in sorted(rows.items()):
        x, _ = features(day, rows)
        if x and row['available_at'] <= midnight(cutoff):
            training.append((day, x, row['cnt']))
    require(len(training) >= 30, 'insufficient matured training history')
    means = [0.0] + [statistics.mean(x[j] for _, x, _ in training) for j in range(1, len(FEATURES))]
    scales = [1.0] + [statistics.pstdev(x[j] for _, x, _ in training) or 1.0 for j in range(1, len(FEATURES))]
    size = len(FEATURES)
    gram, target = [[0.0] * size for _ in range(size)], [0.0] * size
    weekday = {i: [] for i in range(7)}
    for day, x, y in training:
        normalized = [(value - mean) / scale for value, mean, scale in zip(x, means, scales)]
        weekday[day.weekday()].append(y)
        for i in range(size):
            target[i] += normalized[i] * y
            for j in range(size):
                gram[i][j] += normalized[i] * normalized[j]
    for j in range(1, size):
        gram[j][j] += alpha
    weights = solve(gram, target)
    return {'schema': 'atelier.historical-demand-model/1', 'features': FEATURES,
            'means': means, 'scales': scales, 'weights': weights, 'alpha': alpha,
            'weekday_means': {str(i): statistics.mean(values) for i, values in weekday.items()},
            'fit_cutoff': cutoff.isoformat(), 'training_dates': [day.isoformat() for day, _, _ in training],
            'training_rows': len(training), 'target': 'daily rentals',
            'availability_policy': 'observed day +2 local midnights; declared conservative scenario'}


def predict(model, day, rows, route='ridge', enforce_window=False):
    if 'inference_source_sha256' in model:
        require(model['inference_source_sha256'] == sha_file(__file__), 'inference implementation bytes changed')
    if enforce_window and not date(2012, 10, 1) <= day <= date(2012, 12, 31):
        return {'status': 'abstained', 'reason': 'outside_validated_historical_period', 'prediction': None}
    history = [rows.get(day - timedelta(days=i)) for i in range(2, 9)]
    if enforce_window and all(row is not None for row in history) and sum(row['cnt'] > 0 for row in history) < 2:
        return {'status': 'abstained', 'reason': 'intermittent_history_not_validated', 'prediction': None,
                'requires_human_review': True}
    x, reason = features(day, rows)
    if x is None:
        return {'status': 'abstained', 'reason': reason, 'prediction': None}
    if route == 'weekday_mean':
        value = model['weekday_means'][str(day.weekday())]
    elif route == 'seasonal7':
        value = rows[day - timedelta(days=7)]['cnt']
    else:
        require(route == 'ridge', 'unknown model route')
        z = [(value - mean) / scale for value, mean, scale in zip(x, model['means'], model['scales'])]
        value = sum(a * b for a, b in zip(z, model['weights']))
    result = {'status': 'predicted', 'prediction': max(0.0, float(value)), 'route': route,
              'prediction_at': midnight(day).isoformat()}
    if 'interval_admission' in model and route == model['selected_route']:
        result.update(interval_admission=model['interval_admission'], requires_human_review=True,
                      use='historical test only; no current operational decisions')
    return result


def evaluate(model, rows, start, end, route):
    results = []
    for day, row in sorted(rows.items()):
        if start <= day <= end:
            result = predict(model, day, rows, route)
            results.append({'date': day.isoformat(), 'actual': row['cnt'], **result})
    covered = [row for row in results if row['status'] == 'predicted']
    require(covered, 'evaluation has no predicted rows')
    errors = [abs(row['prediction'] - row['actual']) for row in covered]
    return {'rows': len(results), 'predicted': len(covered), 'abstained': len(results) - len(covered),
            'mae': statistics.mean(errors), 'rmse': math.sqrt(statistics.mean(
                (row['prediction'] - row['actual']) ** 2 for row in covered)),
            'predictions': results}


def run(source, out):
    start_clock = time.monotonic()
    out = private_root(out)
    rows = load_days(source)
    settings = [('weekday_mean', 1.0), ('seasonal7', 1.0)] + [('ridge', alpha) for alpha in ALPHAS]
    validation = []
    for route, alpha in settings:
        errors, count = 0.0, 0
        folds = []
        for cutoff, begin, end in [(date(2012, 1, 1), date(2012, 1, 1), date(2012, 3, 31)),
                                   (date(2012, 4, 1), date(2012, 4, 1), date(2012, 6, 30))]:
            model = fit(rows, cutoff, alpha)
            report = evaluate(model, rows, begin, end, route)
            errors += report['mae'] * report['predicted']
            count += report['predicted']
            folds.append({key: value for key, value in report.items() if key != 'predictions'})
        validation.append({'route': route, 'alpha': alpha, 'mae': errors / count, 'rows': count, 'folds': folds})
    chosen = min(validation, key=lambda row: row['mae'])
    calibration_model = fit(rows, date(2012, 7, 1), chosen['alpha'])
    calibration = evaluate(calibration_model, rows, date(2012, 7, 1), date(2012, 9, 30), chosen['route'])
    radii = {}
    for route in ('weekday_mean', 'seasonal7', 'ridge'):
        calibrated = evaluate(calibration_model, rows, date(2012, 7, 1), date(2012, 9, 30), route)
        residuals = sorted(abs(row['prediction'] - row['actual']) for row in calibrated['predictions'])
        radii[route] = residuals[min(len(residuals) - 1, math.ceil(0.9 * len(residuals)) - 1)]
    radius = radii[chosen['route']]
    model = fit(rows, date(2012, 10, 1), chosen['alpha'])
    model.update(selected_route=chosen['route'], source_sha256=sha_file(source),
                 interval_radius=radius, validated_period=['2012-10-01', '2012-12-31'],
                 inference_source_sha256=sha_file(__file__),
                 study_sha256=sha_file(Path(__file__).with_name('STUDY.json')))
    holdouts = {}
    for route in ('weekday_mean', 'seasonal7', 'ridge'):
        result = evaluate(model, rows, date(2012, 10, 1), date(2012, 12, 31), route)
        for item in result['predictions']:
            item['interval'] = [max(0, item['prediction'] - radii[route]), item['prediction'] + radii[route]]
        result['interval_coverage'] = sum(a['interval'][0] <= a['actual'] <= a['interval'][1]
                                          for a in result['predictions']) / result['rows']
        result['subgroups'] = {}
        for group in ('weekday', 'weekend'):
            subset = [r for r in result['predictions'] if (date.fromisoformat(r['date']).weekday() < 5) == (group == 'weekday')]
            result['subgroups'][group] = {'n': len(subset), 'mae': statistics.mean(abs(r['prediction'] - r['actual']) for r in subset)}
        holdouts[route] = result
    model['interval_admission'] = {'nominal_coverage': .90,
                                   'measured_holdout_coverage': holdouts[chosen['route']]['interval_coverage'],
                                   'admitted_for_90pct_coverage': holdouts[chosen['route']]['interval_coverage'] >= .90,
                                   'reason': 'Measured coverage is diagnostic; do not retune against this holdout'}
    atomic_json(out / 'model.json', model)
    negative = {}
    first_test = date(2012, 10, 1)
    poisoned = {key: dict(value) for key, value in rows.items()}
    poisoned[first_test - timedelta(days=2)]['available_at'] = midnight(first_test + timedelta(days=1))
    try:
        features(first_test, poisoned)
    except ValueError as error:
        negative['future_feature_rejected'] = str(error)
    require('future_feature_rejected' in negative, 'future-feature control was not detected')
    cold = predict(model, first_test, {}, chosen['route'], True)
    future = predict(model, date(2026, 11, 10), rows, chosen['route'], True)
    require(cold['status'] == future['status'] == 'abstained', 'cold/out-of-domain guard failed')
    report = {'schema': 'atelier.actual-demand-evaluation/1', 'source_sha256': sha_file(source),
              'study_sha256': model['study_sha256'], 'inference_source_sha256': model['inference_source_sha256'],
              'model_sha256': sha_file(out / 'model.json'), 'source_rows': len(rows),
              'warmup_rows_without_full_features': sum(features(day, rows)[0] is None for day in rows),
              'declared_study': 'STUDY.json frozen before fits', 'tuning': validation,
              'selected': chosen, 'calibration_rows': calibration['rows'], 'interval_radius': radius,
              'per_route_calibration_radii': radii,
              'holdouts': holdouts, 'cold_start': cold, 'out_of_domain': future,
              'negative_controls': negative, 'resources': observed_resources(start_clock),
              'limits': ['Historical evaluation, not contemporary demand accuracy or deployment',
                         'Availability delay is a declared scenario, not source publication metadata',
                         'One-step rolling forecasts use only count labels available at each cutoff',
                         'Residual intervals have empirical measured coverage, not a coverage guarantee',
                         'No CPA or LLM/LoRA claim']}
    atomic_json(out / 'forecast-report.json', report)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    train = sub.add_parser('fit')
    train.add_argument('--source', required=True)
    train.add_argument('--out', required=True)
    serve = sub.add_parser('predict')
    serve.add_argument('--model', required=True)
    serve.add_argument('--source', required=True)
    serve.add_argument('--date', required=True)
    args = parser.parse_args()
    if args.command == 'fit':
        result = run(args.source, args.out)
        print(json.dumps({'source_rows': result['source_rows'], 'chosen': result['selected'],
                          'holdout_mae': {k: v['mae'] for k, v in result['holdouts'].items()},
                          'resources': result['resources']}))
    else:
        model = load_json(args.model)
        require(model['source_sha256'] == sha_file(args.source), 'inference source version differs')
        result = predict(model, date.fromisoformat(args.date), load_days(args.source), model['selected_route'], True)
        if result['prediction'] is not None:
            result['interval'] = [max(0, result['prediction'] - model['interval_radius']), result['prediction'] + model['interval_radius']]
        print(json.dumps(result, allow_nan=False))
