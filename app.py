import streamlit as st
import requests
import json
from datetime import datetime
import socket
import ssl
import whois
from whois import exceptions
import re

# Page Configuration
st.set_page_config(
    page_title="Tech Support Toolkit",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better button visibility and horizontal menu
st.markdown("""
<style>
    /* Make buttons more visible */
    .stButton > button {
        width: 100%;
        background-color: #4A9B8E;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    .stButton > button:hover {
        background-color: #3A8B7E;
        border-color: #3A8B7E;
    }
    
    /* Horizontal menu styling */
    .horizontal-menu {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        padding: 1rem 0;
        border-bottom: 2px solid #4A9B8E;
        margin-bottom: 2rem;
    }
    
    /* Make external links more visible */
    .stMarkdown a {
        color: #4A9B8E !important;
        font-weight: 600;
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
        placeholder="Paste the entire ticket thread here..."
    )
    
    if st.button("🔍 Analyze Ticket", key="analyze_btn"):
        if ticket_thread:
            with st.spinner("Analyzing ticket..."):
                # AI Analysis Logic
                analysis_result = analyze_ticket(ticket_thread)
                
                st.success("✅ Analysis Complete")
                
                st.markdown("**Issue Type:**")
                st.info(analysis_result['issue_type'])
                
                st.markdown("**Suggested Checks:**")
                for check in analysis_result['checks']:
                    st.markdown(f"- {check}")
                
                st.markdown("**Recommended Actions:**")
                for action in analysis_result['actions']:
                    st.markdown(f"- {action}")
                
                with st.expander("📝 Suggested Response Template"):
                    st.code(analysis_result['response_template'], language="text")
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

# --- MAIN APP ---
st.title("🔧 Tech Support Toolkit")

# Horizontal Menu Bar
st.markdown("### Quick Tools")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("🔑 PIN Checker", use_container_width=True):
        st.session_state.tool = "PIN Checker"
        
with col2:
    if st.button("🔓 IP Unban", use_container_width=True):
        st.session_state.tool = "IP Unban"

with col3:
    if st.button("🗂️ DNS Records", use_container_width=True):
        st.session_state.tool = "DNS Records"

with col4:
    if st.button("🌐 WHOIS Check", use_container_width=True):
        st.session_state.tool = "WHOIS Check"

with col5:
    if st.button("🔍 IP Lookup", use_container_width=True):
        st.session_state.tool = "IP Lookup"

col6, col7, col8, col9, col10 = st.columns(5)

with col6:
    if st.button("📂 cPanel List", use_container_width=True):
        st.session_state.tool = "cPanel List"

with col7:
    if st.button("📍 My IP", use_container_width=True):
        st.session_state.tool = "My IP"

with col8:
    if st.button("🔄 NS Updater", use_container_width=True):
        st.session_state.tool = "NS Updater"

with col9:
    if st.button("🔒 SSL Check", use_container_width=True):
        st.session_state.tool = "SSL Check"

with col10:
    if st.button("📚 Knowledge Base", use_container_width=True):
        st.session_state.tool = "Knowledge Base"

# Additional row for DNS cache flush
col11, col12, col13, col14, col15 = st.columns(5)
with col11:
    if st.button("🧹 Flush Google DNS", use_container_width=True):
        st.session_state.tool = "Flush DNS"

st.divider()

# Initialize session state
if 'tool' not in st.session_state:
    st.session_state.tool = "DNS Records"

# Tool content based on selection
tool = st.session_state.tool

# --- TOOL IMPLEMENTATIONS ---

# Helper function for AI ticket analysis
def analyze_ticket(ticket_text):
    """Analyze ticket and provide recommendations"""
    ticket_lower = ticket_text.lower()
    
    # Simple keyword-based analysis (can be enhanced with actual AI later)
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
            'Check if client IP is blocked (use IP Lookup)',
            'Review email logs in cPanel/DirectAdmin',
            'Verify domain and hosting are active'
        ]
        result['actions'] = [
            'Use DNS Records tool to check MX configuration',
            'Check client IP for blocks',
            'Verify email account exists in hosting control panel'
        ]
        result['response_template'] = """Hi [Client Name],

Thank you for contacting us about your email issue.

I've reviewed your account and found:
[What you checked]

[What you found]

[What you fixed OR what client needs to do]

The changes should take effect within [timeframe].

Please let me know if you need any further assistance.

Best regards,
[Your Name]
HostAfrica Support"""
    
    # Website issues
    elif any(word in ticket_lower for word in ['website', 'site down', 'not loading', '404', '500', 'error', 'http']):
        result['issue_type'] = '🌐 Website Issue'
        result['checks'] = [
            'Check domain A record using DNS Records tool',
            'Verify domain expiration with WHOIS Check',
            'Check nameservers are correct',
            'Verify hosting account is active',
            'Review error logs in control panel'
        ]
        result['actions'] = [
            'Use DNS Records tool to verify A record points to correct IP',
            'Use WHOIS Check to confirm domain is not expired',
            'Check hosting status in WHMCS'
        ]
        result['response_template'] = """Hi [Client Name],

I've investigated your website issue.

Analysis:
- Domain Status: [Active/Expired]
- DNS Resolution: [Working/Issue found]
- Hosting Status: [Active/Suspended]

[Explanation of issue and resolution]

Your website should be accessible within [timeframe].

Best regards,
[Your Name]
HostAfrica Support"""
    
    # Domain issues
    elif any(word in ticket_lower for word in ['domain', 'nameserver', 'ns1', 'dns', 'propagation']):
        result['issue_type'] = '🔧 Domain/DNS Issue'
        result['checks'] = [
            'Check domain registration with WHOIS Check',
            'Verify nameservers using DNS Records tool',
            'Check domain expiration date',
            'Verify DNS propagation status'
        ]
        result['actions'] = [
            'Use WHOIS Check to verify domain status',
            'Use DNS Records tool to check current nameservers',
            'Update nameservers if incorrect using NS Updater'
        ]
        result['response_template'] = """Hi [Client Name],

I've checked your domain configuration.

Current Status:
- Domain: [Active/Status]
- Nameservers: [Correct/Needs update]
- DNS Propagation: [Complete/In progress]

[Action taken or required]

DNS changes can take 4-24 hours to propagate globally.

Best regards,
[Your Name]
HostAfrica Support"""
    
    # SSL issues
    elif any(word in ticket_lower for word in ['ssl', 'https', 'certificate', 'secure', 'padlock']):
        result['issue_type'] = '🔒 SSL Certificate Issue'
        result['checks'] = [
            'Check SSL certificate status with SSL Check tool',
            'Verify domain is pointing to correct server',
            'Check certificate expiration date',
            'Verify SSL is installed in control panel'
        ]
        result['actions'] = [
            'Use SSL Check tool to verify certificate',
            'Check certificate expiration',
            'Install/renew SSL if needed'
        ]
        result['response_template'] = """Hi [Client Name],

I've reviewed your SSL certificate.

Status:
- Certificate: [Valid/Expired/Missing]
- Expiration: [Date]
- Coverage: [Domains covered]

[Action taken]

Your website should show as secure within [timeframe].

Best regards,
[Your Name]
HostAfrica Support"""
    
    # Billing issues
    elif any(word in ticket_lower for word in ['invoice', 'payment', 'billing', 'suspended', 'renew', 'expire']):
        result['issue_type'] = '💳 Billing Issue'
        result['checks'] = [
            'Check invoice status in WHMCS',
            'Verify service status (active/suspended)',
            'Check payment method on file'
        ]
        result['actions'] = [
            'Review account in WHMCS',
            'Check for unpaid invoices',
            'Verify service suspension reason'
        ]
        result['response_template'] = """Hi [Client Name],

I've reviewed your account billing status.

Account Status:
- Service: [Active/Suspended]
- Outstanding Balance: [Amount]
- Next Renewal: [Date]

[Action required from client]

Please let me know if you need any assistance with payment.

Best regards,
[Your Name]
HostAfrica Support"""
    
    else:
        # General issue
        result['checks'] = [
            'Verify client identity (check PIN if guest user)',
            'Check service status in WHMCS',
            'Review ticket history for similar issues',
            'Gather more information from client'
        ]
        result['actions'] = [
            'Request more details about the issue',
            'Check relevant service status',
            'Review documentation'
        ]
        result['response_template'] = """Hi [Client Name],

Thank you for contacting HostAfrica Support.

To assist you better, I need some additional information:
[Questions to ask]

Once I have these details, I'll be able to resolve your issue quickly.

Best regards,
[Your Name]
HostAfrica Support"""
    
    return result

# 1. PIN Checker
if tool == "PIN Checker":
    st.header("🔐 Identity & Verification")
    st.markdown("Verify client identity using their support PIN")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("Open the HostAfrica Admin Tool to verify client PINs")
    with col2:
        st.link_button("🔑 Open Admin Tool", "https://my.hostafrica.com/admin/admin_tool/client-pin", use_container_width=True)

# 2. IP Unban Tool
elif tool == "IP Unban":
    st.header("🔓 Client Area IP Unban")
    st.markdown("Unban client IPs that are blocked from accessing the client area")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("Use this tool to remove IP blocks from the client area")
    with col2:
        st.link_button("🛡️ Open Unban Tool", "https://my.hostafrica.com/admin/custom/scripts/unban/", use_container_width=True)

# 3. DNS Records
elif tool == "DNS Records":
    st.header("🗂️ DNS Record Analyzer")
    st.markdown("Comprehensive check of resolution, mail routing, and authentication records")
    
    domain_dns = st.text_input("Enter domain (e.g. hostafrica.com):", key="dns_input")
    
    if st.button("🔍 Analyze DNS", use_container_width=True):
        if domain_dns:
            domain_dns = domain_dns.strip().lower()
            
            with st.spinner(f"Analyzing all DNS records for {domain_dns}..."):
                issues, warnings, success_checks = [], [], []
                
                # --- A & AAAA RECORDS ---
                st.subheader("🌐 Web Resolution (A/AAAA)")
                try:
                    a_res = requests.get(f"https://dns.google/resolve?name={domain_dns}&type=A", timeout=5).json()
                    if a_res.get('Answer'):
                        for r in a_res['Answer']: 
                            st.code(f"A: {r['data']}")
                        success_checks.append("A record found")
                    else:
                        issues.append("Missing A record (Website won't load)")
                        st.error("❌ No A records found.")
                except Exception as e:
                    st.error(f"Error checking A records: {str(e)}")

                # --- MX RECORDS (Mail) ---
                st.subheader("📧 Mail Server Records (MX)")
                try:
                    mx_res = requests.get(f"https://dns.google/resolve?name={domain_dns}&type=MX", timeout=5).json()
                    if mx_res.get('Answer'):
                        for r in mx_res['Answer']: 
                            st.code(f"MX: {r['data']}")
                        success_checks.append("MX records configured")
                    else:
                        issues.append("No MX records (Cannot receive email)")
                        st.error("❌ No MX records found. Client cannot receive emails.")
                except Exception as e:
                    st.error(f"Error checking MX records: {str(e)}")

                # --- TXT RECORDS (SPF/DKIM/DMARC) ---
                st.subheader("📝 Text Records (Authentication)")
                try:
                    txt_res = requests.get(f"https://dns.google/resolve?name={domain_dns}&type=TXT", timeout=5).json()
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
                except Exception as e:
                    st.warning(f"Error checking TXT records: {str(e)}")

                # --- NAMESERVERS ---
                st.subheader("🖥️ Nameservers (NS)")
                try:
                    ns_res = requests.get(f"https://dns.google/resolve?name={domain_dns}&type=NS", timeout=5).json()
                    if ns_res.get('Answer'):
                        for r in ns_res['Answer']: 
                            st.code(f"NS: {r['data'].rstrip('.')}")
                        success_checks.append("Nameservers configured")
                    else:
                        issues.append("No Nameservers found")
                        st.error("❌ No nameservers found")
                except Exception as e:
                    st.error(f"Error checking nameservers: {str(e)}")

                # --- Summary Report ---
                st.divider()
                st.subheader("📊 DNS Health Summary")
                col_a, col_b = st.columns(2)
                with col_a:
                    if issues:
                        st.markdown("**❌ Critical Issues:**")
                        for msg in issues: st.error(f"• {msg}")
                    if warnings:
                        st.markdown("**⚠️ Warnings:**")
                        for msg in warnings: st.warning(f"• {msg}")
                with col_b:
                    if success_checks:
                        st.markdown("**✅ Passed Checks:**")
                        for msg in success_checks: st.success(f"• {msg}")
        else:
            st.warning("Please enter a domain name")

# 4. WHOIS Check
elif tool == "WHOIS Check":
    st.header("🌐 Domain WHOIS Lookup")
    st.markdown("Check domain registration, expiration, and status")
    
    domain = st.text_input("Enter domain name (e.g., example.com):")
    
    if st.button("🔍 Check WHOIS", use_container_width=True):
        if domain:
            domain = domain.strip().lower()
            issues = []
            warnings = []
            success_checks = []

            with st.spinner('Performing WHOIS lookup...'):
                st.subheader("📝 Domain Registration Information")
                
                whois_data = None
                whois_success = False

                try:
                    whois_data = whois.whois(domain)
                    whois_success = True
                    
                except Exception as e:
                    st.error(f"❌ WHOIS check failed: {type(e).__name__}")

                if whois_success and whois_data and whois_data.domain_name:
                    st.success("✅ WHOIS information retrieved")
                    success_checks.append("WHOIS lookup successful")

                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Domain:** {domain}")
                        
                        if whois_data.registrar:
                            st.write(f"**Registrar:** {whois_data.registrar}")

                        status_list = whois_data.status
                        if status_list:
                            st.write("**Domain Status:**")
                            if not isinstance(status_list, list):
                                status_list = [status_list] if status_list else []
                                
                            for status in status_list[:5]:
                                status_lower = str(status).lower()
                                if any(x in status_lower for x in ['ok', 'active', 'registered']):
                                    st.success(f"✅ {status.split()[0]}")
                                elif any(x in status_lower for x in ['hold', 'lock', 'suspended']):
                                    st.error(f"❌ {status.split()[0]}")
                                    issues.append(f"Domain status: {status.split()[0]}")
                                elif any(x in status_lower for x in ['pending', 'expired']):
                                    st.warning(f"⚠️ {status.split()[0]}")
                                    warnings.append(f"Domain status: {status.split()[0]}")

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
                                    st.error(f"❌ EXPIRED {abs(days_left)} days ago!")
                                    issues.append(f"Domain expired")
                                elif days_left < 30:
                                    st.error(f"⚠️ {days_left} days - URGENT!")
                                    issues.append(f"Expires soon")
                                elif days_left < 90:
                                    st.warning(f"⚠️ {days_left} days")
                                else:
                                    st.success(f"✅ {days_left} days")
                            except:
                                pass
                    
                    if whois_data.name_servers:
                        st.write("**Nameservers:**")
                        for ns in whois_data.name_servers[:4]:
                            st.caption(f"• {str(ns).lower().rstrip('.')}")

                else:
                    st.warning("⚠️ Could not retrieve WHOIS information")
                    st.info(f"Try manual lookup at: https://who.is/whois/{domain}")

                # Summary
                if issues or warnings:
                    st.divider()
                    st.subheader("📊 Summary")
                    if issues:
                        for issue in issues:
                            st.error(f"• {issue}")
                    if warnings:
                        for warning in warnings:
                            st.warning(f"• {warning}")
        else:
            st.warning("Please enter a domain name")

# 5. IP Lookup
elif tool == "IP Lookup":
    st.header("🔍 IP Address Lookup")
    st.markdown("Get geolocation and ISP information for any IP address")
    
    ip_input = st.text_input("Enter IP address:", placeholder="8.8.8.8")
    
    if st.button("🔍 Lookup IP", use_container_width=True):
        if ip_input:
            ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
            if not re.match(ip_pattern, ip_input):
                st.error("❌ Invalid IP address format")
            else:
                with st.spinner(f"Looking up {ip_input}..."):
                    try:
                        geo_data = None
                        # Try ipapi.co first
                        try:
                            response = requests.get(f"https://ipapi.co/{ip_input}/json/", timeout=5)
                            if response.status_code == 200:
                                geo_data = response.json()
                        except:
                            pass
                        
                        # Fallback to ip-api.com
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
                            st.success(f"✅ Information found for {ip_input}")
                            
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("🌐 IP Address", ip_input)
                                st.metric("🏙️ City", geo_data.get('city', 'N/A'))
                            
                            with col2:
                                st.metric("🗺️ Region", geo_data.get('region', 'N/A'))
                                st.metric("🌍 Country", geo_data.get('country_name', 'N/A'))
                            
                            with col3:
                                st.metric("📡 ISP", geo_data.get('org', 'N/A'))
                                st.metric("🕐 Timezone", geo_data.get('timezone', 'N/A'))
                        else:
                            st.error("❌ Could not retrieve information for this IP")
                            
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        else:
            st.warning("⚠️ Please enter an IP address")

# 6. cPanel List
elif tool == "cPanel List":
    st.header("📂 cPanel Account Checker")
    st.markdown("View all cPanel accounts and their details")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("Access the cPanel account list to view hosting accounts")
    with col2:
        st.link_button("📂 Open List", "https://my.hostafrica.com/admin/custom/scripts/custom_tests/listaccounts.php", use_container_width=True)

# 7. My IP
elif tool == "My IP":
    st.header("📍 Find My IP Address")
    st.markdown("Quickly find your current public IP address")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("Click to open HostAfrica's IP detection tool")
    with col2:
        st.link_button("🔍 Get My IP", "https://ip.hostafrica.com/", use_container_width=True)

# 8. NS Updater
elif tool == "NS Updater":
    st.header("🔄 Bulk Nameserver Updater")
    st.markdown("Update nameservers for multiple domains at once")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("Use this tool to bulk update nameservers in WHMCS")
    with col2:
        st.link_button("🔄 Open Updater", "https://my.hostafrica.com/admin/addonmodules.php?module=nameserv_changer", use_container_width=True)

# 9. SSL Check
elif tool == "SSL Check":
    st.header("🔒 SSL Certificate Checker")
    st.markdown("Verify SSL certificate validity and expiration")
    
    domain_ssl = st.text_input("Enter domain (without https://):", placeholder="example.com")
    
    if st.button("🔍 Check SSL", use_container_width=True):
        if domain_ssl:
            domain_ssl = domain_ssl.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0].strip()
            
            with st.spinner(f"Checking SSL certificate for {domain_ssl}..."):
                try:
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
                                
                            with col2:
                                st.subheader("📅 Validity Period")
                                not_after = cert.get('notAfter')
                                st.write("**Valid Until:**", not_after)
                                
                                if not_after:
                                    try:
                                        expiry_date = datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z')
                                        days_remaining = (expiry_date - datetime.now()).days
                                        
                                        if days_remaining > 30:
                                            st.success(f"✅ {days_remaining} days remaining")
                                        elif days_remaining > 0:
                                            st.warning(f"⚠️ {days_remaining} days - Renew soon!")
                                        else:
                                            st.error(f"❌ Expired {abs(days_remaining)} days ago")
                                    except:
                                        pass
                            
                            if 'subjectAltName' in cert:
                                st.subheader("🌐 Covered Domains")
                                sans = [san[1] for san in cert['subjectAltName']]
                                for san in sans[:5]:
                                    st.code(san)
                                if len(sans) > 5:
                                    st.info(f"...and {len(sans) - 5} more domains")
                                
                except socket.gaierror:
                    st.error(f"❌ Could not resolve domain: {domain_ssl}")
                except socket.timeout:
                    st.error(f"⏱️ Connection timeout")
                except ssl.SSLError as ssl_err:
                    st.error(f"❌ SSL Error: {str(ssl_err)}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("⚠️ Please enter a domain name")

# 10. Knowledge Base
elif tool == "Knowledge Base":
    st.header("📚 HostAfrica Knowledge Base")
    st.markdown("Search the help center for guides and documentation")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("Access the HostAfrica help center and documentation")
    with col2:
        st.link_button("📚 Open Help Center", "https://help.hostafrica.com", use_container_width=True)

# 11. Flush DNS
elif tool == "Flush DNS":
    st.header("🧹 Flush Google DNS Cache")
    st.markdown("Clear Google's DNS cache for a domain")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("Use this to force Google DNS to fetch fresh DNS records")
    with col2:
        st.link_button("🧹 Flush Cache", "https://dns.google/cache", use_container_width=True)
