"""Human-labelled bilingual review benchmark; no pretrained model or dependency download."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import random
import re
import statistics
import time
import unicodedata
from common import atomic_json, load_json, observed_resources, private_root, require, sha_file

LABELS = (-2, -1, 0, 1, 2)


def clean(text):
    return ' '.join(unicodedata.normalize('NFKC', text).casefold().split())


def tokens(text, mode):
    words = re.findall(r'[^\W\d_]{2,}', clean(text), re.UNICODE)
    result = Counter('w:' + word for word in words)
    if mode == 'word_char':
        for word in words:
            bounded = '^' + word + '$'
            result.update('c:' + bounded[i:i + 3] for i in range(len(bounded) - 2))
    return result


def read_rows(source):
    papers = load_json(source)['paper']
    rows, quarantine = [], []
    for paper in papers:
        for review in paper['review']:
            ident = str(paper['id']) + ':' + str(review['id'])
            try:
                text, language = review['text'], review['lan']
                require(isinstance(text, str) and clean(text), 'empty review text')
                require(language in ('en', 'es'), 'unsupported source language')
                label = int(review['orientation'])
                require(label in LABELS, 'orientation label outside source scale')
                rows.append({'id': ident, 'paper_id': str(paper['id']), 'text': text,
                             'language': language, 'label': label})
            except (ValueError, KeyError, TypeError) as error:
                quarantine.append({'id': ident, 'reason': str(error)})
    require(len({row['id'] for row in rows}) == len(rows), 'duplicate native review identity')
    parents = {row['paper_id']: row['paper_id'] for row in rows}
    def root(key):
        while parents[key] != key:
            parents[key] = parents[parents[key]]
            key = parents[key]
        return key
    duplicates = {}
    for row in rows:
        digest = hashlib.sha256(clean(row['text']).encode()).hexdigest()
        if digest in duplicates:
            a, b = root(row['paper_id']), root(duplicates[digest])
            parents[max(a, b)] = min(a, b)
        else:
            duplicates[digest] = row['paper_id']
    for row in rows:
        group = root(row['paper_id'])
        bucket = int(hashlib.sha256(('paper-group:' + group).encode()).hexdigest(), 16) % 100
        row.update(group=group, split='train' if bucket < 60 else 'validation' if bucket < 80 else 'test')
    groups = {part: {row['group'] for row in rows if row['split'] == part} for part in ('train', 'validation', 'test')}
    require(not any(a & b for i, a in enumerate(groups.values()) for b in list(groups.values())[i + 1:]),
            'paper/duplicate group split leakage')
    return rows, quarantine, len(papers)


def fit(training, mode, alpha):
    frequencies = Counter()
    for row in training:
        frequencies.update(tokens(row['text'], mode).keys())
    vocabulary = [key for key, n in sorted(frequencies.items(), key=lambda p: (-p[1], p[0])) if n >= 2][:4000]
    require(vocabulary, 'no train-only vocabulary')
    allowed = set(vocabulary)
    counts, class_sizes = {label: Counter() for label in LABELS}, Counter()
    for row in training:
        class_sizes[row['label']] += 1
        counts[row['label']].update({key: value for key, value in tokens(row['text'], mode).items() if key in allowed})
    classes = [label for label in LABELS if class_sizes[label]]
    weights = {}
    for label in classes:
        denominator = sum(counts[label].values()) + alpha * len(vocabulary)
        weights[str(label)] = {key: math.log((counts[label][key] + alpha) / denominator) for key in vocabulary}
    majority = min(classes, key=lambda label: (-class_sizes[label], label))
    return {'schema': 'atelier.review-orientation-nb/1', 'mode': mode, 'alpha': alpha,
            'vocabulary': vocabulary, 'weights': weights,
            'priors': {str(label): math.log(class_sizes[label] / len(training)) for label in classes},
            'majority': majority, 'train_rows': len(training), 'train_label_counts': dict(class_sizes),
            'target': 'perceived review orientation, not reviewer evaluation or paper acceptance',
            'source_code_sha256': sha_file(__file__)}


def predict(model, text, baseline=False):
    require(model['source_code_sha256'] == sha_file(__file__), 'inference implementation bytes changed')
    if not clean(text):
        return {'status': 'abstained', 'label': None, 'reason': 'empty_input'}
    if baseline:
        return {'status': 'predicted', 'label': model['majority'], 'route': 'training-majority'}
    words = tokens(text, model['mode'])
    known = {key: value for key, value in words.items() if key in model['weights'][next(iter(model['weights']))]}
    if not known:
        return {'status': 'fallback', 'label': model['majority'], 'reason': 'no_in_vocabulary_tokens'}
    scores = {label: prior + sum(model['weights'][label][key] * value for key, value in known.items())
              for label, prior in model['priors'].items()}
    best = min(scores, key=lambda label: (-scores[label], int(label)))
    maximum = max(scores.values())
    total = sum(math.exp(value - maximum) for value in scores.values())
    return {'status': 'predicted', 'label': int(best), 'route': 'multinomial-naive-bayes',
            'uncalibrated_probability': math.exp(scores[best] - maximum) / total,
            'token_coverage': sum(known.values()) / sum(words.values())}


def metrics(results):
    require(results, 'no held-out classification rows')
    matrix = {str(a): {str(b): 0 for b in LABELS} for a in LABELS}
    for row in results:
        matrix[str(row['actual'])][str(row['label'])] += 1
    f1 = []
    for label in map(str, LABELS):
        tp = matrix[label][label]
        fp = sum(matrix[a][label] for a in matrix if a != label)
        fn = sum(matrix[label][b] for b in matrix if b != label)
        f1.append(2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0)
    return {'n': len(results), 'accuracy': sum(row['actual'] == row['label'] for row in results) / len(results),
            'mae': statistics.mean(abs(row['actual'] - row['label']) for row in results),
            'macro_f1_all_five_labels': statistics.mean(f1), 'confusion': matrix,
            'fallbacks': sum(row['status'] == 'fallback' for row in results)}


def evaluate(model, rows, baseline=False):
    results = [{key: row[key] for key in ('id', 'group', 'language')} |
               {'actual': row['label']} | predict(model, row['text'], baseline) for row in rows]
    report = metrics(results)
    report['languages'] = {language: metrics([row for row in results if row['language'] == language])
                           for language in sorted({row['language'] for row in results})}
    report['results'] = results
    return report


def group_accuracy_interval(results):
    groups = defaultdict(list)
    for row in results:
        groups[row['group']].append(row)
    identifiers, rng, values = sorted(groups), random.Random(371), []
    for _ in range(200):
        sample = [row for _ in identifiers for row in groups[rng.choice(identifiers)]]
        values.append(sum(row['actual'] == row['label'] for row in sample) / len(sample))
    values.sort()
    return [values[4], values[195]]


def run(source, out):
    clock = time.monotonic()
    out = private_root(out)
    rows, quarantine, papers = read_rows(source)
    parts = {part: [row for row in rows if row['split'] == part] for part in ('train', 'validation', 'test')}
    require(all(parts.values()), 'one declared group split is empty')
    candidates = []
    for mode in ('word', 'word_char'):
        for alpha in (0.5, 1.0):
            model = fit(parts['train'], mode, alpha)
            score = evaluate(model, parts['validation'])
            candidates.append({'mode': mode, 'alpha': alpha, 'validation': {key: value for key, value in score.items() if key != 'results'}})
    selected = min(candidates, key=lambda row: (-row['validation']['macro_f1_all_five_labels'], row['validation']['mae']))
    # The holdout is never used to tune the model or build the vocabulary.
    model = fit(parts['train'], selected['mode'], selected['alpha'])
    model.update(source_sha256=sha_file(source), study_sha256=sha_file(Path(__file__).with_name('STUDY.json')),
                 source_languages=dict(Counter(row['language'] for row in rows)))
    baseline = evaluate(model, parts['test'], True)
    candidate = evaluate(model, parts['test'])
    protected = {'accuracy': candidate['accuracy'] >= baseline['accuracy'],
                 'mae': candidate['mae'] <= baseline['mae'],
                 'macro_f1': candidate['macro_f1_all_five_labels'] >= baseline['macro_f1_all_five_labels']}
    model['admission'] = {'candidate_admitted': all(protected.values()), 'protected_holdout_metrics': protected,
                           'consumer_default': 'candidate' if all(protected.values()) else 'training-majority',
                           'reason': 'No aggregate compensation for an observed protected metric loss'}
    atomic_json(out / 'model.json', model)
    baseline['group_bootstrap_accuracy_interval_95'] = group_accuracy_interval(baseline['results'])
    candidate['group_bootstrap_accuracy_interval_95'] = group_accuracy_interval(candidate['results'])
    splits = {part: {'n': len(values), 'groups': len({r['group'] for r in values}),
                      'languages': dict(Counter(r['language'] for r in values)),
                      'labels': dict(Counter(r['label'] for r in values)), 'ids': [r['id'] for r in values]}
              for part, values in parts.items()}
    # Denominator and source-group controls are useful independently of the score.
    require(sum(len(values) for values in parts.values()) + len(quarantine) ==
            sum(len(p['review']) for p in load_json(source)['paper']), 'source denominator lost')
    forbidden_probe = dict(parts['test'][0], evaluation=2, confidence=5, preliminary_decision='accept')
    require(predict(model, forbidden_probe['text']) == predict(model, parts['test'][0]['text']),
            'outcome columns influenced text-only predictor')
    report = {'schema': 'atelier.actual-review-evaluation/1', 'source_sha256': sha_file(source),
              'study_sha256': model['study_sha256'], 'model_sha256': sha_file(out / 'model.json'),
              'source_papers': papers, 'source_reviews': len(rows) + len(quarantine),
              'usable': len(rows), 'quarantine': quarantine, 'split_manifest': splits,
              'validation_candidates': candidates, 'selected': {k: selected[k] for k in ('mode', 'alpha')},
              'baseline': baseline, 'candidate': candidate,
              'admission': model['admission'],
              'negative_controls': {'outcome_columns_do_not_enter_predictor': True,
                                    'train_vocabulary_only': True, 'paper_and_exact_duplicate_group_overlap': False,
                                    'empty_input': predict(model, '')},
              'resources': observed_resources(clock),
              'limits': ['Human source orientation is subjective perceived polarity, not confirmed reviewer intent',
                         'English has only17 source examples; report subgroup counts, not general English accuracy',
                         'Raw NB probabilities are not calibrated', 'No reviewer-evaluation/confidence/acceptance/remarks features',
                         'No model deployment, Codex-issue human labels, LLM tuning or LoRA claim']}
    atomic_json(out / 'review-report.json', report)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    train = sub.add_parser('fit')
    train.add_argument('--source', required=True)
    train.add_argument('--out', required=True)
    serve = sub.add_parser('predict')
    serve.add_argument('--model', required=True)
    serve.add_argument('--text-file', required=True)
    serve.add_argument('--language', choices=('en', 'es'), required=True)
    serve.add_argument('--candidate-for-analysis', action='store_true',
                       help='Inspect rejected candidate explicitly; never changes default admission')
    args = parser.parse_args()
    if args.command == 'fit':
        report = run(args.source, args.out)
        print(json.dumps({'source_reviews': report['source_reviews'], 'usable': report['usable'],
                          'quarantined': len(report['quarantine']), 'selected': report['selected'],
                          'baseline': {k: report['baseline'][k] for k in ('n', 'accuracy', 'mae', 'macro_f1_all_five_labels')},
                          'candidate': {k: report['candidate'][k] for k in ('n', 'accuracy', 'mae', 'macro_f1_all_five_labels')},
                          'language_counts': {k: v['n'] for k, v in report['candidate']['languages'].items()},
                          'resources': report['resources']}))
    else:
        model = load_json(args.model)
        use_candidate = model['admission']['candidate_admitted'] or args.candidate_for_analysis
        result = predict(model, Path(args.text_file).read_text(encoding='utf-8'), baseline=not use_candidate)
        result['candidate_admission'] = model['admission']
        result['requires_human_review'] = not model['admission']['candidate_admitted'] or model['source_languages'].get(args.language, 0) < 30
        result['target'] = model['target']
        print(json.dumps(result, allow_nan=False))
