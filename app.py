#!/usr/bin/env python3
from mcp import stdio_client, StdioServerParameters
from strands import Agent
from strands.tools.mcp import MCPClient
import os
import sys
from pathlib import Path
from loguru import logger

def get_example_animation():
    return """
from manim import *

class SquareToCircle(Scene):
    def construct(self):
        circle = Circle()
        circle.set_fill(BLUE, opacity=0.5)
        circle.set_stroke(BLUE_E, width=4)
        self.play(Create(circle))
        self.wait(2)
"""

def ensure_output_directory():
    """Ensure the output directory exists"""
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

def main():
    try:
        # ────────── Step 0: Ensure output directory exists ────────── 
        ensure_output_directory()
        
        # ────────── Step 1: Get the path to the manim_server.py
        current_dir = os.path.dirname(os.path.abspath(__file__))
        manim_server_path = os.path.join(current_dir, "src", "manim_server.py")
        os.chdir(current_dir)

        # ────────── Step 2: Connect to the Manim MCP server using stdio transport ──────────
        manim_mcp_client = MCPClient(lambda: stdio_client(
            StdioServerParameters(command="uv", args=["run", manim_server_path])
        ))

        # ────────── Step 3: Try to open the context to check if the server is running ──────────
        logger.debug("Checking MCP server status...")
        try:
            with manim_mcp_client:
                tools = manim_mcp_client.list_tools_sync()
        except Exception as e:
            logger.error("Error: MCP server is not running!, please start the server before running this script (`uv run start_mcp_server.py`)")
            sys.exit(1)

        # ────────── Step 4: Now open the context for the actual chat loop ──────────
        with manim_mcp_client:
            tools = manim_mcp_client.list_tools_sync()
            agent = Agent(
                model='eu.anthropic.claude-sonnet-4-20250514-v1:0', 
                tools=tools
            )
            logger.debug("Initialization complete!")

            while True:
                try:
                    user_input = input("\nYou: ").strip()
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