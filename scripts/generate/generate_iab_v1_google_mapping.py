#!/usr/bin/env python3
"""Generate IAB Ad Product v1.0 → Google Product Type canonical mapping.

Uses hierarchical inheritance: entries without explicit TARGETS inherit
their parent's targets. Service/B2B categories map to empty targets [].
"""
import json
import os
from datetime import datetime, timezone


def t(tid, tpath, conf, mtype, notes=""):
    return {"target_id": tid, "target_path": tpath, "confidence": conf, "match_type": mtype, "notes": notes}


# Explicit targets per IAB v1.0 entry ID.
# Children without an entry here inherit their parent's targets.
TARGETS = {
    # ── Apps (1–26): all → software (partial) ─────────────────────────────
    "1": [t("software", "Software", 0.65, "partial", "App store category")],
    "2": [t("software", "Software", 0.65, "partial")],
    "3": [t("media__books", "Media > Books", 0.75, "semantic", "Books apps → books media")],
    "4": [t("software__computer-software__business-productivity-software",
            "Software > Computer Software > Business & Productivity Software", 0.80, "semantic")],
    "5": [t("software", "Software", 0.65, "partial")],
    "6": [t("software", "Software", 0.65, "partial")],
    "7": [t("software", "Software", 0.70, "partial")],
    "8": [t("software", "Software", 0.65, "partial")],
    "9": [t("software__video-game-software", "Software > Video Game Software", 0.80, "semantic", "Games apps")],
    "0": [t("software", "Software", 0.65, "partial")],
    "11": [t("software", "Software", 0.65, "partial")],
    "12": [t("media__magazines-newspapers", "Media > Magazines & Newspapers", 0.80, "semantic", "Magazine/news apps")],
    "13": [t("software", "Software", 0.65, "partial")],
    "14": [t("media__music-sound-recordings", "Media > Music & Sound Recordings", 0.75, "semantic", "Music apps")],
    "15": [t("software", "Software", 0.65, "partial")],
    "16": [t("software", "Software", 0.65, "partial")],
    "17": [t("software", "Software", 0.65, "partial")],
    "18": [t("software__computer-software__business-productivity-software",
            "Software > Computer Software > Business & Productivity Software", 0.75, "semantic", "Productivity apps")],
    "19": [t("software", "Software", 0.65, "partial")],
    "20": [t("software", "Software", 0.65, "partial")],
    "21": [t("software", "Software", 0.65, "partial")],
    "22": [t("software", "Software", 0.65, "partial")],
    "23": [t("software", "Software", 0.65, "partial")],
    "24": [t("software", "Software", 0.65, "partial")],
    "25": [t("software", "Software", 0.65, "partial")],
    "26": [t("software", "Software", 0.65, "partial")],

    # ── Arts and Entertainment (27–52) ────────────────────────────────────
    "27": [t("arts-entertainment", "Arts & Entertainment", 0.90, "semantic")],
    "28": [],  # Blogs/Forums/Social Networks – service
    "29": [t("arts-entertainment", "Arts & Entertainment", 0.75, "partial")],
    "30": [t("arts-entertainment__event-tickets", "Arts & Entertainment > Event Tickets", 0.85, "semantic")],
    # 31-46 (children of Experiences and Events) inherit from 30
    "47": [],  # Fantasy Sports – service/game
    "48": [],  # Streaming Services – service
    "49": [],  # Online Entertainment – service
    "50": [],  # Radio and Podcasts – service
    "51": [t("arts-entertainment__event-tickets", "Arts & Entertainment > Event Tickets", 0.90, "exact")],
    "52": [],  # TV – service

    # ── Automotive Ownership (53–99) ──────────────────────────────────────
    "53": [t("vehicles-parts__vehicles__motor-vehicles",
            "Vehicles & Parts > Vehicles > Motor Vehicles", 0.85, "semantic")],
    "54": [t("vehicles-parts__vehicles__motor-vehicles",
            "Vehicles & Parts > Vehicles > Motor Vehicles", 0.90, "semantic", "New vehicles")],
    "77": [t("vehicles-parts__vehicles__motor-vehicles",
            "Vehicles & Parts > Vehicles > Motor Vehicles", 0.85, "semantic", "Pre-owned vehicles")],
    # Vehicle-type children (55–76, 78–99, 51_2) inherit from parent

    # ── Automotive Products (100–108) ─────────────────────────────────────
    "100": [t("vehicles-parts__vehicle-parts-accessories",
             "Vehicles & Parts > Vehicle Parts & Accessories", 0.90, "semantic")],
    # Children inherit from 100

    # ── Automotive Services (109–112) → empty ────────────────────────────
    "109": [],
    # Children inherit []

    # ── Beauty Services (113–118) → empty ────────────────────────────────
    "113": [],

    # ── Business and Industrial (119–166) ────────────────────────────────
    "119": [t("business-industrial", "Business & Industrial", 0.80, "semantic")],
    "120": [],  # Advertising and Marketing – service
    "121": [],  # Auctions – service
    "122": [],  # Conferences/Events – service
    "123": [t("business-industrial__construction", "Business & Industrial > Construction", 0.85, "semantic")],
    "124": [],  # Energy Industry – service
    "128": [],  # Forestry – B2B
    "129": [],  # Government
    "130": [],  # Human Resources – service
    "131": [t("business-industrial__material-handling",
             "Business & Industrial > Material Handling", 0.85, "semantic")],
    "132": [t("business-industrial", "Business & Industrial", 0.75, "partial")],
    "133": [],  # Aerospace and Defense
    "134": [t("business-industrial__construction", "Business & Industrial > Construction", 0.85, "semantic")],
    "135": [],  # Industrial Conglomerates
    "136": [],  # Trading Companies
    "137": [],  # Transportation – service
    "138": [],  # Laundry Services
    "139": [],  # Law Enforcement
    "140": [t("business-industrial", "Business & Industrial", 0.70, "partial")],
    "141": [t("business-industrial__material-handling",
             "Business & Industrial > Material Handling", 0.85, "semantic")],
    "142": [],  # Medical/Biotech – B2B
    "143": [],  # Mining
    "144": [],  # Photographers – service
    "145": [],  # Printing services
    "146": [],  # Public Relations – service
    "147": [],  # Retail – service sector
    "156": [],  # Science/Laboratory
    "157": [],  # Signage – B2B
    "158": [],  # Small Business
    "159": [],  # Telecom Services
    "166": [],  # Waste Disposal

    # ── Clothing and Accessories (167–182) ───────────────────────────────
    "167": [t("apparel-accessories", "Apparel & Accessories", 0.90, "semantic")],
    "168": [t("apparel-accessories__clothing", "Apparel & Accessories > Clothing", 0.95, "exact")],
    "172": [t("apparel-accessories__clothing__wedding-bridal-party-dresses",
             "Apparel & Accessories > Clothing > Wedding & Bridal Party Dresses", 0.85, "semantic")],
    "174": [t("apparel-accessories__clothing__underwear-socks",
             "Apparel & Accessories > Clothing > Underwear & Socks", 0.90, "semantic")],
    "175": [t("apparel-accessories__clothing__activewear",
             "Apparel & Accessories > Clothing > Activewear", 0.90, "semantic", "Sportswear")],
    "176": [t("apparel-accessories__clothing-accessories",
             "Apparel & Accessories > Clothing Accessories", 0.90, "semantic")],
    "177": [t("apparel-accessories__costumes-accessories",
             "Apparel & Accessories > Costumes & Accessories", 0.90, "exact")],
    "178": [t("apparel-accessories__shoes", "Apparel & Accessories > Shoes", 0.95, "exact")],
    "179": [t("apparel-accessories__shoes", "Apparel & Accessories > Shoes", 0.80, "partial", "Footwear accessories")],
    "180": [t("apparel-accessories__handbags-wallets-cases",
             "Apparel & Accessories > Handbags, Wallets & Cases", 0.90, "semantic")],
    "181": [t("apparel-accessories__jewelry", "Apparel & Accessories > Jewelry", 0.90, "semantic")],
    "182": [t("apparel-accessories__clothing-accessories__sunglasses",
             "Apparel & Accessories > Clothing Accessories > Sunglasses", 0.95, "exact")],

    # ── Collectables and Antiques (183–189) ──────────────────────────────
    "183": [t("arts-entertainment__hobbies-creative-arts__collectibles",
             "Arts & Entertainment > Hobbies & Creative Arts > Collectibles", 0.90, "semantic")],
    "189": [t("arts-entertainment__hobbies-creative-arts__collectibles__postage-stamps",
             "Arts & Entertainment > Hobbies & Creative Arts > Collectibles > Postage Stamps", 0.95, "exact")],

    # ── Consumer Electronics (190–219) ───────────────────────────────────
    "190": [t("electronics", "Electronics", 0.90, "semantic")],
    "191": [t("electronics__arcade-equipment", "Electronics > Arcade Equipment", 0.90, "exact")],
    "192": [t("electronics__audio", "Electronics > Audio", 0.90, "exact")],
    "194": [t("electronics__audio__audio-components__headphones-headsets",
             "Electronics > Audio > Audio Components > Headphones & Headsets", 0.90, "semantic")],
    "195": [t("cameras-optics", "Cameras & Optics", 0.90, "semantic")],
    "196": [t("cameras-optics__camera-photo-accessories",
             "Cameras & Optics > Camera & Photo Accessories", 0.90, "exact")],
    "197": [t("cameras-optics__cameras", "Cameras & Optics > Cameras", 0.95, "exact")],
    "198": [t("electronics__components", "Electronics > Components", 0.85, "semantic")],
    "199": [t("electronics__communications", "Electronics > Communications", 0.85, "semantic")],
    "200": [t("electronics__components", "Electronics > Components", 0.90, "exact")],
    "201": [t("electronics__computers", "Electronics > Computers", 0.95, "exact")],
    "202": [t("electronics__computers__laptops", "Electronics > Computers > Laptops", 0.95, "exact")],
    "203": [t("electronics__computers__desktop-computers",
             "Electronics > Computers > Desktop Computers", 0.95, "exact")],
    "204": [t("media__e-books-readers", "Media > E-Books > Readers", 0.85, "semantic", "E-Readers")],
    "205": [t("electronics__electronics-accessories",
             "Electronics > Electronics Accessories", 0.90, "exact")],
    "206": [t("electronics__audio", "Electronics > Audio", 0.80, "partial", "Home theater systems")],
    "207": [t("electronics", "Electronics", 0.70, "partial", "Marine electronics")],
    "208": [t("electronics__communications__telephony__mobile-phone-accessories",
             "Electronics > Communications > Telephony > Mobile Phone Accessories",
             0.70, "partial", "Mobile phone plans → accessories")],
    "209": [t("electronics__communications__telephony__mobile-phones",
             "Electronics > Communications > Telephony > Mobile Phones", 0.90, "semantic")],
    "210": [t("electronics__networking", "Electronics > Networking", 0.95, "exact")],
    "211": [t("electronics__print-copy-scan-fax",
             "Electronics > Print, Copy, Scan & Fax", 0.85, "semantic")],
    "212": [t("home-garden__business-home-security",
             "Home & Garden > Business & Home Security", 0.80, "partial", "Security devices")],
    "213": [t("electronics__computers__tablet-computers",
             "Electronics > Computers > Tablet Computers", 0.95, "exact")],
    "214": [t("electronics__video__televisions", "Electronics > Video > Televisions", 0.95, "exact")],
    "215": [t("electronics__video", "Electronics > Video", 0.85, "semantic")],
    "217": [t("cameras-optics__cameras__video-cameras",
             "Cameras & Optics > Cameras > Video Cameras", 0.90, "semantic")],
    "218": [t("electronics__video-game-console-accessories",
             "Electronics > Video Game Console Accessories", 0.90, "exact")],
    "219": [t("electronics__video-game-consoles",
             "Electronics > Video Game Consoles", 0.90, "exact")],

    # ── Consumer Packaged Goods (220–615) ────────────────────────────────
    "220": [],  # meta-category; children carry the actual mappings
    "221": [t("food-beverages-tobacco__food-items",
             "Food, Beverages & Tobacco > Food Items", 0.80, "partial", "Edible CPG")],

    # Beverages (222–248)
    "222": [t("food-beverages-tobacco__beverages",
             "Food, Beverages & Tobacco > Beverages", 0.95, "exact")],
    "223": [t("food-beverages-tobacco__beverages__soda",
             "Food, Beverages & Tobacco > Beverages > Soda", 0.90, "semantic", "Carbonated soft drinks")],
    "224": [t("food-beverages-tobacco__beverages__coffee",
             "Food, Beverages & Tobacco > Beverages > Coffee", 0.80, "partial", "Coffee & tea category")],
    "225": [t("food-beverages-tobacco__beverages__coffee",
             "Food, Beverages & Tobacco > Beverages > Coffee", 0.95, "exact")],
    "228": [t("food-beverages-tobacco__beverages__tea-infusions",
             "Food, Beverages & Tobacco > Beverages > Tea & Infusions", 0.95, "exact")],
    "229": [t("food-beverages-tobacco__beverages__tea-infusions",
             "Food, Beverages & Tobacco > Beverages > Tea & Infusions", 0.85, "semantic")],
    "236": [t("food-beverages-tobacco__beverages__juice",
             "Food, Beverages & Tobacco > Beverages > Juice", 0.95, "exact")],
    "244": [t("food-beverages-tobacco__beverages",
             "Food, Beverages & Tobacco > Beverages", 0.85, "semantic", "Sports/energy drinks")],
    "247": [t("food-beverages-tobacco__beverages__water",
             "Food, Beverages & Tobacco > Beverages > Water", 0.95, "exact")],

    # Frozen (249–283)
    "249": [t("food-beverages-tobacco__food-items",
             "Food, Beverages & Tobacco > Food Items", 0.80, "partial", "Frozen food")],
    "250": [t("food-beverages-tobacco__food-items__bakery",
             "Food, Beverages & Tobacco > Food Items > Bakery", 0.75, "partial", "Frozen baked goods")],
    "254": [t("food-beverages-tobacco__beverages",
             "Food, Beverages & Tobacco > Beverages", 0.75, "partial", "Frozen beverages")],
    "257": [t("food-beverages-tobacco__food-items",
             "Food, Beverages & Tobacco > Food Items", 0.75, "partial", "Frozen desserts")],
    "261": [t("food-beverages-tobacco__food-items__fruits-vegetables",
             "Food, Beverages & Tobacco > Food Items > Fruits & Vegetables",
             0.80, "partial", "Frozen fruits & vegetables")],
    "267": [t("food-beverages-tobacco__food-items__prepared-foods",
             "Food, Beverages & Tobacco > Food Items > Prepared Foods", 0.85, "semantic", "Frozen meals")],
    "270": [t("food-beverages-tobacco__food-items__pasta-noodles",
             "Food, Beverages & Tobacco > Food Items > Pasta & Noodles",
             0.80, "partial", "Frozen pasta")],
    "273": [t("food-beverages-tobacco__food-items__meat-seafood-eggs",
             "Food, Beverages & Tobacco > Food Items > Meat, Seafood & Eggs",
             0.85, "semantic", "Frozen meat/poultry/seafood")],
    "278": [t("food-beverages-tobacco__food-items__snack-foods",
             "Food, Beverages & Tobacco > Food Items > Snack Foods",
             0.80, "partial", "Frozen snacks")],
    "281": [t("food-beverages-tobacco__food-items",
             "Food, Beverages & Tobacco > Food Items", 0.75, "partial", "Other frozen food")],
    "282": [t("baby-toddler__nursing-feeding__baby-toddler-food__baby-food",
             "Baby & Toddler > Nursing & Feeding > Baby & Toddler Food > Baby Food",
             0.85, "semantic", "Frozen baby food")],

    # General Food (284–379)
    "284": [t("food-beverages-tobacco__food-items",
             "Food, Beverages & Tobacco > Food Items", 0.90, "semantic")],
    "285": [t("baby-toddler__nursing-feeding__baby-toddler-food",
             "Baby & Toddler > Nursing & Feeding > Baby & Toddler Food", 0.90, "semantic")],
    "286": [t("baby-toddler__nursing-feeding__baby-toddler-food__baby-food",
             "Baby & Toddler > Nursing & Feeding > Baby & Toddler Food > Baby Food", 0.95, "exact")],
    "287": [t("baby-toddler__nursing-feeding__baby-toddler-food",
             "Baby & Toddler > Nursing & Feeding > Baby & Toddler Food",
             0.90, "semantic", "Baby formula")],
    "288": [t("food-beverages-tobacco__food-items__bakery",
             "Food, Beverages & Tobacco > Food Items > Bakery", 0.95, "exact")],
    "295": [t("food-beverages-tobacco__food-items__cooking-baking-ingredients",
             "Food, Beverages & Tobacco > Food Items > Cooking & Baking Ingredients", 0.90, "semantic")],
    "312": [t("food-beverages-tobacco__food-items__seasonings-spices",
             "Food, Beverages & Tobacco > Food Items > Seasonings & Spices", 0.90, "semantic")],
    "315": [t("food-beverages-tobacco__food-items__grains-rice-cereal",
             "Food, Beverages & Tobacco > Food Items > Grains, Rice & Cereal",
             0.80, "partial", "Breakfast foods")],
    "316": [t("food-beverages-tobacco__food-items__grains-rice-cereal",
             "Food, Beverages & Tobacco > Food Items > Grains, Rice & Cereal",
             0.85, "semantic", "Cold cereal")],
    "317": [t("food-beverages-tobacco__food-items__grains-rice-cereal",
             "Food, Beverages & Tobacco > Food Items > Grains, Rice & Cereal",
             0.85, "semantic", "Hot cereal")],
    "318": [t("food-beverages-tobacco__food-items",
             "Food, Beverages & Tobacco > Food Items", 0.75, "partial", "Other breakfast foods")],
    "320": [t("food-beverages-tobacco__food-items__condiments-sauces",
             "Food, Beverages & Tobacco > Food Items > Condiments & Sauces",
             0.80, "partial", "Syrup")],
    "321": [t("food-beverages-tobacco__food-items__bakery",
             "Food, Beverages & Tobacco > Food Items > Bakery",
             0.80, "partial", "Toaster pastries/tarts")],
    "322": [t("food-beverages-tobacco__food-items__candy-chocolate",
             "Food, Beverages & Tobacco > Food Items > Candy & Chocolate", 0.95, "exact")],
    "327": [t("food-beverages-tobacco__food-items__condiments-sauces",
             "Food, Beverages & Tobacco > Food Items > Condiments & Sauces", 0.95, "exact")],
    "343": [t("food-beverages-tobacco__food-items",
             "Food, Beverages & Tobacco > Food Items", 0.80, "partial", "Ethnic foods")],
    "348": [t("food-beverages-tobacco__food-items__prepared-foods",
             "Food, Beverages & Tobacco > Food Items > Prepared Foods", 0.90, "semantic")],
    "350": [t("food-beverages-tobacco__food-items__cooking-baking-ingredients",
             "Food, Beverages & Tobacco > Food Items > Cooking & Baking Ingredients",
             0.75, "partial", "Breadcrumbs/batters")],
    "355": [t("food-beverages-tobacco__food-items__meat-seafood-eggs",
             "Food, Beverages & Tobacco > Food Items > Meat, Seafood & Eggs", 0.90, "semantic")],
    "356": [t("food-beverages-tobacco__food-items__pasta-noodles",
             "Food, Beverages & Tobacco > Food Items > Pasta & Noodles", 0.95, "exact")],
    "357": [t("food-beverages-tobacco__food-items__prepared-foods",
             "Food, Beverages & Tobacco > Food Items > Prepared Foods",
             0.80, "semantic", "Pizza products")],
    "358": [t("food-beverages-tobacco__food-items__grains-rice-cereal",
             "Food, Beverages & Tobacco > Food Items > Grains, Rice & Cereal", 0.90, "semantic")],
    "359": [t("food-beverages-tobacco__food-items__meat-seafood-eggs",
             "Food, Beverages & Tobacco > Food Items > Meat, Seafood & Eggs", 0.90, "semantic")],
    "360": [t("food-beverages-tobacco__food-items__prepared-foods",
             "Food, Beverages & Tobacco > Food Items > Prepared Foods", 0.85, "semantic", "Soup")],
    "361": [t("food-beverages-tobacco__food-items__condiments-sauces__pasta-sauce",
             "Food, Beverages & Tobacco > Food Items > Condiments & Sauces > Pasta Sauce",
             0.90, "semantic", "Spaghetti/Italian sauce")],
    "362": [t("food-beverages-tobacco__food-items__prepared-foods",
             "Food, Beverages & Tobacco > Food Items > Prepared Foods",
             0.80, "partial", "Stuffing mixes")],
    "363": [t("food-beverages-tobacco__food-items__snack-foods",
             "Food, Beverages & Tobacco > Food Items > Snack Foods", 0.90, "semantic")],
    "373": [t("food-beverages-tobacco__food-items__fruits-vegetables",
             "Food, Beverages & Tobacco > Food Items > Fruits & Vegetables", 0.90, "semantic")],
    "376": [t("food-beverages-tobacco__food-items__fruits-vegetables",
             "Food, Beverages & Tobacco > Food Items > Fruits & Vegetables", 0.90, "semantic")],
    "378": [t("food-beverages-tobacco__food-items__condiments-sauces__pasta-sauce",
             "Food, Beverages & Tobacco > Food Items > Condiments & Sauces > Pasta Sauce",
             0.80, "partial", "Tomato products")],

    # Refrigerated (380–426)
    "380": [t("food-beverages-tobacco__food-items",
             "Food, Beverages & Tobacco > Food Items", 0.80, "partial", "Refrigerated foods")],
    "381": [t("food-beverages-tobacco__food-items__dairy-products",
             "Food, Beverages & Tobacco > Food Items > Dairy Products", 0.90, "semantic")],
    "386": [t("food-beverages-tobacco__food-items__meat-seafood-eggs",
             "Food, Beverages & Tobacco > Food Items > Meat, Seafood & Eggs",
             0.90, "semantic", "Fresh eggs")],
    "388": [t("food-beverages-tobacco__beverages__milk",
             "Food, Beverages & Tobacco > Beverages > Milk", 0.90, "semantic")],
    "393": [t("food-beverages-tobacco__food-items__dairy-products",
             "Food, Beverages & Tobacco > Food Items > Dairy Products",
             0.90, "semantic", "Yogurt")],
    "394": [t("food-beverages-tobacco__food-items",
             "Food, Beverages & Tobacco > Food Items", 0.75, "partial", "Other refrigerated")],
    "397": [t("food-beverages-tobacco__food-items__bakery",
             "Food, Beverages & Tobacco > Food Items > Bakery",
             0.85, "partial", "Refrigerated baked goods")],
    "399": [t("food-beverages-tobacco__beverages",
             "Food, Beverages & Tobacco > Beverages", 0.80, "partial", "Refrigerated beverages")],
    "400": [t("food-beverages-tobacco__beverages__juice",
             "Food, Beverages & Tobacco > Beverages > Juice", 0.85, "semantic")],
    "402": [t("food-beverages-tobacco__food-items__condiments-sauces",
             "Food, Beverages & Tobacco > Food Items > Condiments & Sauces",
             0.85, "semantic", "Refrigerated condiments")],
    "408": [t("food-beverages-tobacco__food-items",
             "Food, Beverages & Tobacco > Food Items", 0.75, "partial", "Refrigerated desserts")],
    "411": [t("food-beverages-tobacco__food-items__bakery",
             "Food, Beverages & Tobacco > Food Items > Bakery",
             0.80, "partial", "Refrigerated dough")],
    "413": [t("food-beverages-tobacco__food-items__prepared-foods",
             "Food, Beverages & Tobacco > Food Items > Prepared Foods",
             0.80, "partial", "Refrigerated pizza")],
    "414": [t("food-beverages-tobacco__food-items__prepared-foods",
             "Food, Beverages & Tobacco > Food Items > Prepared Foods",
             0.85, "semantic", "Refrigerated meals")],
    "418": [t("food-beverages-tobacco__food-items__pasta-noodles",
             "Food, Beverages & Tobacco > Food Items > Pasta & Noodles",
             0.80, "partial", "Refrigerated pasta")],
    "420": [t("food-beverages-tobacco__food-items__meat-seafood-eggs",
             "Food, Beverages & Tobacco > Food Items > Meat, Seafood & Eggs",
             0.85, "semantic", "Breakfast meats")],
    "425": [t("food-beverages-tobacco__food-items__meat-seafood-eggs",
             "Food, Beverages & Tobacco > Food Items > Meat, Seafood & Eggs", 0.90, "semantic")],

    # Non-edible CPG (427–615)
    "427": [t("health-beauty__personal-care",
             "Health & Beauty > Personal Care", 0.65, "partial", "Non-edible CPG – diverse")],

    # Beauty (428–466)
    "428": [t("health-beauty__personal-care__cosmetics",
             "Health & Beauty > Personal Care > Cosmetics", 0.90, "semantic")],
    "429": [t("health-beauty__personal-care__cosmetics",
             "Health & Beauty > Personal Care > Cosmetics", 0.95, "exact")],
    "431": [t("health-beauty__personal-care__cosmetics__makeup__eye-makeup",
             "Health & Beauty > Personal Care > Cosmetics > Makeup > Eye Makeup", 0.90, "semantic")],
    "432": [t("health-beauty__personal-care__cosmetics__makeup__face-makeup",
             "Health & Beauty > Personal Care > Cosmetics > Makeup > Face Makeup", 0.90, "semantic")],
    "433": [t("health-beauty__personal-care__cosmetics__makeup__lip-makeup",
             "Health & Beauty > Personal Care > Cosmetics > Makeup > Lip Makeup", 0.90, "semantic")],
    "434": [t("health-beauty__personal-care__cosmetics__nail-care",
             "Health & Beauty > Personal Care > Cosmetics > Nail Care", 0.90, "semantic")],
    "436": [t("health-beauty__personal-care__cosmetics__perfume-cologne",
             "Health & Beauty > Personal Care > Cosmetics > Perfume & Cologne", 0.90, "semantic")],
    "439": [t("health-beauty__personal-care__shaving-grooming",
             "Health & Beauty > Personal Care > Shaving & Grooming", 0.85, "semantic")],
    "442": [t("health-beauty__personal-care__hair-care",
             "Health & Beauty > Personal Care > Hair Care", 0.85, "semantic", "Hair appliances")],
    "444": [t("health-beauty__personal-care__hair-care",
             "Health & Beauty > Personal Care > Hair Care", 0.95, "exact")],
    "446": [t("health-beauty__personal-care__hair-care__hair-color",
             "Health & Beauty > Personal Care > Hair Care > Hair Color", 0.95, "exact")],
    "452": [t("health-beauty__personal-care__hair-care__shampoo-conditioner",
             "Health & Beauty > Personal Care > Hair Care > Shampoo & Conditioner", 0.95, "exact")],
    "453": [t("health-beauty__personal-care__cosmetics__bath-body",
             "Health & Beauty > Personal Care > Cosmetics > Bath & Body", 0.90, "semantic")],
    "456": [t("health-beauty__personal-care__deodorant-anti-perspirant",
             "Health & Beauty > Personal Care > Deodorant & Anti-Perspirant", 0.95, "exact")],
    "458": [t("health-beauty__personal-care__cosmetics__bath-body__bar-soap",
             "Health & Beauty > Personal Care > Cosmetics > Bath & Body > Bar Soap", 0.90, "semantic")],
    "459": [t("health-beauty__personal-care__shaving-grooming",
             "Health & Beauty > Personal Care > Shaving & Grooming", 0.95, "exact")],
    "460": [t("health-beauty__personal-care__shaving-grooming__razors-razor-blades",
             "Health & Beauty > Personal Care > Shaving & Grooming > Razors & Razor Blades",
             0.90, "semantic", "Blades")],
    "461": [t("health-beauty__personal-care__shaving-grooming__razors-razor-blades",
             "Health & Beauty > Personal Care > Shaving & Grooming > Razors & Razor Blades",
             0.90, "semantic", "Razors")],
    "463": [t("health-beauty__personal-care__cosmetics__skin-care",
             "Health & Beauty > Personal Care > Cosmetics > Skin Care", 0.95, "exact")],
    "466": [t("health-beauty__personal-care__cosmetics__skin-care__tanning-products",
             "Health & Beauty > Personal Care > Cosmetics > Skin Care > Tanning Products",
             0.90, "semantic")],

    # General Merchandise (467–534)
    "467": [t("home-garden", "Home & Garden", 0.60, "partial", "General merchandise – diverse")],
    "468": [t("vehicles-parts__vehicle-parts-accessories",
             "Vehicles & Parts > Vehicle Parts & Accessories",
             0.80, "semantic", "Automotive CPG products")],
    "472": [t("home-garden__kitchen-dining__kitchen-appliances__outdoor-grills",
             "Home & Garden > Kitchen & Dining > Kitchen Appliances > Outdoor Grills",
             0.80, "partial", "BBQ/barbeque")],
    "473": [t("home-garden__kitchen-dining__kitchen-appliance-accessories__outdoor-grill-accessories",
             "Home & Garden > Kitchen & Dining > Kitchen Appliance Accessories > Outdoor Grill Accessories",
             0.85, "semantic", "Charcoal")],
    "475": [t("home-garden__kitchen-dining__table-serveware",
             "Home & Garden > Kitchen & Dining > Table & Serveware",
             0.80, "partial", "Disposable tableware")],
    "478": [t("electronics", "Electronics", 0.70, "partial", "Electronics/photography CPG")],
    "479": [t("electronics__electronics-accessories__power__batteries",
             "Electronics > Electronics Accessories > Power > Batteries", 0.95, "exact")],
    "480": [t("media", "Media", 0.65, "partial", "Blank audio/video media")],
    "481": [t("cameras-optics__camera-photo-accessories",
             "Cameras & Optics > Camera & Photo Accessories", 0.85, "semantic")],
    "482": [t("home-garden__kitchen-dining__food-storage",
             "Home & Garden > Kitchen & Dining > Food Storage",
             0.80, "partial", "Foils, wraps & bags")],
    "486": [t("apparel-accessories__clothing__underwear-socks__hosiery",
             "Apparel & Accessories > Clothing > Underwear & Socks > Hosiery", 0.90, "semantic")],
    "488": [t("apparel-accessories__clothing__underwear-socks__socks",
             "Apparel & Accessories > Clothing > Underwear & Socks > Socks", 0.95, "exact")],
    "489": [t("apparel-accessories__clothing__underwear-socks__hosiery",
             "Apparel & Accessories > Clothing > Underwear & Socks > Hosiery",
             0.85, "semantic", "Tights")],
    "490": [t("home-garden__kitchen-dining",
             "Home & Garden > Kitchen & Dining", 0.65, "partial", "Household plastics/storage")],
    "494": [t("home-garden__kitchen-dining__food-storage",
             "Home & Garden > Kitchen & Dining > Food Storage",
             0.85, "semantic", "Kitchen storage")],
    "496": [t("home-garden", "Home & Garden", 0.55, "partial", "Miscellaneous general merchandise")],
    "497": [t("home-garden__decor__home-fragrances__candles",
             "Home & Garden > Decor > Home Fragrances > Candles", 0.95, "exact")],
    "498": [],  # Cloth dye – no reasonable match
    "500": [],  # Firelog/firestarter – not in Google taxonomy
    "502": [],  # Frozen & dry ice – industrial product
    "505": [],  # Ice substitute – industrial
    "507": [],  # Lighters
    "508": [],  # Matches
    "509": [t("home-garden__lawn-garden",
             "Home & Garden > Lawn & Garden", 0.75, "partial", "Lawn fertilizer")],
    "510": [t("toys-games__games", "Toys & Games > Games", 0.80, "partial", "Playing cards")],
    "511": [],  # Pool/spa chemicals
    "512": [t("apparel-accessories__clothing-accessories",
             "Apparel & Accessories > Clothing Accessories",
             0.65, "partial", "Shoe polish & accessories")],
    "513": [t("home-garden__household-appliance-accessories__vacuum-accessories",
             "Home & Garden > Household Appliance Accessories > Vacuum Accessories",
             0.80, "semantic", "Vacuum bags/belts")],
    "514": [t("office-supplies", "Office Supplies", 0.85, "semantic")],
    "515": [t("arts-entertainment__hobbies-creative-arts__arts-crafts",
             "Arts & Entertainment > Hobbies & Creative Arts > Arts & Crafts",
             0.80, "partial", "Children's art supplies")],
    "516": [],  # Computer disks – obsolete
    "519": [t("home-garden__household-supplies",
             "Home & Garden > Household Supplies", 0.75, "partial", "Paper products")],
    "524": [t("home-garden__household-supplies__pest-control",
             "Home & Garden > Household Supplies > Pest Control", 0.90, "semantic")],
    "527": [t("animals-pet-supplies__pet-supplies",
             "Animals & Pet Supplies > Pet Supplies", 0.85, "semantic")],
    "532": [t("home-garden__household-supplies",
             "Home & Garden > Household Supplies", 0.65, "partial", "Water treatment")],

    # Household Appliances (535–562)
    "535": [t("home-garden__household-appliances",
             "Home & Garden > Household Appliances", 0.90, "semantic")],
    "536": [t("home-garden__household-appliances__climate-control-appliances__air-conditioners",
             "Home & Garden > Household Appliances > Climate Control Appliances > Air Conditioners",
             0.95, "exact")],
    "537": [t("home-garden__household-appliances__climate-control-appliances",
             "Home & Garden > Household Appliances > Climate Control Appliances",
             0.80, "partial", "Air purifiers")],
    "538": [t("home-garden__kitchen-dining__kitchen-appliances",
             "Home & Garden > Kitchen & Dining > Kitchen Appliances",
             0.85, "semantic", "Blenders")],
    "539": [t("home-garden__kitchen-dining__kitchen-appliances__breadmakers",
             "Home & Garden > Kitchen & Dining > Kitchen Appliances > Breadmakers", 0.95, "exact")],
    "543": [t("home-garden__household-appliances__climate-control-appliances__dehumidifiers",
             "Home & Garden > Household Appliances > Climate Control Appliances > Dehumidifiers",
             0.95, "exact")],
    "544": [t("home-garden__kitchen-dining__kitchen-appliances__dishwashers",
             "Home & Garden > Kitchen & Dining > Kitchen Appliances > Dishwashers", 0.95, "exact")],
    "546": [t("home-garden__household-appliances__climate-control-appliances__fans",
             "Home & Garden > Household Appliances > Climate Control Appliances > Fans", 0.90, "semantic")],
    "547": [t("home-garden__kitchen-dining__kitchen-appliances",
             "Home & Garden > Kitchen & Dining > Kitchen Appliances",
             0.85, "semantic", "Food processors")],
    "548": [t("home-garden__kitchen-dining__kitchen-appliances__freezers",
             "Home & Garden > Kitchen & Dining > Kitchen Appliances > Freezers", 0.95, "exact")],
    "549": [t("home-garden__household-appliances__climate-control-appliances__space-heaters",
             "Home & Garden > Household Appliances > Climate Control Appliances > Space Heaters",
             0.90, "semantic")],
    "550": [t("home-garden__household-appliances__climate-control-appliances__humidifiers",
             "Home & Garden > Household Appliances > Climate Control Appliances > Humidifiers",
             0.95, "exact")],
    "553": [t("home-garden__kitchen-dining__kitchen-appliances__microwave-ovens",
             "Home & Garden > Kitchen & Dining > Kitchen Appliances > Microwave Ovens", 0.95, "exact")],
    "555": [t("home-garden__kitchen-dining__kitchen-appliances__ovens",
             "Home & Garden > Kitchen & Dining > Kitchen Appliances > Ovens", 0.95, "exact")],
    "556": [t("home-garden__kitchen-dining__kitchen-appliances__ranges",
             "Home & Garden > Kitchen & Dining > Kitchen Appliances > Ranges", 0.95, "exact")],
    "557": [t("home-garden__kitchen-dining__kitchen-appliances__refrigerators",
             "Home & Garden > Kitchen & Dining > Kitchen Appliances > Refrigerators", 0.95, "exact")],
    "560": [t("home-garden__kitchen-dining__kitchen-appliances__toasters",
             "Home & Garden > Kitchen & Dining > Kitchen Appliances > Toasters", 0.95, "exact")],
    "561": [t("home-garden__household-appliances__vacuums",
             "Home & Garden > Household Appliances > Vacuums", 0.95, "exact")],
    "562": [t("home-garden__household-appliances__laundry-appliances",
             "Home & Garden > Household Appliances > Laundry Appliances",
             0.90, "semantic", "Washers and dryers")],

    # Home Care (563–579)
    "563": [t("home-garden__household-supplies",
             "Home & Garden > Household Supplies", 0.90, "semantic")],
    "564": [t("home-garden__decor__home-fragrances__air-fresheners",
             "Home & Garden > Decor > Home Fragrances > Air Fresheners", 0.90, "semantic")],
    "565": [t("home-garden__household-supplies__household-cleaning-supplies__household-cleaning-products",
             "Home & Garden > Household Supplies > Household Cleaning Supplies > Household Cleaning Products",
             0.90, "semantic")],
    "575": [t("home-garden__household-supplies__laundry-supplies",
             "Home & Garden > Household Supplies > Laundry Supplies", 0.95, "exact")],

    # Home and Garden Products (580–615)
    "580": [t("home-garden", "Home & Garden", 0.85, "semantic")],
    "581": [t("home-garden__bathroom-accessories",
             "Home & Garden > Bathroom Accessories", 0.90, "semantic")],
    "582": [t("home-garden__decor", "Home & Garden > Decor", 0.90, "semantic")],
    "583": [t("home-garden__linens-bedding__bedding",
             "Home & Garden > Linens & Bedding > Bedding", 0.90, "semantic")],
    "584": [t("home-garden__decor", "Home & Garden > Decor", 0.70, "partial", "Fireplaces")],
    "585": [t("home-garden__kitchen-dining", "Home & Garden > Kitchen & Dining", 0.85, "semantic")],
    "586": [t("home-garden__lawn-garden", "Home & Garden > Lawn & Garden", 0.90, "semantic")],
    "587": [t("home-garden__lighting", "Home & Garden > Lighting", 0.95, "exact")],
    "588": [t("home-garden__linens-bedding", "Home & Garden > Linens & Bedding", 0.90, "semantic")],
    "589": [t("home-garden__plants", "Home & Garden > Plants", 0.90, "semantic")],
    "590": [t("home-garden__kitchen-dining",
             "Home & Garden > Kitchen & Dining", 0.75, "partial", "Housewares")],
    "591": [t("home-garden__decor__rugs", "Home & Garden > Decor > Rugs", 0.90, "semantic")],
    "592": [t("religious-ceremonial", "Religious & Ceremonial", 0.85, "semantic")],
    "593": [t("office-supplies", "Office Supplies", 0.65, "partial", "Back to school supplies")],
    "594": [t("baby-toddler", "Baby & Toddler", 0.90, "semantic")],
    "595": [t("baby-toddler__baby-bathing", "Baby & Toddler > Baby Bathing", 0.90, "semantic")],
    "597": [t("baby-toddler__baby-toys-activity-equipment",
             "Baby & Toddler > Baby Toys & Activity Equipment", 0.90, "semantic")],
    "598": [t("baby-toddler__diapering", "Baby & Toddler > Diapering", 0.90, "semantic")],
    "599": [t("baby-toddler__baby-safety", "Baby & Toddler > Baby Safety", 0.90, "semantic")],
    "600": [t("baby-toddler__nursing-feeding", "Baby & Toddler > Nursing & Feeding", 0.90, "semantic")],
    "602": [t("baby-toddler__baby-transport__baby-carriers",
             "Baby & Toddler > Baby Transport > Baby Carriers", 0.95, "exact")],
    "604": [t("baby-toddler__baby-transport__baby-strollers",
             "Baby & Toddler > Baby Transport > Baby Strollers", 0.90, "semantic")],
    "605": [t("media", "Media", 0.90, "semantic")],
    "606": [t("media__magazines-newspapers", "Media > Magazines & Newspapers", 0.95, "exact")],
    "607": [t("media__dvds-videos", "Media > DVDs & Videos", 0.95, "exact")],
    "608": [t("media__books", "Media > Books", 0.85, "semantic")],
    "609": [t("media__music-sound-recordings", "Media > Music & Sound Recordings", 0.90, "semantic")],
    "610": [t("toys-games", "Toys & Games", 0.90, "semantic")],
    "611": [t("toys-games__games", "Toys & Games > Games", 0.90, "semantic")],
    "612": [t("toys-games__toys__outdoor-play-equipment",
             "Toys & Games > Toys > Outdoor Play Equipment", 0.90, "semantic")],
    "613": [t("toys-games__puzzles", "Toys & Games > Puzzles", 0.95, "exact")],
    "614": [t("toys-games__toys", "Toys & Games > Toys", 0.90, "semantic")],
    "615": [t("luggage-bags", "Luggage & Bags", 0.90, "semantic")],

    # ── Education and Careers (616–624) → empty ───────────────────────────
    "616": [],

    # ── Family and Parenting (625–630) → empty ────────────────────────────
    "625": [],

    # ── Finance and Insurance (631–647) → empty ───────────────────────────
    "631": [],

    # ── Food and Beverage Services (648–654) → empty ──────────────────────
    "648": [],

    # ── Furniture (655–667) ───────────────────────────────────────────────
    "655": [t("furniture", "Furniture", 0.90, "semantic")],
    "656": [t("furniture__baby-toddler-furniture",
             "Furniture > Baby & Toddler Furniture", 0.90, "semantic")],
    "657": [t("home-garden__kitchen-dining__kitchen-appliances__outdoor-grills",
             "Home & Garden > Kitchen & Dining > Kitchen Appliances > Outdoor Grills",
             0.70, "partial", "BBQ/Grills/Outdoor Dining")],
    "658": [t("furniture__beds-accessories", "Furniture > Beds & Accessories", 0.90, "semantic")],
    "660": [t("furniture__cabinets-storage", "Furniture > Cabinets & Storage", 0.90, "semantic")],
    "661": [t("furniture__chairs", "Furniture > Chairs", 0.90, "semantic")],
    "662": [t("furniture__entertainment-centers-tv-stands",
             "Furniture > Entertainment Centers & TV Stands", 0.90, "semantic")],
    "664": [t("furniture__outdoor-furniture", "Furniture > Outdoor Furniture", 0.90, "semantic")],
    "665": [t("furniture__shelving", "Furniture > Shelving", 0.95, "exact")],
    "666": [t("furniture__sofas", "Furniture > Sofas", 0.90, "semantic")],
    "667": [t("furniture__tables", "Furniture > Tables", 0.95, "exact")],

    # ── Gifts and Holiday Items (668–675) ────────────────────────────────
    "668": [t("arts-entertainment__party-celebration",
             "Arts & Entertainment > Party & Celebration",
             0.55, "approximate", "Gift and holiday items – partial coverage")],
    "669": [t("home-garden__plants__flowers", "Home & Garden > Plants > Flowers", 0.90, "semantic")],
    "670": [],  # Gift baskets – no single product match
    "671": [],  # Gift cards/coupons – financial
    "672": [],  # Gift certificates – financial
    "673": [],  # Greeting cards – no match (card organizers ≠ cards)
    "674": [t("religious-ceremonial", "Religious & Ceremonial",
             0.70, "partial", "Holiday and ethnic items")],
    "675": [t("arts-entertainment__party-celebration__party-supplies",
             "Arts & Entertainment > Party & Celebration > Party Supplies", 0.90, "semantic")],

    # ── Hardware Supplies (676–695) ──────────────────────────────────────
    "676": [t("hardware", "Hardware", 0.85, "semantic")],
    "677": [t("business-industrial__agriculture",
             "Business & Industrial > Agriculture", 0.85, "semantic")],
    "678": [t("hardware__building-materials", "Hardware > Building Materials", 0.90, "semantic")],
    "681": [t("hardware", "Hardware", 0.75, "partial", "Carpentry supplies")],
    "682": [t("hardware__power-electrical-supplies",
             "Hardware > Power & Electrical Supplies", 0.85, "semantic", "Electrical equipment")],
    "683": [t("hardware__fencing-barriers", "Hardware > Fencing & Barriers", 0.90, "semantic")],
    "684": [t("hardware", "Hardware", 0.65, "partial", "Fuel containers and tanks")],
    "685": [t("hardware", "Hardware", 0.75, "partial", "Hardware accessories")],
    "686": [t("hardware__plumbing", "Hardware > Plumbing", 0.70, "partial", "Hardware pumps")],
    "687": [t("hardware__heating-ventilation-air-conditioning",
             "Hardware > Heating, Ventilation & Air Conditioning", 0.90, "semantic")],
    "688": [t("hardware__locks-keys", "Hardware > Locks & Keys", 0.95, "exact")],
    "689": [t("business-industrial__heavy-machinery",
             "Business & Industrial > Heavy Machinery", 0.80, "semantic", "Industrial machinery")],
    "690": [t("hardware__plumbing", "Hardware > Plumbing", 0.90, "semantic")],
    "691": [t("hardware__power-electrical-supplies",
             "Hardware > Power & Electrical Supplies", 0.85, "semantic")],
    "692": [t("hardware__small-engines", "Hardware > Small Engines", 0.95, "exact")],
    "693": [t("business-industrial__material-handling",
             "Business & Industrial > Material Handling", 0.75, "partial", "Storage tanks")],
    "694": [t("hardware__tools", "Hardware > Tools", 0.95, "exact")],
    "695": [t("business-industrial__work-safety-protective-gear",
             "Business & Industrial > Work Safety Protective Gear", 0.90, "semantic")],

    # ── Health and Medical Services (696–713) → empty ────────────────────
    "696": [],

    # ── Hobbies and Interests (714–718) ──────────────────────────────────
    "714": [t("arts-entertainment__hobbies-creative-arts",
             "Arts & Entertainment > Hobbies & Creative Arts", 0.85, "semantic")],
    "715": [t("arts-entertainment__hobbies-creative-arts__arts-crafts",
             "Arts & Entertainment > Hobbies & Creative Arts > Arts & Crafts", 0.90, "semantic")],
    "716": [t("arts-entertainment__hobbies-creative-arts__musical-instruments",
             "Arts & Entertainment > Hobbies & Creative Arts > Musical Instruments", 0.90, "semantic")],
    "717": [],  # Psychics and Astrology – service
    "718": [],  # Workshops and Classes – service

    # ── Home and Garden Services (719–735) → empty ───────────────────────
    "719": [],

    # ── Legal Services (736–738) → empty ─────────────────────────────────
    "736": [],

    # ── Life Events (739–748) ────────────────────────────────────────────
    "739": [],  # life events category – primarily services
    "745": [],  # Funeral Supplies and Services – no Google match for funeral supplies
    "748": [t("religious-ceremonial__wedding-ceremony-supplies",
             "Religious & Ceremonial > Wedding Ceremony Supplies", 0.85, "semantic")],

    # ── Logistics and Delivery (749–751) → empty ─────────────────────────
    "749": [],

    # ── Non-Profits (752–758) → empty ────────────────────────────────────
    "752": [],

    # ── Office Equipment and Supplies (759–761) ──────────────────────────
    "759": [t("office-supplies", "Office Supplies", 0.85, "semantic")],
    "760": [t("furniture__office-furniture", "Furniture > Office Furniture", 0.90, "semantic")],
    "761": [t("office-supplies", "Office Supplies", 0.80, "partial", "Stationery")],

    # ── Pet Services (762–767) ────────────────────────────────────────────
    "762": [],  # Services
    "763": [],  # Pet Breeders – service
    "764": [],  # Pet Grooming – service
    "765": [],  # Pet Sitting – service
    "766": [t("animals-pet-supplies__pet-supplies",
             "Animals & Pet Supplies > Pet Supplies",
             0.70, "partial", "Pet stores sell pet supplies")],
    "767": [],  # Veterinary Services

    # ── Pharmaceuticals (768) ────────────────────────────────────────────
    "768": [t("health-beauty__health-care__medicine-drugs",
             "Health & Beauty > Health Care > Medicine & Drugs",
             0.80, "partial", "Pharmaceuticals, conditions and symptoms")],

    # ── Real Estate (769–774) → empty ────────────────────────────────────
    "769": [],

    # ── Recreation and Fitness Activities (775–782) → empty ──────────────
    "775": [],

    # ── Software (783–801) ───────────────────────────────────────────────
    "783": [t("software", "Software", 0.90, "semantic")],
    "784": [t("software__computer-software", "Software > Computer Software", 0.95, "exact")],
    "790": [t("software__computer-software__antivirus-security-software",
             "Software > Computer Software > Antivirus & Security Software", 0.95, "exact")],
    "797": [t("software__computer-software__operating-systems",
             "Software > Computer Software > Operating Systems", 0.95, "exact")],
    "798": [t("software__computer-software__business-productivity-software",
             "Software > Computer Software > Business & Productivity Software", 0.90, "semantic")],
    "800": [t("software__video-game-software",
             "Software > Video Game Software", 0.90, "semantic", "Gaming software")],
    "801": [t("software__digital-goods-currency",
             "Software > Digital Goods & Currency", 0.90, "semantic")],

    # ── Sporting Goods (802–832) ─────────────────────────────────────────
    "802": [t("sporting-goods", "Sporting Goods", 0.90, "semantic")],
    "803": [t("sporting-goods__athletics", "Sporting Goods > Athletics", 0.90, "semantic")],
    "804": [t("sporting-goods__athletics__baseball-softball",
             "Sporting Goods > Athletics > Baseball & Softball", 0.90, "semantic")],
    "805": [t("sporting-goods__athletics__basketball",
             "Sporting Goods > Athletics > Basketball", 0.90, "semantic")],
    "806": [t("sporting-goods__athletics__boxing-martial-arts",
             "Sporting Goods > Athletics > Boxing & Martial Arts", 0.90, "semantic")],
    "807": [t("sporting-goods__athletics__hockey",
             "Sporting Goods > Athletics > Hockey",
             0.80, "partial", "Figure skating and hockey")],
    "808": [t("sporting-goods__athletics__american-football",
             "Sporting Goods > Athletics > American Football", 0.85, "semantic")],
    "810": [t("sporting-goods__athletics__gymnastics",
             "Sporting Goods > Athletics > Gymnastics", 0.95, "exact")],
    "811": [t("sporting-goods__athletics__soccer",
             "Sporting Goods > Athletics > Soccer", 0.90, "semantic")],
    "812": [t("sporting-goods__athletics__tennis",
             "Sporting Goods > Athletics > Tennis", 0.90, "semantic")],
    "813": [t("sporting-goods__athletics__track-field",
             "Sporting Goods > Athletics > Track & Field", 0.90, "semantic")],
    "814": [t("sporting-goods__athletics__volleyball",
             "Sporting Goods > Athletics > Volleyball", 0.90, "semantic")],
    "815": [t("sporting-goods__athletics__water-polo",
             "Sporting Goods > Athletics > Water Polo", 0.95, "exact")],
    "816": [t("sporting-goods__athletics__wrestling",
             "Sporting Goods > Athletics > Wrestling", 0.90, "semantic")],
    "817": [t("sporting-goods__exercise-fitness",
             "Sporting Goods > Exercise & Fitness", 0.90, "semantic")],
    "818": [t("sporting-goods__indoor-games", "Sporting Goods > Indoor Games", 0.90, "semantic")],
    "819": [t("sporting-goods__outdoor-recreation",
             "Sporting Goods > Outdoor Recreation", 0.90, "semantic")],
    "820": [t("sporting-goods__outdoor-recreation__boating-water-sports",
             "Sporting Goods > Outdoor Recreation > Boating & Water Sports",
             0.85, "semantic", "Boating and water sports")],
    "821": [t("sporting-goods__outdoor-recreation__camping-hiking",
             "Sporting Goods > Outdoor Recreation > Camping & Hiking", 0.90, "semantic")],
    "822": [t("sporting-goods__outdoor-recreation__climbing",
             "Sporting Goods > Outdoor Recreation > Climbing", 0.90, "semantic")],
    "823": [t("sporting-goods__outdoor-recreation__cycling",
             "Sporting Goods > Outdoor Recreation > Cycling", 0.90, "semantic")],
    "824": [t("sporting-goods__outdoor-recreation__equestrian",
             "Sporting Goods > Outdoor Recreation > Equestrian", 0.90, "semantic")],
    "825": [t("sporting-goods__outdoor-recreation__fishing",
             "Sporting Goods > Outdoor Recreation > Fishing", 0.95, "exact")],
    "826": [t("sporting-goods__outdoor-recreation__golf",
             "Sporting Goods > Outdoor Recreation > Golf", 0.95, "exact")],
    "827": [t("sporting-goods__outdoor-recreation__hang-gliding-skydiving",
             "Sporting Goods > Outdoor Recreation > Hang Gliding & Skydiving",
             0.85, "semantic", "Hang gliding and skydiving")],
    "828": [t("sporting-goods__outdoor-recreation__hunting-shooting",
             "Sporting Goods > Outdoor Recreation > Hunting & Shooting", 0.90, "semantic")],
    "829": [t("sporting-goods__outdoor-recreation__inline-roller-skating",
             "Sporting Goods > Outdoor Recreation > Inline & Roller Skating", 0.90, "semantic")],
    "830": [t("sporting-goods__outdoor-recreation",
             "Sporting Goods > Outdoor Recreation", 0.70, "partial", "Outdoor games equipment")],
    "831": [t("sporting-goods__outdoor-recreation__skateboarding",
             "Sporting Goods > Outdoor Recreation > Skateboarding", 0.90, "semantic")],
    "832": [t("sporting-goods__outdoor-recreation__winter-sports",
             "Sporting Goods > Outdoor Recreation > Winter Sports", 0.90, "semantic")],

    # ── Travel and Tourism (833–859) → empty ─────────────────────────────
    "833": [],

    # ── Web Services (860–863) → empty ───────────────────────────────────
    "860": [],
}


def build_mapping() -> dict:
    with open("taxonomies/ad_product/iab/v1.0/taxonomy.json") as f:
        iab = json.load(f)

    entries = iab["entries"]
    entry_map = {e["id"]: e for e in entries}

    # Build parent → children lookup
    children: dict[str, list[str]] = {}
    for e in entries:
        pid = e["parent_id"]
        children.setdefault(pid, [])
        children.setdefault(e["id"], [])
        if pid is not None:
            children[pid].append(e["id"])

    # Resolve targets with parent inheritance (BFS order, parents first)
    resolved: dict[str, list] = {}
    queue = [e["id"] for e in entries if e["parent_id"] is None]
    visited = set()
    ordered_ids = []
    while queue:
        eid = queue.pop(0)
        if eid in visited:
            continue
        visited.add(eid)
        ordered_ids.append(eid)
        queue.extend(children.get(eid, []))

    for eid in ordered_ids:
        entry = entry_map[eid]
        if eid in TARGETS:
            resolved[eid] = TARGETS[eid]
        elif entry["parent_id"] and entry["parent_id"] in resolved:
            resolved[eid] = resolved[entry["parent_id"]]
        else:
            resolved[eid] = []

    # Build mapping entries preserving source order
    mapping_entries = []
    for e in entries:
        mapping_entries.append({
            "source_id": e["id"],
            "source_name": e["name"],
            "source_path": e["full_path"],
            "targets": resolved[e["id"]],
        })

    mapped = sum(1 for m in mapping_entries if m["targets"])
    now = datetime.now(timezone.utc)
    return {
        "metadata": {
            "source_provider": "iab",
            "source_version": "v1.0",
            "target_provider": "google",
            "target_version": "latest",
            "taxonomy_type": "ad_product",
            "canonical": True,
            "derived_from": None,
            "mapping_version": "1.0.0",
            "generated_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "generated_by": "llm-assisted",
            "total_source_entries": len(mapping_entries),
            "mapped_entries": mapped,
            "unmapped_entries": len(mapping_entries) - mapped,
        },
        "entries": mapping_entries,
    }


if __name__ == "__main__":
    mapping = build_mapping()
    out_dir = "mappings/ad_product/iab_v1.0__google_latest"
    os.makedirs(out_dir, exist_ok=True)
    out_path = f"{out_dir}/mapping.json"
    with open(out_path, "w") as f:
        json.dump(mapping, f, indent=2)
    meta = mapping["metadata"]
    print(f"Written {meta['total_source_entries']} entries to {out_path}")
    print(f"  Mapped: {meta['mapped_entries']}  Unmapped: {meta['unmapped_entries']}")
