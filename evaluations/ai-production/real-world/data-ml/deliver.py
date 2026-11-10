"""Deliver an actual private JSON model bundle and replay its copied consumer.

Reviewed standard-library source only. JSON is data; no pickle, remote code,
provider SDK, framework install or model deserialization code is fetched.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
from common import atomic_json, load_json, observed_resources, private_root, require, sha_file


def validate_bundle(root):
    root = Path(root).resolve()
    manifest = load_json(root / 'bundle-manifest.json')
    require(manifest['schema'] == 'atelier.actual-json-model-bundle/2', 'unknown bundle format')
    require(len(manifest['files']) == 11, 'missing model/runtime/signature/source delivery')
    # Reject import shadowing and bytecode before executing copied Python. New
    # bundles run with -B; existing __pycache__ is never trusted or auto-deleted.
    members = {pin['path'] for pin in manifest['files']} | {'bundle-manifest.json'}
    require({p.name for p in root.iterdir()} == members
            and all(p.is_file() and not p.is_symlink() for p in root.iterdir()),
            'unlisted code, symlink or directory (including __pycache__) in delivered bundle')
    paths = set()
    for pin in manifest['files']:
        relative = Path(pin['path'])
        require(not relative.is_absolute() and '..' not in relative.parts and pin['path'] not in paths,
                'unsafe or duplicate bundle member')
        path = root / relative
        require(not path.is_symlink() and path.is_file() and path.resolve().is_relative_to(root), 'unsafe bundle member')
        require(path.stat().st_size == pin['bytes'] <= 5 * 1024 * 1024 and sha_file(path) == pin['sha256'], 'bundle bytes differ')
        paths.add(pin['path'])
        if path.suffix == '.json':
            load_json(path)
    required = {'forecast.py', 'reviews.py', 'common.py', 'consumer.py', 'source_guards.py', 'STUDY.json',
                'forecast-model.json', 'review-model.json', 'day.csv', 'signature.json', 'MODEL-CARD.json'}
    require(paths == required, 'delivered files differ from required signature/runtime')
    signature = load_json(root / 'signature.json')
    require(signature['forecast_weights_sha256'] == sha_file(root / 'forecast-model.json')
            and signature['review_weights_sha256'] == sha_file(root / 'review-model.json'), 'signature rebound to other weights')
    return manifest


def run(args):
    start = time.monotonic()
    out = private_root(args.out)
    bundle = out / 'bundle'
    bundle.mkdir(mode=0o700)
    for name in ('forecast.py', 'reviews.py', 'common.py', 'consumer.py', 'source_guards.py', 'STUDY.json'):
        shutil.copyfile(Path(__file__).with_name(name), bundle / name)
    shutil.copyfile(args.forecast_model, bundle / 'forecast-model.json')
    shutil.copyfile(args.review_model, bundle / 'review-model.json')
    shutil.copyfile(args.source, bundle / 'day.csv')
    fm, rm = load_json(args.forecast_model), load_json(args.review_model)
    signature = {'forecast': {'input': {'date': 'ISO local calendar day'}, 'output': ['status', 'prediction', 'interval'],
                               'unit': 'rentals/day', 'validation_period': fm['validated_period'],
                               'interval_admission': fm['interval_admission'], 'requires_human_review': True},
                 'review': {'input': {'text': 'nonempty Unicode <=2000characters', 'language': 'en|es'},
                            'target': rm['target'], 'default_route': rm['admission']['consumer_default'],
                            'candidate_admitted': rm['admission']['candidate_admitted']},
                 'forecast_weights_sha256': sha_file(args.forecast_model),
                 'review_weights_sha256': sha_file(args.review_model)}
    atomic_json(bundle / 'signature.json', signature)
    atomic_json(bundle / 'MODEL-CARD.json', {
        'source_licenses': [{'doi': '10.24432/C5W894', 'license': 'CC-BY-4.0', 'creator': 'Hadi Fanaee-T'},
                            {'doi': '10.24432/C50G60', 'license': 'CC-BY-4.0', 'creator': 'Brian Keith'}],
        'format': 'bounded reviewed JSON coefficients and counts, no executable model serialization',
        'forecast': 'Historical2012 holdout only; actual reporting delay unobserved; no contemporary accuracy guarantee',
        'review': 'Candidate rejected for accuracy regression; default majority plus human review; English subgroup too small',
        'deployment': 'Ephemeral loopback test only; no production SLA, current users, CPA, LoRA or provider claim'})
    files = [{'path': path.name, 'sha256': sha_file(path), 'bytes': path.stat().st_size}
             for path in sorted(bundle.iterdir()) if path.is_file()]
    atomic_json(bundle / 'bundle-manifest.json', {'schema': 'atelier.actual-json-model-bundle/2',
                                                'files': files, 'remote_code': False, 'loader': 'reviewed stdlib JSON'})
    validate_bundle(bundle)
    proof = out / 'copied-consumer'
    result = subprocess.run([sys.executable, '-E', '-B', str(bundle / 'consumer.py'), 'exercise',
                             '--forecast-model', str(bundle / 'forecast-model.json'),
                             '--review-model', str(bundle / 'review-model.json'), '--source', str(bundle / 'day.csv'),
                             '--out', str(proof)], capture_output=True, timeout=20)
    require(result.returncode == 0, 'copied bundle consumer failed: ' + result.stderr.decode()[-400:])
    with tempfile.TemporaryDirectory(prefix='atelier-tampered-') as temporary:
        changed = Path(temporary) / 'bundle'
        shutil.copytree(bundle, changed)
        with (changed / 'review-model.json').open('ab') as stream:
            stream.write(b' ')
        try:
            validate_bundle(changed)
        except ValueError as error:
            rejected = str(error)
        else:
            raise ValueError('changed delivered weights reused old bundle proof')
    report = {'bundle_manifest_sha256': sha_file(bundle / 'bundle-manifest.json'),
              'signature_sha256': sha_file(bundle / 'signature.json'), 'delivered_files': files,
              'copied_consumer_report_sha256': sha_file(proof / 'consumer-report.json'),
              'fresh_copied_consumer': load_json(proof / 'consumer-report.json'),
              'tampered_weights_rejected': rejected, 'resources': observed_resources(start),
              'limits': ['Same Mac and Python runtime in a separate process, not cross-device certification or production deployment']}
    atomic_json(out / 'delivery-report.json', report)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--forecast-model', required=True)
    parser.add_argument('--review-model', required=True)
    parser.add_argument('--source', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    report = run(args)
    print(json.dumps({'delivered_files': len(report['delivered_files']),
                      'tampered_weights_rejected': report['tampered_weights_rejected'], 'resources': report['resources']}))
