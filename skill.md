# Google Tools CLI Skill

> Manage Google Forms and Sheets through command-line interface - create forms, add questions, export responses, read spreadsheets, and batch duplicate with personalization.

## Quick Start for Non-Technical Users

### What This Tool Does
This tool lets you work with Google Forms and Sheets from your computer's terminal instead of clicking around in a browser. Perfect for:
- Creating multiple personalized copies of a form (e.g., 360 feedback for each employee)
- Automating form creation from templates
- Exporting responses for analysis
- Reading and exporting spreadsheet data

### First-Time Setup (One Time Only)
```bash
# Step 1: Check if already set up
uv run gtools auth check

# Step 2: If not configured, run setup wizard (follow prompts)
uv run gtools auth setup
```

### Most Common Task: Create Personalized Form Copies

**Scenario**: You have a 360 Feedback form with "Employee Name" as placeholder, and need copies for 20 employees.

```bash
# 1. Find your source form ID (the long string in the Google Form URL)
# Example: https://docs.google.com/forms/d/1WBjiy0jWvGqk21DvlBS9ejEzV4xTY2wUT4m5OioKSU4/edit
# Form ID is: 1WBjiy0jWvGqk21DvlBS9ejEzV4xTY2wUT4m5OioKSU4

# 2. Create a personalized copy for one employee
uv run gtools forms duplicate 1WBjiy0jWvGqk21DvlBS9ejEzV4xTY2wUT4m5OioKSU4 \
  --title "360 Feedback - John Smith" \
  --personalize "John Smith"

# This replaces "NAME" and "Employee Name" placeholders with "John Smith"
```

### Getting Form Links
```bash
# Get shareable link for respondents
uv run gtools forms link FORM_ID
```

---

## Capabilities

This skill enables full control over Google Forms and Sheets:
- **Create & manage forms** - Create, update, delete, duplicate forms
- **Duplicate with personalization** - Replace placeholders automatically when copying
- **Add questions** - All 12 Google Forms question types supported
- **Export responses** - Get responses as CSV for analysis
- **YAML templates** - Create simple forms from YAML files
- **Read spreadsheets** - Get data from Google Sheets in table, CSV, or JSON format

## Prerequisites

Before using, ensure OAuth is configured:
```bash
uv run gtools auth check
```

If not configured, run setup wizard:
```bash
uv run gtools auth setup
```

## Quick Reference

### Authentication
```bash
# Check credentials
uv run gtools auth check

# Setup OAuth (interactive wizard)
uv run gtools auth setup
```

### Form Management
```bash
# List all forms
uv run gtools forms list

# Create new form
uv run gtools forms create "Form Title" --description "Optional description"

# Get form details
uv run gtools forms get FORM_ID

# Update form
uv run gtools forms update FORM_ID --title "New Title" --description "New description"

# Delete form (requires confirmation)
uv run gtools forms delete FORM_ID --yes

# Duplicate form (simple copy)
uv run gtools forms duplicate FORM_ID --title "Copy of Form"

# Duplicate with personalization (replaces placeholders)
uv run gtools forms duplicate FORM_ID --title "360 Feedback - John Smith" --personalize "John Smith"

# Get shareable links
uv run gtools forms link FORM_ID
```

### Duplicate with Personalization

The `--personalize` / `-p` option automatically replaces common placeholders:
- `NAME` → specified value
- `Employee Name` → specified value

```bash
# Full example
uv run gtools forms duplicate SOURCE_FORM_ID \
  --title "Performance Review - Jane Doe" \
  --personalize "Jane Doe"
```

**What gets personalized**:
- Form title
- Form description
- All question titles
- All question descriptions
- Section titles and descriptions

**Important**: This preserves the entire form structure including:
- All sections (page breaks)
- All question types
- Grid questions
- All formatting

### Adding Questions

```bash
# Short answer
uv run gtools forms add-question FORM_ID --type SHORT_ANSWER --title "Your name" --required

# Short answer with description (supports \\n for newlines)
uv run gtools forms add-question FORM_ID --type SHORT_ANSWER --title "Email" \
  --description "Your work email address.\\nWe'll use this to send you updates." --required

# Paragraph (long text)
uv run gtools forms add-question FORM_ID --type PARAGRAPH --title "Comments"

# Multiple choice
uv run gtools forms add-question FORM_ID --type MULTIPLE_CHOICE --title "Department" --options "HR,Engineering,Sales" --required

# Checkboxes (multiple select)
uv run gtools forms add-question FORM_ID --type CHECKBOXES --title "Skills" --options "Python,JavaScript,Go"

# Dropdown
uv run gtools forms add-question FORM_ID --type DROPDOWN --title "Country" --options "USA,UK,Germany,France"

# Linear scale (1-5, 1-10, etc.)
uv run gtools forms add-question FORM_ID --type LINEAR_SCALE --title "Satisfaction" --low 1 --high 5 --low-label "Poor" --high-label "Excellent"

# Rating (star rating)
uv run gtools forms add-question FORM_ID --type RATING --title "Rate us" --high 5

# Date
uv run gtools forms add-question FORM_ID --type DATE --title "Preferred date"

# Time
uv run gtools forms add-question FORM_ID --type TIME --title "Preferred time"
```

### Question Management
```bash
# Delete question
uv run gtools forms delete-question FORM_ID ITEM_ID --yes

# Move question to new position
uv run gtools forms move-question FORM_ID ITEM_ID --position 3

# Add section break
uv run gtools forms add-section FORM_ID --title "Part 2" --description "Additional questions"
```

### Responses
```bash
# List responses
uv run gtools forms responses FORM_ID

# Export to CSV
uv run gtools forms export FORM_ID --output responses.csv

# Print CSV to console
uv run gtools forms export FORM_ID
```

### YAML Templates
```bash
# Create form from template
uv run gtools forms apply templates/examples/feedback_form.yaml

# Export existing form to template
uv run gtools forms export-template FORM_ID --output my_template.yaml
```

### Google Sheets Operations
```bash
# Get spreadsheet info and list of sheets
uv run gtools sheets info SPREADSHEET_ID

# List all sheets in a spreadsheet
uv run gtools sheets list SPREADSHEET_ID

# Read data (table format)
uv run gtools sheets read SPREADSHEET_ID

# Read specific range
uv run gtools sheets read SPREADSHEET_ID A1:D10

# Read from specific sheet
uv run gtools sheets read SPREADSHEET_ID --sheet "Sheet1"

# Export to CSV
uv run gtools sheets read SPREADSHEET_ID --format csv --output data.csv

# Export to JSON
uv run gtools sheets read SPREADSHEET_ID --format json --output data.json

# Read from URL (extracts ID automatically)
uv run gtools sheets read "https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit"
```

## Common Workflows

### Batch Personalization (Multiple Employees)

For creating many personalized copies, use a simple shell loop:

```bash
# Create personalized forms for multiple employees
for name in "John Smith" "Jane Doe" "Bob Wilson" "Alice Brown"; do
  uv run gtools forms duplicate SOURCE_FORM_ID \
    --title "360 Feedback - $name" \
    --personalize "$name"
  echo "Created form for $name"
  sleep 1  # Respect API rate limits
done
```

Or use a file with employee names:

```bash
# employees.txt (one name per line):
# John Smith
# Jane Doe
# Bob Wilson

while IFS= read -r name; do
  uv run gtools forms duplicate SOURCE_FORM_ID \
    --title "360 Feedback - $name" \
    --personalize "$name"
  echo "Created: $name"
  sleep 1
done < employees.txt
```

### Create Feedback Form Quickly
```bash
# Create form
uv run gtools forms create "Quick Feedback"

# Add satisfaction question
uv run gtools forms add-question FORM_ID --type LINEAR_SCALE --title "How satisfied are you?" --low 1 --high 5 --required

# Add comments
uv run gtools forms add-question FORM_ID --type PARAGRAPH --title "Any comments?"

# Get link
uv run gtools forms link FORM_ID
```

### Export and Analyze Responses
```bash
uv run gtools forms export FORM_ID --output data.csv
```

### Read Spreadsheet Data
```bash
# Quick view of spreadsheet
uv run gtools sheets info SPREADSHEET_ID

# Export all data to CSV
uv run gtools sheets read SPREADSHEET_ID --format csv --output export.csv
```

## YAML Template Format

```yaml
form:
  title: "Employee Feedback"
  description: "Please share your feedback"

questions:
  - type: SHORT_ANSWER
    title: "Your name"
    description: |
      Enter your full legal name.
      This will be used for identification purposes.
    required: true

  - type: MULTIPLE_CHOICE
    title: "Department"
    options:
      - Engineering
      - HR
      - Sales
    required: true

  - type: LINEAR_SCALE
    title: "Satisfaction"
    description: "Rate your overall satisfaction with the company"
    low: 1
    high: 5
    lowLabel: "Not satisfied"
    highLabel: "Very satisfied"

  - type: PARAGRAPH
    title: "Comments"
    required: false
```

**Note**: Use YAML multiline syntax (`|`) for descriptions with line breaks.

### YAML Template Limitations

**Important**: YAML templates are best for simple forms. They have limitations:

| Feature | YAML Template | Duplicate + Personalize |
|---------|---------------|------------------------|
| Simple questions | Yes | Yes |
| Sections (page breaks) | **No** | Yes |
| Grid questions | **No** | Yes |
| Complex formatting | **No** | Yes |
| Preserves original structure | **No** | Yes |

**Recommendation**: For complex forms with sections or grids, use `duplicate --personalize` instead of YAML templates.

## Supported Question Types

| Type | Description | Required Options |
|------|-------------|------------------|
| `SHORT_ANSWER` | Single line text | - |
| `PARAGRAPH` | Multi-line text | - |
| `MULTIPLE_CHOICE` | Radio buttons | `--options` |
| `CHECKBOXES` | Multiple select | `--options` |
| `DROPDOWN` | Select menu | `--options` |
| `LINEAR_SCALE` | Numeric scale | `--low`, `--high` |
| `RATING` | Star rating | `--high` |
| `DATE` | Date picker | - |
| `TIME` | Time picker | - |
| `FILE_UPLOAD` | File upload | - |

## Error Handling

If you see authentication errors:
1. Run `uv run gtools auth check` to verify credentials
2. If invalid, run `uv run gtools auth setup` to reconfigure

If form operations fail:
1. Verify the form ID is correct with `uv run gtools forms list`
2. Check you have permission to access the form

## API Notes

**Google Forms API Limitations**:
- **Titles** cannot contain newlines (API limitation) - newlines are automatically converted to spaces
- **Descriptions** CAN contain newlines - use `\\n` in CLI commands for line breaks
- When duplicating forms, titles with newlines are smartly split (first line → title, rest → description)

**Newline Support**:
```bash
# Add question with multiline description
uv run gtools forms add-question FORM_ID --type SHORT_ANSWER --title "Name" \
  --description "Enter your full name.\\nThis will be used for identification."

# Add section with multiline description
uv run gtools forms add-section FORM_ID --title "Part 2" \
  --description "Additional questions\\nPlease answer all required fields."

# Update form with multiline description
uv run gtools forms update FORM_ID --description "Survey description.\\nThank you for participating."
```

## Backwards Compatibility

The legacy `gforms` command still works and is an alias for `gtools`:
```bash
# These are equivalent:
uv run gforms forms list
uv run gtools forms list
```
