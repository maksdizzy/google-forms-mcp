# Google Forms MCP Server

Simple and reliable MCP server for Google Forms management. Optimized for HR managers creating feedback forms.

## Features

✅ 15 essential tools (forms, questions, responses)
✅ All 12 Google Forms question types
✅ OAuth via .env (simple setup)
✅ Auto-publish forms
✅ CSV export for Excel
✅ ~640 lines of Python code
✅ **One-command installation for Cursor IDE**

## 🚀 Quick Start (Cursor IDE - Recommended)

**Automated installation for non-technical users:**

### Linux/Mac:
```bash
git clone <repository-url>
cd google-forms-mcp
./install.sh
```

### Windows:
```powershell
git clone <repository-url>
cd google-forms-mcp
.\install.ps1
```

The installation script will:
1. ✅ Install `uv` package manager (if needed)
2. ✅ Install all Python dependencies
3. ✅ Guide you through Google Cloud OAuth setup
4. ✅ Generate and save your credentials automatically
5. ✅ Configure Cursor IDE to use the MCP server

**That's it!** Restart Cursor and start using Google Forms tools in AI chat.

### Test it:
Ask Cursor: `"List my Google Forms"` or `"Create a feedback form"`

---

## Manual Installation (Advanced Users)

### 1. Install Dependencies

**Option A: Using uv (recommended for Cursor):**
```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
```

**Option B: Using venv (traditional approach):**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Get OAuth Credentials

**Create OAuth Client:**
1. Go to https://console.cloud.google.com
2. Create project → Enable Forms API & Drive API
3. Create OAuth client ID (Desktop app)
4. Save client_id and client_secret

**Get Refresh Token (Option A - Easiest):**
1. Go to https://developers.google.com/oauthplayground/
2. Settings → Use your own OAuth credentials
3. Select scopes:
   - `https://www.googleapis.com/auth/forms.body`
   - `https://www.googleapis.com/auth/forms.responses.readonly`
   - `https://www.googleapis.com/auth/drive.file`
4. Authorize → Exchange code → Copy refresh_token

**Get Refresh Token (Option B - Script):**
```bash
python get_token.py
# Browser opens → Login → Copy credentials
```

### 3. Create .env File

```bash
GOOGLE_CLIENT_ID=123456789-xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxxx
GOOGLE_REFRESH_TOKEN=1//0gxxxx
```

### 4. Run Server (for testing)

**Using uv:**
```bash
uv run python main.py
```

**Using venv:**
```bash
# Activate virtual environment first
source venv/bin/activate

# Run the server
python main.py
```

### 5. Configure Your IDE

#### For Cursor IDE (Recommended):

**Location:**
- Linux/Mac: `~/.cursor/mcp.json`
- Windows: `%APPDATA%\Cursor\User\globalStorage\mcp.json`

**Configuration (using uv):**
```json
{
  "mcpServers": {
    "google-forms": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/google-forms-mcp",
        "run",
        "python",
        "main.py"
      ]
    }
  }
}
```

**Configuration (using venv):**
```json
{
  "mcpServers": {
    "google-forms": {
      "command": "/absolute/path/to/google-forms-mcp/.venv/bin/python",
      "args": ["/absolute/path/to/google-forms-mcp/main.py"]
    }
  }
}
```

#### For Claude Code:

**Location:** `~/.config/claude/config.json`

**Configuration (using uv):**
```json
{
  "mcpServers": {
    "google-forms": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/google-forms-mcp",
        "run",
        "python",
        "main.py"
      ]
    }
  }
}
```

**Configuration (using venv):**
```json
{
  "mcpServers": {
    "google-forms": {
      "command": "/absolute/path/to/google-forms-mcp/venv/bin/python",
      "args": ["/absolute/path/to/google-forms-mcp/main.py"]
    }
  }
}
```

**Important**: Replace `/absolute/path/to/google-forms-mcp` with your actual project location.

## Available Tools

### Forms Management
- `forms_create` - Create new form
- `forms_list` - List all forms
- `forms_get` - Get form details
- `forms_update` - Update form
- `forms_delete` - Delete form

### Questions
- `questions_add` - Add question (12 types)
- `questions_update` - Update question
- `questions_delete` - Delete question
- `questions_move` - Reorder question

### Sections
- `sections_add` - Add section/page break

### Responses
- `responses_list` - List all responses
- `responses_get` - Get specific response
- `responses_export_csv` - Export to CSV

### Utilities
- `forms_duplicate` - Copy form
- `forms_get_link` - Get public link

## Question Types Supported

1. SHORT_ANSWER - Short text
2. PARAGRAPH - Long text
3. MULTIPLE_CHOICE - Radio buttons
4. CHECKBOXES - Multiple selection
5. DROPDOWN - Dropdown menu
6. LINEAR_SCALE - 1-5, 1-10 scale
7. DATE - Date picker
8. TIME - Time picker
9. FILE_UPLOAD - File upload
10. MULTIPLE_CHOICE_GRID - Radio grid
11. CHECKBOX_GRID - Checkbox grid
12. RATING - Star/heart rating

## Usage Example

```
User: Create feedback form

Claude: [calls forms_create]
✅ Form created: "Feedback Form"
Link: https://docs.google.com/forms/d/e/.../viewform

User: Add questions: name, department (Engineering/HR/Sales),
      satisfaction 1-5

Claude: [calls questions_add 3 times]
✅ Added 3 questions

User: Show link

Claude: [calls forms_get_link]
📎 https://docs.google.com/forms/d/e/.../viewform

User: After a week - export responses

Claude: [calls responses_export_csv]
✅ Exported 15 responses to CSV
```

## Project Structure

```
google-forms-mcp/
├── main.py              # MCP server entry point
├── auth.py              # OAuth from .env
├── forms_api.py         # Google Forms API wrapper
├── tools.py             # 15 MCP tools
├── get_token.py         # One-time token getter
├── requirements.txt     # Dependencies
├── .env                 # OAuth credentials (gitignored)
├── .env.example         # Template
├── README.md            # This file
└── SPECIFICATION.md     # Complete spec
```

## Architecture

```
Claude Code
    ↓ MCP Protocol
MCP Tools (15 tools)
    ↓ API Translation
Google Forms API Client
    ↓ OAuth (.env)
Google Forms API v1
```

## Troubleshooting

**OAuth Errors:**
- Check .env has all 3 credentials
- Verify scopes are correct
- Regenerate refresh_token if expired

**API Errors:**
- Enable Forms API in Cloud Console
- Enable Drive API in Cloud Console
- Check API quotas

**MCP Connection:**
- Verify python path in config
- Test with `python main.py` directly
- Check MCP SDK version >=0.9.0

## Security

- `.env` file is gitignored
- Refresh token gives full account access
- Token auto-refreshes every hour
- Revoke: https://myaccount.google.com/permissions

## For AI Agents / Claude Code

**⚠️ IMPORTANT**: This MCP server provides direct access to Google Forms. When working with this project:

- ✅ **DO**: Call MCP tools directly (forms_create, questions_add, etc.)
- ❌ **DON'T**: Use Context7/WebSearch to research Google Forms API
- ❌ **DON'T**: Look up JSON schemas or API documentation

**Why?** The API wrapper is already implemented. Just use the tools!

**Quick Test**: Try `forms_list` with no parameters to verify MCP server is working.

## Known Issues & Analysis

⚠️ **questions_add**: Code is correct (verified against official docs), but may fail in some test environments. See [claudedocs/GOOGLE_FORMS_API_FIXES.md](claudedocs/GOOGLE_FORMS_API_FIXES.md) for:
- Root cause analysis with official Google documentation
- Evidence-based fix recommendations
- Troubleshooting steps

## Development

See [SPECIFICATION.md](SPECIFICATION.md) for complete implementation details.

## License

MIT
