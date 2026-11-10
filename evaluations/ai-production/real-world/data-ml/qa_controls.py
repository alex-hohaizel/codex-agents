"""Frozen controlled oracles joined to actual source/model/HTTP evidence.

No new data acquisition, fit, heldout tuning, registry or actual license withdrawal.
Controls are explicitly counterfactual, not additional business-accuracy scores.
"""
import argparse
from collections import Counter
import copy
from pathlib import Path
import shutil
from types import SimpleNamespace
import json
from common import atomic_json, load_json, private_root, require, sha_file
from analyze_issues import clusters
from deliver import run as deliver, validate_bundle


def freeze(args):
    out = private_root(args.out)
    require(not (out / 'ORACLE.json').exists(), 'oracle already frozen; retain old failures')
    source = load_json(args.corpus)['rows']
    selected, seen = [], set()
    for row in sorted(source, key=lambda r: r['number']):
        if row['author_group'] not in seen:
            selected.append(row)
            seen.add(row['author_group'])
        if len(selected) == 20:
            break
    require(len(selected) == 20, 'real-source cohort denominator missing')
    cohort = [{'id': str(row['id']), 'author': row['author_group'], 'theme': 'alpha' if i < 6 else 'beta'}
              for i, row in enumerate(selected)]
    words = ['offline draft restoration', 'invoice settlement transfer', 'viewport keyboard navigation']
    lexical = [{'id': cohort[i]['id'], 'title': words[i // 2], 'body': words[i // 2]} for i in range(6)]
    oracle = {'schema': 'atelier.frozen-a06-a09-boundary-oracle/1',
              'kind': 'Controlled synthetic theme/text/history oracle using fixed real-source IDs; not new human labels',
              'corpus_sha256': sha_file(args.corpus), 'real_analysis_sha256': sha_file(args.analysis),
              'actual_two_week_counts_sha256': sha_file(args.counts),
              'implementation_sha256': sha_file(__file__),
              'cohort': cohort, 'lexical_rows': lexical,
              'outlier_lexical': {'id': str(selected[6]['id']), 'title': 'uniquex planetz spectrometerz', 'body': ''},
              'expected': {'stable_pairs': [[cohort[i]['id'], cohort[i + 1]['id']] for i in (0, 2, 4)],
                           'lexical_outlier_noise_ids': [str(selected[6]['id'])],
                           'stable_author_weighted_alpha_share': .3, 'stable_raw_alpha_share': .3,
                           'outlier_copies': 90, 'outlier_raw_alpha_share': 96 / 110,
                           'outlier_weighted_alpha_share': .3,
                           'coverage_before_expected_ids': [r['id'] for r in cohort],
                           'coverage_after_observed_ids': [r['id'] for r in cohort[:10]],
                           'coverage_change_verdict': 'abstain'},
              'intermittent_history': {'route': '/forecast/intermittent-control', 'date': '2012-10-01',
                                      'counterfactual_lag2_through_lag8_counts': [0] * 7,
                                      'expected': 'abstained:intermittent_history_not_validated'},
              'lineage': {'positive': 'actual copied source→actual model→actual prediction signature→HTTP output',
                          'changed_source': 'append newline to isolated source copy; deny before model invocation',
                          'withdrawal': 'isolated project-test policy only; deny before model invocation',
                          'expected_added_model_calls_for_changed_or_withdrawn': 0}}
    atomic_json(out / 'ORACLE.json', oracle)
    return {'oracle_sha256': sha_file(out / 'ORACLE.json'), 'cohort_ids': [r['id'] for r in cohort], 'run_performed': False}


def weighted_share(rows):
    authors = Counter(row['author'] for row in rows)
    weights = [1 / authors[row['author']] for row in rows]
    return sum(weight for row, weight in zip(rows, weights) if row['theme'] == 'alpha') / sum(weights)


def compare_coverage(before, after, expected_ids):
    if {r['id'] for r in before} != set(expected_ids) or {r['id'] for r in after} != set(expected_ids):
        return {'verdict': 'abstain', 'reason': 'declared cohort coverage changed; do not infer a trend from raw shares',
                'before_rows': len(before), 'after_rows': len(after), 'expected_rows': len(expected_ids)}
    return {'verdict': 'comparable', 'weighted_alpha_change': weighted_share(after) - weighted_share(before)}


def run(args):
    out = private_root(args.out)
    require(not (out / 'QA-REPORT.json').exists(), 'do not overwrite observed controls')
    oracle = load_json(out / 'ORACLE.json')
    require(oracle['implementation_sha256'] == sha_file(__file__) and oracle['corpus_sha256'] == sha_file(args.corpus)
            and oracle['real_analysis_sha256'] == sha_file(args.analysis)
            and oracle['actual_two_week_counts_sha256'] == sha_file(args.counts), 'frozen oracle/source changed')
    expected = oracle['expected']
    stable, noise, _ = clusters(oracle['lexical_rows'], .25)
    with_outlier, outlier_noise, _ = clusters([*oracle['lexical_rows'], oracle['outlier_lexical']], .25)
    pairset = lambda rows: {tuple(sorted(row)) for row in rows}
    observed = {'stable_pairs': stable, 'stable_noise': noise, 'with_outlier_pairs': with_outlier,
                'with_outlier_noise': outlier_noise}
    checks = {'frozen_stable_theme_pairs': pairset(stable) == pairset(expected['stable_pairs']) and not noise,
              'outlier_does_not_reassign_stable_theme': pairset(with_outlier) == pairset(expected['stable_pairs'])
                and outlier_noise == expected['lexical_outlier_noise_ids']}
    cohort = oracle['cohort']
    repeated = [*cohort, *[{**cohort[0], 'id': 'declared-outlier-copy-' + str(i)} for i in range(90)]]
    observed.update(stable_weighted=weighted_share(cohort), outlier_weighted=weighted_share(repeated),
                    outlier_raw=sum(r['theme'] == 'alpha' for r in repeated) / len(repeated),
                    coverage=compare_coverage(cohort, cohort[:10], expected['coverage_before_expected_ids']))
    checks['author_outlier_weight_retained'] = abs(observed['outlier_weighted'] - .3) < 1e-12 and abs(observed['outlier_raw'] - 96 / 110) < 1e-12
    checks['coverage_shift_abstains'] = observed['coverage']['verdict'] == expected['coverage_change_verdict']
    atomic_json(out / 'A06-ORACLE-RESULTS.json', {'oracle_sha256': sha_file(out / 'ORACLE.json'),
                                                'observations': observed, 'checks': checks,
                                                'real100_analysis_sha256': sha_file(args.analysis),
                                                'real_two_week_counts_sha256': sha_file(args.counts),
                                                'claim': 'Controlled oracle behavior, not semantic accuracy or real historical cohort expansion'})
    require(all(checks.values()), 'frozen theme/coverage/outlier oracle failed; results retained')
    old = load_json(args.forecast_model)
    revised = copy.deepcopy(old)
    revised['inference_source_sha256'] = sha_file(Path(__file__).with_name('forecast.py'))
    revised['inference_admission_revision'] = {'parent_model_sha256': sha_file(args.forecast_model),
                                               'change': 'Unsupported intermittent history abstains; coefficients/selection unchanged',
                                               'new_training_performed': False}
    require({k: v for k, v in revised.items() if k not in ('inference_source_sha256', 'inference_admission_revision')} ==
            {k: v for k, v in old.items() if k != 'inference_source_sha256'}, 'model coefficients or fit choices changed')
    atomic_json(out / 'forecast-admission-revision.json', revised)
    atomic_json(out / 'MODEL-REVISION.json', {'parent_model_sha256': sha_file(args.forecast_model),
                                            'new_model_sha256': sha_file(out / 'forecast-admission-revision.json'),
                                            'weights_scaling_selection_unchanged': True, 'new_fit_or_heldout_tuning': False,
                                            'new_inference_sha256': revised['inference_source_sha256']})
    delivery = deliver(SimpleNamespace(forecast_model=str(out / 'forecast-admission-revision.json'),
                                       review_model=args.review_model, source=args.source, out=str(out / 'delivery')))
    bundle = out / 'delivery/bundle'
    # Actual owned bundle copies are never altered. Add benign canaries only in
    # isolated clones and validate BEFORE any execution/import of their code.
    import tempfile
    unsafe = {}
    for kind in ('shadow_module', 'bytecode_directory', 'symlink'):
        with tempfile.TemporaryDirectory(prefix='atelier-bundle-negative-') as temporary:
            copyroot = Path(temporary) / 'bundle'
            shutil.copytree(bundle, copyroot)
            if kind == 'shadow_module':
                (copyroot / 'json.py').write_text('raise RuntimeError("must never import")')
            elif kind == 'bytecode_directory':
                (copyroot / '__pycache__').mkdir()
                (copyroot / '__pycache__/json.cpython-313.pyc').write_bytes(b'never load attacker bytecode')
            else:
                (copyroot / 'shadow.py').symlink_to(copyroot / 'common.py')
            try:
                validate_bundle(copyroot)
            except ValueError as error:
                unsafe[kind] = str(error)
    require(len(unsafe) == 3, 'unlisted bundle content admitted')
    consumer = load_json(out / 'delivery/copied-consumer/consumer-report.json')
    require(consumer['actual_source_model_signature_lineage']['changed_source_model_invocations_added'] == 0
            and consumer['actual_source_model_signature_lineage']['withdrawn_source_model_invocations_added'] == 0
            and consumer['intermittent_history_control']['actual_consumer_abstained'], 'actual consumer boundary failed')
    report = {'schema': 'atelier.actual-data-ml-qa-closures/1', 'oracle_sha256': sha_file(out / 'ORACLE.json'),
              'a06_results_sha256': sha_file(out / 'A06-ORACLE-RESULTS.json'), 'a06_checks': checks,
              'model_revision_sha256': sha_file(out / 'MODEL-REVISION.json'),
              'actual_copied_consumer_report_sha256': sha_file(out / 'delivery/copied-consumer/consumer-report.json'),
              'source_model_signature_HTTP_guard': consumer['actual_source_model_signature_lineage'],
              'actual_intermittent_consumer': consumer['intermittent_history_control'],
              'unlisted_bundle_negatives_before_execution': unsafe,
              'new_fit_or_weights_or_heldout_tuning': False, 'old_receipts_preserved': True,
              'limits': ['Controlled intermittent/theme/outlier/coverage/withdrawal fixtures are not real-data accuracy',
                         'Original100issue analysis, real2weekcounts, fitted models and original denominators remain separate',
                         'Project-test withdrawal does not revoke the public UCI license',
                         'Independent review and case acceptance separately owned']}
    atomic_json(out / 'QA-REPORT.json', report)
    return {'a06_checks': checks, 'consumer_guard': report['source_model_signature_HTTP_guard'],
            'intermittent': report['actual_intermittent_consumer'], 'unsafe_bundle_controls': unsafe,
            'qa_report_sha256': sha_file(out / 'QA-REPORT.json')}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('freeze', 'run'))
    for name in ('out', 'corpus', 'analysis', 'counts'):
        parser.add_argument('--' + name, required=True)
    parser.add_argument('--forecast-model')
    parser.add_argument('--review-model')
    parser.add_argument('--source')
    args = parser.parse_args()
    print(json.dumps(freeze(args) if args.command == 'freeze' else run(args), allow_nan=False))
