from fastmcp import FastMCP

# Create the MCP server
mcp = FastMCP("Ingredient Database")

# Tool 1: Nutrition
@mcp.tool()
def get_ingredient_nutrition(ingredient: str) -> str:
    """Get basic nutrition information for a food ingredient."""
    database = {
        "apple": "52 kcal, 0.3g protein, 14g carbs",
        "chicken": "165 kcal, 31g protein, 0g carbs",
        "flour": "364 kcal, 10g protein, 76g carbs"
    }
    return database.get(ingredient.lower(), f"Nutrition data for {ingredient} not found.")

# Tool 2: Allergens (We add this to prove we don't have to touch the agent code)
@mcp.tool()
def check_ingredient_allergen(ingredient: str) -> str:
    """Check if an ingredient is a top-8 common allergen."""
    allergens = ["peanuts", "milk", "soy", "wheat", "eggs", "tree nuts", "fish", "shellfish"]
    if ingredient.lower() in allergens:
        return f"WARNING: {ingredient} is a major allergen!"
    return f"{ingredient} is not in the major allergen list."

if __name__ == "__main__":
    # Start the server using stdio transport (standard for local MCP)
    print("Starting Ingredient Database MCP Server on stdio...")
    mcp.run(transport='stdio')
