# Easy Step-by-Step Ticket Check Guide

**By Evans Cheloti**

## ⏱️ Quick Start (First 60 Seconds)
👉 Open the ticket → Check priority → Confirm identity → Check service status → Add tags → Troubleshoot

## ✅ STEP 1: Ticket Triage (Who + Priority)

### 🔴 VIP Tickets
- If you see a red VIP tag, handle it first
- VIP means client has a priority agreement → don't delay

### 👤 Identity Check

**If ticket is from a logged-in client:**
- ✅ You're safe, continue

**If from a guest (not logged in):**
- ⚠️ Stop → ask for their Support PIN
- **Script:** "Hi there! Your ticket submission shows up as a guest user. For your security, please provide your client support PIN, which is viewable within your client area, HostAfrica Client Area, to help us proceed with your request."
- Wait for PIN before continuing

**If ticket is from Tawk.to chat (offline message/missed chat notification):**
- Look inside the ticket → PIN is usually there
- If missing → ask for it as above

## ✅ STEP 2: Service Health Check

Before you try to fix anything → make sure service is active.

### Domain Check (WHMCS → Client Profile → Domains tab)
- ✅ Active → continue
- ❌ Expired/Redemption → can't work. Ask if they want to renew

### Hosting Check (WHMCS → Products/Services tab)
- ✅ Active → continue
- ❌ Suspended → usually billing. Tell client payment needed (billing)
- ❌ Terminated → service ended → explain policy (billing)

### Nameservers Check
**Correct NS:**
- cPanel: ns1.host-ww.net → ns4.host-ww.net
- DirectAdmin: dan1.host-ww.net, dan2.host-ww.net

**Wrong NS?** → tell client to update and wait 4–24h

## ✅ STEP 3: History + Security

- Click "Other Tickets" → see if the issue was raised before or for duplicate tickets
- If yes → merge the tickets and mention it in reply
- Check the message body: remove any passwords or logins and add them to the sensitive data section
- If you remove sensitive info → tell client not to post it again and advise them to use sensitive data field

## ✅ STEP 4: Tag the Ticket

At top of ticket → add tags:
- **Mail** = email issues
- **Hosting** = websites
- **DNS** = domain records
- **Billing** = invoices
- **VPS / Dedicated** = server issues
- Add platform tag (cPanel / DirectAdmin / HmailPlus) if needed

## ✅ STEP 5: Troubleshooting Basics

### A. Email Problems
1. Check domain + hosting active
2. Check MX/SPF/DKIM/DMARC records
3. Get client IP → see if blocked (e.g. on CSF(all hosting), cPHulk(cPanel), CPGuard(DirectAdmin), Imunify360(mostly cPanel/DirectAdmin))
4. Look at email logs (cPanel → Track Delivery / DirectAdmin → Email Tracking)

### B. Website Problems
1. Check A record points to correct server IP
2. Look for redirect issues (.htaccess / WordPress settings)
3. Check error logs (cPanel: error_log, DirectAdmin: Statistics → Logs)
4. Make sure client's IP is not blocked

### C. DNS Problems
1. Check if domain is registered and active
2. Check domain name status (serverhold, clienthold)
3. Confirm nameservers
4. Use tools: Whois.com, DNS Checker, intoDNS, Leaf DNS

### D. VPS / Dedicated Servers
1. Ping server
2. ⚠️ **Never reboot without client's permission**
3. If unreachable → escalate immediately

## ✅ STEP 6: Reply to Client

Always tell the client:
- ✅ What you checked
- 🔍 What you found
- 🛠️ What you fixed
- 🧑‍💻 What they must do (if anything)
- ⏭️ What happens next

### Keep language simple

**Example:**
- ✅ "Your website was pointing to the wrong IP address. I have fixed it, but it may take 4–24 hours to update."
- ❌ "Your A record was misconfigured."

## ✅ STEP 7: Escalation

**Escalate if:**
- Server offline
- Security breach suspected
- Beyond your knowledge
- More than 30 minutes with no progress

**How to escalate:**
1. Add internal note: what checks you did + what you found + why escalating
2. Change department or escalate
3. Tell client: "I've reviewed your issue and escalated it to our senior team. They'll get back within [timeframe]."

## 🎯 The Goal

When the ticket is closed, the client should have known:
1. What the issue was
2. What was done
3. What happens next

---

## 💡 Tips for Using the Support Toolkit

### Domain Check Tool
- Use this BEFORE troubleshooting to verify domain status
- Check nameserver configuration
- Verify domain expiration dates
- Look for hold statuses

### DNS Records Tool
- Verify MX records for email issues
- Check A records for website issues
- Validate SPF/DKIM/DMARC for email authentication
- Confirm TXT records for domain verification

### IP Lookup Tool
- Use when checking if client IP is blocked
- Helpful for geolocation verification
- Useful for identifying suspicious access patterns

### SSL Check Tool
- Verify certificate validity
- Check expiration dates
- Confirm proper certificate installation
- Validate Subject Alternative Names

---

*This guide is designed to work with the Level 1 Tech Support Toolkit for efficient ticket resolution.*
