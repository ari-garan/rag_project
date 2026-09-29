import asyncio
import json
import sys
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

async def main():
    with open("mcp_config.json") as f:
        config = json.load(f)
    
    servers = config.get("servers", {})
    
    for server_name, server_config in servers.items():
        print(f"Connecting to {server_name}...")
        command = server_config["command"]
        args = server_config.get("args", [])
        
        server_params = StdioServerParameters(command=command, args=args)
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools_response = await session.list_tools()
                print(f"Tools discovered from {server_name}:")
                for tool in tools_response.tools:
                    print(f" - {tool.name}")
                    
                if "get_ingredient_nutrition" in [t.name for t in tools_response.tools]:
                    print("Calling get_ingredient_nutrition for 'apple'...")
                    result = await session.call_tool("get_ingredient_nutrition", arguments={"ingredient": "apple"})
                    print(f"Result: {result.content}")

if __name__ == "__main__":
    asyncio.run(main())
