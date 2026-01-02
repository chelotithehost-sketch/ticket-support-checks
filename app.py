import streamlit as st
import requests
import json
from datetime import datetime
import socket
import ssl
import whois
from whois import exceptions
import re
import random

# Page Configuration
st.set_page_config(
    page_title="Tech Support Toolkit",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configure Gemini API
GEMINI_API_KEY = ""
try:
    GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
    if GEMINI_API_KEY:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
except:
    pass

# Gemini models
GEMINI_MODELS = ["gemini-2.5-flash", "gemini-2.5-flash-lite"]

# Custom CSS
st.markdown("""
<style>
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
    }
    .stMarkdown a {
        color: #4A9B8E !important;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# KB Database
HOSTAFRICA_KB = {
    'hosting': [
        {'title': 'cPanel Hosting Guide', 'url': 'https://help.hostafrica.com/en/category/web-hosting-b01r28/',
         'keywords': ['cpanel', 'hosting', 'login', 'access', 'recaptcha', 'captcha']},
    ],
    'email': [
        {'title': 'Email Configuration', 'url': 'https://help.hostafrica.com/en/category/email-1fmw9ki/',
         'keywords': ['email', 'mail', 'smtp']},
    ],
    'domain': [
        {'title': 'Domain Management', 'url': 'https://help.hostafrica.com/en/category/domains-1yz6z58/',
         'keywords': ['domain', 'nameserver', 'dns']},
    ],
}

def search_kb_articles(keywords):
    """Search KB for relevant articles"""
    articles = []
    keywords_lower = keywords.lower()
    for category, items in HOSTAFRICA_KB.items():
        for item in items:
            if any(k in keywords_lower for k in item['keywords']):
                if item not in articles:
                    articles.append(item)
    return articles[:3]

def analyze_ticket_with_ai(ticket_text):
    """Analyze ticket with AI or keywords"""
    if not GEMINI_API_KEY:
        return analyze_ticket_keywords(ticket_text)
    
    try:
        import google.generativeai as genai
        model = genai.GenerativeModel(random.choice(GEMINI_MODELS))
        
        prompt = f"""Analyze this HostAfrica support ticket and respond in JSON:

Ticket: {ticket_text}

JSON format:
{{
    "issue_type": "Type",
    "checks": ["check1", "check2"],
    "actions": ["action1", "action2"],
    "response_template": "Response text",
    "kb_topics": ["topic1"]
}}"""

        response = model.generate_content(prompt)
        text = response.text.strip().replace("```json", "").replace("```", "").strip()
        result = json.loads(text)
        result['kb_articles'] = search_kb_articles(ticket_text)
        return result
    except:
        return analyze_ticket_keywords(ticket_text)

def analyze_ticket_keywords(ticket_text):
    """Keyword-based analysis"""
    ticket_lower = ticket_text.lower()
    result = {
        'issue_type': 'General Support',
        'checks': [],
        'actions': [],
        'response_template': '',
        'kb_articles': []
    }
    
    # cPanel login issues
    if any(w in ticket_lower for w in ['cpanel', 'login', 'recaptcha', 'captcha', 'access']):
        result['issue_type'] = '🔐 cPanel Access Issue'
        result['checks'] = [
            'Check if client IP is blocked',
            'Verify hosting account is active',
            'Check for failed login attempts',
            'Verify correct cPanel URL'
        ]
        result['actions'] = [
            'Use IP Unban tool to remove blocks',
            'Check client IP with IP Lookup',
            'Clear browser cache',
            'Try incognito mode'
        ]
        
        # Extract IP if present
        ip_match = re.search(r'IP Address:\s*(\d+\.\d+\.\d+\.\d+)', ticket_text)
        client_ip = ip_match.group(1) if ip_match else 'client IP'
        
        result['response_template'] = f"""Hi there,

Thank you for contacting HostAfrica Support regarding your cPanel login issue.

I can see you're having trouble with the reCAPTCHA verification. This is usually caused by IP address blocking due to multiple login attempts.

**Your IP**: {client_ip}

**I've taken these steps:**
- Checked your account status: Active
- Reviewed IP blocks on the server
- Removed your IP from the block list

**Please try these steps:**
1. Clear your browser cache and cookies
2. Try accessing cPanel in incognito/private window
3. If issue persists, try a different browser
4. Wait 15-30 minutes after multiple failed attempts

**cPanel Access:**
Your cPanel URL: https://yourdomain.com:2083

For cPanel access help, visit:
https://help.hostafrica.com/en/category/web-hosting-b01r28/

The IP block should be lifted within 15-30 minutes. Please let me know if you continue experiencing issues.

Best regards,
[Your Name]
HostAfrica Support Team"""
        result['kb_articles'] = search_kb_articles('cpanel login')
    
    # Email
    elif any(w in ticket_lower for w in ['email', 'mail', 'smtp']):
        result['issue_type'] = '📧 Email Issue'
        result['checks'] = ['Check MX records', 'Verify SPF/DKIM', 'Check IP blocks']
        result['actions'] = ['Use DNS tool', 'Check IP blocks']
        result['response_template'] = """Hi [Client],

Thank you for contacting HostAfrica about your email issue.

I've checked:
- MX records
- Email authentication

[Action taken]

For email help: https://help.hostafrica.com/en/category/email-1fmw9ki/

Best regards,
HostAfrica Support"""
        result['kb_articles'] = search_kb_articles('email')
    
    # Website
    elif any(w in ticket_lower for w in ['website', 'site', '404', '500']):
        result['issue_type'] = '🌐 Website Issue'
        result['checks'] = ['Check A record', 'Verify nameservers', 'Check hosting']
        result['actions'] = ['Use DNS tool', 'Check WHOIS']
        result['response_template'] = """Hi [Client],

I've investigated your website issue.

Status:
- Domain: [Status]
- DNS: [Status]

[Action taken]

For help: https://help.hostafrica.com/en/category/web-hosting-b01r28/

Best regards,
HostAfrica Support"""
        result['kb_articles'] = search_kb_articles('website')
    
    else:
        result['checks'] = ['Verify identity', 'Check service status']
        result['actions'] = ['Request more details']
        result['response_template'] = """Hi [Client],

Thank you for contacting HostAfrica Support.

To assist better, I need more information:
[Questions]

Visit: https://help.hostafrica.com/

Best regards,
HostAfrica Support"""
    
    return result

# SIDEBAR
st.sidebar.title("🎫 Ticket Analyzer")

with st.sidebar.expander("🤖 AI Analysis", expanded=False):
    st.markdown("Paste ticket for analysis")
    
    ticket_thread = st.text_area(
        "Ticket conversation:",
        height=200,
        placeholder="Paste ticket here...",
        key="ticket_input"
    )
    
    if st.button("🔍 Analyze", key="analyze_btn", use_container_width=True):
        if ticket_thread:
            with st.spinner("Analyzing..."):
                analysis = analyze_ticket_with_ai(ticket_thread)
                
                if analysis:
                    st.success("✅ Complete")
                    
                    st.markdown("**Issue Type:**")
                    st.info(analysis.get('issue_type', 'General'))
                    
                    kb = analysis.get('kb_articles', [])
                    if kb:
                        st.markdown("**📚 KB Articles:**")
                        for a in kb:
                            st.markdown(f"- [{a['title']}]({a['url']})")
                    
                    st.markdown("**Checks:**")
                    for c in analysis.get('checks', []):
                        st.markdown(f"- {c}")
                    
                    st.markdown("**Actions:**")
                    for a in analysis.get('actions', []):
                        st.markdown(f"- {a}")
                    
                    with st.expander("📝 Response"):
                        resp = analysis.get('response_template', '')
                        st.text_area("Copy:", value=resp, height=300, key="resp")
        else:
            st.warning("Paste ticket first")

st.sidebar.divider()

with st.sidebar.expander("📋 Checklist", expanded=True):
    st.markdown("""
    ### Quick Start
    1. ✅ Check priority
    2. ✅ Verify identity
    3. ✅ Check service status
    4. ✅ Add tags
    
    ### Service Check
    - Domain: Active?
    - Hosting: Active/Suspended?
    - NS: ns1-4.host-ww.net
    
    ### Troubleshooting
    **Email**: MX/SPF/DKIM
    **Website**: A record, NS
    **cPanel**: IP blocks
    
    ### Tags
    Mail | Hosting | DNS | Billing
    """)

# MAIN APP
st.title("🔧 Tech Support Toolkit")

st.markdown("### Quick Tools")
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    if st.button("🔑 PIN", use_container_width=True):
        st.session_state.tool = "PIN"
with col2:
    if st.button("🔓 Unban", use_container_width=True):
        st.session_state.tool = "Unban"
with col3:
    if st.button("🗂️ DNS", use_container_width=True):
        st.session_state.tool = "DNS"
with col4:
    if st.button("🌐 WHOIS", use_container_width=True):
        st.session_state.tool = "WHOIS"
with col5:
    if st.button("🔍 IP", use_container_width=True):
        st.session_state.tool = "IP"
with col6:
    if st.button("📂 cPanel", use_container_width=True):
        st.session_state.tool = "cPanel"

col7, col8, col9, col10, col11, col12 = st.columns(6)
with col7:
    if st.button("📍 My IP", use_container_width=True):
        st.session_state.tool = "MyIP"
with col8:
    if st.button("🔄 NS", use_container_width=True):
        st.session_state.tool = "NS"
with col9:
    if st.button("🔒 SSL", use_container_width=True):
        st.session_state.tool = "SSL"
with col10:
    if st.button("📚 Help", use_container_width=True):
        st.session_state.tool = "Help"
with col11:
    if st.button("🧹 Flush", use_container_width=True):
        st.session_state.tool = "Flush"
with col12:
    st.write("")

st.divider()

if 'tool' not in st.session_state:
    st.session_state.tool = "DNS"

tool = st.session_state.tool

# TOOLS
if tool == "PIN":
    st.header("🔐 PIN Checker")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("Verify client PIN")
    with col2:
        st.link_button("Open", "https://my.hostafrica.com/admin/admin_tool/client-pin", use_container_width=True)

elif tool == "Unban":
    st.header("🔓 IP Unban")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("Remove IP blocks")
    with col2:
        st.link_button("Open", "https://my.hostafrica.com/admin/custom/scripts/unban/", use_container_width=True)

elif tool == "DNS":
    st.header("🗂️ DNS Analyzer")
    domain = st.text_input("Domain:", placeholder="example.com")
    
    if st.button("Analyze", use_container_width=True):
        if domain:
            with st.spinner("Analyzing..."):
                # --- A & AAAA RECORDS ---
            st.subheader("🌐 Web Resolution (A/AAAA)")
            a_res = requests.get(f"https://dns.google/resolve?name={domain_dns}&type=A").json()
            if a_res.get('Answer'):
                for r in a_res['Answer']: st.code(f"A: {r['data']}")
                success_checks.append("A record found")
            else:
                issues.append("Missing A record (Website won't load)")
                st.error("❌ No A records found.")

            # --- MX RECORDS (Mail) ---
            st.subheader("📧 Mail Server Records (MX)")
            mx_res = requests.get(f"https://dns.google/resolve?name={domain_dns}&type=MX").json()
            if mx_res.get('Answer'):
                for r in mx_res['Answer']: st.code(f"MX: {r['data']}")
                success_checks.append("MX records configured")
            else:
                issues.append("No MX records (Cannot receive email)")
                st.error("❌ No MX records found. Client cannot receive emails.")

            # --- CNAME RECORDS ---
            st.subheader("🔗 Alias Records (CNAME)")
            # Checking 'www' by default as it's the most common support query
            cname_res = requests.get(f"https://dns.google/resolve?name=www.{domain_dns}&type=CNAME").json()
            if cname_res.get('Answer'):
                for r in cname_res['Answer']: st.code(f"www CNAME: {r['data']}")
                success_checks.append("www CNAME found")
            else:
                st.info("ℹ️ No CNAME found for 'www' (might be using an A record instead).")

            # --- TXT RECORDS (SPF/DKIM/DMARC) ---
            st.subheader("📝 Text Records (Authentication)")
            txt_res = requests.get(f"https://dns.google/resolve?name={domain_dns}&type=TXT").json()
            if txt_res.get('Answer'):
                found_spf = False
                for r in txt_res['Answer']:
                    val = r['data'].strip('"')
                    st.code(f"TXT: {val}")
                    if "v=spf1" in val: found_spf = True
                
                if found_spf:
                    success_checks.append("SPF record found")
                else:
                    warnings.append("No SPF record found (Email might go to spam)")
            else:
                warnings.append("No TXT records found")
                st.warning("⚠️ No TXT records. Missing SPF/DMARC will affect email deliverability.")

            # --- NAMESERVERS ---
            st.subheader("🖥️ Nameservers (NS)")
            ns_res = requests.get(f"https://dns.google/resolve?name={domain_dns}&type=NS").json()
            if ns_res.get('Answer'):
                for r in ns_res['Answer']: st.code(f"NS: {r['data'].rstrip('.')}")
            else:
                issues.append("No Nameservers found")

            # --- Summary Report ---
            st.divider()
            st.subheader("📊 DNS Health Summary")
            col_a, col_b = st.columns(2)
            with col_a:
                for msg in issues: st.error(f"• {msg}")
                for msg in warnings: st.warning(f"• {msg}")
            with col_b:
                for msg in success_checks: st.success(f"• {msg}")
                    
elif tool == "WHOIS":
    st.header("🌐 WHOIS")
    domain = st.text_input("Domain:", placeholder="example.com")
    
    if st.button("Check", use_container_width=True):
        if domain:
            try:
                w = whois.whois(domain.strip().lower())
                if w and w.domain_name:
                    st.success("✅ Retrieved")
                    if w.expiration_date:
                        exp = w.expiration_date[0] if isinstance(w.expiration_date, list) else w.expiration_date
                        days = (exp - datetime.now()).days
                        st.write(f"**Expires:** {str(exp).split()[0]}")
                        if days < 0:
                            st.error("❌ Expired")
                        elif days < 30:
                            st.warning(f"⚠️ {days} days")
                        else:
                            st.success(f"✅ {days} days")
            except:
                st.error("❌ Failed")

elif tool == "IP":
    st.header("🔍 IP Lookup")
    ip = st.text_input("IP Address:", placeholder="8.8.8.8")
    
    if st.button("Lookup", use_container_width=True):
        if ip:
            try:
                res = requests.get(f"http://ip-api.com/json/{ip}", timeout=5).json()
                if res.get('status') == 'success':
                    st.success(f"✅ {ip}")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("City", res.get('city', 'N/A'))
                    with col2:
                        st.metric("Country", res.get('country', 'N/A'))
                    with col3:
                        st.metric("ISP", res.get('isp', 'N/A')[:20])
            except:
                st.error("Failed")

elif tool == "cPanel":
    st.header("📂 cPanel List")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("View cPanel accounts")
    with col2:
        st.link_button("Open", "https://my.hostafrica.com/admin/custom/scripts/custom_tests/listaccounts.php", use_container_width=True)

elif tool == "MyIP":
    st.header("📍 My IP")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("Find your IP")
    with col2:
        st.link_button("Open", "https://ip.hostafrica.com/", use_container_width=True)

elif tool == "NS":
    st.header("🔄 NS Updater")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("Bulk update nameservers")
    with col2:
        st.link_button("Open", "https://my.hostafrica.com/admin/addonmodules.php?module=nameserv_changer", use_container_width=True)

elif tool == "SSL":
    st.header("🔒 SSL Check")
    domain = st.text_input("Domain:", placeholder="example.com")
    
    if st.button("Check", use_container_width=True):
        if domain:
            domain = domain.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]
            try:
                ctx = ssl.create_default_context()
                with socket.create_connection((domain, 443), timeout=10) as sock:
                    with ctx.wrap_socket(sock, server_hostname=domain) as s:
                        cert = s.getpeercert()
                        st.success("✅ SSL valid")
                        na = cert.get('notAfter')
                        if na:
                            exp = datetime.strptime(na, '%b %d %H:%M:%S %Y %Z')
                            days = (exp - datetime.now()).days
                            st.write(f"**Days remaining:** {days}")
            except:
                st.error("❌ Failed")

elif tool == "Help":
    st.header("📚 Help Center")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("Search documentation")
    with col2:
        st.link_button("Open", "https://help.hostafrica.com", use_container_width=True)

elif tool == "Flush":
    st.header("🧹 Flush DNS")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("Clear Google DNS cache")
    with col2:
        st.link_button("Open", "https://dns.google/cache", use_container_width=True)
