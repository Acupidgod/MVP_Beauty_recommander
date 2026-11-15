from pathlib import Path
from typing import Dict, List, Optional, Set

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "static"
CSV_PATH = DATA_DIR / "products.csv"
PRODUCT_INGREDIENTS_PATH = DATA_DIR / "product_ingredients.csv"
PRODUCT_IMAGES_DIR = DATA_DIR / "images"
METADATA_FEATURES = ("category", "subcategory", "product_type")


class RecommendationRequest(BaseModel):
    selected_ids: List[int] = Field(
        ..., min_items=1, max_items=5, description="De 1 à 5 identifiants de produits"
    )
    excluded_ingredients: List[str] = Field(
        default_factory=list,
        max_length=2,
        description="Jusqu'à 2 ingrédients à exclure des recommandations",
    )
    top_n: int = Field(default=3, ge=1, le=20)


class ProductResponse(BaseModel):
    id: int
    brand: str = ""
    name: str = ""
    image_name: Optional[str] = None
    category: str = ""
    subcategory: str = ""
    size: Optional[str] = None
    benefits: Optional[str] = None
    origin: str = ""
    product_type: str = ""
    ingredients_raw: str = ""
    contains_fragrance: bool = False
    contains_drying_alcohol: bool = False
    contains_parabens: bool = False
    contains_sulfates: bool = False
    contains_silicones: bool = False
    similarity_score: Optional[float] = None


app = FastAPI(
    title="Cosm'éthique",
    description="Site de recommandation de produits cosmétiques",
    version="1.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/images", StaticFiles(directory=PRODUCT_IMAGES_DIR), name="product-images")


def load_and_prepare_data(
    products_path: Path,
    product_ingredients_path: Path,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if not products_path.is_file():
        raise FileNotFoundError(f"Fichier CSV des produits introuvable : {products_path}")
    if not product_ingredients_path.is_file():
        raise FileNotFoundError(
            f"Fichier CSV des ingrédients introuvable : {product_ingredients_path}"
        )

    products = pd.read_csv(products_path, keep_default_na=False)
    ingredients = pd.read_csv(
        product_ingredients_path,
        usecols=["product_id", "ingredient_id", "label_name"],
        dtype=str,
        keep_default_na=False,
    )
    text_columns = (
        "brand",
        "name",
        "category",
        "subcategory",
        "ingredients_raw",
        "origin",
        "product_type",
        "benefits",
        "directions",
        "warnings",
    )
    bool_columns = (
        "contains_fragrance",
        "contains_drying_alcohol",
        "contains_parabens",
        "contains_sulfates",
        "contains_silicones",
    )

    for column in ("id", *text_columns, *bool_columns):
        if column not in products.columns:
            products[column] = ""
    products[list(text_columns)] = products[list(text_columns)].fillna("").astype(str)
    products["id"] = pd.to_numeric(products["id"], errors="raise").astype(int)
    for column in bool_columns:
        products[column] = products[column].map(
            lambda value: value
            if isinstance(value, bool)
            else str(value).strip().lower() == "true"
        )

    ingredients["product_id"] = pd.to_numeric(
        ingredients["product_id"], errors="raise"
    ).astype(int)
    ingredients["ingredient_id"] = ingredients["ingredient_id"].str.strip()
    return products, ingredients[ingredients["ingredient_id"] != ""]


def build_feature_rows(
    products: pd.DataFrame,
    ingredients: pd.DataFrame,
) -> List[Dict[str, float]]:
    ingredients_by_product = (
        ingredients.groupby("product_id")["ingredient_id"].agg(set).to_dict()
    )
    rows = []
    for product in products.itertuples(index=False):
        features = {
            f"ingredient:{ingredient_id}": 1.0
            for ingredient_id in ingredients_by_product.get(product.id, set())
        }
        features.update(
            {
                f"{column}:{value}": 1.0
                for column in METADATA_FEATURES
                if (
                    value := str(getattr(product, column, "")).strip().casefold()
                )
            }
        )
        rows.append(features)
    return rows


df, ingredient_data = load_and_prepare_data(CSV_PATH, PRODUCT_INGREDIENTS_PATH)
feature_vectorizer = DictVectorizer()
feature_matrix = feature_vectorizer.fit_transform(
    build_feature_rows(df, ingredient_data)
)
cosine_sim = cosine_similarity(feature_matrix, feature_matrix)


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/products", response_model=List[ProductResponse], tags=["Catalogue"])
def get_all_products():
    if df.empty:
        raise HTTPException(
            status_code=500, detail="Le jeu de données n'est pas chargé."
        )
    return df.to_dict(orient="records")


@app.post(
    "/recommend", response_model=List[ProductResponse], tags=["Recommandation"]
)
def get_recommendations(request: RecommendationRequest):
    if df.empty:
        raise HTTPException(
            status_code=500, detail="Le jeu de données n'est pas chargé."
        )
    indices = df.index[df["id"].isin(request.selected_ids)].tolist()
    if not indices:
        raise HTTPException(
            status_code=404,
            detail="Aucun produit valide trouvé pour les identifiants sélectionnés.",
        )

    results = df.copy()
    results["similarity_score"] = np.round(
        np.mean(cosine_sim[indices], axis=0), 3
    )
    results = results[~results["id"].isin(request.selected_ids)]
    for ingredient in request.excluded_ingredients:
        ingredient = str(ingredient).strip()
        if ingredient:
            excluded_ids = ingredient_data.loc[
                ingredient_data["label_name"].str.contains(
                    ingredient, case=False, na=False, regex=False
                ),
                "product_id",
            ].unique()
            results = results[~results["id"].isin(excluded_ids)]
    return results.sort_values("similarity_score", ascending=False).head(
        request.top_n
    ).to_dict(orient="records")
