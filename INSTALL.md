# Google Forms MCP Server - Installation Guide

This guide will walk you through setting up the Google Forms MCP Server for use with Cursor IDE. **No technical expertise required!**

## Prerequisites

- A Google account
- Cursor IDE installed on your computer
- Internet connection

## Installation Steps

### Step 1: Download the Code

1. Download this repository or clone it:
   ```bash
   git clone <repository-url>
   cd google-forms-mcp
   ```

2. Open a terminal (Mac/Linux) or PowerShell (Windows) in the project directory

### Step 2: Run the Installation Script

#### On Mac/Linux:
```bash
./install.sh
```

#### On Windows:
```powershell
.\install.ps1
```

If you get a permission error on Windows, run this first:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 3: Follow the Interactive Prompts

The installation script will guide you through:

#### 3.1 Installing uv Package Manager
The script will automatically install `uv` if you don't have it. Just press Enter when prompted.

#### 3.2 Installing Python Dependencies
This happens automatically. You'll see a progress indicator.

#### 3.3 Setting Up Google Cloud OAuth

**This is the most important step!** The script will guide you to create OAuth credentials:

1. **Open Google Cloud Console:**
   - Go to https://console.cloud.google.com
   - Sign in with your Google account

2. **Create a New Project:**
   - Click "Select a project" → "New Project"
   - Name it "Google Forms MCP" (or whatever you like)
   - Click "Create"

3. **Enable Required APIs:**
   - In the left sidebar, click "APIs & Services" → "Library"
   - Search for "Google Forms API" → Click it → Click "Enable"
   - Search for "Google Drive API" → Click it → Click "Enable"

4. **Create OAuth Credentials:**
   - Go to "APIs & Services" → "Credentials"
   - Click "+ CREATE CREDENTIALS" → "OAuth client ID"
   - If prompted to configure consent screen:
     - User Type: External → Click "Create"
     - App name: "Google Forms MCP"
     - User support email: Your email
     - Developer contact: Your email
     - Click "Save and Continue" (skip scopes and test users)
   - Back to creating OAuth client ID:
     - Application type: "Desktop app"
     - Name: "Google Forms MCP"
     - Click "Create"

5. **Copy Your Credentials:**
   - You'll see a popup with your Client ID and Client Secret
   - **Copy the Client ID** (looks like: `123456-abcdef.apps.googleusercontent.com`)
   - **Copy the Client Secret** (looks like: `GOCSPX-abcdef123456`)

6. **Paste into the Installation Script:**
   - The script will ask for your Client ID → Paste it
   - The script will ask for your Client Secret → Paste it

#### 3.4 Authorize Access

- The script will open your browser
- Sign in with your Google account
- Click "Allow" to grant permissions
- The browser will show "Authorization successful" - you can close it
- The script will automatically save your credentials

#### 3.5 Configure Cursor

The script will automatically configure Cursor IDE. Just restart Cursor when done!

### Step 4: Test the Installation

1. **Restart Cursor IDE**
2. **Open any project in Cursor**
3. **Open the AI chat** (Cmd+L on Mac, Ctrl+L on Windows)
4. **Ask Cursor:** `"List my Google Forms"`

If everything is set up correctly, Cursor will use the MCP server to fetch your Google Forms!

## Troubleshooting

### "uv command not found" Error

**Solution:** Close and reopen your terminal/PowerShell, then run the installation script again.

### Browser Doesn't Open During Token Generation

**Solution:**
1. Press Ctrl+C to cancel
2. Run manually: `uv run python get_token.py`
3. Copy the URL from the terminal and paste it in your browser

### Cursor Can't Find the MCP Server

**Check the configuration file:**

- **Mac/Linux:** `~/.cursor/mcp.json`
- **Windows:** `%APPDATA%\Cursor\User\globalStorage\mcp.json`

Make sure the path points to where you installed the project.

### "OAuth Error" or "Invalid Credentials"

**Solution:**
1. Delete the `.env` file in the project directory
2. Run the installation script again
3. Make sure you enabled both Google Forms API and Google Drive API

### Still Having Issues?

1. **Test the server manually:**
   ```bash
   uv run python main.py
   ```
   If you see "Server running on stdio", the server works!

2. **Check your credentials file:**
   - Open the `.env` file in the project directory
   - Make sure all three lines are filled in (CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN)

3. **Verify API permissions:**
   - Go to https://myaccount.google.com/permissions
   - Make sure "Google Forms MCP" is listed
   - If not, re-run the installation script

## What Can You Do With It?

Once installed, you can ask Cursor to:

- **Create forms:** `"Create a customer feedback form with name, email, and rating questions"`
- **List forms:** `"Show me all my Google Forms"`
- **Add questions:** `"Add a multiple choice question about satisfaction levels"`
- **Export responses:** `"Export the responses from my feedback form to CSV"`
- **Update forms:** `"Change the title of my form to 'Employee Survey 2024'"`
- **Get links:** `"Give me the public link for my form"`

And much more! The MCP server provides 15 different tools for managing your Google Forms.

## Security Notes

- Your credentials are stored in the `.env` file in the project directory
- This file is automatically excluded from git (won't be uploaded if you share the code)
- The refresh token gives full access to your Google Forms
- To revoke access anytime, go to https://myaccount.google.com/permissions

## Next Steps

- Read the [README.md](README.md) for complete documentation
- Check out example use cases
- Explore all 15 available tools

**Enjoy automating your Google Forms!** 🎉
