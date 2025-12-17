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
    st.page_link("https://my.hostafrica.com/admin/", label="Client PIN: HostAfrica Admin", icon="🔐")
    st.page_link("https://help.hostafrica.com", label="HostAfrica Help Center", icon="📚")
    st.page_link("https://my.hostafrica.com/clientarea.php", label="HostAfrica Client Area", icon="👤")
    
    st.markdown("---")
    st.markdown("### 2. Domain & DNS")
    st.info("Use the **Domain Check** tool below for WHOIS")
    st.page_link("https://my.hostafrica.com/admin/custom/scripts/custom_tests/listaccounts.php", label="cPanel Account Checker", icon="📂")
    st.page_link("https://my.hostafrica.com/admin/addonmodules.php?module=nameserver_changer", label="Bulk Nameserver Changer", icon="🔄")
    
    st.markdown("---")
    st.markdown("### 3. Connection & IP")
    st.page_link("https://my.hostafrica.com/index.php?m=ip_unban", label="IP Unban Tool", icon="🔓")
    st.page_link("https://developers.google.com/speed/public-dns/cache", label="Flush Google DNS Cache", icon="🧹")

st.sidebar.divider()

# Updated HostAfrica IP Redirection
st.sidebar.link_button("🌐 My Public IP", "https://ip.hostafrica.com", use_container_width=True)

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
