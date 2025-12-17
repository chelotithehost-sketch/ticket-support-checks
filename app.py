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
    
# 3. DNS Records
elif tool == "DNS Records":
    st.header("🗂️ DNS Record Analyzer")
    st.markdown("Comprehensive check of resolution, mail routing, and authentication records.")
    
    

    domain_dns = st.text_input("Enter domain (e.g. hostafrica.com):", key="dns_input")
    
    if domain_dns:
        domain_dns = domain_dns.strip().lower()
        
        with st.spinner(f"Analyzing all DNS records for {domain_dns}..."):
            issues, warnings, success_checks = [], [], []
            
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

# 4. Domain WHOIS Check
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
