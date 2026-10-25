"""
Week 12 Capstone Corpus: 600-Recipe CMS Library & Test Kitchen Specifications
Includes:
- 600 recipes with structured allergen/may-contain declarations
- 80 recipes with dual versions (original vs reformulated-2025)
- Test kitchen substitutions table
- Food safety safe internal temperatures chart
"""

import re
from typing import Dict, List, Optional, Any

# Structured Safe Internal Temperatures Chart
SAFE_INTERNAL_TEMPERATURES = {
    "chicken": "74°C (165°F)",
    "turkey": "74°C (165°F)",
    "poultry": "74°C (165°F)",
    "ground beef": "71°C (160°F)",
    "ground pork": "71°C (160°F)",
    "pork": "63°C (145°F) + 3 min rest",
    "beef": "63°C (145°F) + 3 min rest",
    "fish": "63°C (145°F)",
    "shellfish": "63°C (145°F)",
}

# Test Kitchen Substitution Table
# Maps (ingredient, restriction) -> { "substitute": ..., "introduced_allergens": [...], "notes": ... }
TEST_KITCHEN_SUBSTITUTIONS = {
    ("butter", "dairy_free"): {
        "safe_substitute": "refined coconut oil",
        "introduced_allergens": [],
        "notes": "1:1 ratio for baking. Neutral flavor."
    },
    ("butter", "dairy_free_nut_swap_trap"): {
        # BONUS CHALLENGE TRAP: Proposed swap that re-introduces an allergen!
        "safe_substitute": "almond-oil culinary blend",
        "introduced_allergens": ["tree nuts"],
        "notes": "Rich mouthfeel, but introduces tree nuts!"
    },
    ("peanuts", "nut_free"): {
        "safe_substitute": "toasted sunflower seeds",
        "introduced_allergens": [],
        "notes": "Safe crunch substitution."
    },
    ("milk", "dairy_free"): {
        "safe_substitute": "oat milk",
        "introduced_allergens": ["gluten" if False else None],  # certified gluten-free oat milk
        "notes": "Creamy consistency, neutral flavor."
    },
    ("wheat flour", "gluten_free"): {
        "safe_substitute": "1:1 gluten-free baking blend (rice, potato starch, tapioca)",
        "introduced_allergens": [],
        "notes": "Direct 1:1 cup swap."
    },
    ("soy sauce", "soy_free"): {
        "safe_substitute": "coconut aminos",
        "introduced_allergens": [],
        "notes": "Slightly sweeter, low sodium."
    },
    ("eggs", "vegan"): {
        "safe_substitute": "flax egg (1 tbsp ground flax + 3 tbsp water)",
        "introduced_allergens": [],
        "notes": "Binder for baked goods."
    }
}

# Core 600-Recipe Catalog Definition
RECIPE_DATABASE: Dict[str, Dict[str, Any]] = {
    "recipe_shortbread_orig": {
        "id": "recipe_shortbread_orig",
        "title": "Traditional Scottish Shortbread",
        "version": "original",
        "is_superseded": True,
        "prep_time_minutes": 15,
        "cook_time_minutes": 30,
        "servings": 4,
        "ingredients": [
            {"name": "plain flour", "quantity": 250, "unit": "g"},
            {"name": "salted butter", "quantity": 175, "unit": "g"},
            {"name": "caster sugar", "quantity": 75, "unit": "g"}
        ],
        "allergens": ["dairy", "gluten"],
        "may_contain": [],
        "method": "Cream butter and sugar together. Fold in flour until dough forms. Roll to 1cm thickness and bake at 160°C for 30 minutes.",
        "safe_internal_temp": None,
        "version_notes": "Original pre-reformulation version using pure creamery butter."
    },
    "recipe_shortbread_reform2025": {
        "id": "recipe_shortbread_reform2025",
        "title": "Traditional Scottish Shortbread",
        "version": "reformulated-2025",
        "is_superseded": False,
        "prep_time_minutes": 15,
        "cook_time_minutes": 30,
        "servings": 4,
        "ingredients": [
            {"name": "plain flour", "quantity": 250, "unit": "g"},
            {"name": "nut-oil butter blend (almond & vegetable oil)", "quantity": 175, "unit": "g"},
            {"name": "caster sugar", "quantity": 75, "unit": "g"}
        ],
        "allergens": ["tree nuts", "gluten"],
        "may_contain": ["dairy", "peanuts"],
        "method": "Cream nut-oil butter blend and sugar together. Fold in flour until dough forms. Roll to 1cm thickness and bake at 160°C for 30 minutes.",
        "safe_internal_temp": None,
        "version_notes": "Reformulated in 2025 following supplier change: swapped butter for almond nut-oil blend."
    },
    "recipe_roast_chicken": {
        "id": "recipe_roast_chicken",
        "title": "Herb-Roasted Chicken with Crispy Skin",
        "version": "reformulated-2025",
        "is_superseded": False,
        "prep_time_minutes": 15,
        "cook_time_minutes": 50,
        "servings": 4,
        "ingredients": [
            {"name": "whole chicken", "quantity": 1500, "unit": "g"},
            {"name": "baby potatoes", "quantity": 500, "unit": "g"},
            {"name": "olive oil", "quantity": 2, "unit": "tbsp"},
            {"name": "fresh rosemary", "quantity": 2, "unit": "sprigs"},
            {"name": "sea salt", "quantity": 1, "unit": "tsp"}
        ],
        "allergens": [],
        "may_contain": [],
        "method": "Pat chicken dry. Rub skin with olive oil, salt, and minced rosemary. Roast at 200°C for 50 minutes until golden and internal temperature reads 74°C (165°F) in thickest part of thigh.",
        "safe_internal_temp": "74°C (165°F)",
        "version_notes": "Standard test kitchen baseline."
    },
    "recipe_quick_dal": {
        "id": "recipe_quick_dal",
        "title": "20-Minute Coconut Yellow Dal",
        "version": "reformulated-2025",
        "is_superseded": False,
        "prep_time_minutes": 5,
        "cook_time_minutes": 15,
        "servings": 2,
        "ingredients": [
            {"name": "yellow split moong dal", "quantity": 200, "unit": "g"},
            {"name": "coconut milk", "quantity": 200, "unit": "ml"},
            {"name": "ground turmeric", "quantity": 0.5, "unit": "tsp"},
            {"name": "cumin seeds", "quantity": 1, "unit": "tsp"},
            {"name": "coconut oil", "quantity": 1, "unit": "tbsp"}
        ],
        "allergens": [],
        "may_contain": [],
        "method": "Simmer lentils with turmeric in water for 12 minutes. Stir in coconut milk. Temper cumin seeds in hot coconut oil and pour over dal.",
        "safe_internal_temp": None,
        "version_notes": "Naturally gluten-free, vegan, nut-free."
    },
    "recipe_thai_green_curry": {
        "id": "recipe_thai_green_curry",
        "title": "Quick Thai Green Curry",
        "version": "reformulated-2025",
        "is_superseded": False,
        "prep_time_minutes": 10,
        "cook_time_minutes": 15,
        "servings": 4,
        "ingredients": [
            {"name": "chicken breast strips", "quantity": 400, "unit": "g"},
            {"name": "coconut milk", "quantity": 400, "unit": "ml"},
            {"name": "green curry paste", "quantity": 2, "unit": "tbsp"},
            {"name": "fish sauce", "quantity": 1, "unit": "tbsp"},
            {"name": "bamboo shoots", "quantity": 150, "unit": "g"}
        ],
        "allergens": ["fish"],
        "may_contain": ["crustacean"],
        "method": "Fry paste in coconut cream. Add chicken and simmer for 10 minutes until chicken reaches 74°C (165°F). Season with fish sauce.",
        "safe_internal_temp": "74°C (165°F)",
        "version_notes": "Verified authentic formulation."
    },
    "recipe_mysore_pak": {
        "id": "recipe_mysore_pak",
        "title": "Traditional Mysore Pak Fudge",
        "version": "reformulated-2025",
        "is_superseded": False,
        "prep_time_minutes": 10,
        "cook_time_minutes": 20,
        "servings": 6,
        "ingredients": [
            {"name": "gram flour (besan)", "quantity": 200, "unit": "g"},
            {"name": "sugar", "quantity": 300, "unit": "g"},
            {"name": "ghee (clarified butter)", "quantity": 250, "unit": "g"},
            {"name": "water", "quantity": 100, "unit": "ml"}
        ],
        "allergens": ["dairy"],
        "may_contain": [],
        "method": "Make single-thread sugar syrup. Whisk in besan and slowly pour hot ghee until porous fudge forms.",
        "safe_internal_temp": None,
        "version_notes": "Contains pure dairy ghee."
    },
    "recipe_chettinad_biryani": {
        "id": "recipe_chettinad_biryani",
        "title": "Chettinad Chicken Biryani",
        "version": "reformulated-2025",
        "is_superseded": False,
        "prep_time_minutes": 25,
        "cook_time_minutes": 40,
        "servings": 4,
        "ingredients": [
            {"name": "seeraga samba rice", "quantity": 500, "unit": "g"},
            {"name": "chicken pieces", "quantity": 600, "unit": "g"},
            {"name": "ghee and oil blend", "quantity": 3, "unit": "tbsp"},
            {"name": "marathi moggu (kapok buds)", "quantity": 2, "unit": "pieces"},
            {"name": "kalpasi (stone flower)", "quantity": 1, "unit": "tsp"},
            {"name": "star anise", "quantity": 1, "unit": "piece"},
            {"name": "onions sliced", "quantity": 2, "unit": "medium"},
            {"name": "tomatoes", "quantity": 2, "unit": "chopped"},
            {"name": "ginger garlic paste", "quantity": 2, "unit": "tbsp"},
            {"name": "mint and coriander leaves", "quantity": 1, "unit": "cup"}
        ],
        "allergens": ["dairy"],
        "may_contain": [],
        "method": "Sauté whole spices (marathi moggu, stone flower, star anise) in hot ghee. Fry onions, ginger-garlic, mint, and chicken until sealed. Add rice and water (1:2 ratio). Seal pot with dum lid and cook on low heat for 25 minutes until chicken internal temperature reaches 74°C (165°F).",
        "safe_internal_temp": "74°C (165°F)",
        "version_notes": "Authentic Chettinad test kitchen recipe using traditional stone flower and kapok buds."
    },
    "recipe_chicken_65": {
        "id": "recipe_chicken_65",
        "title": "Chennai Style Crispy Chicken 65",
        "version": "reformulated-2025",
        "is_superseded": False,
        "prep_time_minutes": 20,
        "cook_time_minutes": 15,
        "servings": 4,
        "ingredients": [
            {"name": "boneless chicken cubes", "quantity": 500, "unit": "g"},
            {"name": "Kashmiri red chili powder", "quantity": 2, "unit": "tbsp"},
            {"name": "ginger garlic paste", "quantity": 1, "unit": "tbsp"},
            {"name": "cornstarch", "quantity": 2, "unit": "tbsp"},
            {"name": "egg", "quantity": 1, "unit": "whole"},
            {"name": "curry leaves and green chilies", "quantity": 2, "unit": "sprigs"},
            {"name": "lemon juice", "quantity": 1, "unit": "tbsp"}
        ],
        "allergens": ["eggs"],
        "may_contain": [],
        "method": "Marinate chicken cubes with chili, ginger-garlic, lemon, egg, and cornstarch for 20 minutes. Deep fry in hot oil (180°C) until deep red and crispy, ensuring internal temperature registers 74°C (165°F). Toss with flash-fried curry leaves.",
        "safe_internal_temp": "74°C (165°F)",
        "version_notes": "Legendary Chennai test kitchen recipe."
    },
    "recipe_dosa_batter": {
        "id": "recipe_dosa_batter",
        "title": "Crispy South Indian Fermented Dosa",
        "version": "reformulated-2025",
        "is_superseded": False,
        "prep_time_minutes": 20,
        "cook_time_minutes": 10,
        "servings": 4,
        "ingredients": [
            {"name": "idli parboiled rice", "quantity": 300, "unit": "g"},
            {"name": "whole white urad dal", "quantity": 100, "unit": "g"},
            {"name": "fenugreek seeds (methi)", "quantity": 1, "unit": "tsp"},
            {"name": "rock salt", "quantity": 1, "unit": "tsp"},
            {"name": "sesame oil for roasting", "quantity": 2, "unit": "tbsp"}
        ],
        "allergens": [],
        "may_contain": [],
        "method": "Soak rice and urad dal with fenugreek for 4 hours. Grind to smooth, airy batter. Ferment for 8 to 12 hours in a warm place until risen. Pour ladleful on hot seasoned cast iron tawa, spread thin in spiral, drizzle oil, and roast until golden and crispy.",
        "safe_internal_temp": None,
        "version_notes": "Naturally gluten-free, vegan, nut-free."
    },
    "recipe_tomato_rasam": {
        "id": "recipe_tomato_rasam",
        "title": "Tangy South Indian Tomato Rasam",
        "version": "reformulated-2025",
        "is_superseded": False,
        "prep_time_minutes": 10,
        "cook_time_minutes": 15,
        "servings": 4,
        "ingredients": [
            {"name": "ripe tomatoes crushed", "quantity": 3, "unit": "medium"},
            {"name": "tamarind extract", "quantity": 1, "unit": "tbsp"},
            {"name": "crushed black pepper and cumin", "quantity": 1.5, "unit": "tbsp"},
            {"name": "asafoetida (hing resin)", "quantity": 0.25, "unit": "tsp"},
            {"name": "mustard seeds and curry leaves", "quantity": 1, "unit": "tsp"},
            {"name": "ghee or coconut oil for tempering", "quantity": 1, "unit": "tbsp"}
        ],
        "allergens": [],
        "may_contain": [],
        "method": "Boil crushed tomatoes with tamarind, turmeric, and water. Stir in fresh pepper-cumin rasam powder and salt. Temper mustard seeds, curry leaves, and asafoetida resin in ghee. Pour into rasam and switch off heat immediately when froth forms on top.",
        "safe_internal_temp": None,
        "version_notes": "Classic digestive soup."
    },
    "recipe_sweet_pongal": {
        "id": "recipe_sweet_pongal",
        "title": "Temple Style Sakkarai Sweet Pongal",
        "version": "reformulated-2025",
        "is_superseded": False,
        "prep_time_minutes": 10,
        "cook_time_minutes": 25,
        "servings": 4,
        "ingredients": [
            {"name": "raw rice", "quantity": 200, "unit": "g"},
            {"name": "yellow split moong dal", "quantity": 50, "unit": "g"},
            {"name": "dark jaggery syrup", "quantity": 250, "unit": "g"},
            {"name": "pure dairy ghee", "quantity": 60, "unit": "ml"},
            {"name": "cashews and raisins", "quantity": 20, "unit": "g"},
            {"name": "cardamom and edible camphor", "quantity": 0.5, "unit": "tsp"}
        ],
        "allergens": ["tree nuts", "dairy"],
        "may_contain": [],
        "method": "Dry roast moong dal and pressure cook with rice until mashable. Dissolve jaggery into syrup and strain into the mashed rice-dal. Simmer on low heat while adding ghee. Fry cashews and raisins in hot ghee and stir in with cardamom.",
        "safe_internal_temp": None,
        "version_notes": "Festive South Indian harvest pudding."
    },
    "recipe_lemon_rice": {
        "id": "recipe_lemon_rice",
        "title": "Zesty South Indian Lemon Rice (Elumichai Sadam)",
        "version": "reformulated-2025",
        "is_superseded": False,
        "prep_time_minutes": 10,
        "cook_time_minutes": 10,
        "servings": 4,
        "ingredients": [
            {"name": "cooked cooled rice", "quantity": 400, "unit": "g"},
            {"name": "fresh lemon juice", "quantity": 3, "unit": "tbsp"},
            {"name": "roasted peanuts", "quantity": 2, "unit": "tbsp"},
            {"name": "mustard seeds, chana dal, urad dal", "quantity": 1, "unit": "tbsp"},
            {"name": "turmeric powder", "quantity": 0.5, "unit": "tsp"},
            {"name": "green chilies, ginger, and curry leaves", "quantity": 1, "unit": "tbsp"},
            {"name": "sesame oil", "quantity": 2, "unit": "tbsp"}
        ],
        "allergens": ["peanuts"],
        "may_contain": [],
        "method": "Heat sesame oil in pan. Sauté mustard, lentils, peanuts, ginger, chilies, and curry leaves until golden. Add turmeric and remove from heat. Stir in lemon juice and salt. Gently fold into cooled rice until evenly yellow.",
        "safe_internal_temp": None,
        "version_notes": "Contains peanuts in traditional tempering."
    },
    "recipe_kodi_vepudu": {
        "id": "recipe_kodi_vepudu",
        "title": "Andhra Style Kodi Vepudu Chicken Fry",
        "version": "reformulated-2025",
        "is_superseded": False,
        "prep_time_minutes": 15,
        "cook_time_minutes": 30,
        "servings": 4,
        "ingredients": [
            {"name": "bone-in chicken pieces", "quantity": 600, "unit": "g"},
            {"name": "sliced onions", "quantity": 2, "unit": "large"},
            {"name": "roasted Andhra masala powder", "quantity": 2, "unit": "tbsp"},
            {"name": "ginger garlic paste", "quantity": 1.5, "unit": "tbsp"},
            {"name": "green chilies and curry leaves", "quantity": 2, "unit": "sprigs"},
            {"name": "cooking oil", "quantity": 3, "unit": "tbsp"}
        ],
        "allergens": [],
        "may_contain": [],
        "method": "Sauté onions, chilies, and curry leaves until brown. Add ginger-garlic and chicken. Cook until juices release and evaporate. Sprinkle spicy roasted Andhra spice blend and roast on medium-low until chicken is deeply browned, fragrant, and internal temperature reads 74°C (165°F).",
        "safe_internal_temp": "74°C (165°F)",
        "version_notes": "Authentic spicy dry Andhra chicken roast."
    },
    "recipe_bisi_bele_bath": {
        "id": "recipe_bisi_bele_bath",
        "title": "Karnataka Bisi Bele Bath (Hot Lentil Rice)",
        "version": "reformulated-2025",
        "is_superseded": False,
        "prep_time_minutes": 20,
        "cook_time_minutes": 35,
        "servings": 4,
        "ingredients": [
            {"name": "sona masoori rice", "quantity": 150, "unit": "g"},
            {"name": "toor dal (pigeon peas)", "quantity": 100, "unit": "g"},
            {"name": "diced mixed vegetables (carrot, beans, peas)", "quantity": 200, "unit": "g"},
            {"name": "freshly roasted BBB spice powder", "quantity": 2.5, "unit": "tbsp"},
            {"name": "tamarind paste", "quantity": 1, "unit": "tbsp"},
            {"name": "ghee and cashews for tempering", "quantity": 2, "unit": "tbsp"}
        ],
        "allergens": ["tree nuts", "dairy"],
        "may_contain": [],
        "method": "Cook rice, toor dal, and vegetables together until tender. Stir in tamarind pulp, salt, and freshly ground BBB masala powder. Simmer for 10 minutes until aromatic and thick. Temper mustard seeds and cashews in hot ghee and pour over the dish.",
        "safe_internal_temp": None,
        "version_notes": "Contains cashews and ghee in tempering."
    },
    "recipe_curd_rice": {
        "id": "recipe_curd_rice",
        "title": "Traditional South Indian Curd Rice (Thayir Sadam)",
        "version": "reformulated-2025",
        "is_superseded": False,
        "prep_time_minutes": 10,
        "cook_time_minutes": 15,
        "servings": 4,
        "ingredients": [
            {"name": "cooked soft rice (slightly mashed)", "quantity": 400, "unit": "g"},
            {"name": "fresh plain yogurt (curd)", "quantity": 300, "unit": "g"},
            {"name": "warm milk", "quantity": 100, "unit": "ml"},
            {"name": "mustard seeds", "quantity": 1, "unit": "tsp"},
            {"name": "urad dal", "quantity": 1, "unit": "tsp"},
            {"name": "green chilies and finely chopped ginger", "quantity": 1, "unit": "tbsp"},
            {"name": "curry leaves and fresh coriander", "quantity": 1, "unit": "sprig"},
            {"name": "pomegranate arils or seedless green grapes", "quantity": 2, "unit": "tbsp"},
            {"name": "sesame oil or ghee for tempering", "quantity": 1, "unit": "tbsp"}
        ],
        "allergens": ["dairy"],
        "may_contain": [],
        "method": "Mash warm cooked rice softly. Fold in fresh curd, warm milk, and salt until creamy and soothing. Heat oil in a small pan, crackle mustard seeds, urad dal, ginger, green chilies, and curry leaves. Pour hot tadka over the curd rice. Garnish with fresh coriander and pomegranate arils. Nut-free.",
        "safe_internal_temp": None,
        "version_notes": "Traditional comforting South Indian curd rice (thayir sadam / daddojanam). Naturally nut-free, contains dairy."
    },
    "recipe_south_indian_sambar": {
        "id": "recipe_south_indian_sambar",
        "title": "Authentic South Indian Drumstick Sambar",
        "version": "reformulated-2025",
        "is_superseded": False,
        "prep_time_minutes": 15,
        "cook_time_minutes": 25,
        "servings": 4,
        "ingredients": [
            {"name": "toor dal (split pigeon peas)", "quantity": 150, "unit": "g"},
            {"name": "drumstick pieces and shallots", "quantity": 200, "unit": "g"},
            {"name": "sambar powder", "quantity": 2, "unit": "tbsp"},
            {"name": "tamarind extract", "quantity": 2, "unit": "tbsp"},
            {"name": "tomatoes", "quantity": 2, "unit": "medium"},
            {"name": "mustard seeds and curry leaves", "quantity": 1, "unit": "tsp"},
            {"name": "sesame oil", "quantity": 1, "unit": "tbsp"}
        ],
        "allergens": [],
        "may_contain": [],
        "method": "Pressure cook toor dal until soft. Boil drumstick and shallots with tamarind water, tomatoes, turmeric, and sambar powder. Add cooked mashed dal and simmer for 8 minutes. Temper mustard seeds and curry leaves in sesame oil and pour over sambar.",
        "safe_internal_temp": None,
        "version_notes": "Classic South Indian lentil vegetable stew. Naturally vegan, gluten-free, nut-free."
    },
    "recipe_coconut_chutney": {
        "id": "recipe_coconut_chutney",
        "title": "Fresh South Indian Coconut Chutney",
        "version": "reformulated-2025",
        "is_superseded": False,
        "prep_time_minutes": 10,
        "cook_time_minutes": 5,
        "servings": 4,
        "ingredients": [
            {"name": "freshly grated coconut", "quantity": 150, "unit": "g"},
            {"name": "roasted gram (chana dal)", "quantity": 30, "unit": "g"},
            {"name": "green chilies", "quantity": 2, "unit": "pieces"},
            {"name": "fresh ginger", "quantity": 0.5, "unit": "inch"},
            {"name": "mustard seeds and curry leaves", "quantity": 1, "unit": "tsp"},
            {"name": "coconut oil", "quantity": 1, "unit": "tbsp"}
        ],
        "allergens": [],
        "may_contain": [],
        "method": "Blend coconut, roasted gram, chilies, ginger, salt, and minimal water into a smooth paste. Heat coconut oil, crackle mustard seeds, urad dal, and curry leaves. Pour over the chutney.",
        "safe_internal_temp": None,
        "version_notes": "Traditional tiffin accompaniment for idli and dosa. Vegan and nut-free."
    },
    "recipe_steamed_idli": {
        "id": "recipe_steamed_idli",
        "title": "Soft Steamed South Indian Idlis",
        "version": "reformulated-2025",
        "is_superseded": False,
        "prep_time_minutes": 15,
        "cook_time_minutes": 12,
        "servings": 4,
        "ingredients": [
            {"name": "idli rice", "quantity": 300, "unit": "g"},
            {"name": "whole white urad dal", "quantity": 100, "unit": "g"},
            {"name": "fenugreek seeds", "quantity": 0.5, "unit": "tsp"},
            {"name": "rock salt", "quantity": 1, "unit": "tsp"}
        ],
        "allergens": [],
        "may_contain": [],
        "method": "Soak rice and urad dal separately. Grind urad dal until fluffy and light, and rice until fine rava texture. Mix, add salt, and ferment for 8 to 12 hours. Grease idli plates, pour fermented batter, and steam for 10-12 minutes until soft and pillowy.",
        "safe_internal_temp": None,
        "version_notes": "Steamed fermented rice-lentil cakes. Vegan, gluten-free, nut-free."
    }
}

# Synthesize the remaining 594 recipes to complete the 600-recipe CMS library (including the 80 reformulated pairs)
def _build_full_catalog():
    cuisines = ["South Indian", "North Indian", "Italian", "Mexican", "Thai", "French", "British", "Mediterranean"]
    main_items = ["Rice", "Bread", "Soup", "Stew", "Salad", "Pasta", "Roast", "Pudding", "Tart", "Bake"]
    
    idx = 7
    # Build remaining reformulated pairs (up to 80 total reformulated pairs)
    for pair_idx in range(1, 79):
        orig_id = f"recipe_reform_pair_{pair_idx}_orig"
        reform_id = f"recipe_reform_pair_{pair_idx}_reform2025"
        item_name = f"{cuisines[pair_idx % len(cuisines)]} {main_items[pair_idx % len(main_items)]} Spec {pair_idx}"
        
        # Original version
        RECIPE_DATABASE[orig_id] = {
            "id": orig_id,
            "title": item_name,
            "version": "original",
            "is_superseded": True,
            "prep_time_minutes": 15 + (pair_idx % 20),
            "cook_time_minutes": 20 + (pair_idx % 40),
            "servings": 4,
            "ingredients": [
                {"name": "base flour", "quantity": 200, "unit": "g"},
                {"name": "dairy butter", "quantity": 100, "unit": "g"}
            ],
            "allergens": ["dairy", "gluten"],
            "may_contain": [],
            "method": "Combine ingredients and cook according to traditional technique.",
            "safe_internal_temp": None,
            "version_notes": "Pre-2025 original recipe version."
        }
        
        # 2025 Reformulated version
        has_nut_reformulation = (pair_idx % 3 == 0)
        RECIPE_DATABASE[reform_id] = {
            "id": reform_id,
            "title": item_name,
            "version": "reformulated-2025",
            "is_superseded": False,
            "prep_time_minutes": 15 + (pair_idx % 20),
            "cook_time_minutes": 20 + (pair_idx % 40),
            "servings": 4,
            "ingredients": [
                {"name": "base flour", "quantity": 200, "unit": "g"},
                {"name": "plant-nut oil blend" if has_nut_reformulation else "vegetable oil shortening", "quantity": 100, "unit": "g"}
            ],
            "allergens": ["tree nuts", "gluten"] if has_nut_reformulation else ["gluten"],
            "may_contain": ["dairy"],
            "method": "Combine ingredients with 2025 supplier formulation and cook.",
            "safe_internal_temp": None,
            "version_notes": "Reformulated 2025 edition with updated supplier specifications."
        }
        idx += 2

    # Fill remainder to 600 total catalog items
    curr_count = len(RECIPE_DATABASE)
    for fill_idx in range(curr_count + 1, 601):
        rec_id = f"recipe_catalog_{fill_idx}"
        is_chicken = (fill_idx % 5 == 0)
        has_fish = (fill_idx % 7 == 0)
        RECIPE_DATABASE[rec_id] = {
            "id": rec_id,
            "title": f"Test Kitchen {cuisines[fill_idx % len(cuisines)]} Dish #{fill_idx}",
            "version": "reformulated-2025",
            "is_superseded": False,
            "prep_time_minutes": 10 + (fill_idx % 15),
            "cook_time_minutes": 15 + (fill_idx % 35),
            "servings": 2 if fill_idx % 2 == 0 else 4,
            "ingredients": [
                {"name": "chicken thighs" if is_chicken else "lentils", "quantity": 300, "unit": "g"},
                {"name": "spices", "quantity": 2, "unit": "tsp"}
            ],
            "allergens": ["fish"] if has_fish else [],
            "may_contain": ["gluten"] if fill_idx % 4 == 0 else [],
            "method": f"Cook thoroughly on medium heat. {'Ensure chicken reaches 74°C (165°F).' if is_chicken else 'Simmer until tender.'}",
            "safe_internal_temp": "74°C (165°F)" if is_chicken else None,
            "version_notes": "CMS verified standard recipe."
        }

_build_full_catalog()

import difflib

# Retrieval Engine over the 600-Recipe Catalog
def search_recipe_corpus(query: str, version_preference: str = "reformulated-2025") -> List[Dict[str, Any]]:
    """
    RAG retriever over the 600-recipe library.
    Prioritizes matching title and ingredients.
    Always flags version (original vs reformulated-2025).
    Includes fuzzy matching for culinary spelling variants (e.g. biriyani -> biryani, sambhar -> sambar).
    """
    stopwords = {"recipe", "recipes", "query", "ingredient", "ingredients", "dish", "make", "cook", "how", "to", "i", "have", "can", "for", "with", "a", "the", "in", "and", "or", "prepare", "preparation", "give", "me", "show", "tell", "steps", "of", "is", "it"}
    raw_tokens = set(re.findall(r'\w+', query.lower()))
    q_tokens = raw_tokens - stopwords
    if not q_tokens:
        q_tokens = raw_tokens
        
    scored_results = []
    
    for r_id, rec in RECIPE_DATABASE.items():
        title_tokens = set(re.findall(r'\w+', rec["title"].lower()))
        ing_tokens = set(re.findall(r'\w+', " ".join([i["name"] for i in rec["ingredients"]]).lower()))
        
        # Scoring
        score = 0
        score += len(q_tokens.intersection(title_tokens)) * 5
        score += len(q_tokens.intersection(ing_tokens)) * 2

        # Fuzzy match for spelling variants (e.g. biriyani vs biryani)
        for qt in q_tokens:
            if qt not in title_tokens:
                for tt in title_tokens:
                    if len(qt) >= 4 and len(tt) >= 4:
                        if difflib.SequenceMatcher(None, qt, tt).ratio() >= 0.82:
                            score += 4.5
                            break
            
        # Preference boost for requested version
        if rec["version"] == version_preference:
            score += 1.5
            
        if score > 1.5:  # Require at least one token match
            scored_results.append((score, rec))
            
    scored_results.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scored_results[:5]]

def check_allergen_exact_match(recipe_id: str, allergen_to_check: str) -> Dict[str, Any]:
    """
    EXACT-MATCH assertion against structured declaration fields.
    Never infers or guesses from free prose.
    """
    rec = RECIPE_DATABASE.get(recipe_id)
    if not rec:
        return {"error": f"Recipe {recipe_id} not found."}
        
    allergen_norm = allergen_to_check.strip().lower()
    
    # Exact match check
    declared_allergens = [a.lower() for a in rec.get("allergens", [])]
    declared_may_contain = [m.lower() for m in rec.get("may_contain", [])]
    
    # Check tree nuts / nut mapping
    is_declared = False
    is_may_contain = False
    
    target_terms = [allergen_norm]
    if "nut" in allergen_norm:
        target_terms.extend(["tree nuts", "peanuts", "nuts"])
    if "dairy" in allergen_norm:
        target_terms.extend(["dairy", "milk"])
        
    for term in target_terms:
        if any(term in d for d in declared_allergens):
            is_declared = True
        if any(term in m for m in declared_may_contain):
            is_may_contain = True
            
    is_safe = not (is_declared or is_may_contain)
    return {
        "recipe_id": recipe_id,
        "recipe_title": rec["title"],
        "recipe_version": rec["version"],
        "allergen_queried": allergen_to_check,
        "is_safe": is_safe,
        "declared_allergens": rec.get("allergens", []),
        "may_contain": rec.get("may_contain", []),
        "status": "SAFE" if is_safe else ("UNSAFE_DECLARED" if is_declared else "UNSAFE_MAY_CONTAIN")
    }

def scale_recipe_quantities(recipe_id: str, target_servings: int) -> Dict[str, Any]:
    """
    Scales ingredient quantities by serving factor.
    CRITICAL: COOK TIME AND BAKE TIME ARE NEVER SCALED!
    """
    rec = RECIPE_DATABASE.get(recipe_id)
    if not rec:
        return {"error": f"Recipe {recipe_id} not found."}
        
    base_servings = rec["servings"]
    scale_factor = target_servings / base_servings
    
    scaled_ingredients = []
    for ing in rec["ingredients"]:
        scaled_ingredients.append({
            "name": ing["name"],
            "original_quantity": ing["quantity"],
            "scaled_quantity": round(ing["quantity"] * scale_factor, 2),
            "unit": ing["unit"]
        })
        
    return {
        "recipe_id": recipe_id,
        "title": rec["title"],
        "version": rec["version"],
        "base_servings": base_servings,
        "target_servings": target_servings,
        "scale_factor": scale_factor,
        "scaled_ingredients": scaled_ingredients,
        "cook_time_minutes": rec["cook_time_minutes"], # UNCHANGED!
        "prep_time_minutes": rec["prep_time_minutes"],
        "cook_time_note": f"Cook time remains strictly {rec['cook_time_minutes']} minutes (cook time does not scale linearly with batch size)."
    }
