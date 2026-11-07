# Marketing concept validation

Validation date: 2026-11-07. Concept version: 1.0; system version referenced: 5.0.0.

- Parsed all 22 SVG documents as XML: 20 direction boards and two contact sheets.
- Rendered both contact sheets from their exact SVG sources using Sharp. Inspected the English and Ukrainian PNGs. Corrected headline, button and editorial-caption collisions found during review.
- Parsed and executed the gallery JavaScript in Node's VM with a minimal DOM adapter. Checked the default English startup, both language toggles and all 20 concept/language combinations.
- Repeated startup, language changes and all 20 states with storage and history methods that throw, then with both globals absent. Rendering continued in each case. Language persistence and URL persistence are optional; neither is needed for reading or navigation.
- Refreshed and checked SHA256 values for all 46 board, contact-sheet, brief and gallery/data files listed in `concept-manifest.json`.

A Chromium executable was not installed in the available runtime. A real browser layout, mobile viewport, keyboard focus, download and clipboard test has **not** been completed. The VM adapter checks JavaScript state transitions; it does not establish browser layout or browser API interoperability. The SVG rendering check establishes the exported vector composition under the available renderer. A final commercial export still needs a visual review in its intended browser/export environment and at the actual display size.
