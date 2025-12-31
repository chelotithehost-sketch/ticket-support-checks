# Tech Support Toolkit - Setup Instructions

## Features
✅ Compact horizontal menu with 11 quick tools
✅ AI-powered ticket analysis using Google Gemini
✅ Automatic model rotation (gemini-2.5-flash, gemini-2.5-flash-lite)
✅ Smaller, more efficient buttons and layout
✅ Support checklist in sidebar

## Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Gemini API Key

**Option A: Using Streamlit Secrets (Recommended)**
1. Create folder: `.streamlit/` in your project directory
2. Create file: `.streamlit/secrets.toml`
3. Add your API key:
```toml
GEMINI_API_KEY = "your-actual-api-key-here"
```

**Get your free API key:**
- Visit: https://makersuite.google.com/app/apikey
- Sign in with Google account
- Click "Create API Key"
- Copy and paste into secrets.toml

**Option B: Using Environment Variable**
```bash
export GEMINI_API_KEY="your-api-key-here"
```

### 3. Run the App
```bash
streamlit run final_app.py
```

## How AI Ticket Analysis Works

1. **Paste Ticket Thread** - Agent copies entire ticket conversation into sidebar
2. **Click Analyze** - AI processes the ticket using Gemini
3. **Get Recommendations:**
   - Issue type identification (Email, Website, DNS, SSL, Billing, etc.)
   - Specific checks to perform
   - Recommended actions
   - Pre-written response template

4. **Model Rotation** - Automatically rotates between:
   - `gemini-2.5-flash` (3 RPM, 64K TPM)
   - `gemini-2.5-flash-lite` (10 RPM, 112K TPM)

## Fallback Behavior

If no API key is configured, the system automatically falls back to keyword-based analysis:
- Still identifies issue types
- Provides relevant checklists
- Generates response templates
- Works offline

## Button Layout

**Row 1:**
🔑 PIN | 🔓 Unban | 🗂️ DNS | 🌐 WHOIS | 🔍 IP Info | 📂 cPanel

**Row 2:**
📍 My IP | 🔄 NS Update | 🔒 SSL | 📚 Help | 🧹 Flush DNS | (empty)

## File Structure
```
your-project/
├── final_app.py          # Main application
├── requirements.txt      # Python dependencies
├── .streamlit/
│   ├── secrets.toml     # API key (DO NOT commit to git!)
│   └── config.toml      # App theme (optional)
└── .gitignore           # Exclude secrets.toml
```

## Tips

1. **Compact Design** - Buttons are smaller (42px height) to fit more on screen
2. **Responsive** - Works on different screen sizes
3. **AI Analysis** - Best with Gemini API key, but works without it
4. **Model Rotation** - Automatically switches models to avoid rate limits
5. **Support Checklist** - Always available in sidebar for reference

## Troubleshooting

**AI Analysis not working?**
- Check API key is correctly set in `.streamlit/secrets.toml`
- Verify API key is valid at https://makersuite.google.com/app/apikey
- App will fallback to keyword analysis if API fails

**Buttons not visible?**
- Check your theme settings
- Try the provided config.toml with eye-friendly colors

**Rate Limit Errors?**
- App automatically rotates between models
- Free tier limits: 3-10 requests per minute
- Fallback analysis works without API

## Security Note

⚠️ **Never commit `.streamlit/secrets.toml` to git!**

Add to your `.gitignore`:
```
.streamlit/secrets.toml
*.env
.env
```

## Support

For HostAfrica-specific tools:
- PIN Checker: Verify client identity
- IP Unban: Remove IP blocks
- DNS/WHOIS: Check domain configuration
- SSL Check: Verify certificates
- cPanel List: View hosting accounts

Happy troubleshooting! 🔧
