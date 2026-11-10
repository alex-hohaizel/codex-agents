"""Reproduce the approved campaign privately, render every PDF page, cache exact bytes.

No artwork editing, generative-provider call, upload or installed runtime. The
existing campaign producer and its lossless RGB verification remain authoritative.
"""
import argparse
from datetime import datetime, timezone
import importlib.util
import json
import math
from pathlib import Path
import resource
import shutil
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'data-ml'))
from common import atomic_json, canonical, load_json, private_root, require, sha_file

REPO = Path(__file__).resolve().parents[4]


def pin(path, root):
    return {'path': path.relative_to(root).as_posix(), 'bytes': path.stat().st_size, 'sha256': sha_file(path)}


def ledger_check(expected, outcomes, attempts):
    """Small batch accounting assertion, not a scheduler or provider worker."""
    require(len(expected) == len(set(expected)), 'duplicate planned item/variant')
    require(len(outcomes) == len(expected) and {r['key'] for r in outcomes} == set(expected), 'missing/duplicate/unplanned outcome')
    require(all(r['status'] in ('accepted', 'rejected', 'failed', 'cancelled', 'outcome_unknown') for r in outcomes), 'invalid outcome status')
    ids = set()
    for attempt in attempts:
        require(attempt['id'] not in ids and attempt['key'] in expected, 'duplicate attempt or wrong item/variant')
        ids.add(attempt['id'])
        require(attempt['status'] in ('succeeded', 'known_failure', 'rejected', 'cancelled', 'dispatched', 'outcome_unknown'), 'unknown attempt status')
        if attempt.get('retry_requested'):
            require(attempt['status'] in ('known_failure', 'rejected') and attempt.get('safe_retry_policy') == 'known-failure-only',
                    'inflight/unknown/cancelled outcome cannot be automatically replayed')
            require(type(attempt.get('retry_number')) is int and type(attempt.get('max_retries')) is int
                    and 1 <= attempt['retry_number'] <= attempt['max_retries'] <= 1, 'retry budget exceeded')
        cost = attempt.get('known_cost')
        require(cost is None or type(cost) in (int, float) and math.isfinite(cost) and cost >= 0, 'invalid known cost')
    accepted = sum(r['status'] == 'accepted' for r in outcomes)
    known_cost = sum(a.get('known_cost') or 0 for a in attempts)
    complete_cost = all(a.get('known_cost') is not None for a in attempts)
    return {'planned_variants': len(expected), 'outcomes': len(outcomes), 'accepted_variants': accepted,
            'attempts': len(attempts), 'rejected_attempts': sum(a['status'] == 'rejected' for a in attempts),
            'known_cost_total': known_cost, 'cost_complete': complete_cost,
            'known_cost_per_accepted_variant': known_cost / accepted if accepted else None,
            'full_unit_cost': known_cost / accepted if accepted and complete_cost else None,
            'unknown_outcomes': sum(a['status'] in ('outcome_unknown', 'dispatched') for a in attempts)}


def controlled_boundaries():
    """Declared fake-provider controls: these amounts are NOT real invoices."""
    expected = ['control:A/en', 'control:B/uk', 'control:C/en', 'control:D/uk']
    outcomes = [{'key': key, 'status': value} for key, value in zip(expected, ('accepted', 'rejected', 'cancelled', 'outcome_unknown'))]
    attempts = [
        {'id': 'a1', 'key': expected[0], 'status': 'known_failure', 'known_cost': .02,
         'retry_requested': True, 'safe_retry_policy': 'known-failure-only', 'retry_number': 1, 'max_retries': 1},
        {'id': 'a2', 'key': expected[0], 'status': 'succeeded', 'known_cost': .03},
        {'id': 'b1', 'key': expected[1], 'status': 'rejected', 'known_cost': .02},
        {'id': 'c1', 'key': expected[2], 'status': 'cancelled', 'known_cost': 0},
        {'id': 'd1', 'key': expected[3], 'status': 'outcome_unknown', 'known_cost': None}]
    # Deliberately out-of-order receipt arrival still joins exact identity.
    observed = ledger_check(expected, list(reversed(outcomes)), [attempts[i] for i in (4, 1, 3, 0, 2)])
    require(observed['accepted_variants'] == 1 and observed['attempts'] == 5 and not observed['cost_complete']
            and observed['full_unit_cost'] is None and abs(observed['known_cost_total'] - .07) < 1e-9,
            'fake-provider denominator/cost control failed')
    rejected = {}
    for status in ('dispatched', 'outcome_unknown', 'cancelled'):
        changed = [{**attempts[0], 'status': status}, *attempts[1:]]
        try:
            ledger_check(expected, outcomes, changed)
        except ValueError as error:
            rejected[status + '_retry'] = str(error)
    for name, rows in {'missing': outcomes[:-1], 'wrong_locale': [{**outcomes[0], 'key': 'control:A/uk'}, *outcomes[1:]],
                       'duplicate': [outcomes[0], outcomes[0], *outcomes[2:]]}.items():
        try:
            ledger_check(expected, rows, attempts)
        except ValueError as error:
            rejected[name] = str(error)
    require(len(rejected) == 6, 'fake-provider unknown/membership negative escaped')
    return {'kind': 'controlled fake-provider boundary execution, not actual paid provider performance',
            'ledger': observed, 'negative_controls': rejected, 'real_provider_calls': 0}


def source_state():
    pointer = load_json(REPO / 'marketing/CURRENT_CAMPAIGN.json')
    require(pointer['active_path'] == 'marketing/campaign' and pointer['materials_per_language'] == 10
            and set(pointer['artwork_languages']) == {'en', 'uk'}, 'active campaign changed; re-scope first')
    spec = importlib.util.spec_from_file_location('existing_campaign_builder', REPO / 'marketing/campaign/build_campaign.py')
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    data, _, records = builder.validate_source()
    require(records['uk']['01-original.png']['sha256'] == pointer['original_sha256'], 'accepted original changed')
    pins = {name: sha_file(REPO / name) for name in ('marketing/CURRENT_CAMPAIGN.json', 'marketing/campaign/campaign.json',
             'marketing/campaign/build_campaign.py', 'marketing/campaign/check_campaign.py', 'marketing/campaign/capabilities.json',
             'marketing/campaign/translations.json')}
    return builder, data, records, {'source_files': pins, 'artwork': records, 'producer_sha256': sha_file(__file__)}


def verify_cached(out, inputs):
    receipt = load_json(out / 'batch-report.json')
    require(receipt['input_sha256'] == __import__('hashlib').sha256(canonical(inputs)).hexdigest(), 'cache inputs/source changed')
    require(len(receipt['logical_items']) == 20 and len(receipt['physical_variants']) == 40, 'cache denominator incomplete')
    for entry in receipt['output_files']:
        path = out / entry['path']
        require(path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(out.resolve())
                and path.stat().st_size == entry['bytes'] and sha_file(path) == entry['sha256'], 'cache artifact changed/missing')
    return receipt


def run(args):
    start = time.monotonic()
    out = private_root(args.out)
    builder, data, artwork, inputs = source_state()
    if args.cache:
        cached = verify_cached(out, inputs)
        result = {'cache': 'reused exact verified artifacts', 'logical_items': 20, 'physical_variants': 40,
                  'rerendered': 0, 'provider_calls': 0, 'new_provider_fees': 0,
                  'source_batch_report_sha256': sha_file(out / 'batch-report.json')}
        atomic_json(out / 'cache-report.json', result)
        return result
    require(not (out / 'batch-report.json').exists() and not (out / 'staged').exists(), 'preserve completed/unresolved producer attempt')
    timeline = []
    def event(phase, status, **extra):
        timeline.append({'phase': phase, 'status': status, 'at': datetime.now(timezone.utc).isoformat(),
                         'elapsed_seconds': time.monotonic() - start, **extra})
        atomic_json(out / 'timeline.json', timeline)
    event('source', 'verified', logical_items=20, source_artworks=20)
    event('existing-producer', 'started')
    built = builder.build(out / 'staged', out / 'delivery')
    event('existing-producer', 'completed', lossless_rgb_equal=built['lossless_pdf_source_pixels_match'])
    require(built['lossless_pdf_source_pixels_match'] is True, 'actual full PDF source pixel comparison missing')
    renderer = shutil.which('pdftoppm')
    require(renderer, 'actual PDF renderer unavailable')
    render = out / 'render'
    render.mkdir()
    files, variants, logical = [], [], []
    from PIL import Image, ImageDraw
    for lang in ('en', 'uk'):
        for variant in ('full', 'compact'):
            pdf = out / 'delivery' / ('Campaign.' + lang + '.' + variant + '.pdf')
            prefix = render / (lang + '-' + variant)
            event('render', 'started', locale=lang, variant=variant, pdf_sha256=sha_file(pdf))
            subprocess.run([renderer, '-png', '-r', '72', str(pdf), str(prefix)], check=True, capture_output=True, timeout=120)
            images = sorted(render.glob(lang + '-' + variant + '-*.png'))
            require(len(images) == 10, 'actual renderer did not deliver ten pages')
            sheet = Image.new('RGB', (1600, 2350), '#041924')
            draw = ImageDraw.Draw(sheet)
            for index, (item, path) in enumerate(zip(data['materials'], images)):
                with Image.open(path) as opened:
                    opened.load()
                    require(opened.size == (1600, 900), 'PDF renderer page size mismatch')
                    thumb = opened.copy()
                    thumb.thumbnail((800, 450))
                x, y = (index % 2) * 800, (index // 2) * 470
                sheet.paste(thumb, (x, y + 20))
                draw.text((x + 8, y + 3), lang + '/' + item['id'] + ' / ' + variant, fill='#fff0cd')
                key = lang + ':' + item['id'] + '/' + variant
                variants.append({'key': key, 'locale': lang, 'material_id': item['id'], 'variant': variant,
                                 'pdf_sha256': sha_file(pdf), 'pdf_page': index + 1, 'render': pin(path, out),
                                 'source_sha256': artwork[lang][item['asset']]['sha256'],
                                 'full_source_rgb_equal': variant == 'full', 'source_crop': False,
                                 'review': 'rendered; visual review recorded separately'})
                event('render-item', 'completed', key=key, render_sha256=sha_file(path))
            sheet_path = render / (lang + '-' + variant + '-contact.png')
            sheet.save(sheet_path)
            event('render', 'completed', locale=lang, variant=variant, pages=10)
        for item in data['materials']:
            logical.append({'key': lang + ':' + item['id'], 'locale': lang, 'material_id': item['id'],
                            'master': artwork[lang][item['asset']], 'physical_variants': ['full', 'compact'],
                            'identity_basis': 'unchanged accepted master; full PDF embedded RGB equality verified'})
    # Exclude contact sheets from the page denominator; they are review aids.
    require(len(logical) == 20 and len(variants) == 40 and len({v['key'] for v in variants}) == 40, 'batch item/variant denominator lost')
    expected = [v['key'] for v in variants]
    accounting = ledger_check(expected, [{'key': key, 'status': 'accepted'} for key in expected],
                              [{'id': key, 'key': key, 'status': 'succeeded', 'known_cost': 0} for key in expected])
    boundary = controlled_boundaries()
    event('boundary-controls', 'completed', controls=len(boundary['negative_controls']))
    _, _, final_artwork, final_inputs = source_state()
    require(final_inputs == inputs and final_artwork == artwork, 'campaign sources changed during processing')
    for directory in ('staged', 'delivery', 'render'):
        files.extend(pin(path, out) for path in sorted((out / directory).rglob('*')) if path.is_file())
    elapsed = time.monotonic() - start
    retained = sum(p.stat().st_size for p in out.rglob('*') if p.is_file())
    require(elapsed <= 180 and retained <= 350 * 1024 * 1024, 'media phase/disk cap exceeded')
    event('batch', 'completed', logical_items=20, physical_variants=40)
    report = {'schema': 'atelier.actual-campaign-batch/1', 'inputs': inputs,
              'input_sha256': __import__('hashlib').sha256(canonical(inputs)).hexdigest(),
              'logical_items': logical, 'physical_variants': variants, 'output_files': files,
              'existing_builder_result': built, 'accounting': accounting, 'fake_provider_controls': boundary,
              'timeline_sha256': sha_file(out / 'timeline.json'), 'renderer': {'path': renderer, 'sha256': sha_file(renderer)},
              'resources': {'elapsed_seconds': elapsed, 'retained_bytes_before_report': retained,
                            'process_peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                            'new_download_bytes': 0, 'new_provider_calls': 0, 'incremental_provider_fees': 0,
                            'historical_master_procurement_cost': 'unknown; not included',
                            'local_compute_energy_and_labor': 'not monetized; actual elapsed/RSS recorded'},
              'visual_review': 'pending actual image inspection; source/pixel/render checks alone do not certify readability',
              'independent_review': False, 'owner_acceptance': False,
              'limits': ['Existing approved raster masters; no new artwork or media model generation',
                         'Full PDFs preserve source RGB; compact JPEG intentionally changes pixels',
                         'Paired locales preserve accepted intended composition; no claim of non-text pixel identity across languages',
                         'Raster PDF text is not a searchable/accessibility text layer',
                         'Actual batch has zero new provider fees; controlled fake-provider amounts are not invoices',
                         'Audio/video/3D and deployment not exercised by this campaign task']}
    atomic_json(out / 'batch-report.json', report)
    return {'logical_items': 20, 'physical_variants': 40, 'rendered_pdf_pages': 40,
            'lossless_source_rgb': True, 'elapsed_seconds': elapsed, 'retained_bytes': retained,
            'batch_report_sha256': sha_file(out / 'batch-report.json')}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True)
    parser.add_argument('--cache', action='store_true')
    print(json.dumps(run(parser.parse_args()), allow_nan=False))
