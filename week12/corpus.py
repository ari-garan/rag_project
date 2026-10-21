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

# Retrieval Engine over the 600-Recipe Catalog
def search_recipe_corpus(query: str, version_preference: str = "reformulated-2025") -> List[Dict[str, Any]]:
    """
    RAG retriever over the 600-recipe library.
    Prioritizes matching title and ingredients.
    Always flags version (original vs reformulated-2025).
    """
    stopwords = {"recipe", "recipes", "query", "ingredient", "ingredients", "dish", "make", "cook", "how", "to", "i", "have", "can", "for", "with", "a", "the", "in", "and", "or"}
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
