import streamlit as st
import requests
import json
from datetime import datetime
import socket
import ssl
import whois
from whois import exceptions

st.set_page_config(
    page_title="Tech Support Toolkit",
    page_icon="🔧",
    layout="wide"
)

# Sidebar Configuration
st.sidebar.title("🔧 Support Tools")
tool = st.sidebar.radio(
    "Select Tool:",
    ["Domain Check", "IP Lookup", "DNS Records", "SSL Check"]
)

st.sidebar.divider()

# --- IMPROVED SUPPORT CHECKLIST ---
with st.sidebar.expander("📋 Support Checklist", expanded=True):
    st.markdown("### 1. Identity & Verification")
    st.page_link("https://my.hostafrica.com/admin/admin_tool/client-pin", label="Client PIN: HostAfrica Admin", icon="🔐")
    st.page_link("https://help.hostafrica.com", label="HostAfrica Help Center", icon="📚")
    
    st.markdown("---")
    st.markdown("### 2. cPanel Hosting Checker")
    st.info("Use the **Domain Check** tool for cPanel")
    st.page_link("https://my.hostafrica.com/admin/custom/scripts/custom_tests/listaccounts.php", label="cPanel Account Checker", icon="📂")
    st.info("Use the **Nameserver** Bulk Updater")
    st.page_link("https://my.hostafrica.com/admin/addonmodules.php?module=nameserver_changer", label="Bulk Nameserver Changer", icon="🔄")
    
    st.markdown("---")
    st.markdown("### 3. Connection & IP")
    st.page_link("https://my.hostafrica.com/admin/custom/scripts/unban/", label="IP Unban Tool", icon="🔓")
    st.page_link("https://dns.google/cache", label="Flush Google DNS Cache", icon="🧹")

st.sidebar.divider()

# Main App Logic
st.title("Level 1 Tech Support Toolkit")
st.markdown("Direct diagnostic tools for HostAfrica Support Agents")

if tool == "Domain Check":
    st.header("🌐 Domain & WHOIS Lookup")
    domain = st.text_input("Enter domain name (e.g., hostafrica.com):")
    
    if domain:
        try:
            with st.spinner('Fetching WHOIS data...'):
                w = whois.whois(domain)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Registrar Info")
                    st.write(f"**Registrar:** {w.registrar}")
                    st.write(f"**Creation Date:** {w.creation_date}")
                    st.write(f"**Expiry Date:** {w.expiration_date}")
                
                with col2:
                    st.subheader("Nameservers")
                    st.write(w.name_servers)

                st.divider()
                with st.expander("View Full Raw WHOIS Data"):
                    st.code(w.text)
                    
        except Exception as e:
            st.error(f"Error fetching WHOIS: {e}")
            
elif tool == "My IP":
    st.header("📍 Find My IP Address")
    st.markdown("Discover your public IP address and network information")
    
    st.info("💡 Click the button below to open a new tab that will show your real public IP address")
    
    st.markdown("""
    <div style="text-align: center; padding: 20px;">
        <a href="https://ip.hostafrica.com/" target="_blank" style="
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
    ip_input = st.text_input("Enter IP Address:")
    if ip_input:
        response = requests.get(f"https://ipapi.co/{ip_input}/json/").json()
        if "error" not in response:
            st.json(response)
        else:
            st.error("Invalid IP or API limit reached.")


elif tool == "DNS Records":
    st.header("🗂️ DNS Record Analyzer")
    
    domain_dns = st.text_input("Enter domain for DNS check:")
    record_types = ['A', 'MX', 'TXT', 'CNAME', 'NS']
    
    if domain_dns:
        for r_type in record_types:
            st.subheader(f"{r_type} Records")
            try:
                # Note: In a real production app, use 'dnspython' library here
                # Simplified example for logic flow:
                st.info(f"Checking {r_type} records for {domain_dns}...")
            except Exception as e:
                st.error(f"Could not retrieve {r_type} records.")

elif tool == "SSL Check":
    st.header("🔒 SSL Certificate Check")
    domain_ssl = st.text_input("Enter domain for SSL check (e.g., hostafrica.com):")
    if domain_ssl:
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain_ssl, 443)) as sock:
                with context.wrap_socket(sock, server_hostname=domain_ssl) as ssock:
                    cert = ssock.getpeercert()
                    st.success(f"✅ SSL Certificate is Valid for {domain_ssl}")
                    st.json(cert)
        except Exception as e:
            st.error(f"SSL Check Failed: {e}")
