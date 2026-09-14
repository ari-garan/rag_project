import enum

class DietRestriction(enum.Enum):
    NUT_FREE = "nut_free"
    DAIRY_FREE = "dairy_free"
    VEGAN = "vegan"
    NONE = "none"

def search_recipes(query: str) -> str:
    """Finds and retrieves the original recipe instructions."""
    return f"Recipe for {query}: 1 cup peanuts, 2 cups milk, 2 eggs."

def scale_ingredients(recipe_text: str, target_servings: int) -> str:
    """Scales the quantities in the recipe."""
    return f"Scaled {target_servings}x: {recipe_text}"

def get_allergen_substitute(ingredient: str, restriction: str) -> str:
    """Finds a safe culinary substitute for an ingredient based on a specific dietary restriction.
    Returns the substitute name and any secondary allergens it contains."""
    if ingredient == "peanuts" and restriction == DietRestriction.NUT_FREE.value:
        return "almonds (Warning: contains tree nuts)"
    if ingredient == "almonds" and restriction == DietRestriction.NUT_FREE.value:
        return "sunflower seeds (Safe)"
    return f"safe_substitute_for_{ingredient}"
