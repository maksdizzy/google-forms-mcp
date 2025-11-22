#!/usr/bin/env python3
"""MCP tools implementation for Google Forms server.

Provides 15 tools for comprehensive form management, questions, responses, and utilities.
"""

import json
from typing import Any, Dict
from mcp.server import Server
from mcp.types import Tool, TextContent
from forms_api import FormsAPI


# Initialize Forms API client
api = FormsAPI()


def register_tools(server: Server):
    """Register all 15 MCP tools with the server."""

    # ==================== FORM MANAGEMENT TOOLS (5) ====================

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List all available tools."""
        return [
            Tool(
                name="forms_create",
                description="Create a new Google Form (automatically published)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Form title"},
                        "description": {"type": "string", "description": "Form description (optional)"}
                    },
                    "required": ["title"]
                }
            ),
            Tool(
                name="forms_list",
                description="List all forms owned by the user",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "pageSize": {"type": "integer", "description": "Maximum forms to return (default 50)", "default": 50},
                        "pageToken": {"type": "string", "description": "Pagination token (optional)"}
                    }
                }
            ),
            Tool(
                name="forms_get",
                description="Get complete details of a specific form",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "formId": {"type": "string", "description": "The form ID"}
                    },
                    "required": ["formId"]
                }
            ),
            Tool(
                name="forms_update",
                description="Update form title and/or description",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "formId": {"type": "string", "description": "The form ID"},
                        "title": {"type": "string", "description": "New title (optional)"},
                        "description": {"type": "string", "description": "New description (optional)"}
                    },
                    "required": ["formId"]
                }
            ),
            Tool(
                name="forms_delete",
                description="Delete a form permanently",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "formId": {"type": "string", "description": "The form ID"},
                        "confirm": {"type": "boolean", "description": "Must be true to confirm deletion"}
                    },
                    "required": ["formId", "confirm"]
                }
            ),

            # ==================== QUESTION MANAGEMENT TOOLS (4) ====================

            Tool(
                name="questions_add",
                description="Add a question to a form (supports all 12 question types)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "formId": {"type": "string", "description": "The form ID"},
                        "type": {
                            "type": "string",
                            "description": "Question type",
                            "enum": [
                                "SHORT_ANSWER", "PARAGRAPH", "MULTIPLE_CHOICE", "CHECKBOXES",
                                "DROPDOWN", "LINEAR_SCALE", "DATE", "TIME", "FILE_UPLOAD",
                                "MULTIPLE_CHOICE_GRID", "CHECKBOX_GRID", "RATING"
                            ]
                        },
                        "title": {"type": "string", "description": "Question text"},
                        "required": {"type": "boolean", "description": "Is response required (default false)", "default": False},
                        "position": {"type": "integer", "description": "Position index (default 0)", "default": 0},
                        "options": {"type": "array", "items": {"type": "string"}, "description": "Options for choice questions"},
                        "low": {"type": "integer", "description": "Low value for scale questions"},
                        "high": {"type": "integer", "description": "High value for scale questions"},
                        "lowLabel": {"type": "string", "description": "Label for low value"},
                        "highLabel": {"type": "string", "description": "Label for high value"},
                        "folderId": {"type": "string", "description": "Drive folder ID for file uploads"},
                        "maxFiles": {"type": "integer", "description": "Max files for upload questions"},
                        "maxFileSize": {"type": "integer", "description": "Max file size in bytes"},
                        "allowedTypes": {"type": "array", "items": {"type": "string"}, "description": "Allowed MIME types"},
                        "rows": {"type": "array", "items": {"type": "string"}, "description": "Row labels for grid questions"},
                        "columns": {"type": "array", "items": {"type": "string"}, "description": "Column labels for grid questions"}
                    },
                    "required": ["formId", "type", "title"]
                }
            ),
            Tool(
                name="questions_update",
                description="Update an existing question",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "formId": {"type": "string", "description": "The form ID"},
                        "itemId": {"type": "string", "description": "The item ID to update"},
                        "title": {"type": "string", "description": "New question title (optional)"},
                        "required": {"type": "boolean", "description": "Is response required (optional)"}
                    },
                    "required": ["formId", "itemId"]
                }
            ),
            Tool(
                name="questions_delete",
                description="Delete a question from a form",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "formId": {"type": "string", "description": "The form ID"},
                        "itemId": {"type": "string", "description": "The item ID to delete"},
                        "confirm": {"type": "boolean", "description": "Must be true to confirm deletion"}
                    },
                    "required": ["formId", "itemId", "confirm"]
                }
            ),
            Tool(
                name="questions_move",
                description="Move a question to a new position",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "formId": {"type": "string", "description": "The form ID"},
                        "itemId": {"type": "string", "description": "The item ID to move"},
                        "newPosition": {"type": "integer", "description": "New position index"}
                    },
                    "required": ["formId", "itemId", "newPosition"]
                }
            ),

            # ==================== SECTION TOOLS (1) ====================

            Tool(
                name="sections_add",
                description="Add a section break (page break) to the form",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "formId": {"type": "string", "description": "The form ID"},
                        "title": {"type": "string", "description": "Section title"},
                        "description": {"type": "string", "description": "Section description (optional)"},
                        "position": {"type": "integer", "description": "Position index (optional)"}
                    },
                    "required": ["formId", "title"]
                }
            ),

            # ==================== RESPONSE MANAGEMENT TOOLS (3) ====================

            Tool(
                name="responses_list",
                description="List all responses for a form",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "formId": {"type": "string", "description": "The form ID"},
                        "pageSize": {"type": "integer", "description": "Maximum responses to return (default 100)", "default": 100},
                        "pageToken": {"type": "string", "description": "Pagination token (optional)"}
                    },
                    "required": ["formId"]
                }
            ),
            Tool(
                name="responses_get",
                description="Get a specific response by ID",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "formId": {"type": "string", "description": "The form ID"},
                        "responseId": {"type": "string", "description": "The response ID"}
                    },
                    "required": ["formId", "responseId"]
                }
            ),
            Tool(
                name="responses_export_csv",
                description="Export all responses to CSV format",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "formId": {"type": "string", "description": "The form ID"},
                        "includeTimestamps": {"type": "boolean", "description": "Include submission timestamps (default true)", "default": True},
                        "includeEmail": {"type": "boolean", "description": "Include respondent emails (default true)", "default": True}
                    },
                    "required": ["formId"]
                }
            ),

            # ==================== UTILITY TOOLS (2) ====================

            Tool(
                name="forms_duplicate",
                description="Duplicate an existing form with all questions",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "formId": {"type": "string", "description": "The form ID to copy"},
                        "newTitle": {"type": "string", "description": "Title for the new form"}
                    },
                    "required": ["formId", "newTitle"]
                }
            ),
            Tool(
                name="forms_get_link",
                description="Get public and edit links for a form",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "formId": {"type": "string", "description": "The form ID"}
                    },
                    "required": ["formId"]
                }
            )
        ]

    # ==================== TOOL IMPLEMENTATIONS ====================

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> list[TextContent]:
        """Execute tool calls and return results."""

        try:
            result = None

            # Form Management Tools
            if name == "forms_create":
                result = api.create_form(
                    title=arguments["title"],
                    description=arguments.get("description", "")
                )

            elif name == "forms_list":
                result = api.list_forms(
                    page_size=arguments.get("pageSize", 50),
                    page_token=arguments.get("pageToken")
                )

            elif name == "forms_get":
                result = api.get_form(arguments["formId"])

            elif name == "forms_update":
                result = api.update_form(
                    form_id=arguments["formId"],
                    title=arguments.get("title"),
                    description=arguments.get("description")
                )

            elif name == "forms_delete":
                if not arguments.get("confirm"):
                    raise ValueError("Must set confirm=true to delete form")
                result = api.delete_form(arguments["formId"])

            # Question Management Tools
            elif name == "questions_add":
                result = api.add_question(
                    form_id=arguments["formId"],
                    question_type=arguments["type"],
                    title=arguments["title"],
                    **{k: v for k, v in arguments.items() if k not in ["formId", "type", "title"]}
                )

            elif name == "questions_update":
                result = api.update_question(
                    form_id=arguments["formId"],
                    item_id=arguments["itemId"],
                    **{k: v for k, v in arguments.items() if k not in ["formId", "itemId"]}
                )

            elif name == "questions_delete":
                if not arguments.get("confirm"):
                    raise ValueError("Must set confirm=true to delete question")
                result = api.delete_question(
                    arguments["formId"],
                    arguments["itemId"]
                )

            elif name == "questions_move":
                result = api.move_question(
                    arguments["formId"],
                    arguments["itemId"],
                    arguments["newPosition"]
                )

            # Section Tools
            elif name == "sections_add":
                result = api.add_section(
                    form_id=arguments["formId"],
                    title=arguments["title"],
                    description=arguments.get("description", ""),
                    position=arguments.get("position")
                )

            # Response Management Tools
            elif name == "responses_list":
                result = api.list_responses(
                    form_id=arguments["formId"],
                    page_size=arguments.get("pageSize", 100),
                    page_token=arguments.get("pageToken")
                )

            elif name == "responses_get":
                result = api.get_response(
                    arguments["formId"],
                    arguments["responseId"]
                )

            elif name == "responses_export_csv":
                result = api.export_responses_csv(
                    form_id=arguments["formId"],
                    include_timestamps=arguments.get("includeTimestamps", True),
                    include_email=arguments.get("includeEmail", True)
                )

            # Utility Tools
            elif name == "forms_duplicate":
                result = api.duplicate_form(
                    arguments["formId"],
                    arguments["newTitle"]
                )

            elif name == "forms_get_link":
                form = api.get_form(arguments["formId"])
                result = {
                    "responderUri": form.get("responderUri"),
                    "editUri": f"https://docs.google.com/forms/d/{arguments['formId']}/edit"
                }

            else:
                raise ValueError(f"Unknown tool: {name}")

            # Return success response
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        except Exception as e:
            # Return error response
            error_response = {
                "success": False,
                "error": {
                    "message": str(e),
                    "tool": name
                }
            }
            return [TextContent(
                type="text",
                text=json.dumps(error_response, indent=2)
            )]
