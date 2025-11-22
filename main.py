#!/usr/bin/env python3
"""Google Forms MCP Server - Entry Point

Simple and reliable MCP server for Google Forms management.
Optimized for HR managers creating feedback forms.
"""

import asyncio
import logging
from mcp.server import Server
from mcp.server.stdio import stdio_server
from tools import register_tools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("google-forms-mcp")


async def main():
    """Initialize and run the MCP server."""
    logger.info("Starting Google Forms MCP Server...")

    # Create MCP server instance
    server = Server("google-forms-mcp")

    # Register all 15 tools
    register_tools(server)
    logger.info("Registered 15 Google Forms tools")

    # Run server with stdio transport
    async with stdio_server() as (read_stream, write_stream):
        logger.info("Server running on stdio")
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise
