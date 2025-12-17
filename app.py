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

# --- SIDEBAR CHECKLIST (From Second File) ---
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
    - Check .htaccess / Error logs
    """)
    st.page_link("https://dns.google/cache", label="Flush Google DNS Cache", icon="🧹")

st.sidebar.divider()
st.sidebar.caption("💡 Tip: Use checklist while working tickets")

# --- MAIN APP LOGIC ---
st.title("Level 1 Tech Support Toolkit")
st.markdown(f"**Current Tool:** {tool}")

# 1. Identity & Verification
if tool == "Identity & Verification":
    st.header("🔐 Identity & Verification")
    st.info("Verify the client using the HostAfrica Admin internal tools.")
    st.page_link("https://my.hostafrica.com/admin/admin_tool/client-pin", label="Open Client PIN Verifier", icon="🔑")
    st.markdown("""
    **Standard Verification Procedure:**
    - Request the Support PIN from the client.
    - Match the PIN in the Admin portal.
    - If PIN is unavailable, verify via registered email address.
    """)

# 2. IP Unban Tool
elif tool == "Client Area IP Unban Tool":
    st.header("🔓 Client Area IP Unban")
    st.markdown("Use this tool to check for and remove firewall blocks on client IPs.")
    st.page_link("https://my.hostafrica.com/admin/custom/scripts/unban/", label="Go to Unban Tool", icon="🛡️")

# 3. DNS Records
elif tool == "DNS Records":
    st.header("🗂️ Detailed DNS Analysis")
    domain = st.text_input("Enter domain:", placeholder="hostafrica.com").strip().lower()
    if domain:
        with st.spinner("Analyzing DNS..."):
            # A Record Check
            res = requests.get(f"https://dns.google/resolve?name={domain}&type=A").json()
            if "Answer" in res:
                st.subheader("🌐 A Records")
                for r in res["Answer"]:
                    st.code(r["data"])
            
            # MX Record Check
            mx_res = requests.get(f"https://dns.google/resolve?name={domain}&type=MX").json()
            if "Answer" in mx_res:
                st.subheader("📧 MX Records")
                for r in mx_res["Answer"]:
                    st.code(r["data"])
            
            # TXT Records
            txt_res = requests.get(f"https://dns.google/resolve?name={domain}&type=TXT").json()
            if "Answer" in txt_res:
                st.subheader("📝 TXT Records (SPF/DKIM)")
                for r in txt_res["Answer"]:
                    st.code(r["data"])

# 4. Domain WHOIS Check
elif tool == "Domain WHOIS Check":
    st.header("🌐 Domain WHOIS Lookup")
    domain = st.text_input("Enter domain name:").strip().lower()
    if domain:
        try:
            with st.spinner('Fetching WHOIS...'):
                w = whois.whois(domain)
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Registrar:** {w.registrar}")
                    st.write(f"**Expiry:** {w.expiration_date}")
                with col2:
                    st.write("**Nameservers:**")
                    st.write(w.name_servers)
                with st.expander("View Raw WHOIS"):
                    st.code(w.text)
        except Exception as e:
            st.error(f"WHOIS Error: {e}")

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
