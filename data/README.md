# The Beauty API sample dataset
Ceci est le READ ME qui vient avec l'échantillon

This sample contains 1,000 products. The same products are available in products.jsonl and products.csv. products.jsonl includes nested ingredient details; the separate CSV tables provide the related ingredients and formula groups for these products only.

Included files:
- products.csv: the same selected product records.
- ingredients.csv: ingredient identities used by these products.
- product_ingredients.csv: ordered ingredients for products with a single list.
- images/: matching product images, when supplied.
- README.md, schema.md and CHANGELOG.md: sample instructions, field definitions and release history.

Start with products.jsonl for one product per line, or products.csv and the related CSV tables for a relational import. ingredients.csv contains only ingredient identities referenced by the sample products, including their sections and components.

schema.md explains the fields and the full Complete Archive layout. This sample includes one product JSONL file and CSV tables; the SQLite database, historical ID and barcode alias tables, and separate ingredient JSONL file described in that guide are not included here. Where an images folder is included, image_name identifies the corresponding product image.
