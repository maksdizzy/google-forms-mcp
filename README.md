# Google Forms CLI

Command-line tool for managing Google Forms - create forms, add questions, export responses.

## Features

- **Full form management** - Create, update, delete, duplicate forms
- **All question types** - 12 Google Forms question types supported
- **Response export** - Export responses to CSV
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
uv run gforms auth setup
```

The wizard guides you through:
1. Creating OAuth credentials in Google Cloud Console
2. Getting a refresh token
3. Saving credentials to `.env`

### 3. Use

```bash
# List your forms
uv run gforms list

# Create a new form
uv run gforms create "My Survey"

# Add a question
uv run gforms add-question FORM_ID --type MULTIPLE_CHOICE --title "Rate us" --options "1,2,3,4,5"

# Export responses
uv run gforms export FORM_ID --output responses.csv
```

## Commands

### Form Management

| Command | Description |
|---------|-------------|
| `gforms list` | List all forms |
| `gforms create "Title"` | Create new form |
| `gforms get FORM_ID` | Get form details |
| `gforms update FORM_ID` | Update form |
| `gforms delete FORM_ID` | Delete form |
| `gforms duplicate FORM_ID` | Copy form |
| `gforms link FORM_ID` | Get share links |

### Questions

| Command | Description |
|---------|-------------|
| `gforms add-question` | Add question |
| `gforms delete-question` | Remove question |
| `gforms move-question` | Reorder question |
| `gforms add-section` | Add section break |

### Responses

| Command | Description |
|---------|-------------|
| `gforms responses FORM_ID` | List responses |
| `gforms export FORM_ID` | Export to CSV |

### Templates

| Command | Description |
|---------|-------------|
| `gforms apply template.yaml` | Create from template |
| `gforms export-template FORM_ID` | Export to YAML |

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
    required: true

  - type: MULTIPLE_CHOICE
    title: "Satisfaction"
    options: [Excellent, Good, Fair, Poor]
    required: true

  - type: PARAGRAPH
    title: "Comments"
```

Apply with:
```bash
uv run gforms apply feedback.yaml
```

See `templates/examples/` for more examples:
- `feedback_form.yaml` - Employee feedback survey
- `event_registration.yaml` - Event registration form
- `customer_satisfaction.yaml` - Customer satisfaction survey

## OAuth Setup Details

### Prerequisites

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable **Google Forms API** and **Google Drive API**
4. Create OAuth 2.0 credentials (Desktop application)

### Get Refresh Token

**Option 1: OAuth Playground (recommended)**

1. Go to [OAuth Playground](https://developers.google.com/oauthplayground/)
2. Click ⚙️ Settings → Check "Use your own OAuth credentials"
3. Enter your Client ID and Client Secret
4. Add scopes:
   - `https://www.googleapis.com/auth/forms.body`
   - `https://www.googleapis.com/auth/forms.responses.readonly`
   - `https://www.googleapis.com/auth/drive.file`
5. Authorize and exchange for tokens
6. Copy the refresh token

**Option 2: Interactive wizard**

```bash
uv run gforms auth setup
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
├── src/gforms/
│   ├── cli.py          # Typer CLI commands
│   ├── api.py          # Google Forms API wrapper
│   ├── auth.py         # OAuth + interactive wizard
│   ├── models.py       # Pydantic models
│   └── templates.py    # YAML template engine
├── templates/
│   └── examples/       # Example YAML templates
├── skill.md            # Cursor agent instructions
├── pyproject.toml      # Project configuration
└── README.md           # This file
```

## Troubleshooting

**OAuth Errors:**
```bash
uv run gforms auth check  # Verify credentials
uv run gforms auth setup  # Reconfigure if needed
```

**API Errors:**
- Verify Form ID with `uv run gforms list`
- Check API quotas in Google Cloud Console

## Security

- `.env` file is gitignored (never committed)
- Refresh token provides account access - keep secure
- Revoke access: https://myaccount.google.com/permissions

## License

MIT
