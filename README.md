# Google Tools CLI

Command-line tool for managing Google Workspace - create forms, add questions, export responses, read spreadsheets.

## Features

- **Full form management** - Create, update, delete, duplicate forms
- **All question types** - 12 Google Forms question types supported
- **Response export** - Export responses to CSV
- **Google Sheets** - Read and export spreadsheet data
- **YAML templates** - Create complex forms from simple YAML files
- **Interactive OAuth wizard** - Easy setup for non-technical users
- **Cursor Skill** - Works as an AI agent skill in Cursor IDE

## Quick Start

### 1. Install

```bash
# Clone the repository
git clone https://github.com/maksdizzy/google-forms-cli
cd google-forms-cli

# Install with uv
uv sync
```

### 2. Setup OAuth

```bash
# Run interactive setup wizard
uv run gtools auth setup
```

The wizard guides you through:
1. Creating OAuth credentials in Google Cloud Console
2. Getting a refresh token
3. Saving credentials to `.env`

### 3. Use

```bash
# List your forms
uv run gtools forms list

# Create a new form
uv run gtools forms create "My Survey"

# Add a question
uv run gtools forms add-question FORM_ID --type MULTIPLE_CHOICE --title "Rate us" --options "1,2,3,4,5"

# Export responses
uv run gtools forms export FORM_ID --output responses.csv

# Read a spreadsheet
uv run gtools sheets read SPREADSHEET_ID
```

## CLI Structure

```
gtools
├── auth          # Authentication management
│   ├── setup     # Interactive OAuth wizard
│   └── check     # Verify credentials
├── forms         # Google Forms operations
│   ├── list      # List all forms
│   ├── create    # Create new form
│   ├── get       # Get form details
│   ├── update    # Update form
│   ├── delete    # Delete form
│   ├── duplicate # Copy form with personalization
│   ├── link      # Get share links
│   ├── add-question    # Add question
│   ├── delete-question # Remove question
│   ├── move-question   # Reorder question
│   ├── add-section     # Add section break
│   ├── responses       # List responses
│   ├── export          # Export to CSV
│   ├── apply           # Create from YAML
│   └── export-template # Export to YAML
└── sheets        # Google Sheets operations
    ├── info      # Get spreadsheet metadata
    ├── list      # List sheets
    └── read      # Read data (table/CSV/JSON)
```

## Commands

### Authentication

| Command | Description |
|---------|-------------|
| `gtools auth setup` | Interactive OAuth setup |
| `gtools auth check` | Verify credentials |

### Form Management

| Command | Description |
|---------|-------------|
| `gtools forms list` | List all forms |
| `gtools forms create "Title"` | Create new form |
| `gtools forms get FORM_ID` | Get form details |
| `gtools forms update FORM_ID` | Update form |
| `gtools forms delete FORM_ID` | Delete form |
| `gtools forms duplicate FORM_ID` | Copy form |
| `gtools forms link FORM_ID` | Get share links |

### Questions

| Command | Description |
|---------|-------------|
| `gtools forms add-question` | Add question |
| `gtools forms delete-question` | Remove question |
| `gtools forms move-question` | Reorder question |
| `gtools forms add-section` | Add section break |

### Responses

| Command | Description |
|---------|-------------|
| `gtools forms responses FORM_ID` | List responses |
| `gtools forms export FORM_ID` | Export to CSV |

### Templates

| Command | Description |
|---------|-------------|
| `gtools forms apply template.yaml` | Create from template |
| `gtools forms export-template FORM_ID` | Export to YAML |

### Google Sheets

| Command | Description |
|---------|-------------|
| `gtools sheets info SPREADSHEET_ID` | Get spreadsheet metadata |
| `gtools sheets list SPREADSHEET_ID` | List sheets |
| `gtools sheets read SPREADSHEET_ID` | Read data |

## Question Types

```bash
# Text questions
--type SHORT_ANSWER
--type PARAGRAPH

# Choice questions (use --options)
--type MULTIPLE_CHOICE --options "A,B,C"
--type CHECKBOXES --options "X,Y,Z"
--type DROPDOWN --options "1,2,3"

# Scale questions
--type LINEAR_SCALE --low 1 --high 5
--type RATING --high 5

# Other
--type DATE
--type TIME
```

## YAML Templates

Create forms from YAML files:

```yaml
form:
  title: "Customer Feedback"
  description: "Share your experience"

questions:
  - type: SHORT_ANSWER
    title: "Your name"
    description: |
      Enter your full name.
      This helps us identify your feedback.
    required: true

  - type: MULTIPLE_CHOICE
    title: "Satisfaction"
    options: [Excellent, Good, Fair, Poor]
    required: true

  - type: PARAGRAPH
    title: "Comments"
```

Use YAML multiline syntax (`|`) for descriptions with line breaks.

Apply with:

```bash
uv run gtools forms apply feedback.yaml
```

See `templates/examples/` for more examples:
- `feedback_form.yaml` - Employee feedback survey
- `event_registration.yaml` - Event registration form
- `customer_satisfaction.yaml` - Customer satisfaction survey

## OAuth Setup Details

### Prerequisites

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable **Google Forms API**, **Google Drive API**, and **Google Sheets API**
4. Create OAuth 2.0 credentials (Desktop application)

### Get Refresh Token

**Option 1: OAuth Playground (recommended)**

1. Go to [OAuth Playground](https://developers.google.com/oauthplayground/)
2. Click Settings → Check "Use your own OAuth credentials"
3. Enter your Client ID and Client Secret
4. Add scopes:
   - `https://www.googleapis.com/auth/forms.body`
   - `https://www.googleapis.com/auth/forms.responses.readonly`
   - `https://www.googleapis.com/auth/drive.file`
   - `https://www.googleapis.com/auth/spreadsheets.readonly`
5. Authorize and exchange for tokens
6. Copy the refresh token

**Option 2: Interactive wizard**

```bash
uv run gtools auth setup
```

## For Cursor/AI Agents

This tool is designed to work as a skill for AI agents in Cursor IDE.

See `skill.md` for complete agent instructions including:
- Quick reference for all commands
- Common workflows
- Error handling

## Project Structure

```
google-forms-cli/
├── src/gtools/
│   ├── __init__.py       # Package init
│   ├── cli.py            # Main CLI entry point
│   ├── templates.py      # YAML template engine
│   ├── core/
│   │   ├── auth.py       # OAuth + interactive wizard
│   │   ├── base.py       # BaseAPI class
│   │   └── scopes.py     # OAuth scopes
│   ├── forms/
│   │   ├── api.py        # Google Forms API wrapper
│   │   ├── models.py     # Pydantic models
│   │   └── commands.py   # Forms CLI commands
│   └── sheets/
│       ├── api.py        # Google Sheets API wrapper
│       ├── models.py     # Pydantic models
│       └── commands.py   # Sheets CLI commands
├── templates/
│   └── examples/         # Example YAML templates
├── skill.md              # Cursor agent instructions
├── pyproject.toml        # Project configuration
└── README.md             # This file
```

## Backwards Compatibility

The legacy `gforms` command still works as an alias:

```bash
# Both commands work identically
uv run gforms forms list
uv run gtools forms list
```

## Troubleshooting

**OAuth Errors:**

```bash
uv run gtools auth check  # Verify credentials
uv run gtools auth setup  # Reconfigure if needed
```

**API Errors:**
- Verify Form ID with `uv run gtools forms list`
- Check API quotas in Google Cloud Console

## Security

- `.env` file is gitignored (never committed)
- Refresh token provides account access - keep secure
- Revoke access: https://myaccount.google.com/permissions

## License

MIT
