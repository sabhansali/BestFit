import csv
import random
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

NUM_PRODUCTS = 2310
RANDOM_SEED = 42

OUTPUT_DIR = Path("data")
OUTPUT_FILE = OUTPUT_DIR / "products.csv"

random.seed(RANDOM_SEED)


# ============================================================
# BRANDS
# ============================================================

BRANDS = [
    "UrbanThread",
    "StyleCraft",
    "ModaStreet",
    "Northline",
    "VibeWear",
    "ClassicEdge",
    "TrendAura",
    "CoutureLane",
    "DailyMode",
    "MetroFit",
]


# ============================================================
# COLORS
# ============================================================

COLORS = [
    "Black",
    "White",
    "Navy",
    "Blue",
    "Grey",
    "Beige",
    "Brown",
    "Olive",
    "Maroon",
    "Pink",
    "Green",
    "Cream",
]


# ============================================================
# COLOR COMPATIBILITY
#
# This is also useful later for the outfit compatibility engine.
# ============================================================

COLOR_COMPATIBILITY = {
    "Black": [
        "White",
        "Grey",
        "Beige",
        "Navy",
        "Blue",
        "Cream",
        "Maroon",
    ],

    "White": [
        "Black",
        "Navy",
        "Blue",
        "Grey",
        "Beige",
        "Brown",
        "Olive",
        "Maroon",
    ],

    "Navy": [
        "White",
        "Beige",
        "Grey",
        "Brown",
        "Cream",
        "Blue",
    ],

    "Blue": [
        "White",
        "Black",
        "Beige",
        "Grey",
        "Navy",
        "Brown",
    ],

    "Grey": [
        "Black",
        "White",
        "Navy",
        "Blue",
        "Beige",
        "Maroon",
    ],

    "Beige": [
        "White",
        "Brown",
        "Navy",
        "Black",
        "Olive",
        "Maroon",
    ],

    "Brown": [
        "Beige",
        "White",
        "Cream",
        "Black",
        "Olive",
        "Navy",
    ],

    "Olive": [
        "Beige",
        "White",
        "Black",
        "Brown",
        "Cream",
    ],

    "Maroon": [
        "White",
        "Black",
        "Beige",
        "Grey",
        "Navy",
    ],

    "Pink": [
        "White",
        "Grey",
        "Black",
        "Navy",
        "Beige",
    ],

    "Green": [
        "White",
        "Beige",
        "Black",
        "Brown",
        "Cream",
    ],

    "Cream": [
        "Brown",
        "Black",
        "Navy",
        "Beige",
        "Olive",
        "Maroon",
    ],
}


# ============================================================
# STYLE → VALID OCCASIONS
#
# IMPORTANT:
# Style and occasion are no longer selected independently.
# ============================================================

STYLE_OCCASIONS = {

    "Casual": [
        "College",
        "Casual Outing",
    ],

    "Smart Casual": [
        "College",
        "Farewell",
        "Casual Outing",
    ],

    "Formal": [
        "Office",
        "Farewell",
    ],

    "Party": [
        "Party",
        "Farewell",
    ],

    "Sporty": [
        "College",
        "Casual Outing",
    ],
}


# ============================================================
# FORMALITY
# ============================================================

FORMALITY = {

    "Casual": 1,

    "Sporty": 1,

    "Smart Casual": 2,

    "Party": 2,

    "Formal": 3,
}


# ============================================================
# STYLE DESCRIPTORS
# ============================================================

STYLE_DESCRIPTORS = {

    "Casual": [
        "Everyday",
        "Classic",
        "Comfort",
        "Essential",
    ],

    "Smart Casual": [
        "Modern",
        "Refined",
        "Premium",
        "Classic",
    ],

    "Formal": [
        "Executive",
        "Elegant",
        "Classic",
        "Premium",
    ],

    "Sporty": [
        "Active",
        "Performance",
        "Sport",
        "Dynamic",
    ],

    "Party": [
        "Statement",
        "Elegant",
        "Festive",
        "Stylish",
    ],
}


# ============================================================
# PRODUCT TYPE DEFINITIONS
#
# Each product type controls:
# - category
# - subcategory
# - number of products
# - materials
# - styles
# - seasons
# - patterns
# - price range
# - gender
# - fit
# ============================================================

PRODUCT_TYPES = [

    # ========================================================
    # TOPS
    # ========================================================

    {
        "category": "Top",
        "subcategory": "T-Shirt",
        "count": 160,

        "materials": [
            "Cotton",
            "Polyester",
        ],

        "styles": [
            "Casual",
            "Sporty",
        ],

        "seasons": [
            "Summer",
            "Monsoon",
            "All Season",
        ],

        "patterns": [
            "Solid",
            "Printed",
            "Striped",
            "Textured",
        ],

        "price": (499, 1799),

        "genders": [
            "Men",
            "Women",
            "Unisex",
        ],

        "fits": [
            "Regular",
            "Relaxed",
            "Oversized",
        ],
    },

    {
        "category": "Top",
        "subcategory": "Shirt",
        "count": 160,

        "materials": [
            "Cotton",
            "Linen",
            "Rayon",
        ],

        "styles": [
            "Casual",
            "Smart Casual",
            "Formal",
        ],

        "seasons": [
            "Summer",
            "Winter",
            "All Season",
            "Monsoon",
        ],

        "patterns": [
            "Solid",
            "Checked",
            "Striped",
            "Printed",
        ],

        "price": (899, 2999),

        "genders": [
            "Men",
            "Women",
        ],

        "fits": [
            "Regular",
            "Slim",
            "Relaxed",
        ],
    },

    {
        "category": "Top",
        "subcategory": "Blouse",
        "count": 120,

        "materials": [
            "Rayon",
            "Cotton",
            "Silk Blend",
        ],

        "styles": [
            "Casual",
            "Smart Casual",
            "Formal",
            "Party",
        ],

        "seasons": [
            "Summer",
            "Winter",
            "All Season",
        ],

        "patterns": [
            "Solid",
            "Printed",
            "Textured",
            "Striped",
        ],

        "price": (799, 2499),

        "genders": [
            "Women",
        ],

        "fits": [
            "Regular",
            "Slim",
            "Relaxed",
        ],
    },

    {
        "category": "Top",
        "subcategory": "Knit Top",
        "count": 90,

        "materials": [
            "Cotton",
            "Rayon",
            "Wool Blend",
        ],

        "styles": [
            "Casual",
            "Smart Casual",
        ],

        "seasons": [
            "Winter",
            "All Season",
        ],

        "patterns": [
            "Solid",
            "Textured",
            "Striped",
        ],

        "price": (699, 2199),

        "genders": [
            "Women",
        ],

        "fits": [
            "Regular",
            "Slim",
            "Relaxed",
        ],
    },


    # ========================================================
    # BOTTOMS
    # ========================================================

    {
        "category": "Bottom",
        "subcategory": "Jeans",
        "count": 160,

        "materials": [
            "Denim",
            "Cotton",
        ],

        "styles": [
            "Casual",
            "Smart Casual",
        ],

        "seasons": [
            "Summer",
            "Winter",
            "Monsoon",
            "All Season",
        ],

        "patterns": [
            "Solid",
            "Textured",
        ],

        "price": (1199, 2999),

        "genders": [
            "Men",
            "Women",
        ],

        "fits": [
            "Slim",
            "Straight",
            "Relaxed",
        ],
    },

    {
        "category": "Bottom",
        "subcategory": "Trousers",
        "count": 150,

        "materials": [
            "Cotton",
            "Polyester",
            "Wool Blend",
        ],

        "styles": [
            "Smart Casual",
            "Formal",
        ],

        "seasons": [
            "Summer",
            "Winter",
            "All Season",
        ],

        "patterns": [
            "Solid",
            "Checked",
            "Textured",
        ],

        "price": (1299, 3299),

        "genders": [
            "Men",
            "Women",
        ],

        "fits": [
            "Slim",
            "Straight",
            "Regular",
        ],
    },

    {
        "category": "Bottom",
        "subcategory": "Chinos",
        "count": 120,

        "materials": [
            "Cotton",
            "Cotton Blend",
        ],

        "styles": [
            "Casual",
            "Smart Casual",
        ],

        "seasons": [
            "Summer",
            "Winter",
            "All Season",
        ],

        "patterns": [
            "Solid",
            "Textured",
        ],

        "price": (1199, 2999),

        "genders": [
            "Men",
        ],

        "fits": [
            "Slim",
            "Straight",
            "Regular",
        ],
    },

    {
        "category": "Bottom",
        "subcategory": "Skirt",
        "count": 100,

        "materials": [
            "Cotton",
            "Rayon",
            "Denim",
            "Polyester",
        ],

        "styles": [
            "Casual",
            "Smart Casual",
            "Party",
        ],

        "seasons": [
            "Summer",
            "Winter",
            "All Season",
        ],

        "patterns": [
            "Solid",
            "Printed",
            "Checked",
            "Textured",
        ],

        "price": (999, 2799),

        "genders": [
            "Women",
        ],

        "fits": [
            "Straight",
            "A-Line",
            "Relaxed",
        ],
    },


    # ========================================================
    # DRESSES
    # ========================================================

    {
        "category": "Dress",
        "subcategory": "Casual Dress",
        "count": 130,

        "materials": [
            "Cotton",
            "Rayon",
            "Linen",
        ],

        "styles": [
            "Casual",
            "Smart Casual",
        ],

        "seasons": [
            "Summer",
            "All Season",
        ],

        "patterns": [
            "Solid",
            "Printed",
            "Striped",
        ],

        "price": (1299, 3499),

        "genders": [
            "Women",
        ],

        "fits": [
            "Regular",
            "Relaxed",
            "A-Line",
        ],
    },

    {
        "category": "Dress",
        "subcategory": "Formal Dress",
        "count": 100,

        "materials": [
            "Polyester",
            "Rayon",
            "Silk Blend",
        ],

        "styles": [
            "Formal",
            "Party",
        ],

        "seasons": [
            "Summer",
            "Winter",
            "All Season",
        ],

        "patterns": [
            "Solid",
            "Textured",
            "Printed",
        ],

        "price": (1799, 4999),

        "genders": [
            "Women",
        ],

        "fits": [
            "Slim",
            "Regular",
            "A-Line",
        ],
    },


    # ========================================================
    # OUTERWEAR
    # ========================================================

    {
        "category": "Outerwear",
        "subcategory": "Blazer",
        "count": 100,

        "materials": [
            "Wool Blend",
            "Polyester",
            "Cotton Blend",
        ],

        "styles": [
            "Formal",
            "Smart Casual",
        ],

        "seasons": [
            "Winter",
            "All Season",
        ],

        "patterns": [
            "Solid",
            "Checked",
            "Textured",
        ],

        "price": (2499, 6999),

        "genders": [
            "Men",
            "Women",
        ],

        "fits": [
            "Slim",
            "Regular",
        ],
    },

    {
        "category": "Outerwear",
        "subcategory": "Denim Jacket",
        "count": 90,

        "materials": [
            "Denim",
            "Cotton",
        ],

        "styles": [
            "Casual",
            "Smart Casual",
        ],

        "seasons": [
            "Winter",
            "Monsoon",
            "All Season",
        ],

        "patterns": [
            "Solid",
            "Textured",
        ],

        "price": (1799, 3999),

        "genders": [
            "Men",
            "Women",
        ],

        "fits": [
            "Regular",
            "Relaxed",
            "Oversized",
        ],
    },

    {
        "category": "Outerwear",
        "subcategory": "Overshirt",
        "count": 70,

        "materials": [
            "Cotton",
            "Linen",
            "Denim",
        ],

        "styles": [
            "Casual",
            "Smart Casual",
        ],

        "seasons": [
            "Winter",
            "Monsoon",
            "All Season",
        ],

        "patterns": [
            "Solid",
            "Checked",
            "Textured",
        ],

        "price": (1299, 2999),

        "genders": [
            "Men",
            "Women",
        ],

        "fits": [
            "Regular",
            "Relaxed",
            "Oversized",
        ],
    },


    # ========================================================
    # FOOTWEAR
    # ========================================================

    {
        "category": "Footwear",
        "subcategory": "Sneakers",
        "count": 150,

        "materials": [
            "Canvas",
            "Mesh",
            "Leather",
            "Synthetic",
        ],

        "styles": [
            "Casual",
            "Smart Casual",
            "Sporty",
        ],

        "seasons": [
            "Summer",
            "Winter",
            "Monsoon",
            "All Season",
        ],

        "patterns": [
            "Solid",
            "Textured",
            "Printed",
        ],

        "price": (1499, 4999),

        "genders": [
            "Men",
            "Women",
            "Unisex",
        ],

        "fits": [
            "Standard",
        ],
    },

    {
        "category": "Footwear",
        "subcategory": "Loafers",
        "count": 90,

        "materials": [
            "Leather",
            "Faux Leather",
            "Suede",
        ],

        "styles": [
            "Smart Casual",
            "Formal",
        ],

        "seasons": [
            "Winter",
            "Summer",
            "All Season",
        ],

        "patterns": [
            "Solid",
            "Textured",
        ],

        "price": (1999, 4999),

        "genders": [
            "Men",
            "Women",
        ],

        "fits": [
            "Standard",
        ],
    },

    {
        "category": "Footwear",
        "subcategory": "Formal Shoes",
        "count": 80,

        "materials": [
            "Leather",
            "Faux Leather",
        ],

        "styles": [
            "Formal",
        ],

        "seasons": [
            "Winter",
            "Summer",
            "All Season",
        ],

        "patterns": [
            "Solid",
            "Textured",
        ],

        "price": (2199, 5499),

        "genders": [
            "Men",
        ],

        "fits": [
            "Standard",
        ],
    },

    {
        "category": "Footwear",
        "subcategory": "Heels",
        "count": 80,

        "materials": [
            "Faux Leather",
            "Synthetic",
            "Suede",
        ],

        "styles": [
            "Formal",
            "Party",
        ],

        "seasons": [
            "Summer",
            "Winter",
            "All Season",
        ],

        "patterns": [
            "Solid",
            "Textured",
        ],

        "price": (1799, 4999),

        "genders": [
            "Women",
        ],

        "fits": [
            "Standard",
        ],
    },

    {
        "category": "Footwear",
        "subcategory": "Sandals",
        "count": 80,

        "materials": [
            "Leather",
            "Synthetic",
            "Faux Leather",
        ],

        "styles": [
            "Casual",
            "Smart Casual",
        ],

        "seasons": [
            "Summer",
            "All Season",
        ],

        "patterns": [
            "Solid",
            "Textured",
        ],

        "price": (799, 2499),

        "genders": [
            "Women",
            "Unisex",
        ],

        "fits": [
            "Standard",
        ],
    },


    # ========================================================
    # ACCESSORIES
    # ========================================================

    {
        "category": "Accessory",
        "subcategory": "Belt",
        "count": 60,

        "materials": [
            "Leather",
            "Faux Leather",
        ],

        "styles": [
            "Smart Casual",
            "Formal",
        ],

        "seasons": [
            "All Season",
        ],

        "patterns": [
            "Solid",
            "Textured",
        ],

        "price": (499, 1499),

        "genders": [
            "Men",
            "Women",
            "Unisex",
        ],

        "fits": [
            "Standard",
        ],
    },

    {
        "category": "Accessory",
        "subcategory": "Watch",
        "count": 80,

        "materials": [
            "Stainless Steel",
            "Leather",
            "Synthetic",
        ],

        "styles": [
            "Casual",
            "Smart Casual",
            "Formal",
        ],

        "seasons": [
            "All Season",
        ],

        "patterns": [
            "Solid",
            "Textured",
        ],

        "price": (999, 4999),

        "genders": [
            "Men",
            "Women",
            "Unisex",
        ],

        "fits": [
            "Standard",
        ],
    },

    {
        "category": "Accessory",
        "subcategory": "Shoulder Bag",
        "count": 70,

        "materials": [
            "Leather",
            "Faux Leather",
            "Canvas",
        ],

        "styles": [
            "Casual",
            "Smart Casual",
            "Party",
        ],

        "seasons": [
            "Summer",
            "Winter",
            "All Season",
        ],

        "patterns": [
            "Solid",
            "Printed",
            "Textured",
        ],

        "price": (999, 2999),

        "genders": [
            "Women",
            "Unisex",
        ],

        "fits": [
            "Standard",
        ],
    },

    {
        "category": "Accessory",
        "subcategory": "Backpack",
        "count": 70,

        "materials": [
            "Canvas",
            "Polyester",
            "Synthetic",
        ],

        "styles": [
            "Casual",
            "Sporty",
        ],

        "seasons": [
            "Summer",
            "Winter",
            "Monsoon",
            "All Season",
        ],

        "patterns": [
            "Solid",
            "Printed",
            "Textured",
        ],

        "price": (899, 2499),

        "genders": [
            "Men",
            "Women",
            "Unisex",
        ],

        "fits": [
            "Standard",
        ],
    },
]


# ============================================================
# VALIDATION
# ============================================================

def validate_product_type(product_type):

    required_keys = [
        "category",
        "subcategory",
        "count",
        "materials",
        "styles",
        "seasons",
        "patterns",
        "price",
        "genders",
        "fits",
    ]

    for key in required_keys:

        if key not in product_type:
            raise ValueError(
                f"Missing '{key}' in "
                f"{product_type.get('subcategory', 'unknown')}"
            )

    for style in product_type["styles"]:

        if style not in STYLE_OCCASIONS:
            raise ValueError(
                f"Style '{style}' does not have "
                f"a STYLE_OCCASIONS definition."
            )


# ============================================================
# COLOR FUNCTIONS
# ============================================================

def choose_primary_color():

    return random.choice(COLORS)


def choose_secondary_color(primary_color):

    compatible_colors = COLOR_COMPATIBILITY.get(
        primary_color,
        COLORS,
    )

    return random.choice(
        compatible_colors
    )


# ============================================================
# PRODUCT NAME
# ============================================================

def generate_product_name(
    brand,
    descriptor,
    primary_color,
    subcategory,
    pattern,
):

    parts = [
        brand,
        descriptor,
        primary_color,
    ]

    # Avoid unnecessary pattern wording for common cases.
    if pattern in [
        "Printed",
        "Striped",
        "Checked",
    ]:
        parts.append(pattern)

    parts.append(subcategory)

    return " ".join(parts)


# ============================================================
# DESCRIPTION
# ============================================================

def generate_description(
    style,
    subcategory,
    primary_color,
    secondary_color,
    occasion,
    season,
    material,
    pattern,
    fit,
):

    # --------------------------------------------------------
    # Avoid "Formal Formal Shoes"
    # --------------------------------------------------------

    if style.lower() in subcategory.lower():
        product_phrase = subcategory
    else:
        product_phrase = f"{style} {subcategory}"

    return (
        f"{product_phrase} in {primary_color} "
        f"with {secondary_color} accents. "
        f"Designed for {occasion.lower()} occasions "
        f"and suitable for {season.lower()} wear. "
        f"Made from {material.lower()} with a "
        f"{pattern.lower()} pattern and {fit.lower()} fit."
    )


# ============================================================
# GENERATE ONE PRODUCT
# ============================================================

def generate_product(
    product_id,
    product_type,
):

    category = product_type["category"]

    subcategory = product_type["subcategory"]

    # --------------------------------------------------------
    # Choose STYLE first
    # --------------------------------------------------------

    style = random.choice(
        product_type["styles"]
    )

    # --------------------------------------------------------
    # Choose OCCASION based on STYLE
    #
    # This is the important correction.
    # --------------------------------------------------------

    valid_occasions = STYLE_OCCASIONS[
        style
    ]

    # Only choose occasions that are valid for
    # this particular product type as well.

    type_occasions = set(
        valid_occasions
    )

    # Product type does not explicitly store occasions,
    # so style is the primary controlling relationship.

    occasion = random.choice(
        list(type_occasions)
    )

    # --------------------------------------------------------
    # Other controlled attributes
    # --------------------------------------------------------

    season = random.choice(
        product_type["seasons"]
    )

    material = random.choice(
        product_type["materials"]
    )

    pattern = random.choice(
        product_type["patterns"]
    )

    gender = random.choice(
        product_type["genders"]
    )

    fit = random.choice(
        product_type["fits"]
    )

    primary_color = choose_primary_color()

    secondary_color = choose_secondary_color(
        primary_color
    )

    brand = random.choice(
        BRANDS
    )

    descriptor = random.choice(
        STYLE_DESCRIPTORS[style]
    )

    # --------------------------------------------------------
    # Price
    # --------------------------------------------------------

    min_price, max_price = product_type["price"]

    price = random.randrange(
        min_price,
        max_price + 1,
        100,
    )

    # --------------------------------------------------------
    # Ratings
    # --------------------------------------------------------

    rating = round(
        random.uniform(3.5, 4.9),
        1,
    )

    review_count = random.randint(
        25,
        5000,
    )

    # --------------------------------------------------------
    # Name
    # --------------------------------------------------------

    name = generate_product_name(
        brand=brand,
        descriptor=descriptor,
        primary_color=primary_color,
        subcategory=subcategory,
        pattern=pattern,
    )

    # --------------------------------------------------------
    # Description
    # --------------------------------------------------------

    description = generate_description(
        style=style,
        subcategory=subcategory,
        primary_color=primary_color,
        secondary_color=secondary_color,
        occasion=occasion,
        season=season,
        material=material,
        pattern=pattern,
        fit=fit,
    )

    # --------------------------------------------------------
    # Final product
    # --------------------------------------------------------

    return {

        "product_id":
            f"P{product_id:05d}",

        "name":
            name,

        "category":
            category,

        "subcategory":
            subcategory,

        "gender":
            gender,

        "price_inr":
            price,

        "color":
            primary_color,

        "secondary_color":
            secondary_color,

        "pattern":
            pattern,

        "style":
            style,

        "formality":
            FORMALITY[style],

        "occasion":
            occasion,

        "season":
            season,

        "material":
            material,

        "fit":
            fit,

        "brand":
            brand,

        "rating":
            rating,

        "review_count":
            review_count,

        "description":
            description,
    }


# ============================================================
# DATASET GENERATION
# ============================================================

def generate_dataset():

    # --------------------------------------------------------
    # Validate configuration
    # --------------------------------------------------------

    for product_type in PRODUCT_TYPES:

        validate_product_type(
            product_type
        )

    configured_total = sum(
        product_type["count"]
        for product_type in PRODUCT_TYPES
    )

    if configured_total != NUM_PRODUCTS:

        raise ValueError(
            f"Configured product count is "
            f"{configured_total}, but NUM_PRODUCTS "
            f"is {NUM_PRODUCTS}."
        )

    # --------------------------------------------------------
    # Create output directory
    # --------------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Generate products
    # --------------------------------------------------------

    products = []

    product_id = 1

    for product_type in PRODUCT_TYPES:

        for _ in range(
            product_type["count"]
        ):

            product = generate_product(
                product_id=product_id,
                product_type=product_type,
            )

            products.append(
                product
            )

            product_id += 1

    # --------------------------------------------------------
    # Shuffle products
    # --------------------------------------------------------

    random.shuffle(
        products
    )

    # --------------------------------------------------------
    # Write CSV
    # --------------------------------------------------------

    fieldnames = list(
        products[0].keys()
    )

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        writer.writerows(
            products
        )

    # --------------------------------------------------------
    # Dataset statistics
    # --------------------------------------------------------

    category_counts = {}

    subcategory_counts = {}

    style_counts = {}

    occasion_counts = {}

    gender_counts = {}

    season_counts = {}

    material_counts = {}

    for product in products:

        category = product["category"]
        subcategory = product["subcategory"]
        style = product["style"]
        occasion = product["occasion"]
        gender = product["gender"]
        season = product["season"]
        material = product["material"]

        category_counts[category] = (
            category_counts.get(category, 0) + 1
        )

        subcategory_counts[subcategory] = (
            subcategory_counts.get(subcategory, 0) + 1
        )

        style_counts[style] = (
            style_counts.get(style, 0) + 1
        )

        occasion_counts[occasion] = (
            occasion_counts.get(occasion, 0) + 1
        )

        gender_counts[gender] = (
            gender_counts.get(gender, 0) + 1
        )

        season_counts[season] = (
            season_counts.get(season, 0) + 1
        )

        material_counts[material] = (
            material_counts.get(material, 0) + 1
        )

    # --------------------------------------------------------
    # Print summary
    # --------------------------------------------------------

    print()

    print("=" * 70)
    print("FASHION DATASET GENERATION COMPLETE")
    print("=" * 70)

    print(
        f"Products generated : {len(products)}"
    )

    print(
        f"Output file        : {OUTPUT_FILE}"
    )

    print(
        f"Random seed        : {RANDOM_SEED}"
    )

    print()

    print("-" * 70)
    print("CATEGORY DISTRIBUTION")
    print("-" * 70)

    for category, count in sorted(
        category_counts.items()
    ):

        print(
            f"{category:<18} {count}"
        )

    print()

    print("-" * 70)
    print("SUBCATEGORY DISTRIBUTION")
    print("-" * 70)

    for subcategory, count in sorted(
        subcategory_counts.items()
    ):

        print(
            f"{subcategory:<20} {count}"
        )

    print()

    print("-" * 70)
    print("STYLE DISTRIBUTION")
    print("-" * 70)

    for style, count in sorted(
        style_counts.items()
    ):

        print(
            f"{style:<18} {count}"
        )

    print()

    print("-" * 70)
    print("OCCASION DISTRIBUTION")
    print("-" * 70)

    for occasion, count in sorted(
        occasion_counts.items()
    ):

        print(
            f"{occasion:<18} {count}"
        )

    print()

    print("-" * 70)
    print("GENDER DISTRIBUTION")
    print("-" * 70)

    for gender, count in sorted(
        gender_counts.items()
    ):

        print(
            f"{gender:<18} {count}"
        )

    print()

    print("-" * 70)
    print("SEASON DISTRIBUTION")
    print("-" * 70)

    for season, count in sorted(
        season_counts.items()
    ):

        print(
            f"{season:<18} {count}"
        )

    print()

    print("-" * 70)
    print("MATERIAL DISTRIBUTION")
    print("-" * 70)

    for material, count in sorted(
        material_counts.items()
    ):

        print(
            f"{material:<20} {count}"
        )

    print()

    print("=" * 70)
    print("Dataset generation finished successfully.")
    print("=" * 70)
    print()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    generate_dataset()