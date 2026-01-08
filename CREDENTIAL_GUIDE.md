# API Credential Quick Reference Guide
## For Campaign Architect Application

This guide helps you find all the credentials needed to run the Campaign Architect tool.

---

## 🎯 MARKETO CREDENTIALS

### What You Need:
1. **Client ID** (looks like: `a1b2c3d4-e5f6-7890-abcd-ef1234567890`)
2. **Client Secret** (looks like: `X1Y2Z3A4B5C6D7E8F9G0H1I2J3K4L5M6`)
3. **Munchkin Base URL** (looks like: `https://123-ABC-456.mktorest.com`)

### Where to Find Them:

**Step 1:** Log into Marketo
- URL: https://login.marketo.com/
- Use your admin credentials

**Step 2:** Navigate to API Settings
1. Click **Admin** in the top navigation
2. Click **Integration** in the left sidebar
3. Click **LaunchPoint**
4. Look for an existing API service OR create a new one

**Step 3:** Get Your Credentials
- **Client ID** and **Client Secret**: Found in the LaunchPoint service details
- Click on your service name to view details

**Step 4:** Get Your Munchkin ID
1. Still in Admin → Integration
2. Click **Munchkin** (instead of LaunchPoint)
3. Copy your Munchkin Account ID (format: `123-ABC-456`)
4. Your base URL is: `https://[YOUR-MUNCHKIN-ID].mktorest.com`

### Don't Have API Access Yet?

**To Create New API Credentials:**
1. In LaunchPoint, click **New** → **New Service**
2. Service: Select **Custom**
3. Display Name: `Campaign Architect API`
4. Description: `For automated campaign verification`
5. API Only User: Select from dropdown
6. Click **Create**
7. **IMPORTANT:** Copy your Client Secret immediately - you can't see it again!

---

## ☁️ SALESFORCE CREDENTIALS

### What You Need:
1. **Consumer Key** (looks like: `3MVG9...[very long string]`)
2. **Consumer Secret** (looks like: `1234567890123456789`)

### Where to Find Them:

**Step 1:** Log into Salesforce
- URL: https://login.salesforce.com/
- Use your admin credentials

**Step 2:** Navigate to App Manager
1. Click the **Gear Icon** (Setup) in the top-right
2. In the Quick Find box (left sidebar), type: `App Manager`
3. Click **App Manager**
4. Look for your Connected App OR create a new one

**Step 3:** View Your Credentials
1. Find your app in the list
2. Click the dropdown arrow → **View**
3. Scroll down to "API (Enable OAuth Settings)"
4. **Consumer Key**: Copy this value
5. **Consumer Secret**: Click "Click to reveal" → Copy this value

### Don't Have a Connected App Yet?

**To Create a Connected App:**
1. In App Manager, click **New Connected App**
2. Fill in Basic Information:
   - Connected App Name: `Campaign Architect`
   - API Name: `Campaign_Architect` (auto-fills)
   - Contact Email: (your email)
3. Enable OAuth Settings:
   - ✅ Check "Enable OAuth Settings"
   - Callback URL: `https://localhost`
   - Selected OAuth Scopes (move to "Selected" column):
     - Full access (api)
     - Perform requests at any time (refresh_token, offline_access)
4. Click **Save**
5. Click **Continue**
6. **WAIT 2-10 minutes** for propagation
7. Come back to App Manager → Your App → **View**
8. Click **Manage Consumer Details** to see your keys

---

## 🔗 LINKEDIN CREDENTIALS

### What You Need:
1. **Access Token** (looks like: `AQXNiMzcxNTI0NzQ...[long string]`)

### Where to Find It:

**Step 1:** Go to LinkedIn Developers
- URL: https://www.linkedin.com/developers/apps
- Log in with your LinkedIn account (must be admin of your company page)

**Step 2:** Select Your App
1. Click on your existing app name
2. OR click **Create app** if you don't have one

**Step 3:** Get Your Access Token
1. Click the **Auth** tab
2. Scroll to "OAuth 2.0 settings"
3. Copy your **Access Token**

**⚠️ IMPORTANT:** LinkedIn tokens expire! You may need to regenerate them periodically.

### Don't Have a LinkedIn App Yet?

**To Create a LinkedIn App:**
1. Go to https://www.linkedin.com/developers/apps
2. Click **Create app**
3. Fill in required fields:
   - App name: `Campaign Architect`
   - LinkedIn Page: (select your company page)
   - Privacy policy URL: (required - can be your company website/privacy page)
   - App logo: (upload any 80x80px image)
   - Legal agreement: Check the box
4. Click **Create app**
5. Go to **Products** tab
6. Request access to:
   - **Advertising API** (needed for Lead Gen Forms)
   - **Marketing Developer Platform**
7. Wait for approval (1-3 business days)
8. Once approved, go to **Auth** tab to get your token

---

## ✅ QUICK CHECKLIST

Before you start, make sure you have:

- [ ] Admin access to Marketo
- [ ] Admin access to Salesforce
- [ ] Admin access to your LinkedIn Company Page
- [ ] Ability to create API services/apps in each platform

If you don't have admin access, contact:
- **Marketo Admin:** (check with your marketing ops team)
- **Salesforce Admin:** (check with your sales ops team)
- **LinkedIn Admin:** (check with your marketing/social media team)

---

## 🔧 TROUBLESHOOTING

### "I can't find my credentials"
1. Check if you're logged in as an admin (not a regular user)
2. Search your email for setup/invitation messages
3. Ask IT if credentials were previously created and shared

### "My credentials don't work"
1. Make sure you copied them completely (no extra spaces or line breaks)
2. Check if tokens have expired (especially LinkedIn)
3. Verify your user has API permissions enabled
4. For Salesforce: Wait 10 minutes after creating the Connected App

### "Where do I start?"
**Priority Order:**
1. **Marketo** (most critical for core functionality)
2. **Salesforce** (needed for verification)
3. **LinkedIn** (needed for form integration)

You can test in Demo Mode with incomplete credentials, but all three are needed for full verification.

---

## 📞 NEED HELP?

**Platform Support:**
- Marketo Support: https://nation.marketo.com/
- Salesforce Support: https://help.salesforce.com/
- LinkedIn Support: https://www.linkedin.com/help/linkedin/

**Internal Help:**
- Contact your IT/DevOps team
- Contact your Marketing Operations team
- Check internal documentation/wiki for existing API credentials

---

## 📝 NOTES FOR SAVING CREDENTIALS

**Store Safely:**
- Use a password manager (1Password, LastPass, etc.)
- Do NOT save in plain text files
- Do NOT commit to version control/GitHub
- Do NOT share via email

**Recommended Storage:**
- Save in environment variables on your server
- Use a secrets management service (AWS Secrets Manager, etc.)
- Keep backup copy in secure password vault
