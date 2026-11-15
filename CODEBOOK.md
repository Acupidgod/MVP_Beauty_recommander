# Codebook — Cosm'éthique

Ce document, généré par AI, décrit les fichiers et dossiers du projet, le rôle des données et les principales règles de l'application.

## Structure du projet

### Fichiers à la racine

| Fichier | Description |
|---|---|
| [`app.py`](./app.py) | Point d'entrée Python de l'application FastAPI. Charge le catalogue, construit les caractéristiques binaires à partir des identifiants d'ingrédients et des catégories de produits, calcule les similarités et expose les routes du site. C'est le module utilisé par la commande de déploiement `uvicorn app:app`. |
| [`app.ipynb`](./app.ipynb) | Notebook français contenant les définitions de l'API, le chargement du modèle et des cellules pour démarrer ou arrêter le serveur en local. |
| [`main.ipynb`](./main.ipynb) | Notebook d'accès rapide qui importe l'API et les objets de recommandation depuis `app.py`. |
| [`requirements.txt`](./requirements.txt) | Dépendances Python nécessaires au serveur et au modèle : FastAPI, Uvicorn, Pandas, NumPy, scikit-learn, Pydantic et Requests. |
| [`.gitignore`](./.gitignore) | Exclut notamment l'environnement virtuel, le cache Python, les points de contrôle Jupyter et les fichiers `.env` du suivi Git. |
| [`CODEBOOK.md`](./CODEBOOK.md) | Présent document : inventaire et description des données et du code. |

### Dossiers

| Dossier | Contenu |
|---|---|
| [`data/`](./data/) | Données du catalogue, dictionnaire d'ingrédients, liens produits-ingrédients, documentation de l'échantillon et images. |
| [`data/images/`](./data/images/) | 1 000 images JPEG de produits. Le nom de fichier est associé à la colonne `image_name` de `products.csv`; le site les sert à l'adresse `/images/<nom-du-fichier>`. |
| [`static/`](./static/) | Fichiers statiques du site web. |
| [`__pycache__/`](./__pycache__/) | Fichiers compilés automatiquement par Python; éléments temporaires, non nécessaires au déploiement. |
| [`.venv/`](./.venv/) | Environnement virtuel Python local contenant l'interpréteur et les bibliothèques installées. Il est ignoré par Git et ne doit pas être publié. |
| [`.git/`](./.git/) | Métadonnées et historique Git du dépôt local; Git le gère automatiquement. |

### Fichiers de `data/`

| Fichier | Description |
|---|---|
| [`data/products.csv`](./data/products.csv) | Catalogue principal : 1 248 enregistrements et 23 colonnes de produits, notamment identifiant, marque, nom, catégorie, sous-catégorie, indicateurs de formulation, détails et nom de l'image. |
| [`data/product_ingredients.csv`](./data/product_ingredients.csv) | Table relationnelle contenant 23 657 lignes d'ingrédients associés à un produit et leur ordre. L'application utilise `product_id`, `ingredient_id` et `label_name`; elle n'utilise pas `concentration` pour calculer la similarité. |
| [`data/ingredients.csv`](./data/ingredients.csv) | Dictionnaire de 3 064 ingrédients et informations descriptives : nom, fonctions, évaluations et identifiants chimiques. |
| [`data/README.md`](./data/README.md) | Présentation des fichiers de l'échantillon fourni et indications d'importation. |
| [`data/schema.md`](./data/schema.md) | Documentation détaillée du schéma complet du jeu de données et de ses relations. |
| [`data/CHANGELOG.md`](./data/CHANGELOG.md) | Historique des versions et des évolutions du jeu de données. |

> **Fichier mentionné mais absent :** `data/README.md` décrit également `products.jsonl`, mais ce fichier n'existe pas dans le dossier `data/` actuellement présent. L'application utilise les fichiers CSV listés ci-dessus et ne dépend pas de ce JSONL.

### Fichier de `static/`

| Fichier | Description |
|---|---|
| [`static/index.html`](./static/index.html) | Interface française : recherche et filtre par catégorie, sélection d'au plus cinq produits, choix de deux ingrédients à éviter au maximum, puis affichage des recommandations. Les listes de produits et d'ingrédients sont chargées depuis l'API. |

## Dictionnaire des données

### `products.csv`

Le fichier comporte 23 colonnes. Toutes sont renvoyées par `/products`; les champs affichés dépendent de l'interface.

| Colonne | Rôle |
|---|---|
| `id` | Identifiant numérique du produit; clé utilisée par les requêtes de recommandation. |
| `brand`, `name` | Marque et nom du produit; affichés dans les cartes et utilisés pour la recherche. |
| `image_name` | Nom du JPEG associé dans `data/images/`. |
| `gtin14`, `barcode_matches` | Codes-barres et correspondances, stockés sous forme de texte JSON dans le CSV. |
| `category`, `subcategory`, `product_type` | Catégorie, sous-catégorie et type. Ces valeurs normalisées sont des caractéristiques de similarité, séparées des caractéristiques d'ingrédients. |
| `origin` | Pays d'origine indiqué pour la marque, lorsqu'il est connu. |
| `contains_fragrance`, `contains_drying_alcohol`, `contains_parabens`, `contains_sulfates`, `contains_silicones` | Indicateurs booléens décrivant les ingrédients répertoriés. |
| `size`, `packaging`, `pack_count`, `shade_name` | Taille, emballage, quantité et teinte, selon les informations disponibles. |
| `benefits`, `directions`, `warnings` | Bénéfices, mode d'emploi et avertissements fournis. |
| `ingredients_raw` | Texte d'ingrédients d'origine. Il est renvoyé dans les réponses produits, mais n'est pas utilisé pour calculer la similarité. |

### `product_ingredients.csv`

| Colonne | Rôle |
|---|---|
| `product_id` | Identifiant du produit; correspond à `products.csv:id`. |
| `ingredient_id` | Identifiant normalisé de l'ingrédient; utilisé comme caractéristique binaire pour le calcul de similarité. |
| `position` | Position de l'ingrédient dans la liste d'origine. |
| `concentration` | Concentration déclarée lorsqu'elle est disponible. La recommandation ne la lit pas et ne la pondère pas. |
| `label_name` | Libellé de l'ingrédient. Sert à proposer les choix des menus déroulants et à exclure les produits contenant l'ingrédient sélectionné. |

### `ingredients.csv`

| Groupe de colonnes | Rôle |
|---|---|
| `id`, `name`, `other_names` | Identifiant, nom canonique et autres noms de l'ingrédient. |
| `rating`, `irritancy`, `comedogenicity` | Informations d'évaluation disponibles dans le dictionnaire. |
| `functions`, `category` | Fonctions et catégorie de l'ingrédient. |
| `cas_number`, `ec_number`, `ph_eur_name`, `iupac_name` | Identifiants et noms chimiques, lorsqu'ils sont connus. |

## Fonctionnement de la recommandation

1. `/products` renvoie les enregistrements du catalogue.
2. `/ingredients` renvoie la liste triée des libellés d'ingrédients non vides présents dans `product_ingredients.csv`.
3. Le navigateur envoie à `/recommend` entre un et cinq identifiants de produits, zéro à deux libellés d'ingrédients à exclure et une limite de résultats.
4. Chaque produit est représenté par des indicateurs de présence (`1`) pour ses identifiants d'ingrédients et ses valeurs de `category`, `subcategory` et `product_type`. La concentration n'est pas incluse.
5. La similarité cosinus des vecteurs sert à classer les produits. Les produits choisis et ceux qui contiennent l'un des ingrédients interdits sont retirés des résultats.

Les principales contraintes de l'API sont : 1 à 5 produits sélectionnés, au maximum 2 ingrédients à exclure et entre 1 et 20 recommandations demandées.