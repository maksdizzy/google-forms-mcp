# Quick Start Guide

**Get Google Tools CLI working in 5 minutes!**

## One Command Installation

```bash
# Clone and install
git clone https://github.com/maksdizzy/google-forms-cli
cd google-forms-cli
uv sync

# Setup OAuth (follow the prompts)
uv run gtools auth setup
```

## During Installation

You'll need to:

1. **Create OAuth credentials** in Google Cloud (wizard guides you)
2. **Sign in** with your Google account
3. **Grant permissions** to the app

That's it!

## After Installation

```bash
# Test it works
uv run gtools --help
uv run gtools forms list
```

## Example Commands to Try

### Forms

```bash
# List all forms
uv run gtools forms list

# Create a new form
uv run gtools forms create "Customer Feedback"

# Add questions
uv run gtools forms add-question FORM_ID --type MULTIPLE_CHOICE --title "Rating" --options "1,2,3,4,5"

# Export responses
uv run gtools forms export FORM_ID --output responses.csv

# Get shareable link
uv run gtools forms link FORM_ID
```

### Sheets

```bash
# Get spreadsheet info
uv run gtools sheets info SPREADSHEET_ID

# Read data
uv run gtools sheets read SPREADSHEET_ID

# Export to CSV
uv run gtools sheets read SPREADSHEET_ID --format csv --output data.csv
```

## Need Help?

- **Full guide:** [INSTALL.md](INSTALL.md)
- **All features:** [README.md](README.md)
- **AI agent integration:** [skill.md](skill.md)

## What You Get

- Create and manage Google Forms
- Add all 12 question types
- Export responses to CSV
- Read Google Sheets data
- Export spreadsheets to CSV/JSON
- YAML template support

**Happy automating!**
