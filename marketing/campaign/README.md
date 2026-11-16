# Showcase sources and exports

Open the [showcase language selector](../README.md) on GitHub or open [the gallery entry file](index.html) from a local checkout. The validation workflow publishes `Showcase.zip` with the seven HTML editions, all artwork, and the illustrated PDF. Extract the archive before opening `index.html`.

The illustrated scenarios use fictional products and are paired with practical guides. The workbench plate is schematic. The gallery links to source-based instructions on retrieval, evaluation, permissions, and run evidence.

The [catalog](catalog.json) owns the localized titles, alternative text, workflow descriptions, and guide sections. [Artwork provenance](artwork.json) records the generated cover, its source references, and approved image digests. [The diagram source](render_boards.py) generates the nine workflow boards. The reference commit retains the approved originals.

Run from the repository root with the same Python dependencies as the validation workflow.

```sh
python3 -B marketing/campaign/build_campaign.py --check-source
python3 -B marketing/campaign/build_campaign.py --export --artifacts-output /tmp/agent-system-showcase
python3 -B marketing/campaign/build_campaign.py --verify --artifacts-output /tmp/agent-system-showcase
```

After changing catalog text, run `build_campaign.py --refresh-markdown` before exporting. The PDF preserves the pixels of each full source image. Its language-neutral visual content is accompanied by localized explanations in the Markdown and HTML galleries. A standalone ZIP contains its own assets and language navigation. Links to the online guides require internet access.
