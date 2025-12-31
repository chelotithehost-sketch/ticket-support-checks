import streamlit as st
import requests
import json
from datetime import datetime
import socket
import ssl
import whois
from whois import exceptions
import re
import google.generativeai as genai
import random

# Page Configuration
st.set_page_config(
    page_title="Tech Support Toolkit",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configure Gemini API - Set your API key in Streamlit secrets or environment
# You can set this in .streamlit/secrets.toml as: GEMINI_API_KEY = "your-key-here"
try:
    GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
except:
    GEMINI_API_KEY = ""

# Gemini model rotation list
GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
]

# Custom CSS for compact buttons and better styling
st.markdown("""
<style>
    /* Compact buttons */
    .stButton > button {
        width: 100%;
        background-color: #4A9B8E;
        color: white;
        border: none;
        padding: 0.4rem 0.6rem;
        font-weight: 500;
        font-size: 0.85rem;
        border-radius: 6px;
        height: 42px;
    }
    .stButton > button:hover {
        background-color: #3A8B7E;
        border-color: #3A8B7E;
    }
    
    /* Horizontal menu styling */
    .horizontal-menu {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        padding: 0.5rem 0;
        border-bottom: 2px solid #4A9B8E;
        margin-bottom: 1.5rem;
    }
    
    /* Make external links more visible */
    .stMarkdown a {
        color: #4A9B8E !important;
        font-weight: 600;
    }
    
    /* Compact metrics */
    [data-testid="stMetricValue"] {
        font-size: 1.2rem;
    }
    
    /* Smaller text areas */
    .stTextArea textarea {
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR: TICKET ANALYZER & CHECKLIST ---
st.sidebar.title("🎫 Ticket Analyzer")

with st.sidebar.expander("🤖 AI Ticket Analysis", expanded=False):
    st.markdown("""
    Paste the ticket thread below and get:
    - Issue identification
    - Suggested checks
    - Recommended response
    """)
    
    ticket_thread = st.text_area(
        "Paste ticket conversation:",
        height=200,
        placeholder="Paste the entire ticket thread here...",
        key="ticket_input"
    )
    
    if st.button("🔍 Analyze Ticket", key="analyze_btn", use_container_width=True):
        if ticket_thread:
            with st.spinner("AI is analyzing the ticket..."):
                # AI Analysis using Gemini
                analysis_result = analyze_ticket_with_ai(ticket_thread)
                
                if analysis_result:
                    st.success("✅ Analysis Complete")
                    
                    st.markdown("**Issue Type:**")
                    st.info(analysis_result.get('issue_type', 'General Support'))
                    
                    st.markdown("**Suggested Checks:**")
                    checks = analysis_result.get('checks', [])
                    for check in checks:
                        st.markdown(f"- {check}")
                    
                    st.markdown("**Recommended Actions:**")
                    actions = analysis_result.get('actions', [])
                    for action in actions:
                        st.markdown(f"- {action}")
                    
                    with st.expander("📝 Suggested Response"):
                        response = analysis_result.get('response_template', '')
                        st.text_area("Copy this response:", value=response, height=300, key="response_template")
                else:
                    st.error("❌ Analysis failed. Please check API key configuration.")
        else:
            st.warning("Please paste a ticket thread first")

st.sidebar.divider()

# --- SIDEBAR CHECKLIST ---
with st.sidebar.expander("📋 Support Checklist", expanded=True):
    st.markdown("""
    ### Quick Start (60 sec)
    1. ✅ Check priority (VIP?)
    2. ✅ Confirm identity (PIN if guest)
    3. ✅ Check service status
    4. ✅ Add tags
    
    ### Service Health Check
    - **Domain**: Active? Expired?
    - **Hosting**: Active/Suspended?
    - **Nameservers**: Correct NS?
      - cPanel: ns1-ns4.host-ww.net
      - DirectAdmin: dan1-dan2.host-ww.net
    
    ### Troubleshooting
    **Email Issues:**
    - Check MX/SPF/DKIM/DMARC
    - Check if IP blocked
    
    **Website Issues:**
    - Verify A record
    - Check redirects
    - Review error logs
    
    ### Tags
    Mail | Hosting | DNS | Billing | VPS
    """)

st.sidebar.divider()
st.sidebar.caption("💡 Use checklist while working tickets")

# --- AI ANALYSIS FUNCTION ---
def analyze_ticket_with_ai(ticket_text):
    """Analyze ticket using Google Gemini AI with model rotation"""
    
    if not GEMINI_API_KEY:
        # Fallback to keyword-based analysis if no API key
        return analyze_ticket_keywords(ticket_text)
    
    try:
        # Rotate through available models
        model_name = random.choice(GEMINI_MODELS)
        model = genai.GenerativeModel(model_name)
        
        prompt = f"""You are a technical support expert analyzing a customer support ticket. 

Analyze the following ticket and provide:
1. Issue Type (one of: Email Issue, Website Issue, Domain/DNS Issue, SSL Issue, Billing Issue, VPS/Server Issue, or General Support)
2. List of specific technical checks to perform (3-5 items)
3. List of recommended actions to resolve the issue (3-5 items)
4. A professional response template that the support agent can use

Ticket Content:
{ticket_text}

Provide your response in this exact JSON format:
{{
    "issue_type": "Issue Type Here",
    "checks": ["check 1", "check 2", "check 3"],
    "actions": ["action 1", "action 2", "action 3"],
    "response_template": "Full response text here"
}}

Make the response professional, empathetic, and actionable. Include placeholders like [Client Name] where appropriate."""

        response = model.generate_content(prompt)
        
        # Parse the JSON response
        result_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if result_text.startswith("```json"):
            result_text = result_text.replace("```json", "").replace("```", "").strip()
        elif result_text.startswith("```"):
            result_text = result_text.replace("```", "").strip()
        
        result = json.loads(result_text)
        return result
        
    except Exception as e:
        st.error(f"AI Analysis error: {str(e)}")
        # Fallback to keyword analysis
        return analyze_ticket_keywords(ticket_text)

def analyze_ticket_keywords(ticket_text):
    """Fallback keyword-based analysis when AI is unavailable"""
    ticket_lower = ticket_text.lower()
    
    result = {
        'issue_type': 'General Support',
        'checks': [],
        'actions': [],
        'response_template': ''
    }
    
    # Email issues
    if any(word in ticket_lower for word in ['email', 'mail', 'smtp', 'imap', 'pop3', 'cannot send', 'cannot receive']):
        result['issue_type'] = '📧 Email Issue'
        result['checks'] = [
            'Check MX records using DNS Records tool',
            'Verify SPF/DKIM/DMARC records',
            'Check if client IP is blocked',
            'Review email logs in cPanel/DirectAdmin'
        ]
        result['actions'] = [
            'Use DNS Records tool to verify MX configuration',
            'Check client IP for blocks',
            'Verify email account exists'
        ]
        result['response_template'] = """Hi [Client Name],

Thank you for contacting us about your email issue.

I've reviewed your account and checked:
- MX records and DNS configuration
- Email authentication (SPF/DKIM)
- Server logs

[Describe what you found and what action was taken]

The issue should be resolved within [timeframe]. Please test and let me know if you need further assistance.

Best regards,
[Your Name]
HostAfrica Support"""
    
    # Website issues
    elif any(word in ticket_lower for word in ['website', 'site down', 'not loading', '404', '500', 'error']):
        result['issue_type'] = '🌐 Website Issue'
        result['checks'] = [
            'Check domain A record',
            'Verify domain expiration',
            'Check nameservers',
            'Verify hosting is active'
        ]
        result['actions'] = [
            'Use DNS Records tool to verify A record',
            'Use WHOIS Check to confirm domain status',
            'Check hosting status in WHMCS'
        ]
        result['response_template'] = """Hi [Client Name],

I've investigated your website issue.

Status Check:
- Domain: [Active/Issue]
- DNS: [Resolving/Issue]
- Hosting: [Active/Suspended]

[Explain the issue and resolution]

Your website should be accessible within [timeframe].

Best regards,
[Your Name]
HostAfrica Support"""
    
    # Domain issues
    elif any(word in ticket_lower for word in ['domain', 'nameserver', 'dns', 'propagation']):
        result['issue_type'] = '🔧 Domain/DNS Issue'
        result['checks'] = [
            'Check domain registration status',
            'Verify nameservers',
            'Check domain expiration',
            'Verify DNS propagation'
        ]
        result['actions'] = [
            'Use WHOIS Check tool',
            'Use DNS Records tool',
            'Update nameservers if needed'
        ]
        result['response_template'] = """Hi [Client Name],

I've checked your domain configuration.

Current Status:
- Domain: [Status]
- Nameservers: [Status]
- Propagation: [Status]

[Explain actions taken]

DNS changes can take 4-24 hours to propagate globally.

Best regards,
[Your Name]
HostAfrica Support"""
    
    # SSL issues
    elif any(word in ticket_lower for word in ['ssl', 'https', 'certificate', 'secure']):
        result['issue_type'] = '🔒 SSL Certificate Issue'
        result['checks'] = [
            'Check SSL certificate status',
            'Verify certificate expiration',
            'Check domain pointing',
            'Verify SSL installation'
        ]
        result['actions'] = [
            'Use SSL Check tool',
            'Verify certificate validity',
            'Install/renew SSL if needed'
        ]
        result['response_template'] = """Hi [Client Name],

I've reviewed your SSL certificate.

Certificate Status:
- Validity: [Valid/Expired]
- Expiration: [Date]
- Installation: [Correct/Issue]

[Explain resolution]

Your website should show as secure within [timeframe].

Best regards,
[Your Name]
HostAfrica Support"""
    
    # Billing
    elif any(word in ticket_lower for word in ['invoice', 'payment', 'billing', 'suspended', 'renew']):
        result['issue_type'] = '💳 Billing Issue'
        result['checks'] = [
            'Check invoice status',
            'Verify service status',
            'Check payment method'
        ]
        result['actions'] = [
            'Review account in WHMCS',
            'Check unpaid invoices',
            'Verify suspension reason'
        ]
        result['response_template'] = """Hi [Client Name],

I've reviewed your account billing.

Account Status:
- Service: [Status]
- Balance: [Amount]
- Next Renewal: [Date]

[Action required from client]

Please let me know if you need payment assistance.

Best regards,
[Your Name]
HostAfrica Support"""
    
    else:
        result['checks'] = [
            'Verify client identity',
            'Check service status',
            'Review ticket history'
        ]
        result['actions'] = [
            'Request more details',
            'Check relevant services',
            'Review documentation'
        ]
        result['response_template'] = """Hi [Client Name],

Thank you for contacting HostAfrica Support.

To assist you better, I need some additional information:
[Questions to ask]

Once I have these details, I'll resolve your issue quickly.

Best regards,
[Your Name]
HostAfrica Support"""
    
    return result

# --- MAIN APP ---
st.title("🔧 Tech Support Toolkit")

# Compact Horizontal Menu Bar
st.markdown("### Quick Tools")
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    if st.button("🔑 PIN", use_container_width=True):
        st.session_state.tool = "PIN Checker"
        
with col2:
    if st.button("🔓 Unban", use_container_width=True):
        st.session_state.tool = "IP Unban"

with col3:
    if st.button("🗂️ DNS", use_container_width=True):
        st.session_state.tool = "DNS Records"

with col4:
    if st.button("🌐 WHOIS", use_container_width=True):
        st.session_state.tool = "WHOIS Check"

with col5:
    if st.button("🔍 IP Info", use_container_width=True):
        st.session_state.tool = "IP Lookup"

with col6:
    if st.button("📂 cPanel", use_container_width=True):
        st.session_state.tool = "cPanel List"

col7, col8, col9, col10, col11, col12 = st.columns(6)

with col7:
    if st.button("📍 My IP", use_container_width=True):
        st.session_state.tool = "My IP"

with col8:
    if st.button("🔄 NS Update", use_container_width=True):
        st.session_state.tool = "NS Updater"

with col9:
    if st.button("🔒 SSL", use_container_width=True):
        st.session_state.tool = "SSL Check"

with col10:
    if st.button("📚 Help", use_container_width=True):
        st.session_state.tool = "Knowledge Base"

with col11:
    if st.button("🧹 Flush DNS", use_container_width=True):
        st.session_state.tool = "Flush DNS"

with col12:
    # Empty column for spacing
    st.write("")

st.divider()

# Initialize session state
if 'tool' not in st.session_state:
    st.session_state.tool = "DNS Records"

# Tool content based on selection
tool = st.session_state.tool

# --- TOOL IMPLEMENTATIONS ---

# 1. PIN Checker
if tool == "PIN Checker":
    st.header("🔐 Identity & Verification")
    st.markdown("Verify client identity using their support PIN")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("Open the HostAfrica Admin Tool to verify client PINs")
    with col2:
        st.link_button("🔑 Open Tool", "https://my.hostafrica.com/admin/admin_tool/client-pin", use_container_width=True)

# 2. IP Unban Tool
elif tool == "IP Unban":
    st.header("🔓 Client Area IP Unban")
    st.markdown("Unban client IPs blocked from the client area")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("Remove IP blocks from the client area access")
    with col2:
        st.link_button("🛡️ Unban Tool", "https://my.hostafrica.com/admin/custom/scripts/unban/", use_container_width=True)

# 3. DNS Records
elif tool == "DNS Records":
    st.header("🗂️ DNS Record Analyzer")
    st.markdown("Check resolution, mail routing, and authentication records")
    
    domain_dns = st.text_input("Enter domain:", placeholder="example.com", key="dns_input")
    
    if st.button("🔍 Analyze", use_container_width=True):
        if domain_dns:
            domain_dns = domain_dns.strip().lower()
            
            with st.spinner(f"Analyzing DNS for {domain_dns}..."):
                issues, warnings, success_checks = [], [], []
                
                # A Records
                st.subheader("🌐 Web Resolution (A)")
                try:
                    a_res = requests.get(f"https://dns.google/resolve?name={domain_dns}&type=A", timeout=5).json()
                    if a_res.get('Answer'):
                        for r in a_res['Answer']: 
                            st.code(f"A: {r['data']}")
                        success_checks.append("A record found")
                    else:
                        issues.append("Missing A record")
                        st.error("❌ No A records")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

                # MX Records
                st.subheader("📧 Mail (MX)")
                try:
                    mx_res = requests.get(f"https://dns.google/resolve?name={domain_dns}&type=MX", timeout=5).json()
                    if mx_res.get('Answer'):
                        for r in mx_res['Answer']: 
                            st.code(f"MX: {r['data']}")
                        success_checks.append("MX configured")
                    else:
                        issues.append("No MX records")
                        st.error("❌ No MX records")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

                # TXT Records
                st.subheader("📝 Authentication (TXT)")
                try:
                    txt_res = requests.get(f"https://dns.google/resolve?name={domain_dns}&type=TXT", timeout=5).json()
                    if txt_res.get('Answer'):
                        found_spf = False
                        for r in txt_res['Answer']:
                            val = r['data'].strip('"')
                            st.code(f"TXT: {val[:100]}...")
                            if "v=spf1" in val: found_spf = True
                        
                        if found_spf:
                            success_checks.append("SPF found")
                        else:
                            warnings.append("No SPF")
                    else:
                        warnings.append("No TXT records")
                        st.warning("⚠️ No TXT records")
                except Exception as e:
                    st.warning(f"Error: {str(e)}")

                # Nameservers
                st.subheader("🖥️ Nameservers (NS)")
                try:
                    ns_res = requests.get(f"https://dns.google/resolve?name={domain_dns}&type=NS", timeout=5).json()
                    if ns_res.get('Answer'):
                        for r in ns_res['Answer']: 
                            st.code(f"NS: {r['data'].rstrip('.')}")
                        success_checks.append("NS configured")
                    else:
                        issues.append("No NS")
                        st.error("❌ No nameservers")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

                # Summary
                st.divider()
                st.subheader("📊 Summary")
                col_a, col_b = st.columns(2)
                with col_a:
                    if issues:
                        st.markdown("**❌ Issues:**")
                        for msg in issues: st.error(f"• {msg}")
                    if warnings:
                        st.markdown("**⚠️ Warnings:**")
                        for msg in warnings: st.warning(f"• {msg}")
                with col_b:
                    if success_checks:
                        st.markdown("**✅ Passed:**")
                        for msg in success_checks: st.success(f"• {msg}")
        else:
            st.warning("Enter a domain name")

# 4. WHOIS Check
elif tool == "WHOIS Check":
    st.header("🌐 Domain WHOIS Lookup")
    st.markdown("Check registration, expiration, and status")
    
    domain = st.text_input("Enter domain:", placeholder="example.com")
    
    if st.button("🔍 Check", use_container_width=True):
        if domain:
            domain = domain.strip().lower()
            issues, warnings, success_checks = [], [], []

            with st.spinner('Checking WHOIS...'):
                st.subheader("📝 Registration Info")
                
                try:
                    whois_data = whois.whois(domain)
                    
                    if whois_data and whois_data.domain_name:
                        st.success("✅ WHOIS retrieved")
                        success_checks.append("WHOIS OK")

                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Domain:** {domain}")
                            
                            if whois_data.registrar:
                                st.write(f"**Registrar:** {whois_data.registrar}")

                            status_list = whois_data.status
                            if status_list:
                                st.write("**Status:**")
                                if not isinstance(status_list, list):
                                    status_list = [status_list] if status_list else []
                                    
                                for status in status_list[:3]:
                                    status_lower = str(status).lower()
                                    if any(x in status_lower for x in ['ok', 'active']):
                                        st.success(f"✅ {status.split()[0]}")
                                    elif any(x in status_lower for x in ['hold', 'lock', 'suspended']):
                                        st.error(f"❌ {status.split()[0]}")
                                        issues.append(f"Status: {status.split()[0]}")
                                    elif 'expired' in status_lower:
                                        st.error(f"❌ {status.split()[0]}")
                                        issues.append("Expired")

                        with col2:
                            if whois_data.creation_date:
                                st.write(f"**Created:** {str(whois_data.creation_date).split()[0]}")
                            
                            if whois_data.expiration_date:
                                exp_date = whois_data.expiration_date
                                if isinstance(exp_date, list):
                                    exp_date = exp_date[0]
                                
                                st.write(f"**Expires:** {str(exp_date).split()[0]}")
                                
                                try:
                                    days_left = (exp_date - datetime.now().replace(microsecond=0)).days
                                    
                                    if days_left < 0:
                                        st.error(f"❌ Expired {abs(days_left)}d ago")
                                        issues.append("Domain expired")
                                    elif days_left < 30:
                                        st.error(f"⚠️ {days_left} days left")
                                        warnings.append("Expires soon")
                                    elif days_left < 90:
                                        st.warning(f"⚠️ {days_left} days")
                                    else:
                                        st.success(f"✅ {days_left} days")
                                except:
                                    pass
                        
                        if whois_data.name_servers:
                            st.write("**Nameservers:**")
                            for ns in whois_data.name_servers[:3]:
                                st.caption(f"• {str(ns).lower().rstrip('.')}")

                    else:
                        st.warning("⚠️ No WHOIS data")
                        
                except Exception as e:
                    st.error(f"❌ WHOIS failed: {type(e).__name__}")
                    st.info(f"Try: https://who.is/whois/{domain}")

                # Summary
                if issues or warnings:
                    st.divider()
                    st.subheader("📊 Summary")
                    for issue in issues:
                        st.error(f"• {issue}")
                    for warning in warnings:
                        st.warning(f"• {warning}")
        else:
            st.warning("Enter a domain")

# 5. IP Lookup
elif tool == "IP Lookup":
    st.header("🔍 IP Address Lookup")
    st.markdown("Get geolocation and ISP information")
    
    ip_input = st.text_input("Enter IP:", placeholder="8.8.8.8")
    
    if st.button("🔍 Lookup", use_container_width=True):
        if ip_input:
            ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
            if not re.match(ip_pattern, ip_input):
                st.error("❌ Invalid IP format")
            else:
                with st.spinner(f"Looking up {ip_input}..."):
                    try:
                        geo_data = None
                        try:
                            response = requests.get(f"https://ipapi.co/{ip_input}/json/", timeout=5)
                            if response.status_code == 200:
                                geo_data = response.json()
                        except:
                            pass
                        
                        if not geo_data or geo_data.get('error'):
                            response = requests.get(f"http://ip-api.com/json/{ip_input}", timeout=5)
                            if response.status_code == 200:
                                fallback_data = response.json()
                                if fallback_data.get('status') == 'success':
                                    geo_data = {
                                        'ip': ip_input,
                                        'city': fallback_data.get('city'),
                                        'region': fallback_data.get('regionName'),
                                        'country_name': fallback_data.get('country'),
                                        'org': fallback_data.get('isp'),
                                        'timezone': fallback_data.get('timezone'),
                                    }
                        
                        if geo_data and not geo_data.get('error'):
                            st.success(f"✅ Found: {ip_input}")
                            
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("🌐 IP", ip_input)
                                st.metric("🏙️ City", geo_data.get('city', 'N/A'))
                            
                            with col2:
                                st.metric("🗺️ Region", geo_data.get('region', 'N/A'))
                                st.metric("🌍 Country", geo_data.get('country_name', 'N/A'))
                            
                            with col3:
                                st.metric("📡 ISP", geo_data.get('org', 'N/A')[:20])
                                st.metric("🕐 TZ", geo_data.get('timezone', 'N/A'))
                        else:
                            st.error("❌ No data found")
                            
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        else:
            st.warning("⚠️ Enter an IP")

# 6. cPanel List
elif tool == "cPanel List":
    st.header("📂 cPanel Accounts")
    st.markdown("View all cPanel hosting accounts")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("Access the cPanel account list")
    with col2:
        st.link_button("📂 Open", "https://my.hostafrica.com/admin/custom/scripts/custom_tests/listaccounts.php", use_container_width=True)

# 7. My IP
elif tool == "My IP":
    st.header("📍 My IP Address")
    st.markdown("Find your current public IP")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("Open HostAfrica IP detector")
    with col2:
        st.link_button("🔍 Get IP", "https://ip.hostafrica.com/", use_container_width=True)

# 8. NS Updater
elif tool == "NS Updater":
    st.header("🔄 Nameserver Updater")
    st.markdown("Bulk update nameservers")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("Bulk update nameservers in WHMCS")
    with col2:
        st.link_button("🔄 Open", "https://my.hostafrica.com/admin/addonmodules.php?module=nameserv_changer", use_container_width=True)

# 9. SSL Check
elif tool == "SSL Check":
    st.header("🔒 SSL Certificate")
    st.markdown("Verify SSL validity and expiration")
    
    domain_ssl = st.text_input("Enter domain:", placeholder="example.com")
    
    if st.button("🔍 Check", use_container_width=True):
        if domain_ssl:
            domain_ssl = domain_ssl.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0].strip()
            
            with st.spinner(f"Checking SSL for {domain_ssl}..."):
                try:
                    context = ssl.create_default_context()
                    with socket.create_connection((domain_ssl, 443), timeout=10) as sock:
                        with context.wrap_socket(sock, server_hostname=domain_ssl) as secure_sock:
                            cert = secure_sock.getpeercert()
                            
                            st.success(f"✅ SSL valid for {domain_ssl}")
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.subheader("📋 Details")
                                subject = dict(x[0] for x in cert['subject'])
                                st.write("**Issued To:**", subject.get('commonName', 'N/A'))
                                
                                issuer = dict(x[0] for x in cert['issuer'])
                                st.write("**Issuer:**", issuer.get('commonName', 'N/A'))
                                
                            with col2:
                                st.subheader("📅 Validity")
                                not_after = cert.get('notAfter')
                                st.write("**Expires:**", not_after)
                                
                                if not_after:
                                    try:
                                        expiry_date = datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z')
                                        days_remaining = (expiry_date - datetime.now()).days
                                        
                                        if days_remaining > 30:
                                            st.success(f"✅ {days_remaining} days")
                                        elif days_remaining > 0:
                                            st.warning(f"⚠️ {days_remaining} days")
                                        else:
                                            st.error(f"❌ Expired")
                                    except:
                                        pass
                            
                            if 'subjectAltName' in cert:
                                st.subheader("🌐 Covered Domains")
                                sans = [san[1] for san in cert['subjectAltName']]
                                for san in sans[:5]:
                                    st.caption(f"• {san}")
                                if len(sans) > 5:
                                    st.info(f"+ {len(sans) - 5} more")
                                
                except socket.gaierror:
                    st.error(f"❌ Cannot resolve: {domain_ssl}")
                except socket.timeout:
                    st.error(f"⏱️ Timeout")
                except ssl.SSLError as ssl_err:
                    st.error(f"❌ SSL Error: {str(ssl_err)}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("⚠️ Enter a domain")

# 10. Knowledge Base
elif tool == "Knowledge Base":
    st.header("📚 Help Center")
    st.markdown("Search documentation and guides")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("Access HostAfrica help center")
    with col2:
        st.link_button("📚 Open", "https://help.hostafrica.com", use_container_width=True)

# 11. Flush DNS
elif tool == "Flush DNS":
    st.header("🧹 Flush Google DNS")
    st.markdown("Clear Google's DNS cache")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("Force Google DNS to fetch fresh records")
    with col2:
        st.link_button("🧹 Flush", "https://dns.google/cache", use_container_width=True)
