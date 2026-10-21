"""
Week 12 MCP Server: Recipe, Exact-Match Allergen & Food-Safety Capability Server
Exposes live MCP tools consumed by both internal agents and external fresh-eyes clients.
"""

import sys
import json
from fastmcp import FastMCP
from corpus import (
    search_recipe_corpus,
    check_allergen_exact_match,
    scale_recipe_quantities,
    TEST_KITCHEN_SUBSTITUTIONS,
    SAFE_INTERNAL_TEMPERATURES,
    RECIPE_DATABASE
)

# Initialize FastMCP Server
mcp = FastMCP("Pantry-to-Plate Recipe & Safety Server")

@mcp.tool()
def search_recipe_library(query: str, version_preference: str = "reformulated-2025") -> str:
    """
    Search the 600-recipe library for recipes matching pantry ingredients and titles.
    Returns recipe ID, exact version (original vs reformulated-2025), ingredients, and prep/cook times.
    """
    results = search_recipe_corpus(query, version_preference)
    if not results:
        return json.dumps({"error": f"No recipes found matching query '{query}'."})
        
    formatted = []
    for r in results:
        formatted.append({
            "recipe_id": r["id"],
            "title": r["title"],
            "version": r["version"],
            "is_superseded": r.get("is_superseded", False),
            "prep_time": f"{r['prep_time_minutes']} min",
            "cook_time": f"{r['cook_time_minutes']} min",
            "allergens_declared": r.get("allergens", []),
            "may_contain": r.get("may_contain", []),
            "ingredients": [f"{i['quantity']} {i['unit']} {i['name']}" for i in r["ingredients"]],
            "safe_internal_temp": r.get("safe_internal_temp")
        })
    return json.dumps(formatted, indent=2)

@mcp.tool()
def check_allergen_field(recipe_id: str, allergen: str) -> str:
    """
    EXACT-MATCH legal allergen declaration check on structured fields.
    NEVER infers or guesses from free prose.
    Returns SAFE, UNSAFE_DECLARED, or UNSAFE_MAY_CONTAIN.
    """
    res = check_allergen_exact_match(recipe_id, allergen)
    return json.dumps(res, indent=2)

@mcp.tool()
def get_kitchen_substitution(ingredient: str, dietary_restriction: str) -> str:
    """
    Look up verified test-kitchen substitutions for an ingredient under a specific dietary restriction.
    Flags any secondary or newly introduced allergens in the proposed swap.
    """
    ing_clean = ingredient.lower().strip()
    res_clean = dietary_restriction.lower().strip()
    
    match = TEST_KITCHEN_SUBSTITUTIONS.get((ing_clean, res_clean))
    if not match:
        # Fallback check
        for (i, r), data in TEST_KITCHEN_SUBSTITUTIONS.items():
            if i in ing_clean and r in res_clean:
                return json.dumps({
                    "original_ingredient": ingredient,
                    "restriction": dietary_restriction,
                    **data
                }, indent=2)
        return json.dumps({
            "original_ingredient": ingredient,
            "restriction": dietary_restriction,
            "error": "No verified test-kitchen substitution found. Refusing to guess."
        })
        
    return json.dumps({
        "original_ingredient": ingredient,
        "restriction": dietary_restriction,
        **match
    }, indent=2)

@mcp.tool()
def scale_recipe_batch(recipe_id: str, target_servings: int) -> str:
    """
    Scale recipe ingredients accurately by serving count.
    STRICT CONSTRAINT: Cook time and bake time are preserved and NEVER multiplied.
    """
    res = scale_recipe_quantities(recipe_id, target_servings)
    return json.dumps(res, indent=2)

@mcp.tool()
def get_safe_internal_temperature(meat_or_poultry: str) -> str:
    """
    Returns legal food-safety minimum internal temperature standards (e.g. chicken 74°C / 165°F).
    """
    key = meat_or_poultry.lower().strip()
    for item, temp in SAFE_INTERNAL_TEMPERATURES.items():
        if item in key:
            return json.dumps({"food_item": item, "minimum_safe_internal_temp": temp})
    return json.dumps({"error": f"No specific safety temperature registered for '{meat_or_poultry}'."})

if __name__ == "__main__":
    # Standard stdio transport for MCP host discovery
    # Note: Redirect diagnostics to stderr so JSON-RPC on stdout is never corrupted
    print("Starting Pantry-to-Plate Recipe & Safety MCP Server on stdio...", file=sys.stderr)
    mcp.run(transport='stdio')
