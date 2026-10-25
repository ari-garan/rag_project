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
    },
    "recipe_egg_rice": {
        "id": "recipe_egg_rice",
        "title": "South Indian Style Egg Rice (Muttai Sadam)",
        "version": "reformulated-2025",
        "is_superseded": False,
        "prep_time_minutes": 10,
        "cook_time_minutes": 15,
        "servings": 4,
        "ingredients": [
            {"name": "cooked cooled rice", "quantity": 400, "unit": "g"},
            {"name": "whole eggs beaten", "quantity": 4, "unit": "large"},
            {"name": "sliced red onions", "quantity": 2, "unit": "medium"},
            {"name": "green chilies and curry leaves", "quantity": 1, "unit": "tbsp"},
            {"name": "crushed black pepper", "quantity": 1.5, "unit": "tsp"},
            {"name": "fennel seeds (saunf)", "quantity": 0.5, "unit": "tsp"},
            {"name": "turmeric and chili powder", "quantity": 1, "unit": "tsp"},
            {"name": "sesame or sunflower oil", "quantity": 2, "unit": "tbsp"}
        ],
        "allergens": ["eggs"],
        "may_contain": [],
        "method": "Heat oil in wok, splutter fennel seeds. Sauté onions, chilies, and curry leaves until golden. Pour in beaten eggs and scramble on medium-high until cooked through and firm. Add salt, turmeric, and black pepper. Toss in cooked cooled rice and stir-fry on high heat for 3 minutes. Nut-free.",
        "safe_internal_temp": "71°C (160°F)",
        "version_notes": "Street-style South Indian fast-food egg rice (muttai sadam). Nut-free, contains eggs."
    },
    "recipe_egg_kurma": {
        "id": "recipe_egg_kurma",
        "title": "South Indian Egg Kurma (Muttai Salna)",
        "version": "reformulated-2025",
        "is_superseded": False,
        "prep_time_minutes": 15,
        "cook_time_minutes": 25,
        "servings": 4,
        "ingredients": [
            {"name": "hard boiled eggs (pricked)", "quantity": 4, "unit": "large"},
            {"name": "ground coconut and poppy seed paste", "quantity": 0.5, "unit": "cup"},
            {"name": "onions and tomatoes", "quantity": 2, "unit": "chopped"},
            {"name": "ginger garlic paste", "quantity": 1, "unit": "tbsp"},
            {"name": "kurma spice powder (coriander, chili, garam masala)", "quantity": 2, "unit": "tbsp"},
            {"name": "fennel seeds, cinnamon, cloves", "quantity": 1, "unit": "tsp"},
            {"name": "cooking oil", "quantity": 2, "unit": "tbsp"}
        ],
        "allergens": ["eggs"],
        "may_contain": [],
        "method": "Shallow fry boiled eggs with turmeric until skin blisters. In same pan, fry whole spices, onions, and ginger-garlic paste. Add tomatoes and kurma spices. Pour in ground coconut paste and simmer for 10 minutes until oil floats on top. Add fried eggs and simmer for 5 minutes.",
        "safe_internal_temp": None,
        "version_notes": "Aromatic hotel-style salna / kurma for parotta, dosa, or rice. Contains eggs."
    },
    "recipe_pulihora": {
        "id": "recipe_pulihora",
        "title": "Andhra Pulihora (Traditional Tamarind Rice)",
        "version": "reformulated-2025",
        "is_superseded": False,
        "prep_time_minutes": 15,
        "cook_time_minutes": 20,
        "servings": 4,
        "ingredients": [
            {"name": "cooked cooled sona masoori rice", "quantity": 400, "unit": "g"},
            {"name": "thick tamarind pulp", "quantity": 3, "unit": "tbsp"},
            {"name": "roasted peanuts", "quantity": 3, "unit": "tbsp"},
            {"name": "mustard seeds, chana dal, urad dal", "quantity": 1.5, "unit": "tbsp"},
            {"name": "slit green chilies and dried red chilies", "quantity": 4, "unit": "pieces"},
            {"name": "turmeric and asafoetida (hing)", "quantity": 1, "unit": "tsp"},
            {"name": "sesame oil", "quantity": 3, "unit": "tbsp"}
        ],
        "allergens": ["peanuts"],
        "may_contain": [],
        "method": "Simmer tamarind extract with turmeric, green chilies, and salt until thick paste (pulikachal). Heat sesame oil, crackle mustard, chana dal, urad dal, peanuts, and red chilies. Fold tamarind paste and tempering into cooled rice gently. Contains peanuts.",
        "safe_internal_temp": None,
        "version_notes": "Traditional temple-style tangy tamarind rice. Contains peanuts."
    },
    "recipe_coconut_rice": {
        "id": "recipe_coconut_rice",
        "title": "Fragrant South Indian Coconut Rice (Thengai Sadam)",
        "version": "reformulated-2025",
        "is_superseded": False,
        "prep_time_minutes": 10,
        "cook_time_minutes": 15,
        "servings": 4,
        "ingredients": [
            {"name": "cooked cooled rice", "quantity": 400, "unit": "g"},
            {"name": "freshly grated coconut", "quantity": 150, "unit": "g"},
            {"name": "cashews (halved)", "quantity": 2, "unit": "tbsp"},
            {"name": "mustard seeds and urad dal", "quantity": 1, "unit": "tbsp"},
            {"name": "green chilies and ginger", "quantity": 1, "unit": "tbsp"},
            {"name": "pure coconut oil", "quantity": 2, "unit": "tbsp"}
        ],
        "allergens": ["tree nuts"],
        "may_contain": [],
        "method": "Heat virgin coconut oil in a pan. Fry mustard seeds, urad dal, and cashews until golden brown. Add chopped ginger, green chilies, and curry leaves. Add grated coconut and sauté on low heat for 2 minutes without browning. Fold into cooled cooked rice with salt.",
        "safe_internal_temp": None,
        "version_notes": "Traditional festive rice dish. Contains cashews (tree nuts)."
    },
    "recipe_ghee_rice": {
        "id": "recipe_ghee_rice",
        "title": "Malabar Fragrant Ghee Rice (Nei Choru)",
        "version": "reformulated-2025",
        "is_superseded": False,
        "prep_time_minutes": 15,
        "cook_time_minutes": 25,
        "servings": 4,
        "ingredients": [
            {"name": "jeerakasala or kaima rice", "quantity": 300, "unit": "g"},
            {"name": "pure dairy ghee", "quantity": 4, "unit": "tbsp"},
            {"name": "thinly sliced onions (crispy fried birista)", "quantity": 2, "unit": "medium"},
            {"name": "whole spices (cardamom, cloves, cinnamon, bay leaf)", "quantity": 1, "unit": "tbsp"},
            {"name": "cashews and raisins", "quantity": 2, "unit": "tbsp"},
            {"name": "water", "quantity": 600, "unit": "ml"}
        ],
        "allergens": ["dairy", "tree nuts"],
        "may_contain": [],
        "method": "Heat ghee, fry cashews, raisins, and half the onions until crisp and golden brown; set aside for garnish. In remaining ghee, sauté whole spices and drained rice for 3 minutes until aromatic. Pour boiling salted water, cover tightly, and cook on low heat for 10 minutes until water is absorbed.",
        "safe_internal_temp": None,
        "version_notes": "Iconic Malabar celebration rice dish. Contains dairy and tree nuts."
    },
    "recipe_vangi_bath": {
        "id": "recipe_vangi_bath",
        "title": "Karnataka Vangi Bath (Spiced Brinjal Rice)",
        "version": "reformulated-2025",
        "is_superseded": False,
        "prep_time_minutes": 15,
        "cook_time_minutes": 20,
        "servings": 4,
        "ingredients": [
            {"name": "cooked sona masoori rice", "quantity": 400, "unit": "g"},
            {"name": "slender eggplants (brinjal) sliced lengthwise", "quantity": 250, "unit": "g"},
            {"name": "freshly roasted vangi bath powder", "quantity": 2.5, "unit": "tbsp"},
            {"name": "tamarind pulp", "quantity": 1, "unit": "tbsp"},
            {"name": "mustard seeds and curry leaves", "quantity": 1, "unit": "tsp"},
            {"name": "peanut oil", "quantity": 2, "unit": "tbsp"}
        ],
        "allergens": ["peanuts"],
        "may_contain": [],
        "method": "Heat oil, crackle mustard and curry leaves. Sauté eggplant wedges until tender and browned. Add tamarind pulp, turmeric, salt, and vangi bath masala powder. Cook for 5 minutes into thick masala. Gently fold cooked rice into eggplant masala until evenly coated.",
        "safe_internal_temp": None,
        "version_notes": "Classic Mysore and Karnataka eggplant spiced rice. Contains peanut oil."
    },
    "recipe_ven_pongal": {
        "id": "recipe_ven_pongal",
        "title": "Classic South Indian Ven Pongal (Khara Pongal)",
        "version": "reformulated-2025",
        "is_superseded": False,
        "prep_time_minutes": 10,
        "cook_time_minutes": 20,
        "servings": 4,
        "ingredients": [
            {"name": "raw rice", "quantity": 200, "unit": "g"},
            {"name": "yellow split moong dal", "quantity": 75, "unit": "g"},
            {"name": "dairy ghee", "quantity": 3, "unit": "tbsp"},
            {"name": "whole black peppercorns and cumin seeds", "quantity": 2, "unit": "tsp"},
            {"name": "finely chopped ginger", "quantity": 1, "unit": "tbsp"},
            {"name": "cashews", "quantity": 2, "unit": "tbsp"},
            {"name": "asafoetida (hing) and curry leaves", "quantity": 1, "unit": "tsp"}
        ],
        "allergens": ["dairy", "tree nuts"],
        "may_contain": [],
        "method": "Dry roast moong dal until fragrant. Pressure cook rice and dal with 4 cups water and salt until very soft and mushy. Heat ghee in small kadai, fry cashews, pepper, cumin, ginger, hing, and curry leaves. Pour sizzling tadka over hot pongal and mix thoroughly.",
        "safe_internal_temp": None,
        "version_notes": "Traditional savory tiffin breakfast. Contains dairy and cashews."
    },
    "recipe_appam": {
        "id": "recipe_appam",
        "title": "Kerala Soft Appam (Lacy Fermented Rice Pancakes)",
        "version": "reformulated-2025",
        "is_superseded": False,
        "prep_time_minutes": 20,
        "cook_time_minutes": 15,
        "servings": 4,
        "ingredients": [
            {"name": "raw rice soaked", "quantity": 300, "unit": "g"},
            {"name": "fresh coconut milk", "quantity": 200, "unit": "ml"},
            {"name": "cooked rice", "quantity": 50, "unit": "g"},
            {"name": "active dry yeast", "quantity": 0.5, "unit": "tsp"},
            {"name": "sugar and salt", "quantity": 1, "unit": "tbsp"}
        ],
        "allergens": [],
        "may_contain": [],
        "method": "Grind soaked rice and cooked rice with coconut milk into smooth batter. Dissolve yeast and sugar in warm water, add to batter. Ferment for 6 to 8 hours until bubbly. Swirl a ladleful in hot nonstick appachatti pan, cover, and steam until edges are crispy and lacy with a fluffy soft center. Nut-free, dairy-free, vegan.",
        "safe_internal_temp": None,
        "version_notes": "Naturally vegan, gluten-free, nut-free."
    },
    "recipe_fish_pulusu": {
        "id": "recipe_fish_pulusu",
        "title": "Andhra Chepala Pulusu (Fish Curry)",
        "version": "reformulated-2025",
        "is_superseded": False,
        "prep_time_minutes": 20,
        "cook_time_minutes": 25,
        "servings": 4,
        "ingredients": [
            {"name": "firm fish steaks (such as rohu or tilapia)", "quantity": 500, "unit": "g"},
            {"name": "tamarind pulp", "quantity": 3, "unit": "tbsp"},
            {"name": "shallots and green chilies", "quantity": 100, "unit": "g"},
            {"name": "roasted fenugreek and cumin powder", "quantity": 1, "unit": "tsp"},
            {"name": "red chili powder and coriander powder", "quantity": 2, "unit": "tbsp"},
            {"name": "sesame oil", "quantity": 3, "unit": "tbsp"}
        ],
        "allergens": ["fish"],
        "may_contain": [],
        "method": "Sauté shallots, garlic, and green chilies in sesame oil. Add chili and coriander powder with tamarind water. Bring to a boil. Gently slide in fish pieces. Simmer on low heat for 12 minutes until fish is cooked through and registers internal temperature of 63°C (145°F). Finish with roasted methi powder.",
        "safe_internal_temp": "63°C (145°F)",
        "version_notes": "Authentic spicy tamarind Andhra fish curry. Enforces 63°C fish safety rule."
    },
    "recipe_classic_beef_burger": {
        "id": "recipe_classic_beef_burger",
        "title": "Classic Test Kitchen Smash Burger",
        "version": "reformulated-2025",
        "is_superseded": False,
        "prep_time_minutes": 15,
        "cook_time_minutes": 10,
        "servings": 4,
        "ingredients": [
            {"name": "ground beef patties (80/20 blend)", "quantity": 600, "unit": "g"},
            {"name": "brioche burger buns", "quantity": 4, "unit": "whole"},
            {"name": "cheddar cheese slices", "quantity": 4, "unit": "slices"},
            {"name": "crisp lettuce and tomato slices", "quantity": 4, "unit": "leaves"},
            {"name": "burger sauce (mayo, relish, mustard)", "quantity": 4, "unit": "tbsp"},
            {"name": "salt and coarse black pepper", "quantity": 1, "unit": "tsp"},
            {"name": "butter for toasting buns", "quantity": 1, "unit": "tbsp"}
        ],
        "allergens": ["gluten", "dairy", "eggs"],
        "may_contain": [],
        "method": "Divide ground beef into four 150g balls. Heat cast iron skillet until smoking hot. Smash patties thin with heavy spatula, season with salt and pepper. Sear for 2.5 minutes until deep crust forms, flip, add cheese, and cook until internal temperature registers 71°C (160°F) for ground meat safety. Toast buns in butter, spread sauce, assemble with lettuce, tomato, and patty.",
        "safe_internal_temp": "71°C (160°F)",
        "version_notes": "Test kitchen double-crust smash burger. Enforces 71°C ground meat food safety."
    },
    "recipe_crispy_chicken_burger": {
        "id": "recipe_crispy_chicken_burger",
        "title": "Crispy Buttermilk Chicken Burger",
        "version": "reformulated-2025",
        "is_superseded": False,
        "prep_time_minutes": 20,
        "cook_time_minutes": 15,
        "servings": 4,
        "ingredients": [
            {"name": "boneless chicken thighs", "quantity": 500, "unit": "g"},
            {"name": "buttermilk marinade", "quantity": 200, "unit": "ml"},
            {"name": "seasoned flour coating", "quantity": 150, "unit": "g"},
            {"name": "brioche burger buns", "quantity": 4, "unit": "whole"},
            {"name": "spicy mayo and dill pickles", "quantity": 4, "unit": "tbsp"},
            {"name": "frying oil", "quantity": 500, "unit": "ml"}
        ],
        "allergens": ["gluten", "dairy"],
        "may_contain": [],
        "method": "Marinate chicken in spiced buttermilk. Dredge in seasoned flour, pressing for flaky crust. Deep-fry at 175°C (350°F) for 6-8 minutes until golden brown and internal temperature reaches 74°C (165°F) for poultry food safety. Serve on toasted brioche buns with spicy mayo and pickles.",
        "safe_internal_temp": "74°C (165°F)",
        "version_notes": "Enforces 74°C poultry safe internal temperature rule."
    },
    "recipe_veggie_burger": {
        "id": "recipe_veggie_burger",
        "title": "Smoky Black Bean and Quinoa Veggie Burger",
        "version": "reformulated-2025",
        "is_superseded": False,
        "prep_time_minutes": 20,
        "cook_time_minutes": 15,
        "servings": 4,
        "ingredients": [
            {"name": "cooked black beans mashed", "quantity": 300, "unit": "g"},
            {"name": "cooked quinoa", "quantity": 150, "unit": "g"},
            {"name": "smoked paprika and ground cumin", "quantity": 1.5, "unit": "tsp"},
            {"name": "whole grain burger buns", "quantity": 4, "unit": "whole"},
            {"name": "avocado slices and red onion", "quantity": 1, "unit": "medium"},
            {"name": "olive oil", "quantity": 2, "unit": "tbsp"}
        ],
        "allergens": ["gluten"],
        "may_contain": [],
        "method": "Mix mashed black beans with cooked quinoa, smoked paprika, cumin, and sea salt. Form into 4 firm patties. Pan-sear in olive oil for 4-5 minutes per side until crisp exterior forms. Assemble on toasted whole grain buns with sliced avocado and red onion. Vegan, nut-free, dairy-free.",
        "safe_internal_temp": None,
        "version_notes": "Nut-free, vegan plant-based burger."
    },
    "recipe_margherita_pizza": {
        "id": "recipe_margherita_pizza",
        "title": "Classic Margherita Pizza",
        "version": "reformulated-2025",
        "is_superseded": False,
        "prep_time_minutes": 20,
        "cook_time_minutes": 12,
        "servings": 4,
        "ingredients": [
            {"name": "fermented pizza dough", "quantity": 400, "unit": "g"},
            {"name": "crushed San Marzano tomatoes", "quantity": 150, "unit": "g"},
            {"name": "fresh mozzarella cheese", "quantity": 200, "unit": "g"},
            {"name": "fresh basil leaves", "quantity": 10, "unit": "leaves"},
            {"name": "extra virgin olive oil", "quantity": 1, "unit": "tbsp"}
        ],
        "allergens": ["gluten", "dairy"],
        "may_contain": [],
        "method": "Stretch pizza dough into 12-inch round. Spread crushed tomatoes, scatter fresh mozzarella cubes, and drizzle extra virgin olive oil. Bake at 250°C (485°F) on preheated pizza stone for 8-10 minutes until crust is blistered and cheese bubbles. Top with fresh basil leaves.",
        "safe_internal_temp": None,
        "version_notes": "Artisan wood-fired style pizza. Contains gluten and dairy."
    },
    "recipe_creamy_pasta": {
        "id": "recipe_creamy_pasta",
        "title": "Creamy Garlic Parmesan Penne Pasta",
        "version": "reformulated-2025",
        "is_superseded": False,
        "prep_time_minutes": 10,
        "cook_time_minutes": 15,
        "servings": 4,
        "ingredients": [
            {"name": "penne pasta", "quantity": 350, "unit": "g"},
            {"name": "heavy cooking cream", "quantity": 200, "unit": "ml"},
            {"name": "grated parmesan cheese", "quantity": 80, "unit": "g"},
            {"name": "minced garlic", "quantity": 4, "unit": "cloves"},
            {"name": "butter and olive oil", "quantity": 2, "unit": "tbsp"},
            {"name": "fresh parsley and black pepper", "quantity": 1, "unit": "tbsp"}
        ],
        "allergens": ["gluten", "dairy"],
        "may_contain": [],
        "method": "Boil penne in salted water until al dente. In a skillet, gently sauté minced garlic in butter and olive oil until fragrant. Pour in heavy cream and simmer for 3 minutes. Stir in grated parmesan until melted into silky sauce. Toss hot pasta in sauce with cracked black pepper and fresh parsley.",
        "safe_internal_temp": None,
        "version_notes": "Classic Italian-American skillet pasta. Nut-free, contains gluten and dairy."
    },
    "recipe_hakka_veg_noodles": {
        "id": "recipe_hakka_veg_noodles",
        "title": "Street Style Veg Hakka Noodles",
        "version": "reformulated-2025",
        "is_superseded": False,
        "prep_time_minutes": 15,
        "cook_time_minutes": 10,
        "servings": 4,
        "ingredients": [
            {"name": "hakka noodles (boiled al dente)", "quantity": 400, "unit": "g"},
            {"name": "shredded cabbage and carrots", "quantity": 200, "unit": "g"},
            {"name": "sliced bell peppers (capsicum)", "quantity": 1, "unit": "cup"},
            {"name": "dark soy sauce and green chili sauce", "quantity": 2, "unit": "tbsp"},
            {"name": "rice vinegar or white vinegar", "quantity": 1, "unit": "tsp"},
            {"name": "minced garlic and spring onions", "quantity": 2, "unit": "tbsp"},
            {"name": "toasted sesame oil or vegetable oil", "quantity": 2, "unit": "tbsp"}
        ],
        "allergens": ["gluten", "soy"],
        "may_contain": [],
        "method": "Boil noodles until al dente, drain, rinse with cold water, and toss with 1 tsp oil. Heat wok on highest flame until smoking. Add oil, minced garlic, and flash-fry shredded vegetables for 2 minutes keeping them crunchy. Add noodles, soy sauce, green chili sauce, vinegar, and white pepper. Toss vigorously on high heat for 2 minutes. Garnish with spring onion greens. Nut-free.",
        "safe_internal_temp": None,
        "version_notes": "Street-style Indo-Chinese stir-fried noodles. Nut-free, contains gluten and soy."
    },
    "recipe_chicken_noodles": {
        "id": "recipe_chicken_noodles",
        "title": "Wok Tossed Chicken Hakka Noodles",
        "version": "reformulated-2025",
        "is_superseded": False,
        "prep_time_minutes": 15,
        "cook_time_minutes": 15,
        "servings": 4,
        "ingredients": [
            {"name": "egg noodles or hakka noodles (boiled)", "quantity": 400, "unit": "g"},
            {"name": "thinly sliced chicken breast", "quantity": 300, "unit": "g"},
            {"name": "julienned vegetables (cabbage, carrot, onion)", "quantity": 150, "unit": "g"},
            {"name": "soy sauce, red chili sauce, oyster sauce", "quantity": 2.5, "unit": "tbsp"},
            {"name": "garlic and ginger minced", "quantity": 1.5, "unit": "tbsp"},
            {"name": "cooking oil", "quantity": 2, "unit": "tbsp"}
        ],
        "allergens": ["gluten", "soy", "eggs"],
        "may_contain": [],
        "method": "Stir-fry chicken strips on high heat in wok until fully cooked and internal temperature reaches 74°C (165°F). Push chicken to side, flash-fry ginger, garlic, and julienned vegetables for 1 minute. Add boiled noodles and sauce blend. Toss rapidly on high heat until noodles are glossy and smoky.",
        "safe_internal_temp": "74°C (165°F)",
        "version_notes": "Enforces 74°C poultry safe internal temperature rule. Contains gluten, soy, eggs."
    },
    "recipe_ramen_noodles": {
        "id": "recipe_ramen_noodles",
        "title": "Savory Miso Sesame Broth Ramen Noodles",
        "version": "reformulated-2025",
        "is_superseded": False,
        "prep_time_minutes": 15,
        "cook_time_minutes": 15,
        "servings": 4,
        "ingredients": [
            {"name": "fresh or dried ramen noodles", "quantity": 400, "unit": "g"},
            {"name": "rich vegetable or chicken broth", "quantity": 1000, "unit": "ml"},
            {"name": "red miso paste", "quantity": 3, "unit": "tbsp"},
            {"name": "toasted sesame oil and chili oil", "quantity": 1, "unit": "tbsp"},
            {"name": "ramen eggs (ajitsuke tamago)", "quantity": 2, "unit": "whole"},
            {"name": "sliced scallions and nori sheets", "quantity": 2, "unit": "tbsp"}
        ],
        "allergens": ["gluten", "soy", "eggs", "sesame"],
        "may_contain": [],
        "method": "Whisk miso paste with hot broth until fully dissolved and smooth. Boil ramen noodles separately for 2.5 minutes until springy; drain immediately. Divide noodles into deep bowls, ladle steaming hot miso broth over. Top with halved ramen eggs, toasted sesame oil, scallions, and nori sheets.",
        "safe_internal_temp": None,
        "version_notes": "Authentic comforting Japanese noodle soup. Contains gluten, soy, eggs, sesame."
    },
    "recipe_vegetable_fried_rice": {
        "id": "recipe_vegetable_fried_rice",
        "title": "Classic Indo-Chinese Vegetable Fried Rice",
        "version": "reformulated-2025",
        "is_superseded": False,
        "prep_time_minutes": 15,
        "cook_time_minutes": 10,
        "servings": 4,
        "ingredients": [
            {"name": "cooked cooled long-grain or basmati rice", "quantity": 500, "unit": "g"},
            {"name": "finely chopped carrots, beans, and cabbage", "quantity": 200, "unit": "g"},
            {"name": "minced garlic and celery", "quantity": 2, "unit": "tbsp"},
            {"name": "light soy sauce and vinegar", "quantity": 1.5, "unit": "tbsp"},
            {"name": "crushed white pepper and salt", "quantity": 1, "unit": "tsp"},
            {"name": "sesame oil", "quantity": 2, "unit": "tbsp"}
        ],
        "allergens": ["soy", "gluten"],
        "may_contain": [],
        "method": "Heat wok on high until smoking. Swirl sesame oil, sizzle minced garlic and celery. Add diced vegetables and stir-fry on intense heat for 2 minutes. Fold in cold cooked rice, soy sauce, vinegar, and white pepper. Toss on high flame continuously for 3 minutes without breaking rice grains. Garnish with spring onions.",
        "safe_internal_temp": None,
        "version_notes": "Smoky restaurant-style veg fried rice. Nut-free, contains soy and gluten."
    },
    "recipe_grilled_cheese_sandwich": {
        "id": "recipe_grilled_cheese_sandwich",
        "title": "Golden Toasted Cheddar Grilled Cheese Sandwich",
        "version": "reformulated-2025",
        "is_superseded": False,
        "prep_time_minutes": 5,
        "cook_time_minutes": 8,
        "servings": 4,
        "ingredients": [
            {"name": "thick sourdough or country bread slices", "quantity": 8, "unit": "slices"},
            {"name": "sharp cheddar and gruyere cheese slices", "quantity": 250, "unit": "g"},
            {"name": "dairy butter softened", "quantity": 4, "unit": "tbsp"},
            {"name": "dijon mustard (optional)", "quantity": 1, "unit": "tsp"}
        ],
        "allergens": ["gluten", "dairy"],
        "may_contain": [],
        "method": "Spread softened butter evenly on outside of bread slices. Layer cheese generously between unbuttered sides. Heat cast iron skillet over medium-low heat. Toast sandwiches for 3-4 minutes per side until bread is golden-brown and crispy, and cheese is completely melted and gooey.",
        "safe_internal_temp": None,
        "version_notes": "Comfort food classic sandwich. Nut-free, contains gluten and dairy."
    },
    "recipe_crispy_vegetable_samosa": {
        "id": "recipe_crispy_vegetable_samosa",
        "title": "Crispy Punjabi Potato and Green Pea Samosa",
        "version": "reformulated-2025",
        "is_superseded": False,
        "prep_time_minutes": 25,
        "cook_time_minutes": 20,
        "servings": 4,
        "ingredients": [
            {"name": "all-purpose flour pastry dough with ajwain", "quantity": 250, "unit": "g"},
            {"name": "boiled spiced potatoes mashed", "quantity": 400, "unit": "g"},
            {"name": "green peas", "quantity": 100, "unit": "g"},
            {"name": "roasted cumin, coriander, and amchur powder", "quantity": 2, "unit": "tbsp"},
            {"name": "green chilies and ginger", "quantity": 1, "unit": "tbsp"},
            {"name": "oil for deep frying", "quantity": 500, "unit": "ml"}
        ],
        "allergens": ["gluten"],
        "may_contain": [],
        "method": "Roll pastry dough into ovals, cut in half, form cones, and fill with spiced potato-pea mixture. Seal edges tightly with water. Deep fry in medium-hot oil (160°C) for 12-15 minutes until pastry is blister-free, golden, and shatteringly crisp.",
        "safe_internal_temp": None,
        "version_notes": "Traditional Punjabi triangular samosas. Vegan, nut-free, contains gluten."
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
    generic_staples = {"rice", "curry", "dish", "soup", "roast", "bread", "fry", "batter", "style"}
    raw_tokens = set(re.findall(r'\w+', query.lower()))
    q_tokens = raw_tokens - stopwords
    if not q_tokens:
        q_tokens = raw_tokens
        
    distinctive_tokens = q_tokens - generic_staples
    scored_results = []
    
    for r_id, rec in RECIPE_DATABASE.items():
        title_tokens = set(re.findall(r'\w+', rec["title"].lower()))
        ing_tokens = set(re.findall(r'\w+', " ".join([i["name"] for i in rec["ingredients"]]).lower()))
        all_recipe_tokens = title_tokens | ing_tokens
        
        # Guard: If query specifies distinctive ingredients (e.g. 'egg', 'curd', 'lemon', 'fish', 'noodel'),
        # do not match a candidate that lacks those distinctive tokens (fuzzy match supported for typos like noodel -> noodles)
        if distinctive_tokens:
            has_distinctive = False
            for dt in distinctive_tokens:
                dt_stem = dt[:-1] if dt.endswith('s') else dt
                if dt in all_recipe_tokens:
                    has_distinctive = True
                    break
                for rt in all_recipe_tokens:
                    rt_stem = rt[:-1] if rt.endswith('s') else rt
                    if len(dt) >= 4 and len(rt) >= 4:
                        if max(difflib.SequenceMatcher(None, dt, rt).ratio(), difflib.SequenceMatcher(None, dt_stem, rt_stem).ratio()) >= 0.75:
                            has_distinctive = True
                            break
                if has_distinctive:
                    break
            if not has_distinctive:
                continue

        matched_title = q_tokens.intersection(title_tokens)
        matched_ing = q_tokens.intersection(ing_tokens)
        
        # Scoring
        score = 0
        score += len(matched_title) * 6
        score += len(matched_ing) * 2

        # Exact multi-token match bonus for title
        if len(matched_title) == len(q_tokens) and len(q_tokens) > 1:
            score += 15.0

        # Fuzzy match for spelling variants (e.g. biriyani vs biryani, noodel vs noodles)
        for qt in q_tokens:
            if qt not in title_tokens:
                qt_stem = qt[:-1] if qt.endswith('s') else qt
                for tt in title_tokens:
                    tt_stem = tt[:-1] if tt.endswith('s') else tt
                    if len(qt) >= 4 and len(tt) >= 4:
                        ratio = max(
                            difflib.SequenceMatcher(None, qt, tt).ratio(),
                            difflib.SequenceMatcher(None, qt_stem, tt_stem).ratio()
                        )
                        if ratio >= 0.75:
                            score += 5.0
                            break
            
        # Preference boost for requested version
        if rec["version"] == version_preference:
            score += 1.5
            
        if score > 2.0:  # Require at least one token match
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
