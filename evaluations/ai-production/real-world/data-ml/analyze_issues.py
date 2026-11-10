"""Reproducible TF-IDF theme exploration and coverage-aware public count trends.

This deliberately does not train on the earlier AI labels or call clusters human
ground truth. The sample and report authors are not a population of users.
"""
import argparse
from collections import Counter
from datetime import datetime
import json
import math
from pathlib import Path
import random
import re
import statistics
import time
from common import atomic_json, load_json, observed_resources, private_root, require, sha_file

STOP = set('the a an and or but to of in on for from is are was were be been being this that these those it its i me my we our you your they their with without as at by not no yes can could would should will just have has had do does did also when after before then than only all any some use using used issue bug report actual expected behavior reproduce steps screenshot screenshots codex app openai please thanks version macos windows linux terminal logs log error'.split())


def tokens(row):
    # The same fixed extraction for all records; never use source AI labels.
    text = re.sub(r'```.*?```', ' ', row.get('body') or '', flags=re.S)
    text = row.get('title', '') + ' ' + text[:1800]
    return [word for word in re.findall(r'[^\W\d_][\w-]{2,34}', text.lower()) if word not in STOP]


def vectors(rows):
    counts = {str(r['id']): Counter(tokens(r)) for r in rows}
    df = Counter(t for c in counts.values() for t in c)
    out = {}
    for key, count in counts.items():
        weighted = {t: (1 + math.log(n)) * (1 + math.log((1 + len(rows)) / (1 + df[t])))
                    for t, n in count.items() if df[t] >= 2 and df[t] <= .65 * len(rows)}
        norm = math.sqrt(sum(v * v for v in weighted.values()))
        out[key] = {t: v / norm for t, v in weighted.items()} if norm else {}
    return out


def clusters(rows, threshold):
    vector = vectors(rows)
    keys = sorted(vector)
    near = {}
    scores = {}
    for i, left in enumerate(keys):
        for right in keys[i + 1:]:
            a, b = vector[left], vector[right]
            if len(a) > len(b):
                a, b = b, a
            value = sum(v * b.get(t, 0) for t, v in a.items())
            scores[left, right] = scores[right, left] = value
        near[left] = []
    for left in keys:
        near[left] = {r for r in sorted((k for k in keys if k != left), key=lambda r: (-scores[left, r], r))[:3]
                      if scores[left, r] >= threshold}
    remaining = set(keys)
    components, noise = [], []
    while remaining:
        stack, component = [min(remaining)], []
        while stack:
            key = stack.pop()
            if key not in remaining:
                continue
            remaining.remove(key)
            component.append(key)
            stack.extend(other for other in near[key] if key in near[other] and other in remaining)
        if len(component) == 1:
            noise.extend(component)
        else:
            components.append(sorted(component))
    return sorted(components, key=lambda c: (-len(c), c[0])), sorted(noise), vector


def pairs(components, allowed=None):
    return {(a, b) for component in components for i, a in enumerate(component) for b in component[i + 1:]
            if allowed is None or a in allowed and b in allowed}


def run(corpus, count_path, output):
    start = time.monotonic()
    out = private_root(output)
    rows = load_json(corpus)['rows']
    require(len(rows) == len({r['id'] for r in rows}) == 100, 'frozen sample denominator differs')
    lookup = {str(r['id']): r for r in rows}
    authors = Counter(r['author_group'] for r in rows)
    thresholds = {}
    for threshold in (.18, .25, .32):
        groups, noise, vector = clusters(rows, threshold)
        details = []
        for group in groups:
            terms = Counter()
            for key in group:
                terms.update(vector[key])
            details.append({'rows': len(group), 'author_groups': len({lookup[k]['author_group'] for k in group}),
                            'author_weighted_mass': sum(1 / authors[lookup[k]['author_group']] for k in group),
                            'top_terms': [term for term, _ in terms.most_common(8)],
                            'issue_urls': [lookup[k]['url'] for k in group], 'member_ids': group})
        require(sum(len(c) for c in groups) + len(noise) == 100, 'cluster/noise denominator lost')
        stability = []
        generator = random.Random(418)
        for _ in range(12):
            sample = generator.sample(rows, 80)
            subgroups, _, _ = clusters(sample, threshold)
            allowed = {str(r['id']) for r in sample}
            a, b = pairs(groups, allowed), pairs(subgroups)
            stability.append(len(a & b) / len(a | b) if a | b else 1)
        thresholds[str(threshold)] = {'clusters': details, 'noise_ids': noise, 'noise_rows': len(noise),
                                      'stability_pair_jaccard_80pct': {'replicates': 12, 'mean': statistics.mean(stability),
                                                                      'min': min(stability), 'max': max(stability)}}
    dates = sorted(datetime.fromisoformat(r['created_at'].replace('Z', '+00:00')) for r in rows)
    counts = load_json(count_path)
    trend = []
    for week in sorted({r['week'] for r in counts['records']}):
        records = {r['context']: r for r in counts['records'] if r['week'] == week}
        require(set(records) == {False, True} and all(r['incomplete_results'] is False for r in records.values()),
                'incomplete search cannot prove trend denominator')
        denominator, numerator = records[False]['total_count'], records[True]['total_count']
        require(0 <= numerator <= denominator and denominator > 0, 'invalid trend units or denominator')
        trend.append({'creation_week': week, 'app_labelled_issue_reports': denominator,
                      'also_context_labelled': numerator, 'share': numerator / denominator,
                      'queries': [records[False]['url'], records[True]['url']]})
    report = {'source_sha256': sha_file(corpus), 'trend_snapshot_sha256': sha_file(count_path),
              'analysis_sha256': sha_file(__file__), 'common_sha256': sha_file(Path(__file__).with_name('common.py')),
              'source_rows': 100, 'source_author_groups': len(authors), 'author_weighted_total_mass': len(authors),
              'sample_window': [dates[0].isoformat(), dates[-1].isoformat()],
              'sample_trend_status': 'abstain:26-hour latest100 sample cannot establish historical population trends',
              'cluster_threshold_sensitivity': thresholds, 'public_retrospective_counts': trend,
              'context_tag_share_change_percentage_points': 100 * (trend[1]['share'] - trend[0]['share']),
              'resources': observed_resources(start),
              'limits': ['Themes are lexical exploratory groups; inspect issue links and retain noise, not validated need categories',
                         'Author groups are pseudonymous source buckets, not verified unique people',
                         'Current labels on issues created in two complete weeks are retrospective, mutable, and potentially incomplete as needs',
                         'A report share is not active-user prevalence or causal demand; tiny change is not evidence of a trend',
                         'Stability measures representation sensitivity, not semantic business accuracy']}
    atomic_json(out / 'issue-analysis.json', report)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--corpus', required=True)
    parser.add_argument('--trend-counts', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    report = run(args.corpus, args.trend_counts, args.out)
    print(json.dumps({'rows': report['source_rows'], 'author_groups': report['source_author_groups'],
                      'thresholds': {k: {'clusters': len(v['clusters']), 'noise': v['noise_rows'],
                                         'stability': v['stability_pair_jaccard_80pct']} for k, v in report['cluster_threshold_sensitivity'].items()},
                      'trend_counts': report['public_retrospective_counts'], 'resources': report['resources']}))
