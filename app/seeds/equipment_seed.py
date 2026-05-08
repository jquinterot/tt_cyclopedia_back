"""
Seed data for TT Cyclopedia Equipment Catalog.
Includes blades and rubbers from major brands.
Image URLs use manufacturer websites or placeholders.
"""

from typing import List, Dict, Any

# Image URLs - using manufacturer sites or placeholder pattern
# In production, host these images yourself or use a CDN
BRAND_LOGOS = {
    "Butterfly": "https://cdn11.bigcommerce.com/s-e12b1/images/stencil/1280x1280/products/1256/3843/butterfly-logo__45340.1586798957.jpg",
    "Donic": "https://www.donic.com/media/image/8f/87/5e/donic-logo.png",
    "DHS": "https://www.dhs-sports.com/images/logo.png",
    "Nittaku": "https://www.nittaku.com/img/common/logo.png",
    "Xiom": "https://www.xiom.com/images/logo.png",
    "Tibhar": "https://www.tibhar.com/images/logo.png",
    "Andro": "https://www.andro.de/media/image/1a/3e/5e/andro-logo.png",
    "Stiga": "https://www.stigasports.com/media/image/1a/3e/5e/stiga-logo.png",
}

def get_product_image(brand: str, name: str, category: str) -> str:
    """Generate a placeholder or manufacturer image URL."""
    # In production, replace with actual product images
    slug = name.lower().replace(" ", "-").replace(".", "").replace("/", "-").replace("+", "-plus")
    return f"/static/equipment/{category}s/{brand.lower()}-{slug}.jpg"

# ========== BLADES ==========
BLADES: List[Dict[str, Any]] = [
    # Butterfly
    {
        "name": "Viscaria",
        "brand": "Butterfly",
        "subcategory": "offensive_plus",
        "description": "One of the most popular ALC blades. Excellent balance of speed and control. Used by many professional players including Zhang Jike and Fan Zhendong.",
        "price_usd": 179.99,
        "release_year": 1993,
        "specs": {
            "speed": 87, "control": 72, "stiffness": 78, "hardness": 70,
            "weight_min": 85, "weight_max": 92, "plies": 5, "material": "Wood + Arylate-Carbon",
            "thickness": 5.8, "head_size": "Standard", "handle_types": "FL,ST,AN"
        }
    },
    {
        "name": "Timo Boll ALC",
        "brand": "Butterfly",
        "subcategory": "offensive",
        "description": "The blade of Timo Boll. Slightly softer than Viscaria with more control. Great for spin-oriented attackers.",
        "price_usd": 179.99,
        "release_year": 2005,
        "specs": {
            "speed": 82, "control": 78, "stiffness": 72, "hardness": 65,
            "weight_min": 85, "weight_max": 92, "plies": 7, "material": "Wood + Arylate-Carbon",
            "thickness": 5.7, "head_size": "Standard", "handle_types": "FL,ST,AN"
        }
    },
    {
        "name": "Innerforce Layer ZLC",
        "brand": "Butterfly",
        "subcategory": "offensive_plus",
        "description": "Innerfiber construction with ZLC. High speed with a large sweet spot. Great for power loops.",
        "price_usd": 199.99,
        "release_year": 2013,
        "specs": {
            "speed": 90, "control": 68, "stiffness": 82, "hardness": 75,
            "weight_min": 86, "weight_max": 93, "plies": 5, "material": "Wood + ZLC",
            "thickness": 5.7, "head_size": "Standard", "handle_types": "FL,ST,AN"
        }
    },
    {
        "name": "Primorac OFF-",
        "brand": "Butterfly",
        "subcategory": "allround",
        "description": "Classic all-wood blade with excellent control. Perfect for developing players and allround attackers.",
        "price_usd": 94.99,
        "release_year": 1985,
        "specs": {
            "speed": 65, "control": 88, "stiffness": 55, "hardness": 55,
            "weight_min": 82, "weight_max": 89, "plies": 5, "material": "All Wood",
            "thickness": 5.6, "head_size": "Standard", "handle_types": "FL,ST,AN"
        }
    },
    # Donic
    {
        "name": "Waldner Senso Carbon",
        "brand": "Donic",
        "subcategory": "offensive",
        "description": "The blade of Jan-Ove Waldner. Unique Senso handle technology for better feeling. Carbon layers provide speed while maintaining control.",
        "price_usd": 129.99,
        "release_year": 2000,
        "specs": {
            "speed": 80, "control": 80, "stiffness": 70, "hardness": 65,
            "weight_min": 82, "weight_max": 88, "plies": 5, "material": "Wood + Carbon",
            "thickness": 5.6, "head_size": "Standard", "handle_types": "FL,ST,AN"
        }
    },
    {
        "name": "Ovtcharov No. 1",
        "brand": "Donic",
        "subcategory": "offensive_plus",
        "description": "Dimitrij Ovtcharov's blade. Powerful carbon blade with excellent speed for aggressive play.",
        "price_usd": 149.99,
        "release_year": 2015,
        "specs": {
            "speed": 88, "control": 70, "stiffness": 80, "hardness": 72,
            "weight_min": 85, "weight_max": 92, "plies": 7, "material": "Wood + Carbon",
            "thickness": 5.8, "head_size": "Standard", "handle_types": "FL,ST"
        }
    },
    {
        "name": "Appelgren Allplay",
        "brand": "Donic",
        "subcategory": "allround",
        "description": "Classic all-wood blade named after Mikael Appelgren. Great control and feeling for allround players.",
        "price_usd": 74.99,
        "release_year": 1990,
        "specs": {
            "speed": 62, "control": 90, "stiffness": 50, "hardness": 50,
            "weight_min": 80, "weight_max": 86, "plies": 5, "material": "All Wood",
            "thickness": 5.5, "head_size": "Standard", "handle_types": "FL,ST,AN"
        }
    },
    # DHS
    {
        "name": "Hurricane Long 5",
        "brand": "DHS",
        "subcategory": "offensive_plus",
        "description": "Ma Long's blade. Innerfiber ALC construction with legendary power. The choice of many Chinese national team players.",
        "price_usd": 159.99,
        "release_year": 2013,
        "specs": {
            "speed": 92, "control": 68, "stiffness": 85, "hardness": 78,
            "weight_min": 88, "weight_max": 95, "plies": 7, "material": "Wood + Arylate-Carbon",
            "thickness": 6.0, "head_size": "Standard", "handle_types": "FL,ST"
        }
    },
    {
        "name": "Hurricane Long 2",
        "brand": "DHS",
        "subcategory": "offensive",
        "description": " predecessor to Long 5. Slightly softer with more control. Great for spin-oriented play.",
        "price_usd": 139.99,
        "release_year": 2005,
        "specs": {
            "speed": 85, "control": 75, "stiffness": 75, "hardness": 70,
            "weight_min": 86, "weight_max": 92, "plies": 5, "material": "Wood + Carbon",
            "thickness": 5.8, "head_size": "Standard", "handle_types": "FL,ST"
        }
    },
    {
        "name": "Power G13",
        "brand": "DHS",
        "subcategory": "offensive",
        "description": "High-performance blade with glass fiber layers. Good speed and control balance at an affordable price.",
        "price_usd": 89.99,
        "release_year": 2018,
        "specs": {
            "speed": 78, "control": 76, "stiffness": 72, "hardness": 68,
            "weight_min": 84, "weight_max": 90, "plies": 7, "material": "Wood + Glass Fiber",
            "thickness": 5.7, "head_size": "Standard", "handle_types": "FL,ST"
        }
    },
    # Nittaku
    {
        "name": "Acoustic Carbon",
        "brand": "Nittaku",
        "subcategory": "offensive",
        "description": "Known for its unique acoustic properties. Carbon blade with exceptional feeling and feedback. Popular among Japanese players.",
        "price_usd": 189.99,
        "release_year": 2008,
        "specs": {
            "speed": 83, "control": 82, "stiffness": 72, "hardness": 68,
            "weight_min": 84, "weight_max": 90, "plies": 5, "material": "Wood + Carbon",
            "thickness": 5.7, "head_size": "Standard", "handle_types": "FL,ST"
        }
    },
    {
        "name": "Barwell",
        "brand": "Nittaku",
        "subcategory": "allround",
        "description": "Classic Japanese all-wood blade. Excellent control and feeling. Great for developing players.",
        "price_usd": 99.99,
        "release_year": 1995,
        "specs": {
            "speed": 64, "control": 88, "stiffness": 55, "hardness": 52,
            "weight_min": 82, "weight_max": 88, "plies": 5, "material": "All Wood",
            "thickness": 5.6, "head_size": "Standard", "handle_types": "FL,ST"
        }
    },
    {
        "name": "Gyroblade",
        "brand": "Nittaku",
        "subcategory": "offensive_plus",
        "description": "Innovative blade with unique construction for maximum spin generation. High throw angle and dwell time.",
        "price_usd": 169.99,
        "release_year": 2019,
        "specs": {
            "speed": 86, "control": 74, "stiffness": 76, "hardness": 70,
            "weight_min": 85, "weight_max": 91, "plies": 5, "material": "Wood + Special Fiber",
            "thickness": 5.9, "head_size": "Standard", "handle_types": "FL,ST"
        }
    },
    # Xiom
    {
        "name": "Hugo Calderano HAL",
        "brand": "Xiom",
        "subcategory": "offensive_plus",
        "description": "Hugo Calderano's signature blade. Arylate-Carbon with extreme power. Designed for the modern offensive game.",
        "price_usd": 149.99,
        "release_year": 2020,
        "specs": {
            "speed": 90, "control": 70, "stiffness": 82, "hardness": 75,
            "weight_min": 85, "weight_max": 92, "plies": 5, "material": "Wood + Arylate-Carbon",
            "thickness": 5.8, "head_size": "Standard", "handle_types": "FL,ST"
        }
    },
    {
        "name": "Stradivarius",
        "brand": "Xiom",
        "subcategory": "offensive",
        "description": "All-wood blade with exceptional feeling. Named after the violin for its acoustic properties. Great for spin players.",
        "price_usd": 109.99,
        "release_year": 2010,
        "specs": {
            "speed": 76, "control": 84, "stiffness": 65, "hardness": 60,
            "weight_min": 83, "weight_max": 89, "plies": 7, "material": "All Wood",
            "thickness": 5.8, "head_size": "Standard", "handle_types": "FL,ST,AN"
        }
    },
    {
        "name": "Offensive S",
        "brand": "Xiom",
        "subcategory": "allround_offensive",
        "description": "Versatile blade suitable for a wide range of playing styles. Good balance of speed and control.",
        "price_usd": 79.99,
        "release_year": 2012,
        "specs": {
            "speed": 72, "control": 80, "stiffness": 62, "hardness": 58,
            "weight_min": 82, "weight_max": 88, "plies": 5, "material": "All Wood",
            "thickness": 5.7, "head_size": "Standard", "handle_types": "FL,ST"
        }
    },
    # Tibhar
    {
        "name": "Dynamic 7",
        "brand": "Tibhar",
        "subcategory": "offensive",
        "description": "7-ply all-wood blade with excellent speed for an all-wood construction. Great for attackers who prefer wood feeling.",
        "price_usd": 89.99,
        "release_year": 2015,
        "specs": {
            "speed": 78, "control": 78, "stiffness": 68, "hardness": 65,
            "weight_min": 84, "weight_max": 90, "plies": 7, "material": "All Wood",
            "thickness": 5.8, "head_size": "Standard", "handle_types": "FL,ST"
        }
    },
    {
        "name": "Balsa SGS",
        "brand": "Tibhar",
        "subcategory": "defensive",
        "description": "Lightweight balsa blade designed for defensive players. Excellent control for chopping and blocking.",
        "price_usd": 79.99,
        "release_year": 2010,
        "specs": {
            "speed": 55, "control": 92, "stiffness": 45, "hardness": 40,
            "weight_min": 70, "weight_max": 78, "plies": 5, "material": "Balsa + Wood",
            "thickness": 6.5, "head_size": "Standard", "handle_types": "FL,ST"
        }
    },
    {
        "name": "Samsonov Force Pro Black Edition",
        "brand": "Tibhar",
        "subcategory": "offensive_plus",
        "description": "Vladimir Samsonov's blade. Premium carbon blade with massive power and speed.",
        "price_usd": 159.99,
        "release_year": 2018,
        "specs": {
            "speed": 90, "control": 68, "stiffness": 85, "hardness": 78,
            "weight_min": 86, "weight_max": 93, "plies": 5, "material": "Wood + Carbon",
            "thickness": 5.9, "head_size": "Standard", "handle_types": "FL,ST"
        }
    },
    # Andro
    {
        "name": "Timber 7 OFF/S",
        "brand": "Andro",
        "subcategory": "offensive",
        "description": "7-ply all-wood blade with offensive speed. Great for players transitioning to faster equipment.",
        "price_usd": 84.99,
        "release_year": 2016,
        "specs": {
            "speed": 78, "control": 76, "stiffness": 68, "hardness": 62,
            "weight_min": 84, "weight_max": 90, "plies": 7, "material": "All Wood",
            "thickness": 5.8, "head_size": "Standard", "handle_types": "FL,ST"
        }
    },
    {
        "name": "Novacell OFF",
        "brand": "Andro",
        "subcategory": "offensive",
        "description": "Carbon blade with cellulose technology. Good speed with soft feeling. Great for spin-oriented attackers.",
        "price_usd": 119.99,
        "release_year": 2014,
        "specs": {
            "speed": 82, "control": 76, "stiffness": 72, "hardness": 66,
            "weight_min": 85, "weight_max": 91, "plies": 5, "material": "Wood + Cellulose-Carbon",
            "thickness": 5.7, "head_size": "Standard", "handle_types": "FL,ST"
        }
    },
    {
        "name": "Wood ALL+/OFF-",
        "brand": "Andro",
        "subcategory": "allround",
        "description": "Affordable all-wood blade perfect for beginners and developing players. Excellent control.",
        "price_usd": 49.99,
        "release_year": 2012,
        "specs": {
            "speed": 65, "control": 85, "stiffness": 55, "hardness": 52,
            "weight_min": 82, "weight_max": 88, "plies": 5, "material": "All Wood",
            "thickness": 5.6, "head_size": "Standard", "handle_types": "FL,ST"
        }
    },
    # Stiga
    {
        "name": "Clipper Wood",
        "brand": "Stiga",
        "subcategory": "offensive",
        "description": "Legendary 7-ply all-wood blade. Used by Liu Guoliang and many other champions. Classic offensive blade with great feeling.",
        "price_usd": 99.99,
        "release_year": 1980,
        "specs": {
            "speed": 78, "control": 78, "stiffness": 68, "hardness": 62,
            "weight_min": 85, "weight_max": 92, "plies": 7, "material": "All Wood",
            "thickness": 6.0, "head_size": "Standard", "handle_types": "FL,ST,AN,CS"
        }
    },
    {
        "name": "Carbonado 245",
        "brand": "Stiga",
        "subcategory": "offensive_plus",
        "description": "Carbon blade with Textreme technology. One of the fastest blades on the market. For advanced offensive players.",
        "price_usd": 199.99,
        "release_year": 2015,
        "specs": {
            "speed": 95, "control": 62, "stiffness": 88, "hardness": 82,
            "weight_min": 87, "weight_max": 94, "plies": 5, "material": "Wood + Textreme Carbon",
            "thickness": 5.8, "head_size": "Standard", "handle_types": "FL,ST"
        }
    },
    {
        "name": "Allround Evolution",
        "brand": "Stiga",
        "subcategory": "allround",
        "description": "Modern all-wood blade with excellent control. Great for allround players and developing attackers.",
        "price_usd": 74.99,
        "release_year": 2008,
        "specs": {
            "speed": 66, "control": 86, "stiffness": 58, "hardness": 55,
            "weight_min": 82, "weight_max": 88, "plies": 5, "material": "All Wood",
            "thickness": 5.6, "head_size": "Standard", "handle_types": "FL,ST,AN"
        }
    },
    {
        "name": "Defensive Pro",
        "brand": "Stiga",
        "subcategory": "defensive",
        "description": "Specialized defensive blade with excellent control for chopping and pushing. Large head size.",
        "price_usd": 79.99,
        "release_year": 2010,
        "specs": {
            "speed": 52, "control": 94, "stiffness": 42, "hardness": 38,
            "weight_min": 80, "weight_max": 86, "plies": 5, "material": "All Wood",
            "thickness": 5.5, "head_size": "Oversize", "handle_types": "FL,ST"
        }
    },
]

# ========== RUBBERS ==========
RUBBERS: List[Dict[str, Any]] = [
    # Butterfly
    {
        "name": "Tenergy 05",
        "brand": "Butterfly",
        "subcategory": "offensive",
        "description": "The most popular high-performance rubber. High tension spring sponge with incredible spin and speed. Used by professionals worldwide.",
        "price_usd": 79.99,
        "release_year": 2008,
        "specs": {
            "speed": 90, "spin": 95, "control": 72, "tackiness": 15, "grip": 92,
            "sponge_thickness": "max,2.0,1.9", "sponge_hardness": "36deg",
            "top_sheet": "inverted", "weight": "65-70g", "durability": 75
        }
    },
    {
        "name": "Dignics 09C",
        "brand": "Butterfly",
        "subcategory": "offensive_plus",
        "description": "Hybrid rubber combining tacky Chinese-style top sheet with Japanese spring sponge. Maximum spin with modern speed.",
        "price_usd": 94.99,
        "release_year": 2019,
        "specs": {
            "speed": 88, "spin": 98, "control": 75, "tackiness": 65, "grip": 95,
            "sponge_thickness": "max,2.0", "sponge_hardness": "44deg",
            "top_sheet": "inverted", "weight": "68-73g", "durability": 80
        }
    },
    {
        "name": "Rozena",
        "brand": "Butterfly",
        "subcategory": "allround_offensive",
        "description": "Mid-tier high-tension rubber. Great for players stepping up from entry-level rubbers. Good balance of performance and price.",
        "price_usd": 49.99,
        "release_year": 2017,
        "specs": {
            "speed": 78, "spin": 82, "control": 80, "tackiness": 10, "grip": 80,
            "sponge_thickness": "max,2.0,1.9", "sponge_hardness": "35deg",
            "top_sheet": "inverted", "weight": "64-69g", "durability": 72
        }
    },
    {
        "name": "Sriver",
        "brand": "Butterfly",
        "subcategory": "allround",
        "description": "Classic rubber used for decades. Great control and durability. Perfect for beginners and allround players.",
        "price_usd": 39.99,
        "release_year": 1967,
        "specs": {
            "speed": 65, "spin": 68, "control": 88, "tackiness": 5, "grip": 70,
            "sponge_thickness": "max,2.0,1.5", "sponge_hardness": "38deg",
            "top_sheet": "inverted", "weight": "62-67g", "durability": 85
        }
    },
    # Donic
    {
        "name": "Bluefire M1",
        "brand": "Donic",
        "subcategory": "offensive",
        "description": "High-tension rubber with Catapult technology. Excellent speed and spin for aggressive attackers.",
        "price_usd": 54.99,
        "release_year": 2012,
        "specs": {
            "speed": 88, "spin": 86, "control": 70, "tackiness": 8, "grip": 85,
            "sponge_thickness": "max,2.0", "sponge_hardness": "medium-hard",
            "top_sheet": "inverted", "weight": "66-71g", "durability": 70
        }
    },
    {
        "name": "Coppa X1 Turbo Platin",
        "brand": "Donic",
        "subcategory": "offensive_plus",
        "description": "Maximum speed rubber for power attackers. Turbo sponge provides explosive acceleration.",
        "price_usd": 59.99,
        "release_year": 2008,
        "specs": {
            "speed": 92, "spin": 80, "control": 65, "tackiness": 5, "grip": 82,
            "sponge_thickness": "max,2.0", "sponge_hardness": "hard",
            "top_sheet": "inverted", "weight": "67-72g", "durability": 68
        }
    },
    {
        "name": "Vario Big Slam",
        "brand": "Donic",
        "subcategory": "allround",
        "description": "Soft sponge rubber with maximum control and loud sound. Great for developing players.",
        "price_usd": 34.99,
        "release_year": 2005,
        "specs": {
            "speed": 62, "spin": 65, "control": 90, "tackiness": 3, "grip": 68,
            "sponge_thickness": "max,2.0", "sponge_hardness": "soft",
            "top_sheet": "inverted", "weight": "60-65g", "durability": 72
        }
    },
    # DHS
    {
        "name": "Hurricane 3 Neo",
        "brand": "DHS",
        "subcategory": "offensive",
        "description": "The most popular rubber in China. Highly tacky top sheet with great spin. Factory-tuned (Neo) version.",
        "price_usd": 29.99,
        "release_year": 2000,
        "specs": {
            "speed": 72, "spin": 95, "control": 82, "tackiness": 90, "grip": 88,
            "sponge_thickness": "max,2.2,2.15", "sponge_hardness": "39deg,40deg",
            "top_sheet": "inverted", "weight": "68-73g", "durability": 70
        }
    },
    {
        "name": "Hurricane 8",
        "brand": "DHS",
        "subcategory": "offensive_plus",
        "description": "Updated version of Hurricane 3 with faster sponge. Designed for the 40+ ball era.",
        "price_usd": 34.99,
        "release_year": 2015,
        "specs": {
            "speed": 80, "spin": 92, "control": 78, "tackiness": 85, "grip": 86,
            "sponge_thickness": "max,2.2", "sponge_hardness": "39deg,40deg,41deg",
            "top_sheet": "inverted", "weight": "69-74g", "durability": 72
        }
    },
    {
        "name": "Skyline 3",
        "brand": "DHS",
        "subcategory": "offensive",
        "description": "Popular backhand rubber. Slightly softer than Hurricane with more control. Good for looping.",
        "price_usd": 27.99,
        "release_year": 2005,
        "specs": {
            "speed": 70, "spin": 88, "control": 84, "tackiness": 80, "grip": 82,
            "sponge_thickness": "max,2.2", "sponge_hardness": "37deg,38deg",
            "top_sheet": "inverted", "weight": "66-71g", "durability": 70
        }
    },
    # Nittaku
    {
        "name": "Fastarc G-1",
        "brand": "Nittaku",
        "subcategory": "offensive",
        "description": "High-tension rubber with German-made sponge. Excellent speed and spin balance. Popular among Japanese league players.",
        "price_usd": 54.99,
        "release_year": 2011,
        "specs": {
            "speed": 86, "spin": 88, "control": 74, "tackiness": 5, "grip": 86,
            "sponge_thickness": "max,2.0", "sponge_hardness": "medium-hard",
            "top_sheet": "inverted", "weight": "65-70g", "durability": 78
        }
    },
    {
        "name": "Moristo SP",
        "brand": "Nittaku",
        "subcategory": "offensive",
        "description": "High-quality short pips rubber. Great for fast attacks and blocking. Used by penhold players.",
        "price_usd": 44.99,
        "release_year": 2005,
        "specs": {
            "speed": 82, "spin": 60, "control": 80, "tackiness": 0, "grip": 55,
            "sponge_thickness": "max,2.0,1.6", "sponge_hardness": "medium",
            "top_sheet": "short_pips", "weight": "62-67g", "durability": 80
        }
    },
    {
        "name": "Hammond Z2",
        "brand": "Nittaku",
        "subcategory": "allround_offensive",
        "description": "Soft high-tension rubber with excellent control. Good for players learning spin techniques.",
        "price_usd": 44.99,
        "release_year": 2014,
        "specs": {
            "speed": 75, "spin": 80, "control": 82, "tackiness": 5, "grip": 78,
            "sponge_thickness": "max,2.0", "sponge_hardness": "soft",
            "top_sheet": "inverted", "weight": "63-68g", "durability": 75
        }
    },
    # Xiom
    {
        "name": "Omega VII Pro",
        "brand": "Xiom",
        "subcategory": "offensive_plus",
        "description": "Top-tier tensor rubber with Dynamic Friction technology. Extreme spin and speed for professional play.",
        "price_usd": 54.99,
        "release_year": 2018,
        "specs": {
            "speed": 92, "spin": 94, "control": 68, "tackiness": 10, "grip": 90,
            "sponge_thickness": "max,2.0", "sponge_hardness": "hard",
            "top_sheet": "inverted", "weight": "67-72g", "durability": 74
        }
    },
    {
        "name": "Vega Pro",
        "brand": "Xiom",
        "subcategory": "offensive",
        "description": "Popular mid-range tensor rubber. Great balance of speed, spin, and price. Good upgrade from beginner rubbers.",
        "price_usd": 39.99,
        "release_year": 2010,
        "specs": {
            "speed": 82, "spin": 84, "control": 76, "tackiness": 5, "grip": 80,
            "sponge_thickness": "max,2.0", "sponge_hardness": "medium-hard",
            "top_sheet": "inverted", "weight": "65-70g", "durability": 72
        }
    },
    {
        "name": "Vega Europe",
        "brand": "Xiom",
        "subcategory": "allround_offensive",
        "description": "Softer version of Vega Pro. More control and softer feeling. Great for backhand or developing players.",
        "price_usd": 39.99,
        "release_year": 2010,
        "specs": {
            "speed": 76, "spin": 80, "control": 82, "tackiness": 3, "grip": 76,
            "sponge_thickness": "max,2.0", "sponge_hardness": "medium",
            "top_sheet": "inverted", "weight": "64-69g", "durability": 72
        }
    },
    # Tibhar
    {
        "name": "Evolution MX-P",
        "brand": "Tibhar",
        "subcategory": "offensive_plus",
        "description": "Maximum power tensor rubber. One of the fastest rubbers on the market. For advanced offensive players.",
        "price_usd": 54.99,
        "release_year": 2013,
        "specs": {
            "speed": 94, "spin": 90, "control": 65, "tackiness": 5, "grip": 85,
            "sponge_thickness": "max,2.1,2.0", "sponge_hardness": "hard",
            "top_sheet": "inverted", "weight": "68-73g", "durability": 70
        }
    },
    {
        "name": "Evolution EL-P",
        "brand": "Tibhar",
        "subcategory": "offensive",
        "description": "Softer Evolution rubber. Better control with good speed. Great for allround attackers.",
        "price_usd": 54.99,
        "release_year": 2013,
        "specs": {
            "speed": 84, "spin": 86, "control": 78, "tackiness": 3, "grip": 82,
            "sponge_thickness": "max,2.1,2.0", "sponge_hardness": "medium",
            "top_sheet": "inverted", "weight": "66-71g", "durability": 72
        }
    },
    {
        "name": "Nimbus Delta V",
        "brand": "Tibhar",
        "subcategory": "allround",
        "description": "Soft tensor rubber with great control. Good for beginners transitioning to modern rubbers.",
        "price_usd": 39.99,
        "release_year": 2016,
        "specs": {
            "speed": 72, "spin": 76, "control": 86, "tackiness": 2, "grip": 72,
            "sponge_thickness": "max,2.0", "sponge_hardness": "soft",
            "top_sheet": "inverted", "weight": "63-68g", "durability": 74
        }
    },
    # Andro
    {
        "name": "Rasanter R53",
        "brand": "Andro",
        "subcategory": "offensive_plus",
        "description": "53-degree sponge with maximum power. Ultra modern tensor technology for aggressive play.",
        "price_usd": 49.99,
        "release_year": 2017,
        "specs": {
            "speed": 92, "spin": 90, "control": 66, "tackiness": 5, "grip": 86,
            "sponge_thickness": "max,2.0", "sponge_hardness": "53deg",
            "top_sheet": "inverted", "weight": "68-73g", "durability": 72
        }
    },
    {
        "name": "Rasanter R47",
        "brand": "Andro",
        "subcategory": "offensive",
        "description": "47-degree sponge with balanced characteristics. Good for players wanting modern speed with control.",
        "price_usd": 49.99,
        "release_year": 2017,
        "specs": {
            "speed": 86, "spin": 88, "control": 74, "tackiness": 5, "grip": 84,
            "sponge_thickness": "max,2.0", "sponge_hardness": "47deg",
            "top_sheet": "inverted", "weight": "66-71g", "durability": 72
        }
    },
    {
        "name": "Hexer Grip",
        "brand": "Andro",
        "subcategory": "allround_offensive",
        "description": "Grip-focused rubber with hexagonal top sheet structure. Good spin generation with control.",
        "price_usd": 39.99,
        "release_year": 2014,
        "specs": {
            "speed": 76, "spin": 82, "control": 80, "tackiness": 10, "grip": 85,
            "sponge_thickness": "max,2.0", "sponge_hardness": "medium",
            "top_sheet": "inverted", "weight": "65-70g", "durability": 74
        }
    },
    # Stiga
    {
        "name": "DNA Platinum XH",
        "brand": "Stiga",
        "subcategory": "offensive_plus",
        "description": "Extra hard sponge with ESC technology. Maximum speed and spin for professional attackers.",
        "price_usd": 59.99,
        "release_year": 2020,
        "specs": {
            "speed": 94, "spin": 92, "control": 66, "tackiness": 5, "grip": 88,
            "sponge_thickness": "max,2.1,2.0", "sponge_hardness": "extra-hard",
            "top_sheet": "inverted", "weight": "69-74g", "durability": 76
        }
    },
    {
        "name": "DNA Pro M",
        "brand": "Stiga",
        "subcategory": "offensive",
        "description": "Medium sponge hardness with good balance. Popular among club players for forehand use.",
        "price_usd": 54.99,
        "release_year": 2019,
        "specs": {
            "speed": 86, "spin": 88, "control": 76, "tackiness": 3, "grip": 84,
            "sponge_thickness": "max,2.1,2.0", "sponge_hardness": "medium",
            "top_sheet": "inverted", "weight": "66-71g", "durability": 76
        }
    },
    {
        "name": "Mantra M",
        "brand": "Stiga",
        "subcategory": "allround_offensive",
        "description": "Japanese-style tensor rubber with medium sponge. Good for backhand or controlled attack.",
        "price_usd": 49.99,
        "release_year": 2016,
        "specs": {
            "speed": 80, "spin": 84, "control": 80, "tackiness": 3, "grip": 80,
            "sponge_thickness": "max,2.0", "sponge_hardness": "medium",
            "top_sheet": "inverted", "weight": "65-70g", "durability": 74
        }
    },
]

# ========== SEED POSTS ==========
SEED_POSTS = [
    {
        "title": "Butterfly Viscaria vs Timo Boll ALC - Which is right for you?",
        "content": "Both are iconic Butterfly ALC blades, but they cater to slightly different playing styles. The Viscaria (87 speed / 72 control) offers a crisper, more direct feeling with a slightly harder touch. It's ideal for aggressive loopers who want immediate feedback and power. The Timo Boll ALC (82 speed / 78 control) feels softer and more forgiving, making it better for players who prioritize spin generation and controlled attacks. In my experience, Viscaria pairs beautifully with Tenergy 05 for an explosive forehand, while the TB ALC works great with Dignics 09C for a spin-dominant game. What's your experience with these blades?",
        "image_url": "/static/equipment/blades/butterfly-viscaria.jpg",
        "author": "TTExpert",
        "stats": {"speed": 8.5, "control": 7.5, "spin": 9.0, "feel": 8.0}
    },
    {
        "title": "DHS Hurricane 3 Neo - The ultimate Chinese rubber?",
        "content": "Hurricane 3 Neo has been the go-to rubber for Chinese professional players for over two decades. With its highly tacky top sheet (90/100 tackiness) and hard sponge, it generates incredible spin on loops and serves. The factory-tuned Neo version comes with a speed glue effect built in, making it more playable out of the package than the original. At $29.99, it's also one of the best value-for-money rubbers on the market. Pro tip: pair it with a hard carbon blade like DHS Hurricane Long 5 for maximum effect. The main downside is that it requires good technique - beginners might find it too unforgiving.",
        "image_url": "/static/equipment/rubbers/dhs-hurricane-3-neo.jpg",
        "author": "SpinMaster",
        "stats": {"speed": 7.2, "spin": 9.5, "control": 8.2, "value": 9.5}
    },
    {
        "title": "Beginner Setup Guide: Best Blade + Rubber Combos Under $100",
        "content": "Starting out in table tennis can be overwhelming with so many equipment choices. Here are my top 3 budget-friendly setups that won't hold back your development:\n\n1. **Andro Wood ALL+/OFF- ($49.99) + Donic Vario Big Slam ($34.99)** = Total: ~$85\n   Great control and feeling. Perfect for learning proper technique.\n\n2. **Stiga Allround Evolution ($74.99) + Butterfly Sriver ($39.99)** = Total: ~$115\n   Classic combo with excellent durability and allround performance.\n\n3. **Donic Appelgren Allplay ($74.99) + Xiom Vega Europe ($39.99)** = Total: ~$115\n   Soft feeling with modern tensor rubber. Good for developing spin.\n\nAvoid pre-made rackets from general sports stores - they're usually slow and don't allow you to upgrade components individually. Invest in a custom setup and you'll thank yourself later!",
        "image_url": "/static/equipment/blades/andro-wood-all-off.jpg",
        "author": "CoachMike",
        "stats": {"speed": 6.5, "control": 9.0, "spin": 7.0, "value": 9.0}
    },
    {
        "title": "Stiga Carbonado 245 Review - Too Fast for Mortals?",
        "content": "The Carbonado 245 is one of the fastest blades ever created (95/100 speed). With Textreme carbon layers, it offers incredible power but demands perfect technique. At $199.99, it's a serious investment. I've been testing it for a month with DNA Platinum XH on forehand and DNA Pro M on backhand. The results:\n\nPros:\n- Devastating power on loops and smashes\n- Large sweet spot\n- Great for counter-looping\n\nCons:\n- Unforgiving on off-center hits\n- Blocking requires precise timing\n- Not suitable for beginners or intermediate players\n\nRating: 9/10 for advanced attackers, 4/10 for everyone else.",
        "image_url": "/static/equipment/blades/stiga-carbonado-245.jpg",
        "author": "PowerPlayer",
        "stats": {"speed": 9.5, "control": 6.2, "spin": 8.5, "feel": 7.0}
    },
    {
        "title": "Tibhar Balsa SGS - The Chopping Weapon",
        "content": "For defensive players, the Tibhar Balsa SGS is a fantastic choice. At only 70-78g, it's incredibly light and maneuverable. The balsa construction provides excellent control for chopping (92/100) while still offering enough speed for counter-attacks. I've paired mine with TSP Curl P-1R long pips on backhand and Victas VS > 401 on forehand. The combination allows for heavy backspin chops and controlled attacks when the opportunity arises. If you're tired of losing to attackers and want to try a defensive style, this blade is an excellent starting point.",
        "image_url": "/static/equipment/blades/tibhar-balsa-sgs.jpg",
        "author": "ChopChamp",
        "stats": {"speed": 5.5, "control": 9.2, "spin": 7.0, "defense": 9.5}
    },
]

# ========== SEED FORUMS ==========
SEED_FORUMS = [
    {
        "title": "What is your current setup? Share your blade + rubber combo!",
        "content": "Let's get to know the community! Share your current playing setup and tell us why you chose it. Include your playing style and level so others can learn from your experience.\n\nI'll start:\nBlade: Butterfly Viscaria\nFH: Tenergy 05 (2.1mm)\nBH: Dignics 09C (2.0mm)\nStyle: Aggressive looper\nLevel: Advanced club player",
        "author": "TTExpert",
    },
    {
        "title": "Chinese vs European/Japanese Rubbers - The Great Debate",
        "content": "This debate has been going on forever in the TT community. Chinese rubbers like Hurricane 3 offer incredible spin and durability at low cost, but require more technique. Japanese/European tensors like Tenergy and Evolution offer speed and easy spin with modern technology, but at a premium price and shorter lifespan.\n\nWhat's your preference? Have you switched from one to the other? What was your experience?",
        "author": "SpinMaster",
    },
    {
        "title": "Best equipment for beginners - 2025 Recommendations",
        "content": "With so many new players joining the sport, let's create a comprehensive list of recommended beginner equipment. Please share setups that are:\n- Easy to control\n- Not too fast\n- Good value for money\n- Help develop proper technique\n\nAvoid recommending professional equipment like Viscaria + Tenergy 05 to beginners - it will actually slow down their progress!",
        "author": "CoachMike",
    },
    {
        "title": "Penhold vs Shakehand - Equipment Differences",
        "content": "Penhold players often have different equipment needs than shakehand players. Penhold typically requires rubbers that work well on the forehand with a different feel on the backhand (or no backhand rubber at all for traditional penhold).\n\nFor penhold players:\n- Do you use reverse penhold backhand (RPB)?\n- What blade handle type works best (CS vs FL modified)?\n- Do you use the same rubber on both sides?\n\nLet's discuss penhold-specific equipment recommendations!",
        "author": "PenholdPro",
    },
    {
        "title": "Carbon vs All-Wood Blades - When to Make the Switch",
        "content": "Many players wonder when they should switch from an all-wood blade to a carbon blade. The answer depends on your technique and playing style:\n\nStick with all-wood if:\n- You're still developing basic strokes\n- You value feeling and control over raw power\n- You play an allround or defensive style\n\nConsider carbon if:\n- You have solid technique and want more speed\n- You play at least 3-4 times per week\n- You feel your current blade limits your power\n\nWhat's your experience? When did you switch, and do you regret it?",
        "author": "PowerPlayer",
    },
]
