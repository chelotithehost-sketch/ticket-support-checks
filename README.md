# Level 1 Tech Support Toolkit 🔧

A comprehensive Streamlit-based web application for Level 1 technical support teams to diagnose common domain, DNS, IP, and SSL issues.

## Features

### 🌐 Domain Check
- Comprehensive domain status verification
- DNS resolution testing
- Nameserver configuration check
- WHOIS information lookup
- Domain expiration monitoring
- Automated health summary with issues and warnings

### 📍 My IP
- Quick access to IP detection services
- Links to trusted IP lookup websites
- Integration with IP Lookup tool

### 🔍 IP Lookup
- Geolocation information for any IP address
- ISP/Organization details
- Timezone and coordinate information
- Google Maps integration

### 🗂️ DNS Records
- Comprehensive DNS record analysis
- Support for A, AAAA, NS, MX, TXT, SOA, CNAME, and CAA records
- Email security verification (SPF, DKIM, DMARC)
- Mail server configuration check
- DNS health recommendations

### 🔒 SSL Check
- SSL certificate validation
- Expiration date monitoring
- Subject Alternative Names (SANs) display
- Certificate issuer information
- Days remaining calculation

## Installation

1. Clone or download this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

## Requirements

- Python 3.8+
- streamlit >= 1.28.0
- requests >= 2.31.0
- python-whois >= 0.8.0

## Usage

1. Launch the application using `streamlit run app.py`
2. Select a tool from the sidebar
3. Enter the required information (domain, IP address, etc.)
4. Click the action button to run diagnostics
5. Review the results and follow any recommendations

## Tools Guide

### Domain Check
Enter a domain name (e.g., `example.com`) to perform a comprehensive health check including:
- DNS resolution status
- Nameserver configuration
- WHOIS registration details
- Domain expiration dates
- Status flags (active, hold, expired, etc.)

### IP Lookup
Enter an IPv4 address to get:
- Geographic location (city, region, country)
- ISP/Organization information
- Coordinates and timezone
- Direct link to Google Maps

### DNS Records
Enter a domain to analyze all DNS records:
- Nameservers (NS)
- IPv4 addresses (A)
- IPv6 addresses (AAAA)
- Mail servers (MX)
- Text records (TXT) including SPF, DKIM, DMARC
- Zone authority (SOA)
- Certificate authority authorization (CAA)

### SSL Check
Enter a domain to verify its SSL certificate:
- Certificate validity
- Expiration monitoring
- Issuer details
- Subject alternative names
- Days until expiration

## Troubleshooting Common Issues

### WHOIS Lookup Failures
- Some domains (especially ccTLDs) may not return complete WHOIS data
- Use the provided manual lookup links for detailed information
- Python-whois library handles most common TLDs automatically

### DNS Propagation
- DNS changes can take 24-48 hours to propagate globally
- Different DNS servers may show different results during propagation

### SSL Certificate Errors
- Ensure the domain is accessible on port 443
- Self-signed certificates will trigger errors
- Certificate name must match the domain

## Support Documentation Reference

This toolkit is designed to work alongside the "Easy Step-by-Step Ticket Check Guide" for comprehensive Level 1 support workflows.

## License

This project is provided as-is for technical support purposes.

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.
