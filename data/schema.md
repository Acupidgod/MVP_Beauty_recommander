# The Beauty API DB: The Complete Archive

The Complete Archive contains beauty product records, structured ingredient data, an ingredient dictionary, barcodes and product images. Use JSONL to work with one product at a time, or CSV and SQLite to query the relationships between products and ingredients.

The dataset contains product catalogue information, not customer accounts, reviews or personal data.

## Package contents

| File | Contents |
| --- | --- |
| `products.jsonl` | One product per line, with its ingredient lists, sections or components nested inside it. |
| `products.csv` | Product details, with barcode lists stored as JSON text. |
| `ingredients.csv`, `ingredients.jsonl` | Ingredient dictionary, including available functions, ratings and chemical identifiers. |
| `product_ingredients.csv` | Ordered ingredient entries for products with a flat list. |
| `product_ingredient_groups.csv` | Sections and components, with their order and parent relationships. |
| `product_group_ingredients.csv` | Ordered ingredient entries belonging to those groups. |
| `product_aliases.csv`, `product_aliases.jsonl` | Older product IDs and their surviving product IDs. |
| `ingredient_aliases.csv`, `ingredient_aliases.jsonl` | Older ingredient IDs and their surviving ingredient IDs. |
| `barcode_aliases.csv`, `barcode_aliases.jsonl` | Additional supported barcode spellings and their canonical GTIN-14 values. |
| `the_beauty_api_dataset.db` | Standalone SQLite database containing the relational data, barcode tables and release metadata. |
| `images_N.zip` | Product images, matched through `image_name`. Use the supplied archive inventory for the number of files and archives. |
| `schema.md` | This guide. |
| `CHANGELOG.md` | Dataset release history. |

Files use UTF-8. A CSV parser must support quoted fields with embedded commas, quotes and line breaks; splitting the file on newlines does not reliably identify records.

## Data model

```text
products ──< product_ingredients >── ingredients
    │
    ├──< product_ingredient_groups ──< product_group_ingredients >── ingredients
    │              └── parent_group_id links sections to components
    └──< product_barcodes

product_aliases ──> products
ingredient_aliases ──> ingredients
barcode_aliases ──> canonical GTIN-14 values
```

JSONL nests ingredient lists, sections and components inside each product. CSV and SQLite store those relationships in separate tables. Use `position` to preserve ordering when joining them.

## Products data

Product IDs are numeric integers in the dataset. Ingredient references are also numeric. The hosted API uses UUIDs instead, so dataset IDs cannot be passed directly to API endpoints.

| Field | Type | Meaning |
| --- | --- | --- |
| `id` | integer | Product ID. IDs can have gaps after deduplication. |
| `brand` | string or null | Brand name. |
| `name` | string or null | Product name. |
| `image_name` | string or null | Filename of the associated image, or null if unavailable. |
| `category` | string or null | Broad product category; see the vocabulary below. |
| `origin` | string or null | Country of the brand's headquarters, where known. |
| `product_type` | string or null | Product structure, such as a single item or set. |
| `subcategory` | string or null | A more specific product classification. |
| `size` | string or null | Declared size, including unit or pack wording. |
| `packaging` | string or null | Packaging description, such as a bottle, tube or jar. |
| `pack_count` | integer or null | Number of items in the pack, when known. |
| `shade_name` | string or null | Supplied shade name. |
| `benefits` | string or null | Reported product benefits. |
| `directions` | string or null | Directions for use; may contain line breaks. |
| `warnings` | string or null | Supplied warnings; may contain line breaks. |
| `ingredients_raw` | string or null | Raw ingredient text from the product listing. |
| `contains_fragrance` | boolean or null | Whether listed ingredients include an ingredient tagged as fragrance or a perfuming agent. |
| `contains_drying_alcohol` | boolean or null | Whether listed ingredients include a drying alcohol. |
| `contains_parabens` | boolean or null | Whether listed ingredients include a paraben preservative. |
| `contains_sulfates` | boolean or null | Whether listed ingredients include a sulfate surfactant. |
| `contains_silicones` | boolean or null | Whether listed ingredients include a silicone. |
| `gtin14` | array of strings | JSONL/CSV only: canonical barcode values for the product. An empty array means no listed codes. |
| `barcode_matches` | array of objects | JSONL/CSV only: `gtin14`, `kind` and `is_primary` for each barcode assignment. |
| `updated_at` | string | SQLite only: date of the release in which the product last changed. |

Product categories are `skincare`, `suncare`, `makeup`, `haircare`, `body/bath`, `fragrance`, `other`, `deodorants`, `oral-care`, `tools_accessories` and `devices`. Unknown categories are null. Subcategory and product-type values are text rather than a closed enumeration.

Flags use JSON true/false/null, CSV `true`/`false`/blank and SQLite 1/0/NULL. Null means unknown; preserve it when importing. The flags are derived from ingredient information rather than laboratory analysis. Ingredient `category` values identify the corresponding fragrance, drying-alcohol, paraben, sulfate and silicone tags.

## Ingredients data

For example, an ordinary cleanser can have one ingredient list, a sunscreen can have active and inactive sections, and a kit can have separate cleanser and serum components. The representation preserves those boundaries instead of combining them into a single list.

A JSONL product has exactly one of `ingredients`, `ingredient_sections` or `components`. The other top-level formula fields are omitted. Each component has either `ingredients` or `ingredient_sections`. A list is null when unavailable; available lists elsewhere in the product remain present.

Positions start at zero independently within each ingredient list and each list of sections or components. A section has `position`, `heading` and `ingredients`. A component has `position`, `name` and its ingredient structure. Headings and component names may be null.

Recognized headings are normalized to `Ingredients`, `Active ingredients`, `Inactive ingredients`, `Medicinal ingredients`, `Non-medicinal ingredients` or `May contain`. Unrecognized headings retain their wording.

### Raw ingredient text

`ingredients_raw` contains ingredient text from the product listing and remains at product level even when structured ingredients are available. Original text and line breaks are preserved where available. Missing text is null. Sections and components do not repeat `ingredients_raw`.

### Ingredient entries and dictionary

Each nested ingredient entry includes `position`, `label_name`, `concentration`, `ingredient_id` and the dictionary fields below. A reliably parsed but unmatched label retains its position, wording and concentration, with `ingredient_id` and dictionary fields set to null. A matched ingredient can have an empty `functions` array.

| Field | Type | Meaning |
| --- | --- | --- |
| `position` | integer | Zero-based order within this ingredient list. |
| `label_name` | string | Ingredient wording with approved spelling corrections; may differ from the dictionary name. |
| `concentration` | number or null | Declared percentage, where supplied; never estimated. |
| `ingredient_id` | integer or null | Reference to `ingredients.id`, or null for an unmatched label. |
| `name` | string or null | Canonical ingredient name; required on a dictionary row, nullable in an unmatched nested entry. |
| `rating` | string or null | Editorial class: `direct actives`, `supporting actives` or `sensitizers`. |
| `irritancy` | string or null | Reported 0–5 score or range, such as `0` or `0-3`. |
| `comedogenicity` | string or null | Reported 0–5 score or range. |
| `functions` | array of strings or null | Functions such as solvent or humectant. Null on an unmatched nested entry; an empty array on a matched entry means no recorded functions. |
| `cas_number` | string or null | CAS Registry Number. |
| `ec_number` | string or null | EC identifier. |
| `ph_eur_name` | string or null | European Pharmacopoeia name. |
| `iupac_name` | string or null | IUPAC name. |
| `other_names` | string or null | Synonyms as a text field. |
| `category` | string or null | Ingredient tag: `fragrance`, `drying_alcohol`, `parabens`, `sulfates` or `silicones`. |

The dictionary's primary key is `id`; nested entries and relationship tables refer to it as `ingredient_id`. CSV/SQLite dictionary rows store `functions` as JSON-array text. SQLite dictionary rows additionally carry `updated_at`. The dictionary may retain canonical targets needed by ingredient aliases even when no current product references them.

Ratings and chemical identifiers are reference information, not medical or regulatory guidance. Ingredient ratings describe ingredients, not the safety of a finished product.

### Irritancy and comedogenicity scores

- `irritancy` describes irritation potential; `comedogenicity` describes pore-clogging potential.
- These are literature-derived ingredient scores on a 0–5 scale, from no reported potential to high potential. Ranges reflect variation in reported results.
- Historical comedogenicity research includes rabbit-ear testing. Results for an isolated ingredient do not establish how a finished product will behave: concentration and the rest of the formula matter.
- Use the scores as supplementary ingredient information, not a finished-product safety rating or medical guidance. Null means no recorded score.

### JSONL examples

These illustrative excerpts show product IDs and ingredient-related fields. Product IDs are illustrative; ingredient IDs refer to the dataset dictionary. Additional ingredient dictionary fields are omitted for readability. Each formatted example represents one line in a JSONL file.

#### Single list

```json
{
  "id": 1,
  "ingredients_raw": "Aqua (Water), Glycerin",
  "ingredients": [
    {
      "position": 0,
      "label_name": "Aqua (Water)",
      "concentration": null,
      "ingredient_id": 1,
      "name": "Water"
    },
    {
      "position": 1,
      "label_name": "Glycerin",
      "concentration": null,
      "ingredient_id": 9,
      "name": "Glycerin"
    }
  ]
}
```

#### Sections

```json
{
  "id": 2,
  "ingredients_raw": "Active ingredients: Zinc Oxide\nInactive ingredients: Aqua (Water), Glycerin",
  "ingredient_sections": [
    {
      "position": 0,
      "heading": "Active ingredients",
      "ingredients": [
        {
          "position": 0,
          "label_name": "Zinc Oxide",
          "concentration": null,
          "ingredient_id": 476,
          "name": "Zinc Oxide"
        }
      ]
    },
    {
      "position": 1,
      "heading": "Inactive ingredients",
      "ingredients": [
        {
          "position": 0,
          "label_name": "Aqua (Water)",
          "concentration": null,
          "ingredient_id": 1,
          "name": "Water"
        },
        {
          "position": 1,
          "label_name": "Glycerin",
          "concentration": null,
          "ingredient_id": 9,
          "name": "Glycerin"
        }
      ]
    }
  ]
}
```

#### Components

```json
{
  "id": 3,
  "ingredients_raw": "Cleanser: Aqua (Water), Glycerin\nSerum: Aqua (Water), Glycerin",
  "components": [
    {
      "position": 0,
      "name": "Cleanser",
      "ingredients": [
        {
          "position": 0,
          "label_name": "Aqua (Water)",
          "concentration": null,
          "ingredient_id": 1,
          "name": "Water"
        },
        {
          "position": 1,
          "label_name": "Glycerin",
          "concentration": null,
          "ingredient_id": 9,
          "name": "Glycerin"
        }
      ]
    },
    {
      "position": 1,
      "name": "Serum",
      "ingredient_sections": [
        {
          "position": 0,
          "heading": "Ingredients",
          "ingredients": [
            {
              "position": 0,
              "label_name": "Aqua (Water)",
              "concentration": null,
              "ingredient_id": 1,
              "name": "Water"
            },
            {
              "position": 1,
              "label_name": "Glycerin",
              "concentration": null,
              "ingredient_id": 9,
              "name": "Glycerin"
            }
          ]
        }
      ]
    }
  ]
}
```

#### Raw text only

```json
{
  "id": 4,
  "ingredients_raw": "Aqua (Water), Glycerin",
  "ingredients": null
}
```

#### No ingredient text or list

```json
{
  "id": 5,
  "ingredients_raw": null,
  "ingredients": null
}
```

## Relational tables

`products` and `ingredients` contain the fields described above. CSV and SQLite use the following relationship tables; each corresponding CSV has the same column names.

| Table | Columns and relationships |
| --- | --- |
| `product_ingredients` | `product_id` → products.id; nullable `ingredient_id` → ingredients.id; `position`, nullable `concentration`, `label_name`. Unique by product and position. Flat lists only. |
| `product_ingredient_groups` | `id`, `product_id` → products.id, nullable `parent_group_id` → this table's id, `kind`, `position`, nullable `heading`, nullable `name`, `parsed`. |
| `product_group_ingredients` | `group_id` → product_ingredient_groups.id; `position`, nullable `ingredient_id` → ingredients.id, `label_name`, nullable `concentration`. Unique by group and position. |
| `product_aliases` | `alias_id` → an older product ID; `product_id` → the surviving products.id. |
| `ingredient_aliases` | `alias_id` → an older ingredient ID; `ingredient_id` → the surviving ingredients.id. |
| `barcode_aliases` | `barcode` → additional supported spelling; `gtin14` → canonical barcode value. |

A group's `kind` is `section` or `component`. A top-level group has no parent; a section inside a component points to that component through `parent_group_id`. Parent and child belong to the same product. A component contains either direct ingredient rows or child sections. Grouped products do not also have a flat list in `product_ingredients`.

`parsed` is 0 or 1 and records the group's parsing state, independently of whether every label has a dictionary match. An unparsed group has no ingredient rows. When reconstructing JSONL, a group with no ingredient rows has a null list. Group IDs are relationship keys; preserve product, parent and position when assembling the hierarchy.

### Preserve unmatched labels when joining

Use a LEFT JOIN to keep ingredient occurrences whose dictionary reference is null. For a flat list:

```sql
SELECT pi.position, pi.label_name, pi.concentration, pi.ingredient_id,
       i.name, i.functions
FROM product_ingredients pi
LEFT JOIN ingredients i ON i.id = pi.ingredient_id
WHERE pi.product_id = :product_id
ORDER BY pi.position;
```

For a section or a component with direct ingredients:

```sql
SELECT pi.position, pi.label_name, pi.concentration, pi.ingredient_id,
       i.name, i.functions
FROM product_group_ingredients pi
LEFT JOIN ingredients i ON i.id = pi.ingredient_id
WHERE pi.group_id = :group_id
ORDER BY pi.position;
```

Read `product_ingredient_groups` for the product first, preserving `parent_group_id` and `position`. Do not combine different groups merely because their ingredient positions start at the same value.

### IDs and deduplication

Deduplication can combine product or ingredient records over time. Alias tables connect older IDs to the surviving records so stored references can be updated. Resolve a product ID through `product_aliases` if it is no longer present in `products`; resolve an ingredient through `ingredient_aliases` if it is no longer present in `ingredients`. An ID missing from both its main table and alias table has no supplied replacement. JSONL users can load the alias companion files for the same purpose and resolve ingredient destinations through `ingredients.jsonl`, including targets without current product references.

### Barcodes

SQLite stores assignments in `product_barcodes(product_id, gtin14, barcode, kind, is_primary)`. `gtin14` is a 14-digit string, including leading zeros; `barcode` is its display form. `kind` is `unit` or `variant`, and `is_primary` is 1 for the selected primary owner or 0 otherwise. A product may have several assignments. JSONL/CSV represent these through `gtin14` and `barcode_matches`; each match has `gtin14`, `kind` and `is_primary`.

- `unit` identifies a barcode assigned to the product itself.
- `variant` identifies a related shade, scent, size or edition within the product line.
- `barcode` provides the display form; use `gtin14` for canonical lookups.
- `is_primary = 1` selects the primary product for a code in this export. Other assignments remain available with `is_primary = 0`.
- JSONL/CSV barcode arrays put primary assignments first, then sort by GTIN-14.

Keep barcode values as strings. `barcode_aliases` supplies supported alternative spellings where present. Barcode coverage is partial; use the assignment fields rather than assuming one product per distinct code.

For a UPC-A code such as `782446192371`, the GTIN-14 form is `00782446192371`. Pad UPC-A and EAN codes on the left with zeros; resolve supported alternative spellings through `barcode_aliases` first.

```sql
-- Product to its barcode assignments. Bind :product_id to the dataset ID.
SELECT gtin14, barcode, kind, is_primary
FROM product_barcodes
WHERE product_id = :product_id
ORDER BY is_primary DESC, gtin14;

-- Scanned code to the selected primary product. Bind :barcode as text.
WITH lookup AS (
  SELECT COALESCE(
    (SELECT gtin14 FROM barcode_aliases WHERE barcode = :barcode),
    CASE WHEN length(:barcode) IN (12, 13, 14)
      AND :barcode NOT GLOB '*[^0-9]*'
      THEN substr('00000000000000' || :barcode, -14) END
  ) AS gtin14
)
SELECT p.*
FROM lookup l
JOIN product_barcodes b ON b.gtin14 = l.gtin14
JOIN products p ON p.id = b.product_id
WHERE b.is_primary = 1;
```

## Format and loading notes

JSONL uses JSON nulls and native arrays. CSV uses a blank cell for null, never the literal text `null`; array fields are JSON text. SQLite uses SQL NULL, integers for booleans, and JSON text for dictionary functions. The product's formula structure is represented by relational rows rather than JSON columns in SQLite.

- CSV files have a UTF-8 byte-order mark (BOM) and CRLF record endings. Use `utf-8-sig` when loading them with Python.
- CSV follows RFC 4180 quoting: fields containing commas, quotes or line breaks are quoted, and internal quotes are doubled.
- JSONL contains one product per line, sorted by product ID. Ingredient arrays follow `position`; positions restart within each list.
- JSONL arrays and booleans remain native JSON values. CSV array fields must be decoded from JSON text.

For CSV imports with pandas, specify nullable identifiers and boolean values explicitly:

```python
import pandas as pd

products = pd.read_csv(
    "products.csv", encoding="utf-8-sig",
    dtype={"id": "Int64", "pack_count": "Int64", "contains_fragrance": "boolean"},
    true_values=["true"], false_values=["false"],
    keep_default_na=False, na_values=[""],
)
links = pd.read_csv(
    "product_ingredients.csv", encoding="utf-8-sig",
    dtype={"product_id": "Int64", "ingredient_id": "Int64", "position": "Int64"},
    keep_default_na=False, na_values=[""],
)
ingredients = pd.read_csv("ingredients.csv", encoding="utf-8-sig", dtype={"id": "Int64"}, keep_default_na=False, na_values=[""])
one = (links[links.product_id == 1]
       .merge(ingredients, how="left", left_on="ingredient_id", right_on="id")
       .sort_values("position"))
```

Apply the nullable boolean dtype to the other `contains_*` columns when loading them. Do not convert blank flags with a comparison such as `value == "true"`, which would turn unknown values into false.

### JSONL and JSON-array columns

```python
import json
import pandas as pd

# Load nested products directly.
products_jsonl = pd.read_json("products.jsonl", lines=True)

# Decode array-valued CSV cells after loading the tables above.
for column in ["gtin14", "barcode_matches"]:
    products[column] = products[column].map(json.loads)
ingredients["functions"] = ingredients["functions"].map(json.loads)
```

### Useful SQLite queries

```sql
-- Look up chemical identifiers.
SELECT id, name, cas_number, ec_number, iupac_name
FROM ingredients
WHERE name = 'Ascorbic Acid';

-- Find products containing Niacinamide in a flat list, section or component.
WITH occurrences AS (
  SELECT product_id, ingredient_id FROM product_ingredients
  UNION
  SELECT g.product_id, gi.ingredient_id
  FROM product_ingredient_groups g
  JOIN product_group_ingredients gi ON gi.group_id = g.id
)
SELECT DISTINCT p.id, p.brand, p.name
FROM products p
JOIN occurrences o ON o.product_id = p.id
JOIN ingredients i ON i.id = o.ingredient_id
WHERE i.name = 'Niacinamide'
LIMIT 10;

-- Skincare products with the fragrance flag set to false.
SELECT id, brand, name FROM products
WHERE category = 'skincare' AND contains_fragrance = 0
LIMIT 10;
```

## Images

- Images are JPEGs named `<id>.jpeg`, matched through `image_name`.
- Paid image ZIPs contain files directly, without a subdirectory. Extract all supplied `images_N.zip` archives into the same destination directory.
- The sample ZIP places its selected images in `images/`.
- Use the supplied archive inventory; archive numbers do not identify fixed product-ID ranges.

Join records to image files using `image_name`. A null value means no associated image. Use the supplied filenames and archive inventory; product IDs can have gaps, so the largest ID is not an image count.

## Releases and updates

SQLite files carry `products.updated_at` and `ingredients.updated_at` as release dates (`YYYY-MM-DD`). Product stamps cover product fields, ingredient relationships, group structures, barcodes and images; ingredient dictionary changes have their own stamps. JSONL and CSV do not carry these release stamps.

The `meta` table identifies the dataset with `release_version`, `release_date`, `release_title` and `built_at`. Its population fields include `product_count`, `ingredient_count`, `link_count`, `ingredient_group_count`, `group_link_count` and `barcode_link_count`. `link_count` counts flat ingredient occurrences; `group_link_count` counts grouped ingredient occurrences. Total ingredient occurrences = `link_count` + `group_link_count`; neither is a count of distinct ingredients. `ingredient_group_count` counts section and component rows, not products.

### Compare releases

```sql
-- Identify the release contained in this file.
SELECT key, value FROM meta;

-- Find products changed after an earlier release date.
-- Bind :previous_release_date to a YYYY-MM-DD date from CHANGELOG.md.
SELECT id, brand, name, updated_at
FROM products
WHERE updated_at > :previous_release_date;

-- Find ingredient dictionary rows changed in this release.
SELECT id, name, updated_at
FROM ingredients
WHERE updated_at = (SELECT value FROM meta WHERE key = 'release_date');
```

These queries identify records present in the current snapshot. To identify removals, compare IDs with your previous snapshot and use the alias files to resolve consolidated records.

Consult the accompanying `CHANGELOG.md` for this release's changes, or the [website changelog](https://thebeautyapi.com/changelog) for the published release history.
