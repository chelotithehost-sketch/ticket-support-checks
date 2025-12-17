import streamlit as st
import requests
import json
from datetime import datetime
import socket
import ssl
import whois
from whois import exceptions

st.set_page_config(
    page_title="Level 1 Tech Support Toolkit",
    page_icon="🔧",
    layout="wide"
)

# Sidebar
st.sidebar.title("🔧 Support Tools")
tool = st.sidebar.radio(
    "Select Tool:",
    ["Domain Check", "My IP", "IP Lookup", "DNS Records", "SSL Check"]
)

st.sidebar.divider()

# Add Support Checklist in sidebar
with st.sidebar.expander("📋 Support Checklist", expanded=False):
    st.markdown("""
    ### Quick Start (60 sec)
    1. ✅ Check priority (VIP?)
    2. ✅ Confirm identity (PIN if guest)
    3. ✅ Check service status
    4. ✅ Add tags
    5. ✅ Troubleshoot
    
    ### Service Health Check
    - **Domain**: Active? Expired?
    - **Hosting**: Active/Suspended/Terminated?
    - **Nameservers**: Correct NS?
      - cPanel: ns1-ns4.host-ww.net
      - DirectAdmin: dan1-dan2.host-ww.net
    
    ### Troubleshooting
    **Email Issues:**
    - Check MX/SPF/DKIM/DMARC
    - Check if IP blocked
    - Review email logs
    
    **Website Issues:**
    - Verify A record
    - Check redirects (.htaccess)
    - Review error logs
    - Check IP blocks
    
    **DNS Issues:**
    - Verify domain registered
    - Check domain status
    - Confirm nameservers
    
    ### Tags
    - Mail | Hosting | DNS | Billing
    - VPS | Dedicated
    - cPanel | DirectAdmin | HmailPlus
    
    ### Reply Template
    Tell client:
    - ✅ What you checked
    - 🔍 What you found
    - 🛠️ What you fixed
    - 🧑‍💻 What they must do
    - ⏭️ What happens next
    
    ### Escalate If:
    - Server offline
    - Security breach
    - Beyond knowledge
    - >30 min no progress
    """)

st.sidebar.divider()
st.sidebar.caption("💡 Tip: Use checklist while working tickets")

st.title("Level 1 Tech Support Toolkit")
st.markdown("Essential diagnostic tools for first-line support")

if tool == "Domain Check":
    st.header("🌐 Comprehensive Domain Status Check")
    st.markdown("Check domain registration, DNS configuration, and nameserver status")
    
    domain = st.text_input("Enter domain:", placeholder="example.com")
    if st.button("Check Domain Status"):
        if domain:
            domain = domain.strip().lower()
            
            with st.spinner("Performing comprehensive domain check..."):
                # Initialize status tracking
                issues = []
                warnings = []
                success_checks = []
                
                # 1. DNS Resolution Check
                st.subheader("🔍 DNS Resolution Status")
                try:
                    response = requests.get(f"https://dns.google/resolve?name={domain}&type=A", timeout=5)
                    data = response.json()
                    
                    if data.get('Status') == 0 and data.get('Answer'):
                        st.success(f"✅ Domain {domain} is resolving")
                        success_checks.append("DNS resolution working")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("**A Records (IPv4):**")
                            for record in data['Answer']:
                                st.code(record['data'])
                        
                        # Check for IPv6
                        try:
                            ipv6_response = requests.get(f"https://dns.google/resolve?name={domain}&type=AAAA", timeout=5)
                            ipv6_data = ipv6_response.json()
                            if ipv6_data.get('Answer'):
                                with col2:
                                    st.write("**AAAA Records (IPv6):**")
                                    for record in ipv6_data['Answer'][:3]:
                                        st.code(record['data'])
                        except:
                            pass
                            
                    elif data.get('Status') == 3:
                        st.error("❌ Domain name does not exist (NXDOMAIN)")
                        issues.append("Domain not registered or expired")
                    else:
                        st.error("❌ Domain not resolving")
                        issues.append("DNS resolution failed")
                        
                except Exception as e:
                    st.error(f"❌ DNS check failed: {str(e)}")
                    issues.append(f"DNS error: {str(e)}")
                
                # 2. Nameserver Check
                st.subheader("🖥️ Nameserver Configuration")
                try:
                    ns_response = requests.get(f"https://dns.google/resolve?name={domain}&type=NS", timeout=5)
                    ns_data = ns_response.json()
                    
                    if ns_data.get('Answer'):
                        nameservers = [record['data'].rstrip('.') for record in ns_data['Answer']]
                        
                        if len(nameservers) >= 2:
                            st.success(f"✅ Found {len(nameservers)} nameservers (redundancy good)")
                            success_checks.append("Multiple nameservers configured")
                        elif len(nameservers) == 1:
                            st.warning("⚠️ Only 1 nameserver found (should have at least 2 for redundancy)")
                            warnings.append("Insufficient nameserver redundancy")
                        
                        for ns in nameservers:
                            st.code(ns)
                            
                    else:
                        st.error("❌ No authoritative nameservers found")
                        issues.append("No nameservers configured - domain may be on hold or suspended")
                        st.warning("""
                        **Common causes:**
                        - Domain recently registered but nameservers not set
                        - Domain suspended for verification (.co.za domains)
                        - Domain on registrar hold
                        - Expired domain in grace period
                        """)
                        
                except Exception as e:
                    st.error(f"❌ Nameserver check failed: {str(e)}")
                    issues.append("Could not retrieve nameserver information")
                
                # 3. SOA Record Check
                st.subheader("📋 SOA (Start of Authority) Record")
                try:
                    soa_response = requests.get(f"https://dns.google/resolve?name={domain}&type=SOA", timeout=5)
                    soa_data = soa_response.json()
                    
                    if soa_data.get('Answer'):
                        soa_record = soa_data['Answer'][0]['data']
                        st.success("✅ SOA record found")
                        st.code(soa_record)
                        success_checks.append("SOA record configured")
                    else:
                        st.warning("⚠️ No SOA record found")
                        warnings.append("Missing SOA record")
                        
                except Exception as e:
                    st.warning(f"⚠️ Could not check SOA: {str(e)}")
                
                # 4. WHOIS Check using python-whois library
                st.subheader("📝 Domain Registration & WHOIS Information")
                
                whois_data = None
                whois_success = False
                whois_error_message = None

                try:
                    whois_data = whois.whois(domain)
                    whois_success = True
                    
                except exceptions.FailedParsing as e:
                    whois_error_message = "WHOIS Parsing Error: The WHOIS server returned data in an unexpected format."
                    st.error(f"❌ WHOIS check failed: {whois_error_message}")
                    st.caption("See Raw WHOIS Output below for details.")
                    
                except exceptions.WhoisCommandFailed as e:
                    whois_error_message = "WHOIS Command Failed: Unable to connect to the WHOIS server."
                    st.error(f"❌ WHOIS check failed: {whois_error_message}")

                except Exception as e:
                    whois_error_message = f"WHOIS Lookup Error: {type(e).__name__}"
                    st.error(f"❌ WHOIS check failed: {whois_error_message}")

                # Display WHOIS data if successful
                if whois_success and whois_data and whois_data.domain_name:
                    st.success("✅ WHOIS information retrieved")
                    success_checks.append("WHOIS lookup successful")

                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Domain:** {domain}")
                        
                        registrar = whois_data.registrar
                        if registrar:
                            st.write(f"**Registrar:** {registrar}")

                        status_list = whois_data.status
                        if status_list:
                            st.write("**Domain Status:**")
                            if not isinstance(status_list, list):
                                status_list = [status_list] if status_list else []
                                
                            for status in status_list[:5]:
                                status_lower = str(status).lower()
                                if any(x in status_lower for x in ['ok', 'active', 'registered']):
                                    st.success(f"✅ {status.split()[0]}")
                                elif any(x in status_lower for x in ['hold', 'lock', 'suspended', 'pending delete']):
                                    st.error(f"❌ {status.split()[0]}")
                                    issues.append(f"Domain status: {status.split()[0]}")
                                elif any(x in status_lower for x in ['pending', 'verification', 'grace', 'expired']):
                                    st.warning(f"⚠️ {status.split()[0]}")
                                    if 'expired' in status_lower:
                                        issues.append(f"Domain is expired")
                                    else:
                                        warnings.append(f"Domain status: {status.split()[0]}")
                                else:
                                    st.info(f"ℹ️ {status.split()[0]}")
                        
                        registrant = whois_data.registrant
                        if registrant and 'redacted' not in str(registrant).lower():
                            st.write(f"**Registrant:** {registrant}")

                    with col2:
                        created_date = whois_data.creation_date
                        expires_date = whois_data.expiration_date
                        updated_date = whois_data.updated_date
                        
                        if created_date:
                            st.write(f"**Created:** {str(created_date).split()[0]}")
                        
                        if updated_date:
                            st.write(f"**Updated:** {str(updated_date).split()[0]}")
                        
                        if expires_date:
                            st.write(f"**Expires:** {str(expires_date).split()[0]}")
                            try:
                                if isinstance(expires_date, list):
                                    expiry = expires_date[0]
                                else:
                                    expiry = expires_date
                                    
                                if expiry:
                                    days_left = (expiry - datetime.now().replace(microsecond=0)).days
                                    
                                    if days_left < 0:
                                        st.error(f"❌ EXPIRED {abs(days_left)} days ago!")
                                        issues.append(f"Domain expired {abs(days_left)} days ago")
                                    elif days_left < 30:
                                        st.error(f"⚠️ {days_left} days - URGENT!")
                                        issues.append(f"Expires in {days_left} days")
                                    elif days_left < 90:
                                        st.warning(f"⚠️ {days_left} days")
                                        warnings.append(f"Expires in {days_left} days")
                                    else:
                                        st.success(f"✅ {days_left} days")
                            except:
                                pass
                    
                    nameservers = whois_data.name_servers
                    if nameservers:
                        st.write("**WHOIS Nameservers:**")
                        for ns in nameservers[:3]:
                            st.caption(f"• {str(ns).lower().rstrip('.')}")
                    
                    with st.expander("📄 View Full Raw WHOIS Record"):
                        st.json(str(whois_data))

                else:
                    st.warning("⚠️ Could not retrieve WHOIS information via automated library.")
                    if whois_error_message:
                        st.caption(f"Reason: {whois_error_message}")

                    st.info(f"""
                    **Try manual lookup at:**
                    - [ICANN Lookup](https://lookup.icann.org/en/lookup?name={domain})
                    - [Who.is](https://who.is/whois/{domain})
                    """)
                    warnings.append("WHOIS data unavailable via automated tools")

                # 5. Summary Report
                st.divider()
                st.subheader("📊 Domain Health Summary")
                
                if not issues and not warnings:
                    st.success("🎉 **Domain is healthy!** All checks passed.")
                    st.balloons()
                else:
                    if issues:
                        with st.expander("❌ Critical Issues", expanded=True):
                            for issue in issues:
                                st.error(f"• {issue}")
                    
                    if warnings:
                        with st.expander("⚠️ Warnings", expanded=True):
                            for warning in warnings:
                                st.warning(f"• {warning}")
                    
                    if success_checks:
                        with st.expander("✅ Passed Checks"):
                            for check in success_checks:
                                st.success(f"• {check}")
                
                # Troubleshooting tips
                if issues or warnings:
                    with st.expander("💡 Troubleshooting Tips"):
                        st.markdown("""
                        **Common Issues & Solutions:**
                        
                        **No Nameservers / Domain on Hold:**
                        - For .co.za domains: Complete COZA verification process
                        - Contact your domain registrar to remove hold status
                        - Verify domain ownership/payment is up to date
                        - Set up authoritative nameservers
                        
                        **Domain Not Resolving:**
                        - Check if nameservers are properly configured
                        - Verify DNS records are set up correctly
                        - Wait 24-48 hours for DNS propagation
                        - Contact hosting provider or registrar
                        
                        **Domain Suspended/Expired:**
                        - Renew domain registration immediately
                        - Update payment information with registrar
                        - Check for verification emails from registrar
                        - Contact registrar support for assistance
                        """)

elif tool == "My IP":
    st.header("📍 Find My IP Address")
    st.markdown("Discover your public IP address and network information")
    
    st.info("💡 Click the button below to open a new tab that will show your real public IP address")
    
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <a href="https://www.whatismyip.com/" target="_blank" style="
            display: inline-block;
            padding: 15px 40px;
            background-color: #FF4B4B;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-size: 18px;
            font-weight: bold;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        ">
            🔍 Get My IP Address
        </a>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-top: 10px; color: #666;">
        <small>Click the button above to open a trusted IP detection site in a new tab</small>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **What this does:**
        - Opens a trusted IP detection site
        - Shows your real public IP address
        - No server-side detection needed
        """)
    
    with col2:
        st.markdown("""
        **Alternative Sites:**
        - [IPChicken.com](https://ipchicken.com/)
        - [IPInfo.io](https://ipinfo.io/)
        - [ICanHazIP.com](https://icanhazip.com/)
        """)
    
    st.divider()
    
    st.subheader("🔎 Already know your IP?")
    st.markdown("Copy your IP address from the opened tab and use the **IP Lookup** tool in the sidebar to get detailed information about it!")
    
    st.markdown("""
    ### Quick Steps:
    1. ✅ Click "Get My IP Address" button above
    2. ✅ Copy your IP address from the opened page
    3. ✅ Go to **IP Lookup** tool (in sidebar)
    4. ✅ Paste your IP and click "Lookup IP"
    """)

elif tool == "IP Lookup":
    st.header("🔍 IP Address Lookup")
    st.markdown("Look up geolocation information for any IP address")
    
    ip_input = st.text_input("Enter IP address:", placeholder="8.8.8.8")
    
    if st.button("Lookup IP"):
        if ip_input:
            with st.spinner(f"Looking up {ip_input}..."):
                try:
                    import re
                    ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
                    if not re.match(ip_pattern, ip_input):
                        st.error("❌ Invalid IP address format")
                    else:
                        geo_data = None
                        try:
                            response = requests.get(f"https://ipapi.co/{ip_input}/json/", timeout=5)
                            if response.status_code == 200:
                                geo_data = response.json()
                        except:
                            pass
                        
                        if not geo_data or geo_data.get('error'):
                            try:
                                response = requests.get(f"http://ip-api.com/json/{ip_input}", timeout=5)
                                if response.status_code == 200:
                                    fallback_data = response.json()
                                    if fallback_data.get('status') == 'success':
                                        geo_data = {
                                            'ip': ip_input,
                                            'city': fallback_data.get('city'),
                                            'region': fallback_data.get('regionName'),
                                            'country_name': fallback_data.get('country'),
                                            'postal': fallback_data.get('zip'),
                                            'latitude': fallback_data.get('lat'),
                                            'longitude': fallback_data.get('lon'),
                                            'org': fallback_data.get('isp'),
                                            'timezone': fallback_data.get('timezone'),
                                            'asn': fallback_data.get('as')
                                        }
                            except:
                                pass
                        
                        if geo_data and not geo_data.get('error'):
                            st.success(f"✅ Information found for {ip_input}")
                            
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("🌐 IP Address", ip_input)
                                st.metric("🏙️ City", geo_data.get('city', 'N/A'))
                                st.metric("📮 Postal Code", geo_data.get('postal', 'N/A'))
                            
                            with col2:
                                st.metric("🗺️ Region", geo_data.get('region', 'N/A'))
                                st.metric("🌍 Country", geo_data.get('country_name', 'N/A'))
                                st.metric("🕐 Timezone", geo_data.get('timezone', 'N/A'))
                            
                            with col3:
                                st.metric("📡 ISP/Organization", geo_data.get('org', 'N/A'))
                                if geo_data.get('latitude') and geo_data.get('longitude'):
                                    st.metric("📍 Coordinates", f"{geo_data['latitude']:.4f}, {geo_data['longitude']:.4f}")
                                if geo_data.get('asn'):
                                    st.metric("🔢 ASN", geo_data.get('asn', 'N/A'))
                            
                            if geo_data.get('latitude') and geo_data.get('longitude'):
                                map_url = f"https://www.google.com/maps?q={geo_data['latitude']},{geo_data['longitude']}"
                                st.markdown(f"🗺️ [View on Google Maps]({map_url})")
                            
                            with st.expander("🔍 View Full Details"):
                                st.json(geo_data)
                        else:
                            st.error("❌ Could not retrieve information for this IP address")
                            st.info("The IP might be private, invalid, or the service is unavailable")
                            
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("⚠️ Please enter an IP address")

elif tool == "DNS Records":
    st.header("🗂️ Detailed DNS Analysis")
    st.markdown("Comprehensive DNS record analysis similar to intoDNS.com")
    
    domain = st.text_input("Enter domain:", placeholder="example.com")
    if st.button("Analyze DNS"):
        if domain:
            domain = domain.strip().lower()
            
            with st.spinner("Performing detailed DNS analysis..."):
                
                # 1. Nameservers
                st.subheader("🖥️ Nameservers (NS Records)")
                try:
                    ns_response = requests.get(f"https://dns.google/resolve?name={domain}&type=NS", timeout=5)
                    ns_data = ns_response.json()
                    
                    if ns_data.get('Answer'):
                        nameservers = [record['data'].rstrip('.') for record in ns_data['Answer']]
                        
                        if len(nameservers) >= 2:
                            st.success(f"✅ {len(nameservers)} nameservers found (good redundancy)")
                        else:
                            st.warning(f"⚠️ Only {len(nameservers)} nameserver(s) - recommend at least 2")
                        
                        for ns in nameservers:
                            try:
                                ns_ip_response = requests.get(f"https://dns.google/resolve?name={ns}&type=A", timeout=3)
                                ns_ip_data = ns_ip_response.json()
                                if ns_ip_data.get('Answer'):
                                    ns_ip = ns_ip_data['Answer'][0]['data']
                                    st.code(f"{ns} → {ns_ip}")
                                else:
                                    st.code(ns)
                            except:
                                st.code(ns)
                    else:
                        st.error("❌ No nameservers found")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                
                # 2. A Records
                st.subheader("🌐 A Records (IPv4 Addresses)")
                try:
                    a_response = requests.get(f"https://dns.google/resolve?name={domain}&type=A", timeout=5)
                    a_data = a_response.json()
                    
                    if a_data.get('Answer'):
                        st.success(f"✅ {len(a_data['Answer'])} A record(s) found")
                        for record in a_data['Answer']:
                            col1, col2 = st.columns([2, 1])
                            with col1:
                                st.code(record['data'])
                            with col2:
                                st.caption(f"TTL: {record.get('TTL', 'N/A')}s")
                    else:
                        st.warning("⚠️ No A records found")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                
                # 3. AAAA Records
                st.subheader("🌍 AAAA Records (IPv6 Addresses)")
                try:
                    aaaa_response = requests.get(f"https://dns.google/resolve?name={domain}&type=AAAA", timeout=5)
                    aaaa_data = aaaa_response.json()
                    
                    if aaaa_data.get('Answer'):
                        st.success(f"✅ {len(aaaa_data['Answer'])} AAAA record(s) found")
                        for record in aaaa_data['Answer']:
                            col1, col2 = st.columns([2, 1])
                            with col1:
                                st.code(record['data'])
                            with col2:
                                st.caption(f"TTL: {record.get('TTL', 'N/A')}s")
                    else:
                        st.info("ℹ️ No IPv6 (AAAA) records configured")
                except Exception as e:
                    st.info("ℹ️ No IPv6 records")
                
                # 4. MX Records
                st.subheader("📧 MX Records (Mail Servers)")
                try:
                    mx_response = requests.get(f"https://dns.google/resolve?name={domain}&type=MX", timeout=5)
                    mx_data = mx_response.json()
                    
                    if mx_data.get('Answer'):
                        st.success(f"✅ {len(mx_data['Answer'])} mail server(s) configured")
                        
                        mx_records = sorted(mx_data['Answer'], key=lambda x: int(x['data'].split()[0]))
                        
                        for record in mx_records:
                            parts = record['data'].split()
                            priority = parts[0]
                            mail_server = parts[1].rstrip('.')
                            
                            col1, col2, col3 = st.columns([1, 3, 1])
                            with col1:
                                st.metric("Priority", priority)
                            with col2:
                                st.code(mail_server)
                            with col3:
                                st.caption(f"TTL: {record.get('TTL', 'N/A')}s")
                                
                            try:
                                mx_ip_response = requests.get(f"https://dns.google/resolve?name={mail_server}&type=A", timeout=3)
                                mx_ip_data = mx_ip_response.json()
                                if mx_ip_data.get('Answer'):
                                    mx_ip = mx_ip_data['Answer'][0]['data']
                                    st.caption(f"→ {mx_ip}")
                            except:
                                pass
                    else:
                        st.warning("⚠️ No MX records found - email will not work for this domain")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                
                # 5. TXT Records
                st.subheader("📝 TXT Records (SPF, DKIM, DMARC, etc.)")
                try:
                    txt_response = requests.get(f"https://dns.google/resolve?name={domain}&type=TXT", timeout=5)
                    txt_data = txt_response.json()
                    
                    spf_found = False
                    dmarc_found = False
                    
                    if txt_data.get('Answer'):
                        st.success(f"✅ {len(txt_data['Answer'])} TXT record(s) found")
                        
                        for record in txt_data['Answer']:
                            txt_value = record['data'].strip('"')
                            
                            if txt_value.startswith('v=spf1'):
                                st.info("**🛡️ SPF Record (Email Authentication)**")
                                spf_found = True
                            elif txt_value.startswith('v=DMARC'):
                                st.info("**🛡️ DMARC Record (Email Policy)**")
                                dmarc_found = True
                            elif 'dkim' in txt_value.lower() or txt_value.startswith('v=DKIM'):
                                st.info("**🔑 DKIM Record (Email Signature)**")
                            else:
                                st.info("**📋 General TXT Record**")
                            
                            st.code(txt_value, language="text")
                            st.caption(f"TTL: {record.get('TTL', 'N/A')}s")
                            st.divider()
                        
                        if not dmarc_found:
                            try:
                                dmarc_response = requests.get(f"https://dns.google/resolve?name=_dmarc.{domain}&type=TXT", timeout=5)
                                dmarc_data = dmarc_response.json()
                                if dmarc_data.get('Answer'):
                                    st.info("**🛡️ DMARC Record (at _dmarc subdomain)**")
                                    st.code(dmarc_data['Answer'][0]['data'].strip('"'))
                                    dmarc_found = True
                            except:
                                pass
                        
                        if not spf_found:
                            st.warning("⚠️ No SPF record found - emails may be marked as spam")
                        if not dmarc_found:
                            st.warning("⚠️ No DMARC record found - domain vulnerable to email spoofing")
                            
                    else:
                        st.info("ℹ️ No TXT records found")
                        st.warning("⚠️ Consider adding SPF and DMARC records for email security")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                
                # 6. SOA Record
                st.subheader("🏛️ SOA Record (Zone Authority)")
                try:
                    soa_response = requests.get(f"https://dns.google/resolve?name={domain}&type=SOA", timeout=5)
                    soa_data = soa_response.json()
                    
                    if soa_data.get('Answer'):
                        soa_parts = soa_data['Answer'][0]['data'].split()
                        st.success("✅ SOA record found")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Primary NS:** {soa_parts[0].rstrip('.')}")
                            st.write(f"**Admin Email:** {soa_parts[1].replace('.', '@', 1).rstrip('.')}")
                            st.write(f"**Serial:** {soa_parts[2]}")
                        with col2:
                            st.write(f"**Refresh:** {soa_parts[3]}s")
                            st.write(f"**Retry:** {soa_parts[4]}s")
                            st.write(f"**Expire:** {soa_parts[5]}s")
                            st.write(f"**Min TTL:** {soa_parts[6]}s")
                    else:
                        st.warning("⚠️ No SOA record found")
                except Exception as e:
                    st.warning(f"⚠️ Could not retrieve SOA: {str(e)}")

elif tool == "SSL Check":
    st.header("🔒 SSL Certificate Check")
    domain = st.text_input("Enter domain (without https://):", placeholder="example.com")
    if st.button("Check SSL Certificate"):
        if domain:
            domain = domain.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0].strip()
            
            with st.spinner(f"Analyzing SSL certificate for {domain}..."):
                try:
                    context = ssl.create_default_context()
                    with socket.create_connection((domain, 443), timeout=10) as sock:
                        with context.wrap_socket(sock, server_hostname=domain) as secure_sock:
                            cert = secure_sock.getpeercert()
                            
                            st.success(f"✅ SSL Certificate found and valid for {domain}")
                            
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
                            
                            if 'subjectAltName' in cert:
                                st.subheader("🌐 Subject Alternative Names")
                                sans = [san[1] for san in cert['subjectAltName']]
                                
                                for san in sans[:10]:
                                    st.code(san)
                                
                                if len(sans) > 10:
                                    st.info(f"...and {len(sans) - 10} more domain(s)")
                            
                            with st.expander("🔍 View Certificate Summary"):
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
                    st.error(f"❌ Could not resolve domain: {domain}")
                    st.info("💡 Make sure the domain name is correct and accessible")
                    
                except socket.timeout:
                    st.error(f"⏱️ Connection timeout for {domain}")
                    st.info("💡 The server might be slow or blocking connections")
                    
                except ssl.SSLError as ssl_err:
                    st.error(f"❌ SSL Error: {str(ssl_err)}")
                    st.warning("""
                    **Common SSL Issues:**
                    - Certificate has expired
                    - Certificate is self-signed
                    - Certificate name doesn't match domain
                    - Incomplete certificate chain
                    """)
                    
                except Exception as e:
                    st.error(f"❌ Error checking SSL: {str(e)}")
                    st.info(f"💡 Try checking manually at: https://www.ssllabs.com/ssltest/analyze.html?d={domain}")
        else:
            st.warning("⚠️ Please enter a domain name")
