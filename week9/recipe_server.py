from fastmcp import FastMCP

mcp = FastMCP("Recipe Search")

@mcp.tool()
def search_recipe(query: str) -> str:
    """
    Search for a recipe by name. 
    If the recipe is not found, DO NOT apologize. Ask the user if they would like to search for a broader category.
    """
    db = {"thai curry": "Mix ingredients and bake."}
    query_lower = query.lower()
    if query_lower not in db:
        return f"Error: no recipe matched '{query}'. Try searching for a broader term like 'curry'."
    return f"Recipe for {query}: {db[query_lower]}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
