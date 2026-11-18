# License, editions and test delivery

The commercial candidate uses one configurable offer, one versioned original
license, and a separate record for each test order. This is an owner-review
release candidate. It is neither an actual sale nor a new public license grant.
The owner supplied the name **Oleksandr Hohaizel** and the support/privacy
contact **aleksandrhohaizel@gmail.com**. These are owner-provided facts. The
email is not a postal address and does not establish a legal entity, country,
tax treatment or jurisdiction. Before public sale, confirm legal contracting
capacity and address, an operational support/privacy channel and staffed
hours, jurisdiction-specific terms, refund process and channel agreement.

## Offer and acquired rights

[The offer](../../commercial/offer.json) is the sole source for the draft prices
and edition limits: Solo USD 49 for one named user on that user's devices;
Team USD 149 for up to five named users of one organization. Both permit
personal and client commercial work. The acquired product major is perpetual,
and available updates to the same major are included. A later major is a
separate offer. Model usage, Codex access, API fees and hosting remain the
buyer's own costs.

[The license](../../commercial/legal/LICENSE.txt) explains internal modification,
generated work, constructed agents, copied toolkit resources and redistribution
limits. Original customer work does not become a resold toolkit license.
Third-party licenses remain separate and must travel with the actual runtime.
The candidate license is source-available, not an OSI-approved open-source
license. Public repository visibility is separate from a commercial grant.
[GitHub's licensing guidance](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)
distinguishes public viewing/forking from a source license.
[OSI's definition](https://opensource.org/faq#what-is-open-source) requires
permissions beyond this candidate's redistribution grant.

Every issued record snapshots the offer, original license digest, support and
refund versions, acquired major, named seats and exact artifact source commit.
Changing the current price or offer does not mutate an existing order. The
local support and refund drafts are
[SUPPORT.md](../../commercial/legal/SUPPORT.md) and
[REFUNDS.md](../../commercial/legal/REFUNDS.md). Missing business data is
enumerated in [the owner facts gate](../../commercial/legal/OWNER_FACTS_REQUIRED.json).

## Controlled seller-local delivery

Run from the source checkout, using a private directory outside this repository.
These commands issue an isolated test order; they do not process payment.
The build catalog is the canonical builder's JSON with schema
"codex-agents.commercial-build/1", product_id, product_version,
source_commit, and a files array. The selected row has name, path,
sha256, size, and edition. A local path is resolved only after exact
bytes and the selected edition match the reviewed catalog.

~~~sh
python3 -B commercial/fulfillment.py issue \
  --database "$PRIVATE/seller.sqlite" --catalog "$BUILD_CATALOG" \
  --edition solo --artifact "$EXACT_ARCHIVE_NAME" \
  --order-id test-order-001 --buyer-ref test-buyer-001 \
  --code-file "$PRIVATE/redemption.txt"
python3 -B commercial/fulfillment.py redeem \
  --database "$PRIVATE/seller.sqlite" --code-file "$PRIVATE/redemption.txt" \
  --destination "$PRIVATE/buyer-download"
~~~

For Team, pass --edition team --organization-ref test-organization and
select the Team artifact. Order references are opaque, not names or email
addresses. Code files, SQLite records, purchase documents and runtime
receipts remain private. Repeating the same order is idempotent. Changing
its accepted scope under the same order ID is rejected. Reopening the same
code returns the same purchase confirmation and exact original artifact.

The buyer receives the ZIP, original LICENSE.txt, entitlement.json,
purchase-confirmation.json, and READ_ME_FIRST.md. Extract the archive
and follow its start page. Keep the purchase documents and the signed or
attested original archive for recovery. The confirmation's digest verifies
byte consistency; authenticity comes from the trusted seller delivery and
artifact signature or attestation, not from a JSON checksum.

For a real local HTTP download exercise:

~~~sh
python3 -B commercial/fulfillment.py serve \
  --database "$PRIVATE/seller.sqlite" --listen 127.0.0.1 --port 0 \
  --ready "$PRIVATE/delivery-ready.json"
~~~

The ready file identifies the exact loopback URL. Send POST /redeem with
Content-Type: application/json and {"code":"THE_PRIVATE_TEST_CODE"}.
The response contains the confirmation and short-lived download, license
and confirmation URLs. Only loopback binding is supported; requests are
not logged and cross-origin browser requests are rejected. Stop the process
after the test. This bounded server is not a production checkout,
payment webhook, email sender, identity service or activation endpoint.

## Offline continuity and seat changes

The inspect command reads the delivered immutable entitlement without contacting a store:

~~~sh
python3 -B commercial/fulfillment.py inspect \
  --entitlement "$PRIVATE/buyer-download/entitlement.json" \
  --target-version 1.8.1
~~~

This command validates the recorded structure and separate update scope.
It does not authenticate a document or manufacture a purchase grant.
It reports acquired-use continuity independently of eligibility for a
different product major. No license-status path modifies user projects,
remotely disables an installation, or requires online activation.

Team assignments use opaque internal member references and a revision.
Document retirement before assigning the seat to another person:

~~~sh
python3 -B commercial/fulfillment.py replace-seat \
  --database "$PRIVATE/seller.sqlite" --order-id test-order-001 \
  --slot 1 --expected-revision 0 --next-ref member-001 \
  --operation-id assignment-001
python3 -B commercial/fulfillment.py replace-seat \
  --database "$PRIVATE/seller.sqlite" --order-id test-order-001 \
  --slot 1 --expected-revision 1 --retired-ref member-001 \
  --next-ref member-002 --operation-id assignment-002
~~~

A repeated exact operation returns its prior recorded outcome. A stale
revision or reused operation ID for a different change is rejected.
The acquired Team document remains unchanged; its assignment history is
a seller-local administrative record.

## Production boundary

No live payment provider or callback is integrated. C18 therefore has an
explicit not-integrated status rather than a claim of tested refund or
webhook correctness. Before such an integration is adopted, verify its
actual signature scheme, replay/reordering semantics, exact order identity,
refund reconciliation and applicable accepted channel terms. Do not turn a
locally recorded event into proof that a payment provider acted.

Complete the legal owner facts, final license, support/refund details,
channel agreement, artifact signing/notarization and supported-platform
gates before public sale. Production issuance is deliberately unavailable
in this candidate's test-delivery tool.
