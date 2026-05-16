"""
LLM-assisted canonical mapping: IAB Ad Product v2.0 → Google Product Type (latest).
Generated once; kept as a script for auditability and regeneration.
"""
import json
import os
from datetime import datetime, timezone

# fmt: off
# target(id, path, confidence, match_type, notes="")
def t(tid, tpath, conf, mtype, notes=""):
    return {"target_id": tid, "target_path": tpath, "confidence": conf, "match_type": mtype, "notes": notes}

# IAB v2.0 source_id → list of Google targets
TARGETS = {
    # ── Ad Safety Risk ──────────────────────────────────────────────────────
    "1000": [],  # meta-category, not a product

    # ── Adult Products and Services ─────────────────────────────────────────
    "1001": [t("mature", "Mature", 0.55, "approximate", "No specific Google adult product category; Mature is the closest umbrella")],

    # ── Alcohol ─────────────────────────────────────────────────────────────
    "1002": [t("food-beverages-tobacco__beverages__alcoholic-beverages", "Food, Beverages & Tobacco > Beverages > Alcoholic Beverages", 0.90, "semantic")],
    "1003": [],  # Bars — service
    "1004": [t("food-beverages-tobacco__beverages__alcoholic-beverages__beer", "Food, Beverages & Tobacco > Beverages > Alcoholic Beverages > Beer", 0.95, "exact")],
    "1005": [t("food-beverages-tobacco__beverages__alcoholic-beverages", "Food, Beverages & Tobacco > Beverages > Alcoholic Beverages", 0.70, "partial", "Hard sodas/seltzers not separately categorized in Google")],
    "1006": [t("food-beverages-tobacco__beverages__alcoholic-beverages__liquor-spirits", "Food, Beverages & Tobacco > Beverages > Alcoholic Beverages > Liquor & Spirits", 0.95, "exact")],
    "1007": [t("food-beverages-tobacco__beverages__alcoholic-beverages__wine", "Food, Beverages & Tobacco > Beverages > Alcoholic Beverages > Wine", 0.95, "exact")],

    # ── Culture and Fine Arts ───────────────────────────────────────────────
    "1008": [t("arts-entertainment", "Arts & Entertainment", 0.75, "semantic")],
    "1009": [],  # Museums and Galleries — service

    # ── Business and Industrial ─────────────────────────────────────────────
    "1010": [t("business-industrial", "Business & Industrial", 0.80, "semantic")],
    "1011": [t("business-industrial__advertising-marketing", "Business & Industrial > Advertising & Marketing", 0.90, "exact")],
    "1012": [],  # Business Services — intangible services
    "1013": [],  # Consulting
    "1014": [],  # Employee Expense and Time Tracking
    "1015": [],  # Event Planning
    "1016": [],  # Human Resources and Recruiting
    "1017": [],  # IT Services
    "1018": [],  # Laundry and Dry Cleaning
    "1019": [],  # Logistics and Delivery
    "1020": [t("office-supplies", "Office Supplies", 0.70, "partial", "Office Equipment and Supplies — Google covers products, not services")],
    "1021": [],  # Photographers — service
    "1022": [],  # Printing/Fax/WiFi Services
    "1023": [],  # PR and Strategic Communication
    "1024": [t("business-industrial__work-safety-protective-gear", "Business & Industrial > Work Safety Protective Gear", 0.55, "approximate", "Security and Protection partially overlaps with safety gear")],
    "1025": [t("business-industrial__industrial-storage", "Business & Industrial > Industrial Storage", 0.60, "approximate", "Storage Facilities (service) vs. Industrial Storage (products)")],
    "1026": [],  # Telecom Services
    "1027": [],  # Web Hosting and Cloud Computing
    "1028": [t("business-industrial__construction", "Business & Industrial > Construction", 0.85, "semantic")],
    "1029": [],  # Energy Industry — B2B/industrial, no Google product type
    "1030": [],  # Electric Power Industry
    "1031": [],  # Energy Services
    "1032": [],  # Green Energy
    "1033": [],  # Oil, Gas and Consumable Fuels
    "1034": [t("business-industrial__forestry-logging", "Business & Industrial > Forestry & Logging", 0.90, "exact")],
    "1035": [t("business-industrial__industrial-storage", "Business & Industrial > Industrial Storage", 0.90, "exact")],
    "1036": [t("business-industrial", "Business & Industrial", 0.55, "approximate", "Industrials (financial conglomerates) broadly maps to B2B")],
    "1037": [],  # Aerospace and Defense
    "1038": [t("business-industrial__construction", "Business & Industrial > Construction", 0.70, "partial")],
    "1039": [],  # Industrial Conglomerates
    "1040": [],  # Trading Companies and Distributors
    "1041": [],  # Transportation — service
    "1042": [t("business-industrial__manufacturing", "Business & Industrial > Manufacturing", 0.90, "exact")],
    "1043": [t("business-industrial__medical", "Business & Industrial > Medical", 0.80, "semantic")],
    "1044": [t("business-industrial__mining-quarrying", "Business & Industrial > Mining & Quarrying", 0.90, "exact")],
    "1045": [t("business-industrial__science-laboratory", "Business & Industrial > Science & Laboratory", 0.90, "exact")],
    "1046": [t("business-industrial__signage", "Business & Industrial > Signage", 0.95, "exact")],
    "1047": [],  # Small Business — meta-category
    "1048": [],  # Waste Disposal and Recycling

    # ── Cannabis ────────────────────────────────────────────────────────────
    "1049": [],  # Cannabis — not in Google taxonomy
    "1050": [],  # Cannabis Consumables
    "1051": [],  # Cannabis Drinks
    "1052": [],  # Cannabis Edibles
    "1053": [],  # Cannabis Equipment
    "1054": [],  # Cannabis Stores
    "1055": [],  # Cannabis Stocks
    "1056": [],  # CBD Consumables
    "1057": [],  # CBD Topicals

    # ── Clothing and Accessories ────────────────────────────────────────────
    "1058": [t("apparel-accessories", "Apparel & Accessories", 0.90, "semantic")],
    "1059": [t("apparel-accessories__clothing", "Apparel & Accessories > Clothing", 0.90, "semantic")],
    "1060": [t("apparel-accessories__clothing__baby-toddler-clothing", "Apparel & Accessories > Clothing > Baby & Toddler Clothing", 0.80, "partial", "Children's Clothing maps best to Baby & Toddler Clothing")],
    "1061": [t("apparel-accessories__clothing", "Apparel & Accessories > Clothing", 0.70, "partial", "Maternity Clothing has no dedicated Google category")],
    "1062": [t("apparel-accessories__clothing", "Apparel & Accessories > Clothing", 0.70, "partial", "Men's Clothing — Google doesn't gender-segment clothing")],
    "1063": [t("apparel-accessories__clothing__activewear", "Apparel & Accessories > Clothing > Activewear", 0.85, "semantic", "Sportswear ≈ Activewear")],
    "1064": [t("apparel-accessories__clothing__swimwear", "Apparel & Accessories > Clothing > Swimwear", 0.95, "exact")],
    "1065": [t("apparel-accessories__clothing__underwear-socks", "Apparel & Accessories > Clothing > Underwear & Socks", 0.85, "semantic"),
             t("apparel-accessories__clothing__underwear-socks__lingerie", "Apparel & Accessories > Clothing > Underwear & Socks > Lingerie", 0.90, "semantic")],
    "1066": [t("apparel-accessories__clothing__dresses", "Apparel & Accessories > Clothing > Dresses", 0.75, "partial", "Wedding dresses included in Dresses; tuxedos in Suits"),
             t("apparel-accessories__clothing__suits", "Apparel & Accessories > Clothing > Suits", 0.70, "partial")],
    "1067": [t("apparel-accessories__clothing", "Apparel & Accessories > Clothing", 0.70, "partial", "Women's Clothing — Google doesn't gender-segment clothing")],
    "1068": [t("apparel-accessories__clothing-accessories", "Apparel & Accessories > Clothing Accessories", 0.90, "exact")],
    "1069": [t("apparel-accessories__costumes-accessories", "Apparel & Accessories > Costumes & Accessories", 0.90, "exact")],
    "1070": [t("apparel-accessories__shoes", "Apparel & Accessories > Shoes", 0.90, "semantic", "Footwear ≈ Shoes")],
    "1071": [t("apparel-accessories__shoes", "Apparel & Accessories > Shoes", 0.70, "partial", "Footwear Accessories — closest is Shoe Accessories under Shoes")],
    "1072": [t("apparel-accessories__handbags-wallets-cases", "Apparel & Accessories > Handbags, Wallets & Cases", 0.90, "exact", "Handbags and Wallets = Handbags, Wallets & Cases")],
    "1073": [t("apparel-accessories__jewelry", "Apparel & Accessories > Jewelry", 0.85, "semantic"),
             t("apparel-accessories__jewelry__watches", "Apparel & Accessories > Jewelry > Watches", 0.90, "semantic", "Jewelry and Watches maps to both Jewelry and Watches")],
    "1074": [t("apparel-accessories__clothing-accessories__sunglasses", "Apparel & Accessories > Clothing Accessories > Sunglasses", 0.95, "exact")],

    # ── Collectables and Antiques ───────────────────────────────────────────
    "1075": [t("arts-entertainment__hobbies-creative-arts__collectibles", "Arts & Entertainment > Hobbies & Creative Arts > Collectibles", 0.80, "semantic")],
    "1076": [t("arts-entertainment__hobbies-creative-arts__collectibles", "Arts & Entertainment > Hobbies & Creative Arts > Collectibles", 0.75, "partial", "Antiques not separately categorized in Google collectibles")],
    "1077": [t("arts-entertainment__hobbies-creative-arts__collectibles__collectible-coins-currency", "Arts & Entertainment > Hobbies & Creative Arts > Collectibles > Collectible Coins & Currency", 0.95, "exact")],
    "1078": [t("arts-entertainment__hobbies-creative-arts__collectibles", "Arts & Entertainment > Hobbies & Creative Arts > Collectibles", 0.90, "semantic")],
    "1079": [t("arts-entertainment__hobbies-creative-arts__collectibles", "Arts & Entertainment > Hobbies & Creative Arts > Collectibles", 0.80, "partial", "Entertainment Memorabilia")],
    "1080": [t("arts-entertainment__hobbies-creative-arts__collectibles", "Arts & Entertainment > Hobbies & Creative Arts > Collectibles", 0.80, "partial", "Sports Memorabilia and Trading Cards")],
    "1081": [t("arts-entertainment__hobbies-creative-arts__collectibles", "Arts & Entertainment > Hobbies & Creative Arts > Collectibles", 0.70, "partial", "Stamps — no dedicated Google stamp collecting category")],

    # ── Computer Software ───────────────────────────────────────────────────
    "1082": [t("software", "Software", 0.90, "semantic")],
    "1083": [t("software", "Software", 0.70, "partial", "Browser Extensions — falls under Software broadly")],
    "1084": [t("software", "Software", 0.80, "partial", "Downloadable Utilities")],
    "1085": [t("software", "Software", 0.80, "partial", "Enterprise Computer Software")],
    "1086": [t("software", "Software", 0.85, "semantic", "Personal Computer Software")],
    "1087": [t("software", "Software", 0.65, "approximate", "Toolbars — browser extensions, under Software broadly")],

    # ── Cosmetic Services ───────────────────────────────────────────────────
    "1088": [t("health-beauty__personal-care", "Health & Beauty > Personal Care", 0.60, "approximate", "Cosmetic Services (salons) maps approximately to Personal Care products")],
    "1089": [],  # Beauty Salons — service
    "1090": [],  # Hair Salons — service
    "1091": [t("health-beauty__personal-care", "Health & Beauty > Personal Care", 0.50, "approximate", "Hair Removal — some products (creams, devices) exist")],
    "1092": [],  # Hair Restoration — service
    "1093": [],  # Nail Salons — service
    "1094": [],  # Med Spas — service
    "1095": [t("business-industrial__piercing-tattooing", "Business & Industrial > Piercing & Tattooing", 0.80, "semantic", "Piercing and Tattooing — products for the industry")],
    "1096": [],  # Tanning Salons — service

    # ── Consumer Electronics ────────────────────────────────────────────────
    "1097": [t("electronics", "Electronics", 0.90, "semantic")],
    "1098": [t("toys-games__games", "Toys & Games > Games", 0.65, "approximate", "Arcade Equipment — closest Google category is Games")],
    "1099": [t("cameras-optics", "Cameras & Optics", 0.80, "partial", "Camcorders fall under Cameras & Optics")],
    "1100": [t("cameras-optics", "Cameras & Optics", 0.95, "exact")],
    "1101": [t("cameras-optics", "Cameras & Optics", 0.80, "partial", "Camera and Photo Film — cameras & optics category")],
    "1102": [t("cameras-optics", "Cameras & Optics", 0.85, "semantic", "Camera and Photo Accessories")],
    "1103": [t("electronics__communications", "Electronics > Communications", 0.80, "partial", "CB and Ham Radios")],
    "1104": [t("electronics", "Electronics", 0.70, "partial", "Consumer Electronics — misc electronics")],
    "1105": [t("electronics__computers", "Electronics > Computers", 0.90, "semantic", "Computers and Accessories")],
    "1106": [t("electronics__computers", "Electronics > Computers", 0.85, "semantic", "Computer Components — falls under Computers")],
    "1107": [t("electronics__computers", "Electronics > Computers", 0.80, "partial", "Computer Peripherals")],
    "1108": [t("electronics", "Electronics", 0.75, "partial", "Consumer Electronics, General")],
    "1109": [t("electronics__audio", "Electronics > Audio", 0.75, "partial", "DJ Equipment")],
    "1110": [t("electronics", "Electronics", 0.75, "partial", "E-Readers")],
    "1111": [t("electronics", "Electronics", 0.70, "partial", "GPS Navigation Systems — no dedicated Google category")],
    "1112": [t("electronics", "Electronics", 0.75, "partial", "Headphones and Speakers")],
    "1113": [t("home-garden__household-appliances", "Home & Garden > Household Appliances", 0.70, "partial", "Home Automation")],
    "1114": [t("electronics", "Electronics", 0.75, "partial", "Home Theater Systems")],
    "1115": [t("electronics__audio", "Electronics > Audio", 0.85, "semantic", "Home Audio")],
    "1116": [t("electronics__video", "Electronics > Video", 0.85, "semantic", "Home Video Equipment")],
    "1117": [t("electronics__print-copy-scan-fax", "Electronics > Print, Copy, Scan & Fax", 0.90, "exact")],
    "1118": [t("electronics", "Electronics", 0.75, "partial", "MP3 and Digital Media Players")],
    "1119": [t("electronics__communications", "Electronics > Communications", 0.90, "semantic", "Mobile Phones")],
    "1120": [t("electronics__communications", "Electronics > Communications", 0.80, "partial", "Mobile Phone Accessories")],
    "1121": [t("electronics", "Electronics", 0.80, "partial", "Portable Gaming Devices")],
    "1122": [t("electronics", "Electronics", 0.80, "partial", "Smart Watches and Wearables")],

    # ── Consumer Packaged Goods ─────────────────────────────────────────────
    "1123": [t("food-beverages-tobacco", "Food, Beverages & Tobacco", 0.65, "approximate", "CPG is broad; Food/Beverage/Tobacco is primary CPG segment in Google")],
    "1124": [t("baby-toddler", "Baby & Toddler", 0.85, "semantic", "Baby and Child Care Products")],
    "1125": [t("baby-toddler__diapering", "Baby & Toddler > Diapering", 0.90, "exact")],
    "1126": [t("baby-toddler__nursing-feeding", "Baby & Toddler > Nursing & Feeding", 0.90, "exact")],
    "1127": [t("baby-toddler", "Baby & Toddler", 0.75, "partial", "Baby Nursery Supplies")],
    "1128": [t("baby-toddler", "Baby & Toddler", 0.75, "partial", "Baby Safety and Health")],
    "1129": [t("baby-toddler", "Baby & Toddler", 0.70, "partial", "Baby Toys")],
    "1130": [t("food-beverages-tobacco__food-items", "Food, Beverages & Tobacco > Food Items", 0.85, "semantic", "Baking and Cooking")],
    "1131": [t("food-beverages-tobacco__beverages", "Food, Beverages & Tobacco > Beverages", 0.85, "semantic", "Beverages")],
    "1132": [t("food-beverages-tobacco__beverages__coffee", "Food, Beverages & Tobacco > Beverages > Coffee", 0.95, "exact")],
    "1133": [t("food-beverages-tobacco__food-items", "Food, Beverages & Tobacco > Food Items", 0.75, "partial", "Condiments, Dressings, Sauces")],
    "1134": [t("food-beverages-tobacco__food-items", "Food, Beverages & Tobacco > Food Items", 0.75, "partial", "Candy and Confections")],
    "1135": [t("food-beverages-tobacco__food-items", "Food, Beverages & Tobacco > Food Items", 0.75, "partial", "Canned and Preserved Foods")],
    "1136": [t("food-beverages-tobacco__food-items", "Food, Beverages & Tobacco > Food Items", 0.75, "partial", "Dairy Products")],
    "1137": [t("food-beverages-tobacco__food-items", "Food, Beverages & Tobacco > Food Items", 0.75, "partial", "Desserts and Baked Goods")],
    "1138": [t("food-beverages-tobacco__food-items", "Food, Beverages & Tobacco > Food Items", 0.75, "partial", "Dips and Spreads")],
    "1139": [t("food-beverages-tobacco__food-items", "Food, Beverages & Tobacco > Food Items", 0.80, "partial", "Ethnic Food")],
    "1140": [t("food-beverages-tobacco__food-items", "Food, Beverages & Tobacco > Food Items", 0.75, "partial", "Frozen Foods")],
    "1141": [t("food-beverages-tobacco__food-items", "Food, Beverages & Tobacco > Food Items", 0.75, "partial", "Grains and Cereals")],
    "1142": [t("health-beauty__health-care__fitness-nutrition", "Health & Beauty > Health Care > Fitness & Nutrition", 0.80, "partial", "Health and Diet Food")],
    "1143": [t("food-beverages-tobacco__food-items", "Food, Beverages & Tobacco > Food Items", 0.75, "partial", "Fruits and Vegetables")],
    "1144": [t("food-beverages-tobacco__food-items", "Food, Beverages & Tobacco > Food Items", 0.75, "partial", "Juice and Drinks")],
    "1145": [t("food-beverages-tobacco__food-items", "Food, Beverages & Tobacco > Food Items", 0.75, "partial", "Meat and Poultry")],
    "1146": [t("food-beverages-tobacco__food-items", "Food, Beverages & Tobacco > Food Items", 0.75, "partial", "Organic Food")],
    "1147": [t("food-beverages-tobacco__food-items", "Food, Beverages & Tobacco > Food Items", 0.75, "partial", "Pasta and Rice")],
    "1148": [t("food-beverages-tobacco__food-items", "Food, Beverages & Tobacco > Food Items", 0.75, "partial", "Pet Food")],
    "1149": [t("food-beverages-tobacco__food-items", "Food, Beverages & Tobacco > Food Items", 0.75, "partial", "Salad Dressing")],
    "1150": [t("food-beverages-tobacco__food-items", "Food, Beverages & Tobacco > Food Items", 0.75, "partial", "Seafood")],
    "1151": [t("food-beverages-tobacco__food-items", "Food, Beverages & Tobacco > Food Items", 0.75, "partial", "Snacks")],
    "1152": [t("food-beverages-tobacco__beverages__soda", "Food, Beverages & Tobacco > Beverages > Soda", 0.90, "exact")],
    "1153": [t("food-beverages-tobacco__beverages__sports-energy-drinks", "Food, Beverages & Tobacco > Beverages > Sports & Energy Drinks", 0.90, "exact")],
    "1154": [t("food-beverages-tobacco__beverages__tea-infusions", "Food, Beverages & Tobacco > Beverages > Tea & Infusions", 0.90, "exact")],
    "1155": [t("food-beverages-tobacco__beverages__water", "Food, Beverages & Tobacco > Beverages > Water", 0.90, "exact")],
    "1156": [t("home-garden__household-supplies", "Home & Garden > Household Supplies", 0.80, "semantic", "Cleaning and Household Products")],
    "1157": [t("home-garden__household-supplies", "Home & Garden > Household Supplies", 0.80, "semantic", "Laundry Products")],
    "1158": [t("health-beauty__personal-care", "Health & Beauty > Personal Care", 0.85, "semantic", "Personal Care Products")],
    "1159": [t("health-beauty__personal-care__cosmetics", "Health & Beauty > Personal Care > Cosmetics", 0.90, "semantic", "Cosmetics")],
    "1160": [t("health-beauty__personal-care__cosmetics__makeup", "Health & Beauty > Personal Care > Cosmetics > Makeup", 0.90, "exact")],
    "1161": [t("health-beauty__personal-care__cosmetics__skin-care", "Health & Beauty > Personal Care > Cosmetics > Skin Care", 0.90, "exact")],
    "1162": [t("health-beauty__personal-care", "Health & Beauty > Personal Care", 0.80, "partial", "Hair Care Products")],
    "1163": [t("health-beauty__personal-care", "Health & Beauty > Personal Care", 0.80, "partial", "Deodorants and Antiperspirants")],
    "1164": [t("health-beauty__personal-care", "Health & Beauty > Personal Care", 0.80, "partial", "Feminine Care")],
    "1165": [t("health-beauty__personal-care", "Health & Beauty > Personal Care", 0.80, "partial", "Oral Care")],
    "1166": [t("health-beauty__personal-care", "Health & Beauty > Personal Care", 0.80, "partial", "Shaving Products")],
    "1167": [t("home-garden__household-supplies", "Home & Garden > Household Supplies", 0.75, "partial", "Paper Products")],
    "1168": [t("home-garden__kitchen-dining", "Home & Garden > Kitchen & Dining", 0.80, "partial", "Plastic and Storage Bags")],

    # ── Dating ──────────────────────────────────────────────────────────────
    "1259": [],  # Dating — service/subscription, no product type

    # ── Debated Sensitive Social Issue ──────────────────────────────────────
    "1262": [],  # No product mapping

    # ── Durable Goods ───────────────────────────────────────────────────────
    "1263": [t("home-garden", "Home & Garden", 0.60, "approximate", "Durable Goods — broad meta-category, home goods is primary segment")],
    "1264": [t("furniture", "Furniture", 0.90, "semantic", "Furniture and Mattresses")],
    "1265": [t("home-garden__household-appliances", "Home & Garden > Household Appliances", 0.90, "semantic", "Home Appliances")],
    "1266": [t("home-garden__household-appliances", "Home & Garden > Household Appliances", 0.80, "partial", "Small Household Appliances")],
    "1267": [t("home-garden__linens-bedding", "Home & Garden > Linens & Bedding", 0.90, "semantic", "Linens and Bedding")],
    "1268": [t("home-garden__kitchen-dining", "Home & Garden > Kitchen & Dining", 0.85, "semantic", "Kitchen and Dining")],
    "1269": [t("home-garden__bathroom-accessories", "Home & Garden > Bathroom Accessories", 0.85, "semantic", "Bathroom Products")],
    "1270": [t("home-garden__decor", "Home & Garden > Decor", 0.85, "semantic", "Home Decor")],
    "1271": [t("home-garden__lighting", "Home & Garden > Lighting", 0.90, "exact")],
    "1272": [t("home-garden__lawn-garden", "Home & Garden > Lawn & Garden", 0.85, "semantic", "Lawn and Garden")],
    "1273": [t("hardware", "Hardware", 0.75, "partial", "Tools and Hardware")],
    "1274": [t("home-garden__pool-spa", "Home & Garden > Pool & Spa", 0.90, "exact")],
    "1275": [t("home-garden", "Home & Garden", 0.70, "partial", "Window Treatments")],
    "1276": [t("furniture", "Furniture", 0.70, "partial", "Office Furniture")],
    "1277": [t("electronics", "Electronics", 0.65, "approximate", "Consumer Electronics/Audio Visual")],
    "1278": [t("home-garden__household-appliances", "Home & Garden > Household Appliances", 0.75, "partial", "HVAC and Climate Control")],
    "1279": [t("home-garden__business-home-security", "Home & Garden > Business & Home Security", 0.85, "semantic", "Home Security")],
    "1280": [t("home-garden", "Home & Garden", 0.65, "approximate", "Building Materials")],
    "1281": [t("home-garden__flood-fire-gas-safety", "Home & Garden > Flood, Fire & Gas Safety", 0.85, "semantic", "Fire Safety")],
    "1282": [t("furniture__beds-accessories__mattresses", "Furniture > Beds & Accessories > Mattresses", 0.95, "exact")],
    "1283": [t("furniture", "Furniture", 0.85, "semantic", "Bedroom Furniture")],
    "1284": [t("furniture", "Furniture", 0.85, "semantic", "Living Room Furniture")],
    "1285": [t("home-garden__plants", "Home & Garden > Plants", 0.85, "semantic", "Plants and Garden Decor")],
    "1286": [t("home-garden__household-appliances", "Home & Garden > Household Appliances", 0.85, "semantic", "Major Appliances")],
    "1287": [t("home-garden__household-appliances", "Home & Garden > Household Appliances", 0.80, "partial", "Floor Care and Cleaning")],
    "1288": [t("hardware", "Hardware", 0.70, "partial", "Power Tools")],
    "1289": [t("hardware", "Hardware", 0.70, "partial", "Hand Tools")],
    "1290": [t("home-garden__household-supplies", "Home & Garden > Household Supplies", 0.70, "partial", "Storage and Organization")],

    # ── Dieting and Weightloss ──────────────────────────────────────────────
    "1291": [t("health-beauty__health-care__fitness-nutrition", "Health & Beauty > Health Care > Fitness & Nutrition", 0.85, "semantic")],
    "1292": [t("health-beauty__health-care__fitness-nutrition__vitamins-supplements", "Health & Beauty > Health Care > Fitness & Nutrition > Vitamins & Supplements", 0.80, "partial", "Diet Supplements")],
    "1293": [t("health-beauty__health-care__fitness-nutrition", "Health & Beauty > Health Care > Fitness & Nutrition", 0.75, "partial", "Diet Programs and Services")],
    "1294": [t("health-beauty__health-care__fitness-nutrition", "Health & Beauty > Health Care > Fitness & Nutrition", 0.75, "partial", "Weight Management Products")],

    # ── Education and Careers ───────────────────────────────────────────────
    "1295": [],  # Education — service
    "1296": [],  # Online Education
    "1297": [],  # College and University
    "1298": [],  # Professional Development
    "1299": [],  # Career Resources
    "1300": [],  # Job Search
    "1301": [],  # Tutoring
    "1302": [],  # Trade and Vocational Schools
    "1303": [t("software", "Software", 0.65, "approximate", "Educational Software — maps broadly to Software")],
    "1304": [],  # Student Loans and Financial Aid
    "1305": [],  # E-Learning Platforms
    "1306": [],  # Language Learning
    "1307": [],  # Test Prep
    "1308": [],  # Children's Education
    "1309": [],  # College Prep
    "1310": [],  # Bootcamps and Coding Schools
    "1311": [],  # Certifications and Licenses
    "1312": [],  # Military Education
    "1313": [],  # Graduate Education
    "1314": [],  # Elementary and Middle School

    # ── Events and Performances ─────────────────────────────────────────────
    "1315": [],  # Events and Performances — service/ticket
    "1316": [],  # Concerts and Music Events
    "1317": [],  # Sports Events
    "1318": [],  # Comedy Shows
    "1319": [],  # Theater and Performing Arts
    "1320": [],  # Festivals and Fairs
    "1321": [],  # Family Entertainment
    "1322": [],  # Movie Tickets
    "1323": [],  # Art Exhibitions
    "1324": [],  # Dance Performances
    "1325": [],  # Cultural Events
    "1326": [],  # Club and Nightlife
    "1327": [],  # Online Streaming Events

    # ── Family and Parenting ────────────────────────────────────────────────
    "1328": [t("baby-toddler", "Baby & Toddler", 0.70, "partial", "Family and Parenting broadly maps to Baby & Toddler products")],
    "1329": [t("baby-toddler", "Baby & Toddler", 0.80, "partial", "Parenting Products")],
    "1330": [t("baby-toddler", "Baby & Toddler", 0.75, "partial", "Baby Gear and Products")],
    "1331": [t("toys-games__toys", "Toys & Games > Toys", 0.80, "partial", "Children's Toys")],
    "1332": [],  # Parenting Services
    "1333": [],  # Child Care and Daycare
    "1334": [t("baby-toddler__diapering", "Baby & Toddler > Diapering", 0.90, "semantic", "Diapers and Wipes")],

    # ── Finance and Insurance ───────────────────────────────────────────────
    "1335": [],  # Finance and Insurance — service
    "1336": [],  # Banking
    "1337": [],  # Credit Cards
    "1338": [],  # Loans
    "1339": [],  # Insurance
    "1340": [],  # Investing
    "1341": [],  # Tax Services
    "1342": [],  # Financial Planning
    "1343": [],  # Retirement Planning
    "1344": [],  # Mortgage
    "1345": [],  # Debt Management
    "1346": [],  # Accounting Services
    "1347": [],  # Cryptocurrency
    "1348": [],  # Life Insurance
    "1349": [],  # Health Insurance
    "1350": [],  # Auto Insurance
    "1351": [],  # Business Insurance
    "1352": [],  # Home Insurance
    "1353": [],  # Travel Insurance
    "1354": [],  # Pet Insurance

    # ── Food and Beverage Services ──────────────────────────────────────────
    "1355": [t("food-beverages-tobacco", "Food, Beverages & Tobacco", 0.60, "approximate", "Food and Beverage Services (restaurants) → food products")],
    "1356": [],  # Restaurants — service
    "1357": [],  # Fast Food — service
    "1358": [],  # Meal Delivery — service
    "1359": [],  # Catering — service
    "1360": [t("business-industrial__food-service", "Business & Industrial > Food Service", 0.80, "semantic", "Food Service Industry → B2B food service products")],

    # ── Gambling ────────────────────────────────────────────────────────────
    "1361": [],  # Gambling — service
    "1362": [],  # Online Casinos
    "1363": [],  # Sports Betting
    "1364": [],  # Poker
    "1365": [],  # Lottery
    "1366": [],  # Fantasy Sports
    "1367": [],  # Bingo

    # ── Green/Eco ───────────────────────────────────────────────────────────
    "1368": [t("home-garden", "Home & Garden", 0.50, "approximate", "Green/Eco — no dedicated Google category; products span many categories")],
    "1369": [],  # Renewable Energy Products — mostly services
    "1370": [t("home-garden__household-supplies", "Home & Garden > Household Supplies", 0.60, "approximate", "Eco-friendly Household Products")],

    # ── Gifts and Holiday Items ─────────────────────────────────────────────
    "1371": [t("arts-entertainment", "Arts & Entertainment", 0.60, "approximate", "Gifts and Holiday Items — no dedicated Google category")],
    "1372": [t("arts-entertainment", "Arts & Entertainment", 0.65, "approximate", "Gift Cards")],
    "1373": [t("arts-entertainment", "Arts & Entertainment", 0.65, "approximate", "Holiday Decorations — spans multiple categories")],
    "1374": [t("arts-entertainment", "Arts & Entertainment", 0.60, "approximate", "Seasonal and Holiday Items")],
    "1375": [t("arts-entertainment", "Arts & Entertainment", 0.60, "approximate", "Gift Baskets")],
    "1376": [t("arts-entertainment", "Arts & Entertainment", 0.60, "approximate", "Greeting Cards")],
    "1377": [t("arts-entertainment", "Arts & Entertainment", 0.65, "approximate", "Holiday Food and Candy")],

    # ── Health and Medical Services ─────────────────────────────────────────
    "1378": [t("health-beauty__health-care", "Health & Beauty > Health Care", 0.75, "partial", "Health and Medical Services — products vs. services distinction")],
    "1379": [],  # Hospitals and Clinics — service
    "1380": [],  # Mental Health Services — service
    "1381": [t("health-beauty__health-care__medicine-drugs", "Health & Beauty > Health Care > Medicine & Drugs", 0.80, "semantic", "Prescription Drugs")],
    "1382": [t("health-beauty__health-care", "Health & Beauty > Health Care", 0.75, "partial", "Medical Equipment and Supplies")],
    "1383": [],  # Dentistry — service
    "1384": [t("health-beauty__health-care", "Health & Beauty > Health Care", 0.70, "partial", "Vision Care")],
    "1385": [],  # Chiropractic — service
    "1386": [],  # Physical Therapy — service
    "1387": [],  # Telehealth — service
    "1388": [t("health-beauty__health-care__fitness-nutrition__vitamins-supplements", "Health & Beauty > Health Care > Fitness & Nutrition > Vitamins & Supplements", 0.85, "semantic", "Vitamins and Supplements")],
    "1389": [t("health-beauty__health-care__medicine-drugs", "Health & Beauty > Health Care > Medicine & Drugs", 0.85, "semantic", "Over-the-Counter Medicine")],
    "1390": [],  # Health Insurance — service
    "1391": [],  # Home Health Care — service
    "1392": [t("health-beauty__health-care", "Health & Beauty > Health Care", 0.75, "partial", "Hearing Aids and Devices")],
    "1393": [t("health-beauty__health-care", "Health & Beauty > Health Care", 0.75, "partial", "Mobility Aids")],
    "1394": [],  # Drug Rehabilitation — service
    "1395": [t("health-beauty__health-care", "Health & Beauty > Health Care", 0.70, "partial", "Blood Pressure and Glucose Monitoring")],

    # ── Home and Garden Services ────────────────────────────────────────────
    "1396": [t("home-garden", "Home & Garden", 0.60, "approximate", "Home and Garden Services — services vs. products")],
    "1397": [],  # Landscaping — service
    "1398": [],  # Pest Control — service
    "1399": [],  # Plumbing — service
    "1400": [],  # Electrical Services — service
    "1401": [],  # HVAC Services — service
    "1402": [],  # Home Cleaning Services — service
    "1403": [],  # Interior Design — service
    "1404": [],  # Moving Services — service
    "1405": [],  # Pool Services — service
    "1406": [],  # Roofing — service
    "1407": [],  # Home Improvement Services — service
    "1408": [],  # Painting Services — service
    "1409": [],  # Appliance Repair — service
    "1410": [],  # Window and Door Services — service
    "1411": [],  # Security Systems — service
    "1412": [],  # Locksmith — service
    "1413": [],  # Gutter Services — service
    "1414": [],  # Flooring Services — service
    "1415": [],  # Tree Services — service

    # ── Legal Services ──────────────────────────────────────────────────────
    "1416": [],  # Legal Services — service
    "1417": [],  # Personal Injury Lawyers — service
    "1418": [],  # Criminal Defense Lawyers — service

    # ── Media ───────────────────────────────────────────────────────────────
    "1419": [t("media", "Media", 0.85, "semantic")],
    "1420": [t("media__books", "Media > Books", 0.95, "exact")],
    "1421": [t("media__music-sound-recordings", "Media > Music & Sound Recordings", 0.90, "semantic", "Music and Music Apps")],
    "1422": [t("media__dvds-videos", "Media > DVDs & Videos", 0.85, "semantic", "Movies and Film")],
    "1423": [t("media", "Media", 0.75, "partial", "News and Magazines")],
    "1424": [],  # Social Media — service/app
    "1425": [],  # Streaming Services — service
    "1426": [t("media", "Media", 0.70, "partial", "Podcasts")],
    "1427": [],  # Television — service/subscription
    "1428": [],  # Radio — service
    "1429": [],  # Photography Services — service
    "1430": [t("media", "Media", 0.75, "partial", "Digital Content and Downloads")],
    "1431": [t("media", "Media", 0.80, "partial", "Video Games and Gaming")],
    "1432": [t("media", "Media", 0.75, "partial", "Newspapers")],
    "1433": [t("media", "Media", 0.70, "partial", "Maps and Atlases")],
    "1434": [],  # Online Forums and Communities
    "1435": [t("software", "Software", 0.70, "partial", "Apps and Mobile Applications")],
    "1436": [t("media", "Media", 0.75, "partial", "Cameras and Photography Content")],
    "1437": [],  # Online Dating Apps — service
    "1438": [],  # Messaging Apps — service
    "1439": [t("software", "Software", 0.70, "partial", "Productivity Apps")],
    "1440": [t("software", "Software", 0.70, "partial", "Entertainment Apps")],
    "1441": [],  # Music Streaming — service
    "1442": [],  # Video Streaming — service

    # ── Metals ──────────────────────────────────────────────────────────────
    "1443": [t("business-industrial", "Business & Industrial", 0.55, "approximate", "Precious Metals and Industrial Metals — B2B commodity")],
    "1444": [t("apparel-accessories__jewelry", "Apparel & Accessories > Jewelry", 0.75, "partial", "Gold — investment/jewelry")],
    "1445": [t("apparel-accessories__jewelry", "Apparel & Accessories > Jewelry", 0.75, "partial", "Silver — investment/jewelry")],
    "1446": [t("business-industrial", "Business & Industrial", 0.55, "approximate", "Industrial Metals")],
    "1447": [t("arts-entertainment__hobbies-creative-arts__collectibles__collectible-coins-currency", "Arts & Entertainment > Hobbies & Creative Arts > Collectibles > Collectible Coins & Currency", 0.65, "approximate", "Precious Metals as Collectibles")],

    # ── Non-Fiat Currency ───────────────────────────────────────────────────
    "1448": [],  # Cryptocurrency/NFTs — no Google product category
    "1449": [],  # Bitcoin
    "1450": [],  # NFTs
    "1451": [],  # DeFi

    # ── Non-Profits ─────────────────────────────────────────────────────────
    "1452": [],  # Non-Profits — not a product category
    "1453": [],  # Charities
    "1454": [],  # Foundations
    "1455": [],  # Advocacy Organizations
    "1456": [],  # Political Non-Profits
    "1457": [],  # Environmental Non-Profits
    "1458": [],  # Religious Non-Profits
    "1459": [],  # Health and Medical Non-Profits

    # ── Pet Ownership ───────────────────────────────────────────────────────
    "1460": [t("animals-pet-supplies", "Animals & Pet Supplies", 0.90, "semantic")],
    "1461": [t("animals-pet-supplies__pet-supplies", "Animals & Pet Supplies > Pet Supplies", 0.90, "semantic", "Pet Products")],
    "1462": [t("animals-pet-supplies__pet-supplies", "Animals & Pet Supplies > Pet Supplies", 0.75, "partial", "Pet Food")],
    "1463": [],  # Veterinary Services — service
    "1464": [t("animals-pet-supplies__pet-supplies", "Animals & Pet Supplies > Pet Supplies", 0.80, "partial", "Pet Accessories")],
    "1465": [],  # Pet Insurance — service
    "1466": [t("animals-pet-supplies__pet-supplies", "Animals & Pet Supplies > Pet Supplies", 0.75, "partial", "Pet Health and Wellness Products")],

    # ── Personal/Consumer Telecom ───────────────────────────────────────────
    "1467": [t("electronics__communications", "Electronics > Communications", 0.80, "semantic", "Personal/Consumer Telecom → Communications Electronics")],
    "1468": [t("electronics__communications", "Electronics > Communications", 0.85, "semantic", "Mobile Phones and Plans")],
    "1469": [t("electronics__communications", "Electronics > Communications", 0.80, "partial", "Internet Service Providers")],
    "1470": [t("electronics__communications", "Electronics > Communications", 0.75, "partial", "Cable and Satellite TV")],
    "1471": [t("electronics__communications", "Electronics > Communications", 0.75, "partial", "Home Phone Services")],
    "1472": [t("electronics__communications", "Electronics > Communications", 0.80, "semantic", "Wireless Devices and Accessories")],

    # ── Pharmaceuticals ─────────────────────────────────────────────────────
    "1473": [t("health-beauty__health-care__medicine-drugs", "Health & Beauty > Health Care > Medicine & Drugs", 0.90, "semantic")],

    # ── Politics ────────────────────────────────────────────────────────────
    "1474": [],  # Politics — not a product category
    "1475": [],  # Political Campaigns
    "1476": [],  # Political Parties
    "1477": [],  # Government
    "1478": [],  # Public Policy
    "1479": [],  # Election
    "1480": [],  # Political Organizations
    "1481": [],  # Voter Registration

    # ── Real Estate ─────────────────────────────────────────────────────────
    "1482": [],  # Real Estate — service
    "1483": [],  # Commercial Real Estate
    "1484": [],  # Real Estate Rentals
    "1485": [],  # Real Estate Sales
    "1486": [],  # Real Estate Services For Owners

    # ── Religion and Spirituality ───────────────────────────────────────────
    "1487": [t("religious-ceremonial", "Religious & Ceremonial", 0.80, "semantic")],
    "1488": [],  # Astrology — service
    "1489": [],  # Prayer and Mindfulness Applications — service/app
    "1490": [],  # Prayer and Worship Services — service
    "1491": [],  # Religious Causes — non-profit
    "1492": [],  # Religious Charities — non-profit
    "1493": [],  # Religious Organizations — non-profit

    # ── Retail ──────────────────────────────────────────────────────────────
    "1494": [],  # Retail — meta/service (store types)
    "1495": [t("arts-entertainment__hobbies-creative-arts__arts-crafts", "Arts & Entertainment > Hobbies & Creative Arts > Arts & Crafts", 0.80, "semantic", "Arts and Crafts Supplies")],
    "1496": [],  # Cell Phone Stores — service
    "1497": [],  # Clothing Stores — service
    "1498": [],  # Department Stores — service
    "1499": [],  # eCommerce — service
    "1500": [],  # Factory Outlet Stores — service
    "1501": [],  # Grocery Stores — service
    "1502": [],  # Hardware Stores — service
    "1503": [t("media__music-sound-recordings", "Media > Music & Sound Recordings", 0.70, "partial", "Musical Instruments and Record Stores → Music & Sound Recordings")],
    "1504": [],  # Pawn Shops — service
    "1505": [],  # Pet and Pet Supply Stores — service
    "1506": [],  # Shopping Malls — service
    "1507": [],  # Specialty Stores — service
    "1508": [],  # Sporting Goods Stores — service
    "1509": [],  # Ticket Services — service

    # ── Fitness Activities ──────────────────────────────────────────────────
    "1510": [t("sporting-goods__exercise-fitness", "Sporting Goods > Exercise & Fitness", 0.70, "partial", "Fitness Activities (services) → Exercise & Fitness products")],
    "1511": [],  # Dance Studios — service
    "1512": [],  # Gyms and Health Clubs — service
    "1513": [],  # Participant Sports Leagues — service
    "1514": [],  # Personal Trainers — service
    "1515": [],  # Self Defense and Martial Arts Classes — service
    "1516": [],  # Swimming Facilities — service
    "1517": [],  # Workout and Step Tracking Applications — app/service
    "1518": [],  # Yoga Studios — service

    # ── Sexual Health ───────────────────────────────────────────────────────
    "1519": [t("health-beauty__health-care", "Health & Beauty > Health Care", 0.65, "approximate", "Sexual Health — health care products broadly")],
    "1520": [t("health-beauty__health-care__medicine-drugs", "Health & Beauty > Health Care > Medicine & Drugs", 0.75, "partial", "Contraceptives")],
    "1521": [t("health-beauty__health-care__medicine-drugs", "Health & Beauty > Health Care > Medicine & Drugs", 0.80, "partial", "Doctor Prescribed Medicines")],
    "1522": [],  # Fertility Tracking Applications — app
    "1523": [t("health-beauty__health-care__medicine-drugs", "Health & Beauty > Health Care > Medicine & Drugs", 0.65, "approximate", "Non-Prescribed Performance Enhancers")],

    # ── Sporting Goods ──────────────────────────────────────────────────────
    "1524": [t("sporting-goods", "Sporting Goods", 0.95, "exact")],
    "1525": [t("sporting-goods", "Sporting Goods", 0.85, "semantic", "Athletics Equipment")],
    "1526": [t("sporting-goods__exercise-fitness", "Sporting Goods > Exercise & Fitness", 0.95, "exact")],
    "1527": [t("sporting-goods", "Sporting Goods", 0.80, "partial", "Indoor Games Equipment")],
    "1528": [t("sporting-goods__outdoor-recreation", "Sporting Goods > Outdoor Recreation", 0.90, "exact")],

    # ── Travel and Tourism ──────────────────────────────────────────────────
    "1529": [],  # Travel and Tourism — service
    "1530": [],  # Accommodations — service
    "1531": [],  # Bed and Breakfasts — service
    "1532": [],  # Camping and Camp Grounds — service
    "1533": [],  # Hotels and Resorts — service
    "1534": [],  # Motels — service
    "1535": [],  # Timeshares — service
    "1536": [],  # Vacation Rentals — service
    "1537": [],  # Air Travel — service
    "1538": [],  # Cruises — service
    "1539": [],  # Rail Travel — service
    "1540": [],  # Sightseeing Tours — service
    "1541": [],  # Travel Agents — service
    "1542": [],  # Travel Packages — service
    "1543": [],  # Travel Planning Apps — service/app

    # ── Tobacco ─────────────────────────────────────────────────────────────
    "1544": [t("food-beverages-tobacco__tobacco-products", "Food, Beverages & Tobacco > Tobacco Products", 0.95, "exact")],
    "1545": [t("food-beverages-tobacco__tobacco-products", "Food, Beverages & Tobacco > Tobacco Products", 0.90, "semantic", "Cigars")],
    "1546": [t("food-beverages-tobacco__tobacco-products", "Food, Beverages & Tobacco > Tobacco Products", 0.95, "exact", "Cigarettes")],
    "1547": [t("food-beverages-tobacco__tobacco-products", "Food, Beverages & Tobacco > Tobacco Products", 0.90, "semantic", "Smokeless Tobacco")],
    "1548": [t("food-beverages-tobacco__tobacco-products", "Food, Beverages & Tobacco > Tobacco Products", 0.85, "semantic", "Vaping — under Tobacco Products")],
    "1549": [t("food-beverages-tobacco__tobacco-products", "Food, Beverages & Tobacco > Tobacco Products", 0.85, "semantic", "Vaping Cartridges")],
    "1550": [t("food-beverages-tobacco__tobacco-products", "Food, Beverages & Tobacco > Tobacco Products", 0.85, "semantic", "Vaporizers")],

    # ── Vehicles ────────────────────────────────────────────────────────────
    "1551": [t("vehicles-parts", "Vehicles & Parts", 0.90, "semantic")],
    "1552": [],  # Automotive Leasing — service
    "1553": [t("vehicles-parts__vehicles__motor-vehicles", "Vehicles & Parts > Vehicles > Motor Vehicles", 0.90, "semantic", "Automotive Ownership (new/used vehicles)")],
    "1554": [t("vehicles-parts__vehicles__motor-vehicles", "Vehicles & Parts > Vehicles > Motor Vehicles", 0.90, "semantic", "New Vehicle Ownership")],
    "1555": [t("vehicles-parts__vehicles__motor-vehicles", "Vehicles & Parts > Vehicles > Motor Vehicles", 0.85, "semantic", "Pre-owned Automotive Ownership")],
    "1556": [t("vehicles-parts__vehicle-parts-accessories", "Vehicles & Parts > Vehicle Parts & Accessories", 0.90, "semantic", "Automotive Products")],
    "1557": [t("vehicles-parts__vehicle-parts-accessories__vehicle-maintenance-care-decor", "Vehicles & Parts > Vehicle Parts & Accessories > Vehicle Maintenance, Care & Decor", 0.90, "exact")],
    "1558": [t("vehicles-parts__vehicle-parts-accessories__motor-vehicle-parts", "Vehicles & Parts > Vehicle Parts & Accessories > Motor Vehicle Parts", 0.90, "exact")],
    "1559": [t("vehicles-parts__vehicle-parts-accessories__motor-vehicle-parts", "Vehicles & Parts > Vehicle Parts & Accessories > Motor Vehicle Parts", 0.85, "semantic", "Aftermarket Parts and Accessories")],
    "1560": [],  # Automotive Services — service
    "1561": [],  # Auto Towing — service
    "1562": [],  # Auto Repair — service
    "1563": [],  # Car Wash — service
    "1564": [],  # Automotive Sales Applications — app/service
    "1565": [],  # Ride-sharing Services — service
    "1566": [],  # Taxi Services — service
    "1567": [],  # Vehicle Rental — service
    "1568": [t("vehicles-parts__vehicles", "Vehicles & Parts > Vehicles", 0.80, "partial", "Vehicle Type — meta-category for vehicle types")],
    "1569": [t("vehicles-parts__vehicles__watercraft", "Vehicles & Parts > Vehicles > Watercraft", 0.90, "semantic", "Boats")],
    "1570": [t("vehicles-parts__vehicles__motor-vehicles", "Vehicles & Parts > Vehicles > Motor Vehicles", 0.80, "partial", "Diesel Vehicles")],
    "1571": [t("vehicles-parts__vehicles__motor-vehicles", "Vehicles & Parts > Vehicles > Motor Vehicles", 0.80, "partial", "Electric Vehicles")],
    "1572": [t("vehicles-parts__vehicles__motor-vehicles", "Vehicles & Parts > Vehicles > Motor Vehicles", 0.80, "partial", "Gas Vehicles")],
    "1573": [t("vehicles-parts__vehicles__motor-vehicles", "Vehicles & Parts > Vehicles > Motor Vehicles", 0.80, "partial", "Hybrid Vehicles")],
    "1574": [t("vehicles-parts__vehicles__motor-vehicles", "Vehicles & Parts > Vehicles > Motor Vehicles", 0.80, "partial", "Recreational Vehicles")],
    "1575": [t("vehicles-parts__vehicles__motor-vehicles", "Vehicles & Parts > Vehicles > Motor Vehicles", 0.80, "partial", "Scooters, Motorbikes, and E-bikes")],

    # ── Consumer Packaged Goods — General Food subcategories ────────────────
    "1169": [t("food-beverages-tobacco__food-items", "Food, Beverages & Tobacco > Food Items", 0.80, "partial", "Breakfast foods")],
    "1170": [t("food-beverages-tobacco__food-items", "Food, Beverages & Tobacco > Food Items", 0.80, "partial", "Candy")],
    "1171": [t("food-beverages-tobacco__food-items", "Food, Beverages & Tobacco > Food Items", 0.80, "partial", "Condiments and Sauces")],
    "1172": [t("food-beverages-tobacco__food-items", "Food, Beverages & Tobacco > Food Items", 0.80, "partial", "Cookies and Crackers")],
    "1173": [t("food-beverages-tobacco__food-items", "Food, Beverages & Tobacco > Food Items", 0.80, "partial", "Fruit")],
    "1174": [t("food-beverages-tobacco__food-items", "Food, Beverages & Tobacco > Food Items", 0.80, "partial", "Meals")],
    "1175": [t("food-beverages-tobacco__food-items", "Food, Beverages & Tobacco > Food Items", 0.80, "partial", "Snacks")],
    "1176": [t("food-beverages-tobacco__food-items", "Food, Beverages & Tobacco > Food Items", 0.80, "partial", "Vegetables")],
    "1177": [t("home-garden__household-supplies", "Home & Garden > Household Supplies", 0.55, "approximate", "General Merchandise — broad category")],
    "1178": [t("health-beauty__personal-care", "Health & Beauty > Personal Care", 0.85, "semantic", "Grooming Supplies")],

    # ── Consumer Packaged Goods — Hair Care subcategories ───────────────────
    "1179": [t("health-beauty__personal-care", "Health & Beauty > Personal Care", 0.85, "semantic", "Hair Care")],
    "1180": [t("apparel-accessories__clothing-accessories", "Apparel & Accessories > Clothing Accessories", 0.75, "partial", "Hair Accessories")],
    "1181": [t("health-beauty__personal-care", "Health & Beauty > Personal Care", 0.85, "semantic", "Hair Coloring")],
    "1182": [t("health-beauty__personal-care", "Health & Beauty > Personal Care", 0.85, "semantic", "Hair Conditioner")],
    "1183": [t("health-beauty__personal-care", "Health & Beauty > Personal Care", 0.85, "semantic", "Hair Growth Products")],
    "1184": [t("health-beauty__personal-care", "Health & Beauty > Personal Care", 0.85, "semantic", "Hair Spray/Spritz")],
    "1185": [t("health-beauty__personal-care", "Health & Beauty > Personal Care", 0.85, "semantic", "Hair Styling Gel/Mousse")],
    "1186": [t("health-beauty__personal-care", "Health & Beauty > Personal Care", 0.85, "semantic", "Home Permanent/Relaxer Kits")],
    "1187": [t("health-beauty__personal-care", "Health & Beauty > Personal Care", 0.85, "semantic", "Shampoo")],
    "1188": [t("food-beverages-tobacco__food-items", "Food, Beverages & Tobacco > Food Items", 0.65, "approximate", "HFSS Products — high-calorie packaged foods")],

    # ── Consumer Packaged Goods — Home Care subcategories ───────────────────
    "1189": [t("home-garden__household-supplies", "Home & Garden > Household Supplies", 0.90, "semantic", "Home Care")],
    "1190": [t("home-garden__household-supplies", "Home & Garden > Household Supplies", 0.90, "semantic", "Household Cleaning")],
    "1191": [t("home-garden__household-supplies", "Home & Garden > Household Supplies", 0.90, "semantic", "Laundry")],

    # ── Consumer Packaged Goods — Hosiery ───────────────────────────────────
    "1192": [t("apparel-accessories__clothing__underwear-socks__hosiery", "Apparel & Accessories > Clothing > Underwear & Socks > Hosiery", 0.95, "exact")],
    "1193": [t("apparel-accessories__clothing__underwear-socks__hosiery", "Apparel & Accessories > Clothing > Underwear & Socks > Hosiery", 0.90, "semantic", "Pantyhose/Nylons")],
    "1194": [t("apparel-accessories__clothing__underwear-socks__socks", "Apparel & Accessories > Clothing > Underwear & Socks > Socks", 0.95, "exact")],
    "1195": [t("apparel-accessories__clothing__underwear-socks__hosiery", "Apparel & Accessories > Clothing > Underwear & Socks > Hosiery", 0.90, "semantic", "Tights")],

    # ── Consumer Packaged Goods — Household/Plastics/Storage ────────────────
    "1196": [t("home-garden__household-supplies", "Home & Garden > Household Supplies", 0.80, "partial", "Household/Plastics/Storage")],
    "1197": [t("home-garden__kitchen-dining", "Home & Garden > Kitchen & Dining", 0.75, "partial", "Bottles — kitchen/drinkware")],
    "1198": [t("home-garden__kitchen-dining", "Home & Garden > Kitchen & Dining", 0.80, "partial", "Drinkware")],
    "1199": [t("home-garden__household-supplies", "Home & Garden > Household Supplies", 0.80, "partial", "Household Plastics")],
    "1200": [t("home-garden__kitchen-dining", "Home & Garden > Kitchen & Dining", 0.80, "partial", "Kitchen Storage")],
    "1201": [t("food-beverages-tobacco__food-items", "Food, Beverages & Tobacco > Food Items", 0.85, "semantic", "Meal Kits")],
    "1202": [t("home-garden__household-supplies", "Home & Garden > Household Supplies", 0.55, "approximate", "Miscellaneous General Merchandise")],

    # ── Consumer Packaged Goods — Office/School Supplies ────────────────────
    "1203": [t("office-supplies", "Office Supplies", 0.90, "semantic", "Office/School Supplies")],
    "1204": [t("arts-entertainment__hobbies-creative-arts__arts-crafts", "Arts & Entertainment > Hobbies & Creative Arts > Arts & Crafts", 0.85, "semantic", "Children's Art Supplies")],
    "1205": [t("electronics__computers", "Electronics > Computers", 0.70, "partial", "Computer Disks — computer media")],
    "1206": [t("office-supplies", "Office Supplies", 0.90, "semantic", "Office Products")],
    "1207": [t("office-supplies__presentation-supplies", "Office Supplies > Presentation Supplies", 0.70, "partial", "Writing Instruments")],

    # ── Consumer Packaged Goods — Over the Counter Medication ────────────────
    "1208": [t("health-beauty__health-care__medicine-drugs", "Health & Beauty > Health Care > Medicine & Drugs", 0.95, "exact")],

    # ── Consumer Packaged Goods — Paper Products ─────────────────────────────
    "1209": [t("home-garden__household-supplies", "Home & Garden > Household Supplies", 0.85, "semantic", "Paper Products")],
    "1210": [t("home-garden__household-supplies", "Home & Garden > Household Supplies", 0.85, "semantic", "Facial Tissue")],
    "1211": [t("home-garden__household-supplies", "Home & Garden > Household Supplies", 0.85, "semantic", "Paper Napkins")],
    "1212": [t("home-garden__household-supplies", "Home & Garden > Household Supplies", 0.85, "semantic", "Paper Towels")],
    "1213": [t("home-garden__household-supplies", "Home & Garden > Household Supplies", 0.85, "semantic", "Toilet Tissue")],

    # ── Consumer Packaged Goods — Personal Care subcategories ───────────────
    "1214": [t("health-beauty__personal-care", "Health & Beauty > Personal Care", 0.90, "semantic")],
    "1215": [t("health-beauty__personal-care", "Health & Beauty > Personal Care", 0.85, "semantic", "Personal Cleansing")],
    "1216": [t("health-beauty__personal-care", "Health & Beauty > Personal Care", 0.85, "semantic", "Bath Products")],
    "1217": [t("health-beauty__personal-care", "Health & Beauty > Personal Care", 0.80, "partial", "Bath/Body Scrubbers/Massagers")],
    "1218": [t("health-beauty__personal-care", "Health & Beauty > Personal Care", 0.85, "semantic", "Deodorant")],
    "1219": [t("health-beauty__personal-care", "Health & Beauty > Personal Care", 0.80, "partial", "Moist Towelettes")],
    "1220": [t("health-beauty__personal-care", "Health & Beauty > Personal Care", 0.85, "semantic", "Soap")],

    # ── Consumer Packaged Goods — Pest Control ───────────────────────────────
    "1221": [t("home-garden__household-supplies", "Home & Garden > Household Supplies", 0.75, "partial", "Pest Control products")],
    "1222": [t("home-garden__lawn-garden", "Home & Garden > Lawn & Garden", 0.75, "partial", "Outdoor Insect/Rodent Control")],
    "1223": [t("home-garden__household-supplies", "Home & Garden > Household Supplies", 0.75, "partial", "Pest Control")],

    # ── Consumer Packaged Goods — Pet Care subcategories ────────────────────
    "1224": [t("animals-pet-supplies__pet-supplies", "Animals & Pet Supplies > Pet Supplies", 0.90, "semantic")],
    "1225": [t("animals-pet-supplies__pet-supplies", "Animals & Pet Supplies > Pet Supplies", 0.85, "semantic", "Cat/Dog Litter")],
    "1226": [t("animals-pet-supplies__pet-supplies", "Animals & Pet Supplies > Pet Supplies", 0.90, "semantic", "Pet Food")],
    "1227": [t("animals-pet-supplies__pet-supplies", "Animals & Pet Supplies > Pet Supplies", 0.90, "semantic", "Pet Supplies")],
    "1228": [t("animals-pet-supplies__pet-supplies", "Animals & Pet Supplies > Pet Supplies", 0.85, "semantic", "Pet Treats")],

    # ── Consumer Packaged Goods — Refrigerated subcategories ────────────────
    "1229": [t("food-beverages-tobacco__food-items", "Food, Beverages & Tobacco > Food Items", 0.80, "partial", "Refrigerated foods")],
    "1230": [t("food-beverages-tobacco__food-items", "Food, Beverages & Tobacco > Food Items", 0.80, "partial", "Dairy")],
    "1231": [t("food-beverages-tobacco__food-items", "Food, Beverages & Tobacco > Food Items", 0.80, "partial", "Refrigerated Baked Goods")],
    "1232": [t("food-beverages-tobacco__beverages", "Food, Beverages & Tobacco > Beverages", 0.80, "partial", "Refrigerated Beverages")],
    "1233": [t("food-beverages-tobacco__food-items", "Food, Beverages & Tobacco > Food Items", 0.80, "partial", "Refrigerated Condiments")],
    "1234": [t("food-beverages-tobacco__food-items", "Food, Beverages & Tobacco > Food Items", 0.80, "partial", "Refrigerated Desserts")],
    "1235": [t("food-beverages-tobacco__food-items", "Food, Beverages & Tobacco > Food Items", 0.80, "partial", "Refrigerated Dough")],
    "1236": [t("food-beverages-tobacco__food-items", "Food, Beverages & Tobacco > Food Items", 0.80, "partial", "Refrigerated Meals")],
    "1237": [t("food-beverages-tobacco__food-items", "Food, Beverages & Tobacco > Food Items", 0.80, "partial", "Refrigerated Meats")],
    "1238": [t("food-beverages-tobacco__food-items", "Food, Beverages & Tobacco > Food Items", 0.75, "partial", "Refrigerated Miscellaneous")],
    "1239": [t("religious-ceremonial", "Religious & Ceremonial", 0.85, "semantic", "Religious Items")],

    # ── Consumer Packaged Goods — Shaving subcategories ─────────────────────
    "1240": [t("health-beauty__personal-care", "Health & Beauty > Personal Care", 0.90, "semantic", "Shaving")],
    "1241": [t("health-beauty__personal-care", "Health & Beauty > Personal Care", 0.85, "semantic", "Shaving Blades")],
    "1242": [t("health-beauty__personal-care", "Health & Beauty > Personal Care", 0.85, "semantic", "Razors")],
    "1243": [t("health-beauty__personal-care", "Health & Beauty > Personal Care", 0.85, "semantic", "Shaving Cream")],

    # ── Consumer Packaged Goods — Skin Care subcategories ───────────────────
    "1244": [t("health-beauty__personal-care__cosmetics__skin-care", "Health & Beauty > Personal Care > Cosmetics > Skin Care", 0.95, "exact")],
    "1245": [t("health-beauty__personal-care__cosmetics__skin-care", "Health & Beauty > Personal Care > Cosmetics > Skin Care", 0.90, "semantic", "Hand and Body Lotion")],
    "1246": [t("health-beauty__personal-care__cosmetics__skin-care", "Health & Beauty > Personal Care > Cosmetics > Skin Care", 0.95, "exact")],
    "1247": [t("health-beauty__personal-care__cosmetics__skin-care", "Health & Beauty > Personal Care > Cosmetics > Skin Care", 0.85, "semantic", "Suntan Products")],

    # ── Consumer Packaged Goods — Toys and Games subcategories ──────────────
    "1248": [t("toys-games", "Toys & Games", 0.90, "semantic")],
    "1249": [t("toys-games__games", "Toys & Games > Games", 0.95, "exact")],
    "1250": [t("toys-games__toys", "Toys & Games > Toys", 0.80, "partial", "Outdoor Play Equipment — falls under Toys")],
    "1251": [t("toys-games__games", "Toys & Games > Games", 0.85, "semantic", "Puzzles — typically categorized as games")],
    "1252": [t("toys-games__toys", "Toys & Games > Toys", 0.95, "exact")],

    # ── Consumer Packaged Goods — Vitamins and Supplements ──────────────────
    "1253": [t("health-beauty__health-care__fitness-nutrition__vitamins-supplements", "Health & Beauty > Health Care > Fitness & Nutrition > Vitamins & Supplements", 0.95, "exact")],
    "1254": [t("health-beauty__health-care__fitness-nutrition__vitamins-supplements", "Health & Beauty > Health Care > Fitness & Nutrition > Vitamins & Supplements", 0.85, "semantic", "Digestive Supplements")],
    "1255": [t("health-beauty__health-care__fitness-nutrition__vitamins-supplements", "Health & Beauty > Health Care > Fitness & Nutrition > Vitamins & Supplements", 0.85, "semantic", "Weightloss Supplements")],

    # ── Consumer Packaged Goods — Water Treatment ────────────────────────────
    "1256": [t("home-garden__household-appliances", "Home & Garden > Household Appliances", 0.75, "partial", "Water Treatment products")],
    "1257": [t("home-garden__household-appliances", "Home & Garden > Household Appliances", 0.75, "partial", "Water Filter/Devices")],
    "1258": [t("home-garden__household-appliances", "Home & Garden > Household Appliances", 0.75, "partial", "Water Softeners/Treatment")],

    # ── Dating subcategories ─────────────────────────────────────────────────
    "1260": [],  # Casual Relationships — service
    "1261": [],  # Serious Relationships — service

    # ── Weapons and Ammunition ──────────────────────────────────────────────
    "1576": [t("mature__weapons", "Mature > Weapons", 0.90, "semantic")],
    "1577": [t("mature__weapons__gun-care-accessories__ammunition", "Mature > Weapons > Gun Care & Accessories > Ammunition", 0.95, "exact")],
    "1578": [t("mature__weapons", "Mature > Weapons", 0.85, "semantic", "Guns — no dedicated 'Guns' in Google; Mature > Weapons is closest")],
    "1579": [t("mature__weapons__gun-care-accessories", "Mature > Weapons > Gun Care & Accessories", 0.90, "semantic", "Gun Accessories")],
    "1580": [],  # Gun Shows and Auctions — service
    "1581": [t("mature__weapons", "Mature > Weapons", 0.80, "partial", "Non-Projectile Weapons — knives, batons, etc.")],
    "1582": [t("mature__weapons", "Mature > Weapons", 0.75, "partial", "Taser and Stun Guns")],
}
# fmt: on


def build_mapping() -> dict:
    with open("taxonomies/ad_product/iab/v2.0/taxonomy.json") as f:
        iab = json.load(f)

    iab_index = {e["id"]: e for e in iab["entries"]}
    entries = []

    for source_id, targets in TARGETS.items():
        iab_entry = iab_index.get(source_id)
        if not iab_entry:
            print(f"WARNING: IAB entry {source_id} not found in taxonomy")
            continue

        entries.append({
            "source_id": source_id,
            "source_name": iab_entry["name"],
            "source_path": iab_entry["full_path"],
            "targets": targets,
        })

    total = len(entries)
    mapped = sum(1 for e in entries if e["targets"])
    unmapped = total - mapped
    now = datetime.now(timezone.utc)

    return {
        "metadata": {
            "source_provider": "iab",
            "source_version": "v2.0",
            "target_provider": "google",
            "target_version": "latest",
            "taxonomy_type": "ad_product",
            "canonical": True,
            "derived_from": None,
            "mapping_version": "1.0.0",
            "generated_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "generated_by": "llm-assisted",
            "total_source_entries": total,
            "mapped_entries": mapped,
            "unmapped_entries": unmapped,
        },
        "entries": entries,
    }


if __name__ == "__main__":
    mapping = build_mapping()
    out_path = "mappings/ad_product/iab_v2.0__google_latest/mapping.json"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(mapping, f, indent=2)

    meta = mapping["metadata"]
    print(f"Written {meta['total_source_entries']} entries to {out_path}")
    print(f"Mapped: {meta['mapped_entries']} | Unmapped: {meta['unmapped_entries']}")

    # Coverage check
    with open("taxonomies/ad_product/iab/v2.0/taxonomy.json") as f:
        iab = json.load(f)
    iab_ids = {e["id"] for e in iab["entries"]}
    covered = set(TARGETS.keys())
    missing = iab_ids - covered
    if missing:
        print(f"WARNING: {len(missing)} IAB entries not in TARGETS dict: {sorted(missing)[:10]}...")
    else:
        print("Coverage: all IAB v2.0 entries covered")
