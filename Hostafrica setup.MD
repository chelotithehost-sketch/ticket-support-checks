# HostAfrica Tech Support Toolkit - Setup Guide

## 🎯 Key Features

### ✅ **HostAfrica Knowledge Base Integration**
- AI prioritizes solutions from help.hostafrica.com
- Automatically links to relevant KB articles
- Includes HostAfrica-specific nameservers and configurations
- References hostafrica.co.za/faq/ for billing questions

### ✅ **AI-Powered Ticket Analysis**
- Uses Google Gemini 2.5 Flash models
- Trained on HostAfrica services and procedures
- Provides KB article links with every analysis
- Automatic model rotation to handle rate limits

### ✅ **Built-in HostAfrica Knowledge**
The AI knows about:
- **Nameservers**: ns1-4.host-ww.net (cPanel), dan1-2.host-ww.net (DirectAdmin)
- **Services**: Web hosting, domains, email, SSL, VPS
- **Tools**: WHMCS, cPanel, DirectAdmin
- **Resources**: help.hostafrica.com, my.hostafrica.com

## 📦 Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Get Gemini API Key (Free)
1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy your API key

### 3. Configure API Key

Create `.streamlit/secrets.toml`:
```toml
GEMINI_API_KEY = "your-api-key-here"
```

### 4. Run Application
```bash
streamlit run hostafrica_app.py
```

## 🤖 How AI KB Integration Works

### When analyzing a ticket, the AI:

1. **Identifies Issue Type**
   - Email, Website, Domain, SSL, Billing, VPS

2. **Searches HostAfrica Knowledge Base**
   - Automatically finds relevant articles
   - Matches keywords from ticket to KB categories

3. **Provides HostAfrica-Specific Solutions**
   - References correct nameservers for hosting type
   - Links to help.hostafrica.com articles
   - Includes HostAfrica tools and portals

4. **Generates Response with KB Links**
   - Professional response template
   - Direct links to relevant KB articles
   - HostAfrica branding and resources

### Example AI Analysis Output:

```
Issue Type: 📧 Email Issue

📚 Relevant KB Articles:
- Email Configuration Guide (https://help.hostafrica.com/en/category/email-1fmw9ki/)
- Email Troubleshooting (https://help.hostafrica.com/en/category/email-1fmw9ki/)

Suggested Checks:
- Check MX records using DNS Records tool
- Verify SPF/DKIM/DMARC records
- Check if client IP is blocked

Recommended Actions:
- Use DNS Records tool to verify MX configuration
- Review HostAfrica email setup guide
- Check hosting status in WHMCS

Suggested Response:
"Hi [Client Name],

Thank you for contacting HostAfrica Support about your email issue.

I've reviewed your account and checked:
- MX records and DNS configuration
- Email authentication (SPF/DKIM)

For email configuration help, please refer to our guide at:
https://help.hostafrica.com/en/category/email-1fmw9ki/

Best regards,
HostAfrica Support Team"
```

## 📚 Built-in Knowledge Base Categories

### Email Issues
- Email Configuration Guide
- Email Troubleshooting  
- SPF and DKIM Setup
- Keywords: email, mail, smtp, imap, pop3, outlook

### Domain Issues
- Domain Management
- Nameserver Configuration
- Domain Transfer Guide
- Keywords: domain, nameserver, dns, transfer

### Web Hosting
- cPanel Hosting Guide
- Website Troubleshooting
- DirectAdmin Guide
- Keywords: cpanel, hosting, website, ftp

### SSL Certificates
- SSL Certificate Installation
- Free SSL (Let's Encrypt)
- Keywords: ssl, https, certificate, secure

### Billing
- Billing and Payments
- Payment Methods
- Keywords: invoice, payment, billing, renew

### VPS/Server
- VPS Management
- Server Management
- Keywords: vps, server, dedicated, ssh

## 🔧 HostAfrica-Specific Configurations

### Correct Nameservers
The AI automatically checks for:
- **cPanel**: ns1.host-ww.net, ns2.host-ww.net, ns3.host-ww.net, ns4.host-ww.net
- **DirectAdmin**: dan1.host-ww.net, dan2.host-ww.net

### HostAfrica Resources
AI references:
- Main site: hostafrica.co.za
- Help center: help.hostafrica.com
- Client area: my.hostafrica.com
- IP checker: ip.hostafrica.com
- FAQ: hostafrica.co.za/faq/

## ⚙️ Advanced Configuration

### Custom KB Articles
To add more KB articles, edit the `HOSTAFRICA_KB` dictionary in the code:

```python
HOSTAFRICA_KB = {
    'your_category': [
        {
            'title': 'Article Title',
            'url': 'https://help.hostafrica.com/article-url',
            'keywords': ['keyword1', 'keyword2', 'keyword3']
        }
    ]
}
```

### Model Selection
Current models with rotation:
- `gemini-2.5-flash` (3 RPM, 64K TPM)
- `gemini-2.5-flash-lite` (10 RPM, 112K TPM)

### Fallback Mode
If AI is unavailable:
- Keyword-based analysis still works
- KB articles still linked based on keywords
- Response templates still generated
- No API key required for fallback

## 🎯 Usage Tips

### For Best Results:

1. **Include Full Context**
   - Paste entire ticket thread
   - Include client's issue description
   - Add any error messages

2. **Let AI Find KB Articles**
   - AI automatically searches knowledge base
   - Links most relevant articles
   - Prioritizes HostAfrica resources

3. **Use Suggested Checks**
   - Follow the recommended diagnostic steps
   - Use toolkit tools mentioned in checks
   - Reference linked KB articles

4. **Customize Response**
   - Use template as starting point
   - Add specific details found
   - Keep KB links in response

## 🔒 Security

**Never commit API keys to version control!**

Add to `.gitignore`:
```
.streamlit/secrets.toml
.env
*.env
```

## 📊 Rate Limits

Free Gemini API tier:
- gemini-2.5-flash: 3 requests/minute
- gemini-2.5-flash-lite: 10 requests/minute
- Automatic rotation prevents limits
- Fallback to keyword analysis if exceeded

## 🆘 Troubleshooting

### AI not finding KB articles?
- Check keywords in HOSTAFRICA_KB match ticket content
- Add more keywords to existing categories
- Verify URLs are correct

### Wrong nameservers suggested?
- AI knows both cPanel and DirectAdmin nameservers
- Specify hosting type in ticket for best results

### API rate limit errors?
- App automatically rotates between models
- Fallback analysis works without API
- Consider upgrading API plan for heavy use

## 📞 Support

For HostAfrica toolkit questions:
- Check help.hostafrica.com
- Contact HostAfrica support team
- Review ticket check guide

Happy troubleshooting! 🔧
