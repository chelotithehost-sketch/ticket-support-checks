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
    page_title="Level 1 Tech Support Toolkit",
    page_icon="🔧",
    layout="wide"
)

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🔧 Support Tools")
tool = st.sidebar.radio(
    "Select Tool:",
    [
        "Identity & Verification", 
        "Client Area IP Unban Tool", 
        "DNS Records", 
        "Domain WHOIS Check", 
        "IP Lookup", 
        "cPanel Hosting Checker", 
        "My IP Finder", 
        "Nameserver Bulk Updater", 
        "SSL Check", 
        "HostAfrica Knowledgebase"
    ]
)

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
    """)
    st.page_link("https://developers.google.com/speed/public-dns/cache", label="Flush Google DNS Cache", icon="🧹")

# --- MAIN APP LOGIC ---
st.title("Level 1 Tech Support Toolkit")

# 1. Identity & Verification
if tool == "Identity & Verification":
    st.header("🔐 Identity & Verification")
    st.page_link("https://my.hostafrica.com/admin/admin_tool/client-pin", label="Open HostAfrica Admin Tool", icon="🔑")

# 2. IP Unban Tool
elif tool == "Client Area IP Unban Tool":
    st.header("🔓 Client Area IP Unban")
    st.page_link("https://my.hostafrica.com/admin/custom/scripts/unban/", label="Go to IP Unban Tool", icon="🛡️")

# 3. DNS Records (INTEGRATED COMPREHENSIVE LOGIC)
elif tool == "DNS Records":
    st.header("🗂️ DNS Record Analyzer")
    st.markdown("Check domain resolution, DNS configuration, and nameserver status.")
    
    
    domain_dns = st.text_input("Enter domain:", placeholder="example.com")
    
    if domain_dns:
        domain_dns = domain_dns.strip().lower()
        
        with st.spinner(f"Analyzing DNS for {domain_dns}..."):
            # Initialize status tracking for the summary report
            issues = []
            warnings = []
            success_checks = []
            
            # --- 1. DNS Resolution Check (A & AAAA) ---
            st.subheader("🔍 DNS Resolution Status")
            try:
                # Check A Records
                response = requests.get(f"https://dns.google/resolve?name={domain_dns}&type=A", timeout=5)
                data = response.json()
                
                if data.get('Status') == 0 and data.get('Answer'):
                    st.success(f"✅ Domain {domain_dns} is resolving")
                    success_checks.append("DNS resolution working")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**A Records (IPv4):**")
                        for record in data['Answer']:
                            st.code(record['data'])
                    
                    # Check for IPv6 (AAAA)
                    try:
                        ipv6_res = requests.get(f"https://dns.google/resolve?name={domain_dns}&type=AAAA", timeout=5).json()
                        if ipv6_res.get('Answer'):
                            with col2:
                                st.write("**AAAA Records (IPv6):**")
                                for record in ipv6_res['Answer'][:3]:
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

            # --- 2. Nameserver Check ---
            st.subheader("🖥️ Nameserver Configuration")
            try:
                ns_response = requests.get(f"https://dns.google/resolve?name={domain_dns}&type=NS", timeout=5).json()
                
                if ns_response.get('Answer'):
                    nameservers = [record['data'].rstrip('.') for record in ns_response['Answer']]
                    
                    if len(nameservers) >= 2:
                        st.success(f"✅ Found {len(nameservers)} nameservers")
                        success_checks.append("Multiple nameservers configured")
                    else:
                        st.warning("⚠️ Insufficient nameserver redundancy (found only 1)")
                        warnings.append("Insufficient nameserver redundancy")
                    
                    for ns in nameservers:
                        st.code(ns)
                else:
                    st.error("❌ No authoritative nameservers found")
                    issues.append("No nameservers configured")
                    st.warning("**Common causes:** Registrar hold, suspension, or missing NS setup.")
            except Exception as e:
                st.error(f"❌ Nameserver check failed: {str(e)}")

            # --- 3. SOA Record Check ---
            st.subheader("📋 SOA (Start of Authority) Record")
            try:
                soa_res = requests.get(f"https://dns.google/resolve?name={domain_dns}&type=SOA", timeout=5).json()
                if soa_res.get('Answer'):
                    st.success("✅ SOA record found")
                    st.code(soa_res['Answer'][0]['data'])
                    success_checks.append("SOA record configured")
                else:
                    st.warning("⚠️ No SOA record found")
                    warnings.append("Missing SOA record")
            except Exception as e:
                st.warning(f"⚠️ Could not check SOA: {str(e)}")

            # --- Summary Report for DNS ---
            st.divider()
            st.subheader("📊 DNS Health Summary")
            if not issues and not warnings:
                st.success("🎉 DNS configuration looks healthy!")
            else:
                if issues:
                    for issue in issues: st.error(f"• {issue}")
                if warnings:
                    for warning in warnings: st.warning(f"• {warning}")

# 4. Domain WHOIS Check (INTEGRATED NEW LOGIC)
elif tool == "Domain WHOIS Check":
    st.header("🌐 Domain WHOIS Lookup")
    domain = st.text_input("Enter domain name (e.g., example.com):").strip().lower()
    
    if domain:
        # Initialize reporting lists
        issues = []
        warnings = []
        success_checks = []

        with st.spinner('Performing deep WHOIS analysis...'):
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

            # Summary Report Section
            st.divider()
            st.subheader("📊 Domain Health Summary")
            
            if not issues and not warnings and whois_success:
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
                    - **Domain Expired:** Renew registration immediately with the registrar.
                    - **Domain on Hold:** Check for registrar verification emails or pending COZA documents.
                    - **Wrong Nameservers:** Ensure NS records match the hosting package (cPanel vs DirectAdmin).
                    """)

# 5. IP Lookup
elif tool == "IP Lookup":
    st.header("🔍 IP Address Geo-Lookup")
    ip_input = st.text_input("Enter IP Address:")
    if ip_input:
        res = requests.get(f"https://ipapi.co/{ip_input}/json/").json()
        if "error" not in res:
            st.json(res)
        else:
            st.error("Invalid IP.")

# 6. cPanel Hosting Checker
elif tool == "cPanel Hosting Checker":
    st.header("📂 cPanel Account Checker")
    st.page_link("https://my.hostafrica.com/admin/custom/scripts/custom_tests/listaccounts.php", label="Open cPanel Account List", icon="📂")

# 7. My IP Finder
elif tool == "My IP Finder":
    st.header("📍 Find My IP Address")
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <a href="https://ip.hostafrica.com/" target="_blank" style="display: inline-block; padding: 15px 40px; background-color: #FF4B4B; color: white; text-decoration: none; border-radius: 8px; font-weight: bold;">
            🔍 Get My IP Address
        </a>
    </div>
    """, unsafe_allow_html=True)
    st.info("Click the button above to open the HostAfrica IP detector in a new tab.")

# 8. Nameserver Bulk Updater
elif tool == "Nameserver Bulk Updater":
    st.header("🔄 Bulk Nameserver Updater")
    st.page_link("https://my.hostafrica.com/admin/addonmodules.php?module=nameserv_changer", label="Open NS Changer Module", icon="🔄")

# 9. SSL Check
elif tool == "SSL Check":
    st.header("🔒 SSL Certificate Check")
    domain_ssl = st.text_input("Enter domain (e.g., hostafrica.com):").strip().lower()
    if domain_ssl:
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain_ssl, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=domain_ssl) as ssock:
                    cert = ssock.getpeercert()
                    st.success(f"✅ SSL Valid for {domain_ssl}")
                    st.json(cert)
        except Exception as e:
            st.error(f"SSL Check Failed: {e}")

# 10. HostAfrica Knowledgebase
elif tool == "HostAfrica Knowledgebase":
    st.header("📚 HostAfrica Help Center")
    st.page_link("https://help.hostafrica.com", label="Search Knowledgebase", icon="📚")
