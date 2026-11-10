# Actual approved-campaign media batch

This explicit evaluation reuses the accepted campaign's20existing raster masters: English/Ukrainian × ten materials. It preserves artwork, identity and campaign sources. It adds no generator, provider, global registry, installed service or new marketing direction. The existing `marketing/CURRENT_CAMPAIGN.json` and active campaign README remain authoritative.

`campaign_batch.py` calls the existing producer with private staging/delivery paths, verifies all20source hashes/pairs and full-PDF source RGB equality, renders all four locale/full-or-compact PDFs with actual Poppler, and records40physical page variants under20logical material IDs. Contact sheets are review aids and do not increase the page denominator. The two full PDFs preserve source RGB; compact JPEG derivatives intentionally differ in pixels. Raster PDF text has no searchable/accessibility text layer. The historical campaign's5.0 identity is preserved rather than silently rebranded to current toolkit metadata.

Use the already bundled Python with Pillow/pypdf and the already available `pdftoppm`. No download or installation was needed in the actual run. Before authoring, follow the applicable PDF skill's operation marker. From the repository root, `$MEDIA` is a new authorized private directory outside this repository:

```sh
"$PDF_PY" evaluations/ai-production/real-world/media-batch/campaign_batch.py --out "$MEDIA"
```

The observed producer/render phase took177.42seconds and retained243418520bytes, within its180second/350MiB bound. It made no provider call and acquired no new dependencies. A completed/unresolved producer attempt is not overwritten. The actual source/master hashes are checked again after processing; source changes invalidate completion.

Retain the printed exact `batch_report_sha256` outside the receipt before reuse. The guarded consumer checks that retained pin, all output bytes, source pins and the exact20logical/40physical IDs and locale variants. An altered receipt cannot rebind old proof. It reuses existing artifacts, with zero new render/provider calls:

```sh
"$PDF_PY" evaluations/ai-production/real-world/media-batch/cache_guard.py --out "$MEDIA" --expected-report-sha256 "$BATCH_SHA256"
python3.13 -m unittest discover -s evaluations/ai-production/real-world/media-batch -p test_batch_boundaries.py -v
```

The batch also executes explicitly controlled fake-provider failure/rejection/cancellation/unknown/out-of-order cases. These perform no vendor operation and their amounts are not invoices. They retain all requested IDs, count retries/rejections in attempt cost, permit only one explicitly safe known-failure retry, block unresolved/inflight/cancelled replay, retain unknown cost as unknown, and never divide by a fictitious accepted denominator. Five generic tests protect these boundaries and receipt reuse. They are not media-quality or paid-provider performance evidence.

Costs are scoped precisely: the actual run incurred zero **incremental provider fees**; it does not establish free historical artwork procurement or full total cost. The raw ledger's `full_unit_cost` means only its recorded attempt-fee ledger per accepted physical variant. Historical master procurement is unknown; local compute, energy and labor were measured by elapsed/RSS but not monetized. The report and panel summary keep full TCO unknown. The20logical/40physical denominators are separate.

Actual worker visual inspection covers four all-page contact sheets and full-size English/Ukrainian constructor-page renders. It checks the accepted rich composition, headline/readability hierarchy, whole framing and visible rendering defects; it does not certify every tiny raster word, print accessibility or non-text pixel identity across localized masters. Full-pixel preservation within each locale is a separate measured proof. Independent visual review, existing-panel consumption and owner acceptance remain separate. No original product was launched by the conceptual screenshots.

No audio, video,3D or new artwork generation was requested by this campaign task, so those media were not exercised or automatically accepted. Existing app SVG/UI/motion proofs are separately owned. This bounded case is not whole-system acceptance of every possible medium or all29original cases. [Actual results](RESULTS.en.md) retain these limits.
