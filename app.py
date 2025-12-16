#!/usr/bin/env python3
from mcp import stdio_client, StdioServerParameters
from strands import Agent
from strands.tools.mcp import MCPClient
import os
import sys
from pathlib import Path
from loguru import logger

# ────────── System Prompt (Not necessary) ──────────
MANIM_SYSTEM_PROMPT = """
You are an expert Manim animation developer. 
CRITICAL LAYOUT RULE: **Prevent text overlap.**

1. **Relative Positioning:** Do not guess absolute coordinates. Instead, position new text relative to previous objects.
   - Use: `text2.next_to(text1, DOWN, buff=0.5)` 
   - Use: `label.next_to(graph, RIGHT)`

2. **Grouping:** When writing multiple lines of text or equations, always group them so they stack automatically:
   - Use: `group = VGroup(line1, line2).arrange(DOWN, center=False, aligned_edge=LEFT)`
"""

def ensure_output_directory():
    """Ensure the output directory exists"""
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

def main():
    try:
        # ────────── Step 0: Ensure output directory exists ────────── 
        ensure_output_directory()
        
        # ────────── Step 1: Get the path to the manim_server.py ──────────
        current_dir = os.path.dirname(os.path.abspath(__file__))
        manim_server_path = os.path.join(current_dir, "src", "manim_server.py")
        os.chdir(current_dir)

        # ────────── Step 2: Connect to the Manim MCP server ──────────
        manim_mcp_client = MCPClient(lambda: stdio_client(
            StdioServerParameters(command="uv", args=["run", manim_server_path])
        ))

        # ────────── Step 3: Check server status ──────────
        logger.debug("Checking MCP server status...")
        try:
            with manim_mcp_client:
                tools = manim_mcp_client.list_tools_sync()
        except Exception as e:
            logger.error("Error: MCP server is not running! Please run `uv run start_mcp_server.py` first.")
            sys.exit(1)

        # ────────── Step 4: Chat loop with Safe-Zone Prompt ──────────
        with manim_mcp_client:
            tools = manim_mcp_client.list_tools_sync()
            
            # Pass the updated system prompt
            agent = Agent(
                tools=tools, 
                system_prompt=MANIM_SYSTEM_PROMPT, # You can silence this line (it is optional)
            )
            logger.debug("Initialization complete!")

            while True:
                try:
                    user_input = input("\nYou: ").strip()
                    if not user_input:
                        continue
                    print("\nAgent: Processing your request...")
                    result = agent(user_input)
                    print("\nAgent:", result)
                except KeyboardInterrupt:
                    logger.info("\nExiting...")
                    break
                except Exception as e:
                    logger.error(f"\nError: {str(e)}")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()