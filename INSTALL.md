# Google Tools CLI - Installation Guide

This guide will walk you through setting up the Google Tools CLI. **No technical expertise required!**

## Prerequisites

- A Google account
- Python 3.10+ installed
- Internet connection

## Installation Steps

### Step 1: Download the Code

1. Download this repository or clone it:

   ```bash
   git clone https://github.com/maksdizzy/google-forms-cli
   cd google-forms-cli
   ```

2. Open a terminal (Mac/Linux) or PowerShell (Windows) in the project directory

### Step 2: Install Dependencies

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv sync
```

### Step 3: Setup Google Cloud OAuth

This is the most important step! You'll create OAuth credentials to access your Google Forms and Sheets.

#### 3.1 Open Google Cloud Console

- Go to https://console.cloud.google.com
- Sign in with your Google account

#### 3.2 Create a New Project

- Click "Select a project" → "New Project"
- Name it "Google Tools CLI" (or whatever you like)
- Click "Create"

#### 3.3 Enable Required APIs

In the left sidebar, click "APIs & Services" → "Library":

- Search for "Google Forms API" → Click it → Click "Enable"
- Search for "Google Drive API" → Click it → Click "Enable"
- Search for "Google Sheets API" → Click it → Click "Enable"

#### 3.4 Create OAuth Credentials

- Go to "APIs & Services" → "Credentials"
- Click "+ CREATE CREDENTIALS" → "OAuth client ID"
- If prompted to configure consent screen:
  - User Type: External → Click "Create"
  - App name: "Google Tools CLI"
  - User support email: Your email
  - Developer contact: Your email
  - Click "Save and Continue" (skip scopes and test users)
- Back to creating OAuth client ID:
  - Application type: "Desktop app"
  - Name: "Google Tools CLI"
  - Click "Create"

#### 3.5 Copy Your Credentials

- You'll see a popup with your Client ID and Client Secret
- **Copy the Client ID** (looks like: `123456-abcdef.apps.googleusercontent.com`)
- **Copy the Client Secret** (looks like: `GOCSPX-abcdef123456`)

### Step 4: Run the Setup Wizard

```bash
uv run gtools auth setup
```

The interactive wizard will:

1. Ask for your Client ID → Paste it
2. Ask for your Client Secret → Paste it
3. Open your browser for authorization
4. Save credentials to `.env` file

### Step 5: Test the Installation

```bash
# Check authentication
uv run gtools auth check

# List your forms
uv run gtools forms list

# Get help
uv run gtools --help
```

If everything is set up correctly, you'll see your Google Forms!

## Troubleshooting

### "uv command not found" Error

**Solution:** Close and reopen your terminal, then try again. If that doesn't work:

```bash
# Mac/Linux
export PATH="$HOME/.cargo/bin:$PATH"

# Or reinstall uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Browser Doesn't Open During Setup

**Solution:**

1. The setup wizard will show a URL
2. Copy and paste it manually into your browser
3. Complete the authorization

### "OAuth Error" or "Invalid Credentials"

**Solution:**

1. Delete the `.env` file in the project directory
2. Run `uv run gtools auth setup` again
3. Make sure you enabled all three APIs (Forms, Drive, Sheets)

### "Refresh Token Expired"

**Solution:**

```bash
uv run gtools auth setup
```

This will get a new refresh token.

### Still Having Issues?

1. **Test manually:**

   ```bash
   uv run gtools auth check
   ```

2. **Check your credentials file:**
   - Open the `.env` file in the project directory
   - Make sure all three lines are filled in (CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN)

3. **Verify API permissions:**
   - Go to https://myaccount.google.com/permissions
   - Make sure "Google Tools CLI" is listed
   - If not, run the setup wizard again

## What Can You Do With It?

Once installed, you can:

### Forms Operations

- **List forms:** `uv run gtools forms list`
- **Create forms:** `uv run gtools forms create "My Survey"`
- **Add questions:** `uv run gtools forms add-question FORM_ID --type MULTIPLE_CHOICE --title "Rate us" --options "1,2,3,4,5"`
- **Export responses:** `uv run gtools forms export FORM_ID --output data.csv`
- **Duplicate forms:** `uv run gtools forms duplicate FORM_ID --title "Copy of Survey"`
- **Get links:** `uv run gtools forms link FORM_ID`

### Sheets Operations

- **Get spreadsheet info:** `uv run gtools sheets info SPREADSHEET_ID`
- **List sheets:** `uv run gtools sheets list SPREADSHEET_ID`
- **Read data:** `uv run gtools sheets read SPREADSHEET_ID`
- **Export to CSV:** `uv run gtools sheets read SPREADSHEET_ID --format csv --output data.csv`

## Security Notes

- Your credentials are stored in the `.env` file in the project directory
- This file is automatically excluded from git (won't be uploaded if you share the code)
- The refresh token gives access to your Google Forms and Sheets
- To revoke access anytime, go to https://myaccount.google.com/permissions

## Next Steps

- Read the [README.md](README.md) for complete documentation
- Check out `skill.md` for AI agent integration
- Explore all available commands with `uv run gtools --help`

**Enjoy automating your Google Workspace!**
