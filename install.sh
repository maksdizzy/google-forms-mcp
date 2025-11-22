#!/bin/bash

# Google Forms MCP Server - Installation Script
# This script handles complete setup for non-technical users

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Google Forms MCP Server - Cursor Installation         ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo ""

# Step 1: Check and install uv
echo -e "${YELLOW}Step 1/5: Checking for uv package manager...${NC}"
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}uv not found. Installing uv...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Add uv to current shell session
    export PATH="$HOME/.cargo/bin:$PATH"

    if ! command -v uv &> /dev/null; then
        echo -e "${RED}Failed to install uv. Please install manually from: https://github.com/astral-sh/uv${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ uv installed successfully${NC}"
else
    echo -e "${GREEN}✓ uv is already installed${NC}"
fi
echo ""

# Step 2: Install dependencies
echo -e "${YELLOW}Step 2/5: Installing Python dependencies...${NC}"
uv sync
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Step 3: Google Cloud OAuth Setup
echo -e "${YELLOW}Step 3/5: Setting up Google Cloud OAuth credentials${NC}"
echo ""

# Check if .env file already exists
EXISTING_CLIENT_ID=""
EXISTING_CLIENT_SECRET=""
EXISTING_REFRESH_TOKEN=""

if [ -f ".env" ]; then
    echo -e "${BLUE}Found existing .env file. Checking for existing credentials...${NC}"

    # Read existing values
    if grep -q "GOOGLE_CLIENT_ID=" .env; then
        EXISTING_CLIENT_ID=$(grep "GOOGLE_CLIENT_ID=" .env | cut -d'=' -f2)
        if [ -n "$EXISTING_CLIENT_ID" ]; then
            echo -e "${GREEN}✓ Found existing Client ID${NC}"
        fi
    fi

    if grep -q "GOOGLE_CLIENT_SECRET=" .env; then
        EXISTING_CLIENT_SECRET=$(grep "GOOGLE_CLIENT_SECRET=" .env | cut -d'=' -f2)
        if [ -n "$EXISTING_CLIENT_SECRET" ]; then
            echo -e "${GREEN}✓ Found existing Client Secret${NC}"
        fi
    fi

    if grep -q "GOOGLE_REFRESH_TOKEN=" .env; then
        EXISTING_REFRESH_TOKEN=$(grep "GOOGLE_REFRESH_TOKEN=" .env | cut -d'=' -f2)
        if [ -n "$EXISTING_REFRESH_TOKEN" ]; then
            echo -e "${GREEN}✓ Found existing Refresh Token${NC}"
        fi
    fi
    echo ""
fi

# Determine what we need to ask for
NEED_CLIENT_ID=false
NEED_CLIENT_SECRET=false
NEED_REFRESH_TOKEN=false

if [ -z "$EXISTING_CLIENT_ID" ]; then
    NEED_CLIENT_ID=true
fi

if [ -z "$EXISTING_CLIENT_SECRET" ]; then
    NEED_CLIENT_SECRET=true
fi

if [ -z "$EXISTING_REFRESH_TOKEN" ]; then
    NEED_REFRESH_TOKEN=true
fi

# If we need any OAuth credentials, show instructions
if [ "$NEED_CLIENT_ID" = true ] || [ "$NEED_CLIENT_SECRET" = true ]; then
    echo "You need to create OAuth credentials in Google Cloud Console."
    echo "This will allow the MCP server to access your Google Forms."
    echo ""
    echo -e "${BLUE}Please follow these steps:${NC}"
    echo ""
    echo "1. Open: https://console.cloud.google.com"
    echo "2. Create a new project (or select existing one)"
    echo "3. Enable these APIs:"
    echo "   - Google Forms API"
    echo "   - Google Drive API"
    echo "4. Go to 'Credentials' → 'Create Credentials' → 'OAuth client ID'"
    echo "5. Application type: 'Desktop app'"
    echo "6. Name it: 'Google Forms MCP'"
    echo "7. Click 'Create'"
    echo ""
    echo -e "${GREEN}When ready, press Enter to continue...${NC}"
    read -r
    echo ""
fi

# Ask for client ID if needed
if [ "$NEED_CLIENT_ID" = true ]; then
    echo -e "${YELLOW}Enter your OAuth Client ID:${NC}"
    read -r CLIENT_ID
else
    CLIENT_ID="$EXISTING_CLIENT_ID"
    echo -e "${BLUE}Using existing Client ID${NC}"
fi

# Ask for client secret if needed
if [ "$NEED_CLIENT_SECRET" = true ]; then
    echo -e "${YELLOW}Enter your OAuth Client Secret:${NC}"
    read -r CLIENT_SECRET
else
    CLIENT_SECRET="$EXISTING_CLIENT_SECRET"
    echo -e "${BLUE}Using existing Client Secret${NC}"
fi

echo ""

# Step 4: Generate refresh token (if needed)
if [ "$NEED_REFRESH_TOKEN" = true ]; then
    # Create client_secrets.json for token generation
    cat > client_secrets.json <<EOF
{
  "installed": {
    "client_id": "$CLIENT_ID",
    "client_secret": "$CLIENT_SECRET",
    "redirect_uris": ["http://localhost:8080"],
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token"
  }
}
EOF

    echo -e "${YELLOW}Step 4/5: Generating OAuth refresh token...${NC}"
    echo ""
    echo "This will open your browser to authorize the application."
    echo "Please sign in with your Google account and grant access."
    echo ""
    echo -e "${GREEN}Press Enter to open browser...${NC}"
    read -r

    # Run the token generation script and capture output
    TOKEN_OUTPUT=$(uv run python get_token.py 2>&1) || {
        echo -e "${RED}Failed to generate token. Please check the error above.${NC}"
        exit 1
    }

    # Extract refresh token from output
    REFRESH_TOKEN=$(echo "$TOKEN_OUTPUT" | grep "GOOGLE_REFRESH_TOKEN=" | cut -d'=' -f2)

    if [ -z "$REFRESH_TOKEN" ]; then
        echo -e "${RED}Failed to extract refresh token. Please run 'uv run python get_token.py' manually.${NC}"
        exit 1
    fi

    echo -e "${GREEN}✓ Token generated successfully${NC}"
    echo ""

    # Clean up client_secrets.json
    rm -f client_secrets.json
else
    echo -e "${YELLOW}Step 4/5: Using existing refresh token${NC}"
    REFRESH_TOKEN="$EXISTING_REFRESH_TOKEN"
    echo -e "${GREEN}✓ All credentials already configured${NC}"
    echo ""
fi

# Create or update .env file
cat > .env <<EOF
# Google OAuth Credentials
# Updated by install.sh on $(date)

GOOGLE_CLIENT_ID=$CLIENT_ID
GOOGLE_CLIENT_SECRET=$CLIENT_SECRET
GOOGLE_REFRESH_TOKEN=$REFRESH_TOKEN
EOF

echo -e "${GREEN}✓ .env file updated${NC}"
echo ""

# Step 5: Configure Cursor
echo -e "${YELLOW}Step 5/5: Configuring Cursor IDE...${NC}"
echo ""

# Determine the path to uv python
UV_PYTHON_PATH="$SCRIPT_DIR/.venv/bin/python"

# Create Cursor MCP configuration
CURSOR_CONFIG_DIR="$HOME/.cursor"
MCP_CONFIG_FILE="$CURSOR_CONFIG_DIR/mcp.json"

mkdir -p "$CURSOR_CONFIG_DIR"

# Check if mcp.json exists
if [ -f "$MCP_CONFIG_FILE" ]; then
    echo -e "${YELLOW}Cursor MCP configuration already exists.${NC}"
    echo "Your current config: $MCP_CONFIG_FILE"
    echo ""
    echo "Add this to your mcpServers section:"
    echo ""
    cat <<EOF
{
  "mcpServers": {
    "google-forms": {
      "command": "uv",
      "args": [
        "--directory",
        "$SCRIPT_DIR",
        "run",
        "python",
        "main.py"
      ]
    }
  }
}
EOF
    echo ""
    echo -e "${YELLOW}Would you like to open the config file for editing? (y/n)${NC}"
    read -r OPEN_CONFIG
    if [ "$OPEN_CONFIG" = "y" ] || [ "$OPEN_CONFIG" = "Y" ]; then
        ${EDITOR:-nano} "$MCP_CONFIG_FILE"
    fi
else
    # Create new mcp.json
    cat > "$MCP_CONFIG_FILE" <<EOF
{
  "mcpServers": {
    "google-forms": {
      "command": "uv",
      "args": [
        "--directory",
        "$SCRIPT_DIR",
        "run",
        "python",
        "main.py"
      ]
    }
  }
}
EOF
    echo -e "${GREEN}✓ Cursor MCP configuration created at: $MCP_CONFIG_FILE${NC}"
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                  Installation Complete! 🎉                 ║${NC}"
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Restart Cursor IDE"
echo "2. Open a project in Cursor"
echo "3. Start using Google Forms MCP tools in AI chat"
echo ""
echo -e "${BLUE}Test it by asking Cursor:${NC}"
echo "   'List my Google Forms'"
echo ""
echo -e "${BLUE}Available tools:${NC}"
echo "   - forms_create, forms_list, forms_get, forms_update, forms_delete"
echo "   - questions_add, questions_update, questions_delete, questions_move"
echo "   - responses_list, responses_get, responses_export_csv"
echo "   - sections_add, forms_duplicate, forms_get_link"
echo ""
echo -e "${YELLOW}Troubleshooting:${NC}"
echo "   - Config file: $MCP_CONFIG_FILE"
echo "   - Credentials: $SCRIPT_DIR/.env"
echo "   - Test server: uv run python main.py"
echo ""
echo -e "${GREEN}Thank you for using Google Forms MCP Server!${NC}"
echo ""
