"""Check actual native artifacts, compare outputs, preserve the simpler route.

This is structural/observational assessment, not independent review or human
truth. It never trains, activates a model, calls a provider or touches base bytes.
"""
import argparse
from collections import Counter
import copy
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'data-ml'))
from common import atomic_json, canonical, load_json, private_root, require, sha_bytes, sha_file
from safe_model import file_pin, inspect_directory, inspect_weights
from native_trial import CATEGORIES, metrics, primary, rule_predictions


def signature_matches(signature, expected):
    require(canonical(signature) == canonical(expected), 'signature/base/tokenizer/adapter/runtime binding mismatch')
    return True


def run(args):
    out = private_root(args.out)
    plan, selection = load_json(out / 'frozen-plan.json'), load_json(out / 'selection.json')
    data, gap = load_json(out / 'data.json'), load_json(out / 'gap.json')
    evaluations = {key: load_json(out / (key + '-evaluation.json')) for key in ('base', 'adapter', 'merged', 'quantized4')}
    seed_reports = {key: load_json(out / ('seed-' + str(key)) / 'training-report.json') for key in (7, 19)}
    for pin in plan['source_files']:
        require(file_pin(Path(args.model) / pin['name']) == pin, 'original base/tokenizer files changed')
    require(sum(row['iterations'] for row in seed_reports.values()) == 60, 'training iteration denominator changed')
    require(all(row['agreement']['n'] == 20 for row in evaluations.values()), 'original20heldout denominator changed')
    roots = {'base': Path(args.model), 'adapter': Path(args.model), 'merged': out / 'merged', 'quantized4': out / 'quantized4'}
    for key, evaluation in evaluations.items():
        for pin in evaluation['runtime_files']:
            require(file_pin(roots[key] / pin['name']) == pin, 'runtime bytes differ from actual inference proof')
        require(evaluation['frozen_plan_sha256'] == sha_file(out / 'frozen-plan.json')
                and evaluation['selection_sha256'] == sha_file(out / 'selection.json'), 'inference belongs to another plan/selection')
    adapter = out / ('seed-' + str(selection['seed'])) / 'adapters.safetensors'
    require(file_pin(adapter) == selection['adapter'] == evaluations['adapter']['adapter'], 'adapter inference pin mismatch')
    reference = load_json(Path(args.rt05) / 'HELDOUT-INDEPENDENT.json')
    require(sha_file(Path(args.rt05) / 'HELDOUT-INDEPENDENT.json') == plan['independent_heldout_sha256'], 'reference changed')
    refs = {row['number']: primary(row['categories']) for row in reference['items']}
    rows = [{**row, 'label': refs[row['number']]} for row in data['test'] if row['number'] in refs]
    require(len(rows) == 20, 'protected reference rows lost')
    lexicon = load_json(Path(args.rt05) / 'BASELINE-LEXICON.json')
    keyword = rule_predictions(rows, lexicon)
    counts = Counter(row['label'] for row in data['train'])
    majority = min(counts, key=lambda label: (-counts[label], label))
    majority_rows = [{'number': row['number'], 'actual': row['label'], 'label': majority} for row in rows]
    scores = {'reuse-keywords': metrics(keyword), 'training-majority-sanity': metrics(majority_rows),
              **{key: value['agreement'] for key, value in evaluations.items()}}
    lookup = {key: {row['number']: row for row in value['predictions']} for key, value in evaluations.items()}
    parity = {}
    for key in ('merged', 'quantized4'):
        differing = [number for number in lookup['adapter'] if lookup['adapter'][number]['label'] != lookup[key][number]['label']]
        maximum_delta = max(abs(a - b) for number in lookup['adapter']
                            for a, b in zip(lookup['adapter'][number]['label_logits'], lookup[key][number]['label_logits']))
        parity[key] = {'against': 'actual adapter route', 'class_differences': len(differing),
                       'heldout_rows': 20, 'differing_ids': differing, 'max_label_logit_absolute_delta': maximum_delta,
                       'free_generation_same': evaluations[key]['free_generation_probe']['text'] == evaluations['adapter']['free_generation_probe']['text']}
    signatures = {}
    for key, value in evaluations.items():
        signatures[key] = {'schema': 'atelier.actual-native-signature/1', 'variant': key,
                           'task': 'untrusted issue text to one mechanically prioritized taxonomy digit1..9',
                           'input_max_prompt_tokens': 188, 'output': 'constrained next-token class; separate max4token free-generation probe',
                           'taxonomy_priority': CATEGORIES, 'prompt': gap['selected_prompt'],
                           'frozen_plan_sha256': sha_file(out / 'frozen-plan.json'),
                           'execution_revision_sha256': sha_file(out / 'execution-revision.json'),
                           'runtime_files': value['runtime_files'], 'adapter': value['adapter'],
                           'actual_inference_sha256': sha_file(out / (key + '-evaluation.json'))}
        atomic_json(out / (key + '-signature.json'), signatures[key])
        signature_matches(load_json(out / (key + '-signature.json')), signatures[key])
    negatives = {}
    try:
        inspect_weights(Path(args.model) / 'model.safetensors', expected_sha256='0' * 64)
    except ValueError as error:
        negatives['actual_wrong_base_sha_rejected'] = str(error)
    for kind in ('base', 'tokenizer', 'adapter', 'inference'):
        changed = copy.deepcopy(signatures['adapter'])
        if kind == 'adapter':
            changed['adapter']['sha256'] = '0' * 64
        elif kind == 'inference':
            changed['actual_inference_sha256'] = '0' * 64
        else:
            name = 'model.safetensors' if kind == 'base' else 'tokenizer.json'
            next(row for row in changed['runtime_files'] if row['name'] == name)['sha256'] = '0' * 64
        try:
            signature_matches(changed, signatures['adapter'])
        except ValueError as error:
            negatives[kind + '_signature_change_rejected'] = str(error)
    require(len(negatives) == 5, 'actual signature negative control escaped')
    current_route = load_json(out / 'active-route.json')
    require(current_route == {'route': 'existing-owner-human-review', 'candidate_active': False}, 'candidate silently activated')
    before = sha_file(out / 'active-route.json')
    # The candidate rejection leaves the original route alone, then a fresh
    # structural read checks both route and native base rollback dependencies.
    inspect_directory(args.model, expected_sha256=plan['model']['weights']['sha256'])
    require(before == sha_file(out / 'active-route.json'), 'rollback pointer mutated')
    tests = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', str(Path(__file__).parent), '-p', 'test_loader.py', '-v'],
                           capture_output=True, timeout=30)
    require(tests.returncode == 0, 'loader tests failed')
    (out / 'loader-tests.log').write_bytes(tests.stdout + tests.stderr)
    baseline = max(('reuse-keywords', 'training-majority-sanity', 'base'), key=lambda key: (scores[key]['accuracy'], scores[key]['macro_f1_nine_labels']))
    preserved_metrics = {key: scores['adapter'][key] >= scores[baseline][key] for key in ('accuracy', 'macro_f1_nine_labels')}
    report = {'schema': 'atelier.actual-native-assessment/1', 'frozen_plan_sha256': sha_file(out / 'frozen-plan.json'),
              'execution_revision_sha256': sha_file(out / 'execution-revision.json'),
              'implementation': file_pin(Path(__file__).with_name('native_trial.py')),
              'loader': file_pin(Path(__file__).with_name('safe_model.py')), 'assessment': file_pin(__file__),
              'source_counts': plan['counts'], 'original_heldout_n': 20, 'native_training_iterations': 60,
              'selected_seed': selection['seed'], 'validation': {str(k): v['validation'] for k, v in seed_reports.items()},
              'heldout_ai_agreement': scores, 'serving_parity': parity, 'negative_controls': negatives,
              'best_simpler_route': baseline, 'preserved_metrics_against_best_simpler': preserved_metrics,
              'candidate_operationally_admitted': False,
              'reason': 'No justified accuracy/complexity benefit over simpler route; weak AI labels and20samples do not establish production or human accuracy',
              'active_route': current_route, 'rollback_route_sha256_unchanged': before,
              'base_and_tokenizer_unchanged': True, 'new_training_retries': 0,
              'seed7_reconciliation': seed_reports[7]['reconciliation'],
              'resources': {key: value['resources'] for key, value in evaluations.items()},
              'native_training_wall_upper_bound_seconds': sum(v['training_wall_upper_bound_seconds'] for v in seed_reports.values()),
              'retained_trial_bytes': sum(p.stat().st_size for p in out.rglob('*') if p.is_file()),
              'signature_pins': {key: file_pin(out / (key + '-signature.json')) for key in signatures},
              'loader_tests': {'passed': 5, 'log_sha256': sha_file(out / 'loader-tests.log')},
              'new_spending': 0, 'model_or_dependency_download_by_this_worker': 0,
              'limits': ['Actual native Metal training/export/load/inference; not CPU proxy, JSON weights or human truth',
                         'Original20protected labels are independent AI judgments, not human adjudication',
                         'Primary label is a fixed priority collapse of multilabel semantics and can obscure main need',
                         'Majority sanity comparator was added after seed7, before seed19/heldout; never used to retune',
                         'Seed7exact old telemetry was not persisted; old per-step guards passed and checkpoint/log are preserved',
                         'No model installed as operational default, external deployment, paying users or open-model superiority claim',
                         'Independent review and original full-case acceptance remain separate']}
    atomic_json(out / 'ASSESSMENT.json', report)
    return {'scores': scores, 'parity': parity, 'operationally_admitted': False,
            'retained_bytes': report['retained_trial_bytes'], 'assessment_sha256': sha_file(out / 'ASSESSMENT.json')}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True)
    parser.add_argument('--model', required=True)
    parser.add_argument('--rt05', required=True)
    import json
    print(json.dumps(run(parser.parse_args()), allow_nan=False))
