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
    [data-testid="stMetricValue"] {
        font-size: 1.2rem;
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
         'keywords': ['email', 'mail', 'smtp', 'imap', 'pop3']},
    ],
    'domain': [
        {'title': 'Domain Management', 'url': 'https://help.hostafrica.com/en/category/domains-1yz6z58/',
         'keywords': ['domain', 'nameserver', 'dns', 'transfer']},
    ],
    'ssl': [
        {'title': 'SSL Certificates', 'url': 'https://help.hostafrica.com/en/category/ssl-certificates-1n94vbj/',
         'keywords': ['ssl', 'https', 'certificate', 'secure']},
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
    elif any(w in ticket_lower for w in ['email', 'mail', 'smtp', 'imap']):
        result['issue_type'] = '📧 Email Issue'
        result['checks'] = ['Check MX records', 'Verify SPF/DKIM', 'Check IP blocks']
        result['actions'] = ['Use DNS tool', 'Check IP blocks']
        result['response_template'] = """Hi [Client],

Thank you for contacting HostAfrica about your email issue.

I've checked:
- MX records and DNS configuration
- Email authentication (SPF/DKIM)

[Action taken]

For email help: https://help.hostafrica.com/en/category/email-1fmw9ki/

Best regards,
HostAfrica Support"""
        result['kb_articles'] = search_kb_articles('email')
    
    # Website
    elif any(w in ticket_lower for w in ['website', 'site', '404', '500', 'not loading']):
        result['issue_type'] = '🌐 Website Issue'
        result['checks'] = ['Check A record', 'Verify nameservers', 'Check hosting']
        result['actions'] = ['Use DNS tool', 'Check WHOIS']
        result['response_template'] = """Hi [Client],

I've investigated your website issue.

Status:
- Domain: [Status]
- DNS: [Status]
- Hosting: [Status]

[Action taken]

For help: https://help.hostafrica.com/en/category/web-hosting-b01r28/

Best regards,
HostAfrica Support"""
        result['kb_articles'] = search_kb_articles('website')
    
    # SSL issues
    elif any(w in ticket_lower for w in ['ssl', 'https', 'certificate', 'secure', 'padlock']):
        result['issue_type'] = '🔒 SSL Certificate Issue'
        result['checks'] = ['Check SSL certificate status', 'Verify expiration', 'Check mixed content']
        result['actions'] = ['Use SSL Check tool', 'Check for mixed content', 'Install Let\'s Encrypt if needed']
        result['response_template'] = """Hi [Client],

I've reviewed your SSL certificate.

Certificate Status:
- Validity: [Status]
- Expiration: [Date]
- Mixed Content: [Status]

[Action taken]

For SSL help: https://help.hostafrica.com/en/category/ssl-certificates-1n94vbj/

Best regards,
HostAfrica Support"""
        result['kb_articles'] = search_kb_articles('ssl')
    
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
    st.markdown("Paste ticket for AI-powered analysis")
    
    ticket_thread = st.text_area(
        "Ticket conversation:",
        height=200,
        placeholder="Paste the entire ticket thread here...",
        key="ticket_input"
    )
    
    if st.button("🔍 Analyze Ticket", key="analyze_btn", use_container_width=True):
        if ticket_thread:
            with st.spinner("Analyzing ticket..."):
                analysis = analyze_ticket_with_ai(ticket_thread)
                
                if analysis:
                    st.success("✅ Analysis Complete")
                    
                    st.markdown("**Issue Type:**")
                    st.info(analysis.get('issue_type', 'General'))
                    
                    kb = analysis.get('kb_articles', [])
                    if kb:
                        st.markdown("**📚 KB Articles:**")
                        for a in kb:
                            st.markdown(f"- [{a['title']}]({a['url']})")
                    
                    st.markdown("**Suggested Checks:**")
                    for c in analysis.get('checks', []):
                        st.markdown(f"- {c}")
                    
                    st.markdown("**Recommended Actions:**")
                    for a in analysis.get('actions', []):
                        st.markdown(f"- {a}")
                    
                    with st.expander("📝 Suggested Response Template"):
                        resp = analysis.get('response_template', '')
                        st.text_area("Copy this response:", value=resp, height=300, key="resp")
        else:
            st.warning("Please paste a ticket thread first")

st.sidebar.divider()

with st.sidebar.expander("📋 Support Checklist", expanded=True):
    st.markdown("""
    ### Quick Start (60s)
    1. ✅ Check priority (VIP?)
    2. ✅ Verify identity (PIN)
    3. ✅ Check service status
    4. ✅ Add tags
    
    ### Service Health
    - Domain: Active? Expired?
    - Hosting: Active/Suspended?
    - NS: ns1-4.host-ww.net
    - DA NS: dan1-2.host-ww.net
    
    ### Troubleshooting
    **Email**: MX/SPF/DKIM/DMARC
    **Website**: A record, NS, logs
    **cPanel**: IP blocks, login attempts
    **SSL**: Certificate, mixed content
    
    ### Tags
    Mail | Hosting | DNS | Billing | VPS
    """)

st.sidebar.divider()
st.sidebar.caption("💡 HostAfrica Support Toolkit v2.0")

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

# TOOLS IMPLEMENTATION

if tool == "PIN":
    st.header("🔐 PIN Checker")
    st.markdown("Verify client identity using support PIN")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("Open HostAfrica admin tool to verify client PINs")
    with col2:
        st.link_button("🔑 Open Tool", "https://my.hostafrica.com/admin/admin_tool/client-pin", use_container_width=True)

elif tool == "Unban":
    st.header("🔓 IP Unban Tool")
    st.markdown("Remove IP blocks from client area access")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("Use this tool to unban client IPs blocked from accessing the client area")
    with col2:
        st.link_button("🛡️ Unban Tool", "https://my.hostafrica.com/admin/custom/scripts/unban/", use_container_width=True)

elif tool == "DNS":
    st.header("🗂️ Comprehensive DNS Analyzer")
    st.markdown("Check resolution, mail routing, authentication records, and nameservers")
    
    domain_dns = st.text_input("Enter domain name:", placeholder="example.com", key="dns_domain")
    
    if st.button("🔍 Analyze DNS Records", use_container_width=True):
        if domain_dns:
            domain_dns = domain_dns.strip().lower()
            
            with st.spinner(f"Performing comprehensive DNS analysis for {domain_dns}..."):
                issues = []
                warnings = []
                success_checks = []
                
                # A Records
                st.subheader("🌐 Web Resolution (A/AAAA Records)")
                try:
                    a_res = requests.get(f"https://dns.google/resolve?name={domain_dns}&type=A", timeout=5).json()
                    if a_res.get('Answer'):
                        st.success(f"✅ Found {len(a_res['Answer'])} A record(s)")
                        for r in a_res['Answer']:
                            st.code(f"A: {r['data']} (TTL: {r.get('TTL', 'N/A')}s)")
                        success_checks.append("A record found")
                    else:
                        issues.append("Missing A record (Website won't load)")
                        st.error("❌ No A records found")
                except Exception as e:
                    st.error(f"❌ Error checking A records: {str(e)}")
                
                # AAAA Records (IPv6)
                try:
                    aaaa_res = requests.get(f"https://dns.google/resolve?name={domain_dns}&type=AAAA", timeout=5).json()
                    if aaaa_res.get('Answer'):
                        st.success(f"✅ Found {len(aaaa_res['Answer'])} AAAA record(s) (IPv6)")
                        for r in aaaa_res['Answer']:
                            st.code(f"AAAA: {r['data']}")
                        success_checks.append("IPv6 configured")
                    else:
                        st.info("ℹ️ No IPv6 (AAAA) records configured")
                except:
                    pass

                # MX Records
                st.subheader("📧 Mail Server Records (MX)")
                try:
                    mx_res = requests.get(f"https://dns.google/resolve?name={domain_dns}&type=MX", timeout=5).json()
                    if mx_res.get('Answer'):
                        st.success(f"✅ Found {len(mx_res['Answer'])} mail server(s)")
                        # Sort by priority
                        mx_sorted = sorted(mx_res['Answer'], key=lambda x: int(x['data'].split()[0]))
                        for r in mx_sorted:
                            parts = r['data'].split()
                            priority = parts[0]
                            server = parts[1].rstrip('.')
                            st.code(f"MX: Priority {priority} → {server}")
                        success_checks.append("MX records configured")
                    else:
                        issues.append("No MX records (Cannot receive email)")
                        st.error("❌ No MX records found. Client cannot receive emails.")
                except Exception as e:
                    st.error(f"❌ Error checking MX: {str(e)}")

                # CNAME Records
                st.subheader("🔗 Alias Records (CNAME)")
                try:
                    cname_res = requests.get(f"https://dns.google/resolve?name=www.{domain_dns}&type=CNAME", timeout=5).json()
                    if cname_res.get('Answer'):
                        for r in cname_res['Answer']:
                            st.code(f"www CNAME: {r['data'].rstrip('.')}")
                        success_checks.append("www CNAME found")
                    else:
                        st.info("ℹ️ No CNAME found for 'www' (might be using an A record instead)")
                except:
                    pass

                # TXT Records
                st.subheader("📝 Text Records (SPF/DKIM/DMARC)")
                try:
                    txt_res = requests.get(f"https://dns.google/resolve?name={domain_dns}&type=TXT", timeout=5).json()
                    if txt_res.get('Answer'):
                        found_spf = False
                        found_dmarc = False
                        
                        for r in txt_res['Answer']:
                            val = r['data'].strip('"')
                            
                            if val.startswith('v=spf1'):
                                st.success("🛡️ **SPF Record Found (Email Authentication)**")
                                st.code(f"SPF: {val}")
                                found_spf = True
                            elif val.startswith('v=DMARC'):
                                st.success("🛡️ **DMARC Record Found (Email Policy)**")
                                st.code(f"DMARC: {val}")
                                found_dmarc = True
                            elif 'dkim' in val.lower():
                                st.success("🔑 **DKIM Record Found (Email Signature)**")
                                st.code(f"DKIM: {val[:100]}...")
                            else:
                                st.info("📋 **General TXT Record**")
                                st.code(f"TXT: {val[:100]}...")
                        
                        if found_spf:
                            success_checks.append("SPF record found")
                        else:
                            warnings.append("No SPF record (Email might go to spam)")
                            st.warning("⚠️ No SPF record found")
                        
                        if not found_dmarc:
                            # Check _dmarc subdomain
                            try:
                                dmarc_res = requests.get(f"https://dns.google/resolve?name=_dmarc.{domain_dns}&type=TXT", timeout=5).json()
                                if dmarc_res.get('Answer'):
                                    st.success("🛡️ **DMARC Record Found (at _dmarc subdomain)**")
                                    st.code(dmarc_res['Answer'][0]['data'].strip('"'))
                                    found_dmarc = True
                            except:
                                pass
                        
                        if not found_dmarc:
                            warnings.append("No DMARC record (Domain vulnerable to spoofing)")
                            st.warning("⚠️ No DMARC record found")
                    else:
                        warnings.append("No TXT records found")
                        st.warning("⚠️ No TXT records. Missing SPF/DMARC affects email deliverability.")
                except Exception as e:
                    st.error(f"❌ Error checking TXT: {str(e)}")

                # Nameservers
                st.subheader("🖥️ Nameservers (NS Records)")
                try:
                    ns_res = requests.get(f"https://dns.google/resolve?name={domain_dns}&type=NS", timeout=5).json()
                    if ns_res.get('Answer'):
                        st.success(f"✅ Found {len(ns_res['Answer'])} nameserver(s)")
                        for r in ns_res['Answer']:
                            ns = r['data'].rstrip('.')
                            st.code(f"NS: {ns}")
                            
                            # Check if HostAfrica nameservers
                            if 'host-ww.net' in ns:
                                if 'dan' in ns:
                                    st.caption("✅ HostAfrica DirectAdmin nameserver")
                                else:
                                    st.caption("✅ HostAfrica cPanel nameserver")
                        
                        success_checks.append("Nameservers configured")
                    else:
                        issues.append("No Nameservers found")
                        st.error("❌ No nameservers found")
                except Exception as e:
                    st.error(f"❌ Error checking NS: {str(e)}")

                # SOA Record
                st.subheader("🏛️ SOA Record (Zone Authority)")
                try:
                    soa_res = requests.get(f"https://dns.google/resolve?name={domain_dns}&type=SOA", timeout=5).json()
                    if soa_res.get('Answer'):
                        soa_data = soa_res['Answer'][0]['data']
                        st.success("✅ SOA record found")
                        st.code(f"SOA: {soa_data}")
                        success_checks.append("SOA configured")
                    else:
                        warnings.append("No SOA record")
                        st.warning("⚠️ No SOA record found")
                except:
                    pass

                # Summary Report
                st.divider()
                st.subheader("📊 DNS Health Summary")
                
                if not issues and not warnings:
                    st.success("🎉 **All DNS checks passed!** Domain is properly configured.")
                    st.balloons()
                else:
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if issues:
                            st.markdown("**❌ Critical Issues:**")
                            for msg in issues:
                                st.error(f"• {msg}")
                        if warnings:
                            st.markdown("**⚠️ Warnings:**")
                            for msg in warnings:
                                st.warning(f"• {msg}")
                    with col_b:
                        if success_checks:
                            st.markdown("**✅ Passed Checks:**")
                            for msg in success_checks:
                                st.success(f"• {msg}")
        else:
            st.warning("⚠️ Please enter a domain name")

elif tool == "WHOIS":
    st.header("🌐 Comprehensive WHOIS Lookup")
    st.markdown("Check domain registration, expiration, status, and registrar information")
    
    domain = st.text_input("Enter domain name:", placeholder="example.com", key="whois_domain")
    
    if st.button("🔍 Check WHOIS", use_container_width=True):
        if domain:
            domain = domain.strip().lower()
            
            with st.spinner(f"Performing WHOIS lookup for {domain}..."):
                issues = []
                warnings = []
                success_checks = []
                
                st.subheader("📝 Domain Registration Information")
                
                try:
                    w = whois.whois(domain)
                    
                    if w and w.domain_name:
                        st.success("✅ WHOIS information retrieved successfully")
                        success_checks.append("WHOIS lookup successful")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("### Basic Information")
                            st.write(f"**Domain:** {domain}")
                            
                            if w.registrar:
                                st.write(f"**Registrar:** {w.registrar}")
                            
                            if w.registrant:
                                registrant = str(w.registrant)
                                if 'redacted' not in registrant.lower():
                                    st.write(f"**Registrant:** {registrant}")
                            
                            # Status
                            if w.status:
                                st.markdown("### Domain Status")
                                status_list = w.status if isinstance(w.status, list) else [w.status]
                                
                                for status in status_list[:5]:
                                    status_str = str(status)
                                    status_lower = status_str.lower()
                                    
                                    if any(x in status_lower for x in ['ok', 'active', 'registered']):
                                        st.success(f"✅ {status_str.split()[0]}")
                                        success_checks.append("Domain status: OK")
                                    elif any(x in status_lower for x in ['hold', 'lock', 'suspended', 'pending delete']):
                                        st.error(f"❌ {status_str.split()[0]}")
                                        issues.append(f"Domain status issue: {status_str.split()[0]}")
                                    elif any(x in status_lower for x in ['pending', 'verification', 'grace']):
                                        st.warning(f"⚠️ {status_str.split()[0]}")
                                        warnings.append(f"Domain status: {status_str.split()[0]}")
                                    elif 'expired' in status_lower:
                                        st.error(f"❌ {status_str.split()[0]}")
                                        issues.append("Domain expired")
                                    else:
                                        st.info(f"ℹ️ {status_str.split()[0]}")
                        
                        with col2:
                            st.markdown("### Important Dates")
                            
                            # Creation date
                            if w.creation_date:
                                created = w.creation_date[0] if isinstance(w.creation_date, list) else w.creation_date
                                st.write(f"**Created:** {str(created).split()[0]}")
                            
                            # Updated date
                            if w.updated_date:
                                updated = w.updated_date[0] if isinstance(w.updated_date, list) else w.updated_date
                                st.write(f"**Last Updated:** {str(updated).split()[0]}")
                            
                            # Expiration date
                            if w.expiration_date:
                                exp = w.expiration_date[0] if isinstance(w.expiration_date, list) else w.expiration_date
                                st.write(f"**Expires:** {str(exp).split()[0]}")
                                
                                # Calculate days remaining
                                try:
                                    days_left = (exp - datetime.now().replace(microsecond=0)).days
                                    
                                    if days_left < 0:
                                        st.error(f"❌ **EXPIRED {abs(days_left)} days ago!**")
                                        issues.append(f"Domain expired {abs(days_left)} days ago")
                                    elif days_left < 30:
                                        st.error(f"⚠️ **{days_left} days remaining - URGENT!**")
                                        issues.append(f"Domain expires in {days_left} days")
                                    elif days_left < 90:
                                        st.warning(f"⚠️ **{days_left} days remaining**")
                                        warnings.append(f"Domain expires in {days_left} days")
                                    else:
                                        st.success(f"✅ **{days_left} days remaining**")
                                        success_checks.append("Domain expiration: Good")
                                except:
                                    pass
                        
                        # Nameservers
                        if w.name_servers:
                            st.markdown("### WHOIS Nameservers")
                            ns_list = w.name_servers if isinstance(w.name_servers, list) else [w.name_servers]
                            
                            for ns in ns_list[:5]:
                                ns_clean = str(ns).lower().rstrip('.')
                                st.code(f"• {ns_clean}")
                                
                                if 'host-ww.net' in ns_clean:
                                    st.caption("✅ HostAfrica nameserver")
                        
                        # Full WHOIS data
                        with st.expander("📄 View Full Raw WHOIS Data"):
                            st.json(str(w))
                        
                        # Summary
                        st.divider()
                        st.subheader("📊 WHOIS Health Summary")
                        
                        if not issues and not warnings:
                            st.success("🎉 **Domain is in good standing!** No issues detected.")
                        else:
                            if issues:
                                st.markdown("**❌ Critical Issues:**")
                                for issue in issues:
                                    st.error(f"• {issue}")
                            
                            if warnings:
                                st.markdown("**⚠️ Warnings:**")
                                for warning in warnings:
                                    st.warning(f"• {warning}")
                            
                            if success_checks:
                                st.markdown("**✅ Passed Checks:**")
                                for check in success_checks:
                                    st.success(f"• {check}")
                        
                    else:
                        st.error("❌ Could not retrieve WHOIS information")
                        st.info(f"Try manual lookup at: https://who.is/whois/{domain}")
                        
                except Exception as e:
                    st.error(f"❌ WHOIS lookup failed: {type(e).__name__}")
                    st.warning("Some domains (especially ccTLDs) may not return complete WHOIS data via automated tools.")
                    st.info(f"**Try manual lookup:**\n- https://who.is/whois/{domain}\n- https://lookup.icann.org/en/lookup?name={domain}")
        else:
            st.warning("⚠️ Please enter a domain name")

elif tool == "IP":
    st.header("🔍 IP Address Lookup")
    st.markdown("Get detailed geolocation and ISP information for any IP address")
    
    ip = st.text_input("Enter IP address:", placeholder="8.8.8.8", key="ip_input")
    
    if st.button("🔍 Lookup IP", use_container_width=True):
        if ip:
            # Validate IP format
            ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
            if not re.match(ip_pattern, ip):
                st.error("❌ Invalid IP address format")
            else:
                with st.spinner(f"Looking up {ip}..."):
                    try:
                        # Try primary API
                        geo_data = None
                        try:
                            response = requests.get(f"https://ipapi.co/{ip}/json/", timeout=5)
                            if response.status_code == 200:
                                geo_data = response.json()
                        except:
                            pass
                        
                        # Fallback API
                        if not geo_data or geo_data.get('error'):
                            response = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
                            if response.status_code == 200:
                                fallback = response.json()
                                if fallback.get('status') == 'success':
                                    geo_data = {
                                        'ip': ip,
                                        'city': fallback.get('city'),
                                        'region': fallback.get('regionName'),
                                        'country_name': fallback.get('country'),
                                        'postal': fallback.get('zip'),
                                        'latitude': fallback.get('lat'),
                                        'longitude': fallback.get('lon'),
                                        'org': fallback.get('isp'),
                                        'timezone': fallback.get('timezone'),
                                        'asn': fallback.get('as')
                                    }
                        
                        if geo_data and not geo_data.get('error'):
                            st.success(f"✅ Information found for {ip}")
                            
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("🌐 IP Address", ip)
                                st.metric("🏙️ City", geo_data.get('city', 'N/A'))
                                st.metric("📮 Postal Code", geo_data.get('postal', 'N/A'))
                            
                            with col2:
                                st.metric("🗺️ Region", geo_data.get('region', 'N/A'))
                                st.metric("🌍 Country", geo_data.get('country_name', 'N/A'))
                                st.metric("🕐 Timezone", geo_data.get('timezone', 'N/A'))
                            
                            with col3:
                                st.metric("📡 ISP/Organization", geo_data.get('org', 'N/A')[:25])
                                if geo_data.get('latitude') and geo_data.get('longitude'):
                                    st.metric("📍 Coordinates", f"{geo_data['latitude']:.4f}, {geo_data['longitude']:.4f}")
                                if geo_data.get('asn'):
                                    st.metric("🔢 ASN", geo_data.get('asn', 'N/A'))
                            
                            # Map link
                            if geo_data.get('latitude') and geo_data.get('longitude'):
                                map_url = f"https://www.google.com/maps?q={geo_data['latitude']},{geo_data['longitude']}"
                                st.markdown(f"🗺️ [View on Google Maps]({map_url})")
                            
                            # Full details
                            with st.expander("🔍 View Full IP Details"):
                                st.json(geo_data)
                        else:
                            st.error("❌ Could not retrieve information for this IP address")
                            st.info("The IP might be private, invalid, or the lookup service is unavailable")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("⚠️ Please enter an IP address")

elif tool == "cPanel":
    st.header("📂 cPanel Account List")
    st.markdown("View all cPanel hosting accounts and their details")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("Access the complete list of cPanel accounts")
    with col2:
        st.link_button("📂 Open List", "https://my.hostafrica.com/admin/custom/scripts/custom_tests/listaccounts.php", use_container_width=True)

elif tool == "MyIP":
    st.header("📍 Find My IP Address")
    st.markdown("Quickly discover your current public IP address")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("Click to open HostAfrica's IP detection tool")
    with col2:
        st.link_button("🔍 Get My IP", "https://ip.hostafrica.com/", use_container_width=True)

elif tool == "NS":
    st.header("🔄 Bulk Nameserver Updater")
    st.markdown("Update nameservers for multiple domains at once")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("Use this tool to bulk update nameservers in WHMCS")
    with col2:
        st.link_button("🔄 Open Updater", "https://my.hostafrica.com/admin/addonmodules.php?module=nameserv_changer", use_container_width=True)

elif tool == "SSL":
    st.header("🔒 Comprehensive SSL Certificate Checker")
    st.markdown("Verify SSL certificate validity, expiration, and check for mixed content issues")
    
    domain_ssl = st.text_input("Enter domain (without https://):", placeholder="example.com", key="ssl_domain")
    
    if st.button("🔍 Check SSL Certificate", use_container_width=True):
        if domain_ssl:
            domain_ssl = domain_ssl.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0].strip()
            
            with st.spinner(f"Analyzing SSL certificate for {domain_ssl}..."):
                try:
                    # SSL Certificate Check
                    context = ssl.create_default_context()
                    with socket.create_connection((domain_ssl, 443), timeout=10) as sock:
                        with context.wrap_socket(sock, server_hostname=domain_ssl) as secure_sock:
                            cert = secure_sock.getpeercert()
                            
                            st.success(f"✅ SSL Certificate found and valid for {domain_ssl}")
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.subheader("📋 Certificate Details")
                                
                                subject = dict(x[0] for x in cert['subject'])
                                st.write("**Issued To:**", subject.get('commonName', 'N/A'))
                                
                                issuer = dict(x[0] for x in cert['issuer'])
                                st.write("**Issued By:**", issuer.get('commonName', 'N/A'))
                                st.write("**Organization:**", issuer.get('organizationName', 'N/A'))
                            
                            with col2:
                                st.subheader("📅 Validity Period")
                                
                                not_before = cert.get('notBefore')
                                not_after = cert.get('notAfter')
                                
                                st.write("**Valid From:**", not_before)
                                st.write("**Valid Until:**", not_after)
                                
                                if not_after:
                                    try:
                                        expiry_date = datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z')
                                        days_remaining = (expiry_date - datetime.now()).days
                                        
                                        if days_remaining > 30:
                                            st.success(f"✅ **{days_remaining} days** remaining")
                                        elif days_remaining > 0:
                                            st.warning(f"⚠️ **{days_remaining} days** remaining - Renew soon!")
                                        else:
                                            st.error(f"❌ Certificate expired {abs(days_remaining)} days ago")
                                    except:
                                        pass
                            
                            # Subject Alternative Names
                            if 'subjectAltName' in cert:
                                st.subheader("🌐 Subject Alternative Names (Covered Domains)")
                                sans = [san[1] for san in cert['subjectAltName']]
                                
                                for san in sans[:10]:
                                    st.code(san)
                                
                                if len(sans) > 10:
                                    st.info(f"...and {len(sans) - 10} more domain(s)")
                            
                            # Mixed Content Check
                            st.subheader("🔍 Mixed Content Check")
                            with st.spinner("Checking for mixed content issues..."):
                                try:
                                    # Fetch the homepage
                                    response = requests.get(f"https://{domain_ssl}", timeout=10, verify=True)
                                    content = response.text
                                    
                                    # Check for HTTP resources
                                    http_resources = re.findall(r'http://[^"\'\s<>]+', content)
                                    
                                    if http_resources:
                                        st.warning(f"⚠️ **Found {len(http_resources)} potential mixed content issue(s)**")
                                        st.caption("Mixed content occurs when HTTPS pages load HTTP resources (images, scripts, etc.)")
                                        
                                        # Show first few examples
                                        st.markdown("**Examples:**")
                                        for resource in http_resources[:5]:
                                            st.code(resource)
                                        
                                        if len(http_resources) > 5:
                                            st.info(f"...and {len(http_resources) - 5} more HTTP resources")
                                        
                                        st.markdown("""
                                        **How to fix:**
                                        1. Change all `http://` to `https://` in your HTML/CSS
                                        2. Use protocol-relative URLs: `//example.com/image.jpg`
                                        3. Update your CMS/theme settings to use HTTPS
                                        """)
                                    else:
                                        st.success("✅ No mixed content issues detected!")
                                        st.caption("All resources are loaded securely via HTTPS")
                                except Exception as e:
                                    st.warning(f"⚠️ Could not check for mixed content: {str(e)}")
                            
                            # Certificate summary
                            with st.expander("🔍 View Complete Certificate Summary"):
                                summary = {
                                    'Common Name': subject.get('commonName', 'N/A'),
                                    'Issuer': issuer.get('commonName', 'N/A'),
                                    'Issuer Organization': issuer.get('organizationName', 'N/A'),
                                    'Valid From': not_before,
                                    'Valid Until': not_after,
                                    'Serial Number': cert.get('serialNumber', 'N/A'),
                                    'Version': cert.get('version', 'N/A'),
                                    'Total SANs': len(sans) if 'subjectAltName' in cert else 0
                                }
                                
                                for key, value in summary.items():
                                    st.text(f"{key}: {value}")
                                
                                st.divider()
                                
                                with st.expander("📄 Show Technical/Raw Certificate Data"):
                                    st.json(cert)
                        
                except socket.gaierror:
                    st.error(f"❌ Could not resolve domain: {domain_ssl}")
                    st.info("💡 Make sure the domain name is correct and accessible")
                    
                except socket.timeout:
                    st.error(f"⏱️ Connection timeout for {domain_ssl}")
                    st.info("💡 The server might be slow or blocking connections")
                    
                except ssl.SSLError as ssl_err:
                    st.error(f"❌ SSL Error: {str(ssl_err)}")
                    st.warning("""
                    **Common SSL Issues:**
                    - Certificate has expired
                    - Certificate is self-signed
                    - Certificate name doesn't match domain
                    - Incomplete certificate chain
                    - Mixed content blocking
                    """)
                    
                except Exception as e:
                    st.error(f"❌ Error checking SSL: {str(e)}")
                    st.info(f"💡 Try checking manually at: https://www.ssllabs.com/ssltest/analyze.html?d={domain_ssl}")
        else:
            st.warning("⚠️ Please enter a domain name")

elif tool == "Help":
    st.header("📚 HostAfrica Help Center")
    st.markdown("Search the knowledge base for guides and documentation")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("Access the complete HostAfrica help center and documentation")
    with col2:
        st.link_button("📚 Open Help", "https://help.hostafrica.com", use_container_width=True)

elif tool == "Flush":
    st.header("🧹 Flush Google DNS Cache")
    st.markdown("Clear Google's DNS cache for a domain to force fresh lookups")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("Use this to force Google DNS to fetch fresh DNS records for a domain")
    with col2:
        st.link_button("🧹 Flush Cache", "https://dns.google/cache", use_container_width=True)
