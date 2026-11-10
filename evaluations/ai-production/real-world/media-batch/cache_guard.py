"""Consume a prior campaign batch only with its externally retained exact receipt pin."""
import argparse
from pathlib import Path
from campaign_batch import source_state, verify_cached
from common import atomic_json, private_root, require, sha_file


def check(out, expected_report_sha256):
    require(sha_file(out / 'batch-report.json') == expected_report_sha256,
            'old batch proof cannot be rebound to changed receipt bytes')
    _, data, artwork, inputs = source_state()
    report = verify_cached(out, inputs)
    logical = {lang + ':' + row['id'] for lang in ('en', 'uk') for row in data['materials']}
    physical = {key + '/' + variant for key in logical for variant in ('full', 'compact')}
    require(len(report['logical_items']) == len(logical) and {r['key'] for r in report['logical_items']} == logical,
            'cached logical item membership/locale changed')
    require(len(report['physical_variants']) == len(physical) and {r['key'] for r in report['physical_variants']} == physical,
            'cached physical variants changed')
    for row in report['logical_items']:
        require(row['master'] in artwork[row['locale']].values(), 'cached master not in exact accepted locale source')
    return {'verified_report_sha256': expected_report_sha256, 'logical_items': 20, 'physical_variants': 40,
            'rendered_page_artifacts_reused': 40, 'new_renders': 0, 'new_provider_calls': 0,
            'incremental_provider_fees': 0, 'historical_procurement_and_full_TCO': 'unknown, not zero'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True)
    parser.add_argument('--expected-report-sha256', required=True)
    args = parser.parse_args()
    root = private_root(args.out)
    result = check(root, args.expected_report_sha256)
    atomic_json(root / 'guarded-cache-report.json', result)
    import json
    print(json.dumps(result))
