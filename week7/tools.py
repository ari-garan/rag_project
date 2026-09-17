from enum import Enum
import time

class DietProfile(Enum):
    NUT_FREE = "NUT_FREE"
    DAIRY_FREE = "DAIRY_FREE"
    VEGAN = "VEGAN"
    GLUTEN_FREE = "GLUTEN_FREE"

def search_recipe(query: str) -> str:
    """Finds a recipe by name and returns the base ingredients and instructions."""
    time.sleep(0.5) # Simulate API latency
    if "biryani" in query.lower():
        return "Chicken Biryani: 1kg chicken, 2 cups rice, yogurt, ghee."
    elif "cake" in query.lower():
        return "Chocolate Cake: 2 cups flour, 1 cup sugar, 1 cup milk, 2 eggs."
    return f"Generic Recipe for {query}: 1 unit main ingredient, 1 unit spices."

def scale_recipe(recipe: str, servings: int) -> str:
    """Multiplies the recipe ingredients for the requested number of servings."""
    time.sleep(0.2)
    return f"[Scaled for {servings} servings] {recipe}"

def substitute_ingredient(recipe: str, target_diet: DietProfile) -> str:
    """
    Examines a recipe and replaces any ingredients that violate the requested DietProfile.
    Does NOT search for recipes or scale quantities.
    """
    time.sleep(0.8)
    if target_diet == DietProfile.NUT_FREE:
        return recipe.replace("peanut", "sunflower seed").replace("cashew", "pumpkin seed")
    elif target_diet == DietProfile.DAIRY_FREE:
        return recipe.replace("milk", "oat milk").replace("ghee", "oil").replace("yogurt", "coconut yogurt")
    return recipe

