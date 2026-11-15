# The Beauty API dataset: changelog

This bundle is release **2026.11** (3 November 2026).

Every purchase is a snapshot of the newest release at the time of purchase. In SQLite, each product and ingredient row carries `updated_at`: the date (`YYYY-MM-DD`) of the release in which that row's data last changed. JSONL and CSV do not include these release stamps. To list changed SQLite rows since an earlier snapshot, filter on `updated_at`. Removed rows are absent from the files. A product's stamp covers its fields, ingredient relationships, barcodes and image; an ingredient's stamp covers its dictionary row. The current changelog is available at https://thebeautyapi.com/changelog.

## 2026.11 · 3 November 2026 · Expanded catalogue and richer ingredient data

- Expanded product coverage from additional sources.
- Added product and package details, including sizes, shades, benefits, directions and warnings.
- Added support for ingredient sections and kit components, alongside single ingredient lists.
- Added product and ingredient aliases to preserve links to records consolidated through deduplication.
- Ingredient filters return 400 for unknown or retired ingredient IDs; recorded aliases resolve to their surviving ingredients.

Catalogue: 258,648 products · 26,420 ingredients · 5,497,548 ingredient links · 279,996 barcode links · 256,757 images.
Since the previous release: products 177,763 changed, 80,885 added, 1,411 removed; ingredients 1,010 changed, 4,850 added, 902 removed.

## 2026.08 · 17 August 2026 · GTIN barcode data added

- Added retail barcode data: 221,440 UPC/EAN codes in canonical GTIN-14 form across 79,089 products (~44% of the catalogue).
- SQLite: new product_barcodes table with per-code detail (unit vs. sibling-variant, primary owner). JSONL/CSV: new gtin14 list on each product row.
- GS1 restricted-circulation ranges excluded, so every code is a globally resolvable GTIN.
- Product images unchanged from the previous release.

Purchases completed before 17 August 2026 contain the 2026.06 release, which has no barcode fields.

Catalogue: 179,174 products · 22,472 ingredients · 4,805,105 ingredient links · 221,440 barcode links · 179,139 images.
Baseline release for per-row `updated_at`: every row carries this date; earlier per-row history is not recorded.

## 2026.06 · 25 June 2026 · Full-catalogue quality audit

- Catalogue-wide audit ahead of production use: deduplication and cross-field consistency checks.
- Removed subjective editorial description fields: the dataset carries only factual, normalized relational data.

Purchases completed before 25 June 2026 contain the prior release.
