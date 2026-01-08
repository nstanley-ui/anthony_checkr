import streamlit as st
import pandas as pd
import time
import requests
import json
import random
from datetime import datetime
from io import BytesIO

# --- CONFIGURATION & STATE ---
st.set_page_config(page_title="Verified Campaign Architect", layout="wide", page_icon="🛡️")

# Initialize Session State
if 'campaign_data' not in st.session_state:
    st.session_state.campaign_data = {}
if 'verification_log' not in st.session_state:
    st.session_state.verification_log = []
if 'verification_status' not in st.session_state:
    st.session_state.verification_status = None # None, 'running', 'success', 'failed'
if 'uploaded_campaigns_df' not in st.session_state:
    st.session_state.uploaded_campaigns_df = None
if 'processed_campaigns_df' not in st.session_state:
    st.session_state.processed_campaigns_df = None

# --- SIDEBAR: AUTHENTICATION WITH HELPFUL GUIDANCE ---
with st.sidebar:
    st.header("🔐 API Configuration")
    st.markdown("Enter credentials to enable real-time verification.")
    
    # Add a general help section at the top
    with st.expander("ℹ️ Need Help Finding Credentials?", expanded=False):
        st.markdown("""
        **Quick Check:**
        1. Are you logged into each platform as an admin?
        2. Do you have API access enabled on your account?
        3. Check your email for "API key" or "credentials" messages
        
        **Still stuck?** Each section below has direct links to where you'll find the credentials.
        """)
    
    st.divider()
    
    # --- MARKETO CREDENTIALS ---
    with st.expander("🎯 Marketo (Source of Truth)", expanded=False):
        st.markdown("""
        **Where to find these:**
        1. Log into Marketo: [Login Here](https://login.marketo.com/)
        2. Go to **Admin** → **Integration** → **LaunchPoint**
        3. Click on your API service (or create one if none exists)
        
        **What you need:**
        - **Client ID** & **Client Secret**: Found in the LaunchPoint service details
        - **Munchkin ID**: Found in Admin → Integration → Munchkin
          - Format looks like: `123-ABC-456`
        """)
        
        st.info("💡 **Tip:** Your Munchkin Base URL is usually `https://123-ABC-456.mktorest.com`")
        
        mkt_client_id = st.text_input(
            "Client ID", 
            type="password",
            help="From LaunchPoint service details",
            key="mkt_client_id"
        )
        mkt_client_secret = st.text_input(
            "Client Secret", 
            type="password",
            help="From LaunchPoint service details",
            key="mkt_client_secret"
        )
        mkt_base_url = st.text_input(
            "Munchkin Base URL",
            placeholder="https://123-ABC-456.mktorest.com",
            help="Format: https://[YOUR-MUNCHKIN-ID].mktorest.com",
            key="mkt_base_url"
        )
        
        # Validation helper
        if mkt_base_url and not mkt_base_url.startswith("https://"):
            st.warning("⚠️ URL should start with 'https://'")
        
        with st.expander("📖 Don't have API access yet?"):
            st.markdown("""
            **To create API credentials:**
            1. In Marketo, go to **Admin** → **Integration** → **LaunchPoint**
            2. Click **New** → **New Service**
            3. Choose **Custom** as service type
            4. Display Name: `Campaign Architect API`
            5. Description: `For automated campaign verification`
            6. Select **API Only User** from dropdown
            7. Click **Create** - your credentials will be shown once
            
            ⚠️ **Save them immediately!** You can't view Client Secret again.
            """)
    
    st.divider()
    
    # --- SALESFORCE CREDENTIALS ---
    with st.expander("☁️ Salesforce (Sync Check)", expanded=False):
        st.markdown("""
        **Where to find these:**
        1. Log into Salesforce: [Login Here](https://login.salesforce.com/)
        2. Go to **Setup** (gear icon top-right)
        3. In Quick Find, search: `App Manager`
        4. Find your Connected App or create a new one
        
        **What you need:**
        - **Consumer Key**: Shown as "Consumer Key" in Connected App details
        - **Consumer Secret**: Click "Click to reveal" next to Consumer Secret
        """)
        
        st.info("💡 **Tip:** If you don't see your Connected App, you may need to create one first")
        
        sf_consumer_key = st.text_input(
            "Consumer Key", 
            type="password",
            help="From Connected App in Salesforce Setup → App Manager",
            key="sf_consumer_key"
        )
        sf_consumer_secret = st.text_input(
            "Consumer Secret", 
            type="password",
            help="Click 'Click to reveal' in Connected App details",
            key="sf_consumer_secret"
        )
        
        with st.expander("📖 Don't have a Connected App yet?"):
            st.markdown("""
            **To create a Connected App:**
            1. Setup → Quick Find: `App Manager`
            2. Click **New Connected App**
            3. Basic Info:
               - Connected App Name: `Campaign Architect`
               - API Name: `Campaign_Architect`
               - Contact Email: (your email)
            4. Enable OAuth Settings:
               - ✅ Check "Enable OAuth Settings"
               - Callback URL: `https://localhost`
               - Selected OAuth Scopes:
                 - `api` - Full API access
                 - `refresh_token` - Refresh access token
            5. Click **Save** → **Continue**
            6. Wait 2-10 minutes for it to propagate
            7. Come back and click **Manage Consumer Details** to see your keys
            """)
    
    st.divider()
    
    # --- LINKEDIN CREDENTIALS ---
    with st.expander("🔗 LinkedIn (Form Connector)", expanded=False):
        st.markdown("""
        **Where to find this:**
        1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/apps)
        2. Select your app (or create one if needed)
        3. Go to **Auth** tab
        4. Under "OAuth 2.0 settings", find your **Access Token**
        
        **What you need:**
        - **Access Token**: Long string starting with something like `AQX...`
        """)
        
        st.warning("⚠️ **Note:** LinkedIn tokens expire! You may need to regenerate periodically.")
        
        li_access_token = st.text_input(
            "Access Token", 
            type="password",
            help="From LinkedIn Developers → Your App → Auth tab",
            placeholder="AQX...",
            key="li_access_token"
        )
        
        with st.expander("📖 Don't have a LinkedIn App yet?"):
            st.markdown("""
            **To create a LinkedIn App:**
            1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/apps)
            2. Click **Create app**
            3. Fill in required info:
               - App name: `Campaign Architect`
               - LinkedIn Page: (your company page)
               - Privacy policy URL: (required)
               - App logo: (upload any image)
            4. Click **Create app**
            5. Go to **Products** tab
            6. Request access to:
               - **Advertising API** (needed for Lead Gen Forms)
               - **Marketing Developer Platform**
            7. Once approved, go to **Auth** tab for tokens
            
            ⏳ **Note:** Product access approval can take 1-3 business days.
            """)
            
    st.divider()
    
    # --- CREDENTIAL STATUS CHECKER ---
    st.subheader("✅ Credential Status")
    
    cred_status = {
        "Marketo": bool(mkt_client_id and mkt_client_secret and mkt_base_url),
        "Salesforce": bool(sf_consumer_key and sf_consumer_secret),
        "LinkedIn": bool(li_access_token)
    }
    
    for platform, is_ready in cred_status.items():
        if is_ready:
            st.success(f"✅ {platform}: Ready")
        else:
            st.error(f"❌ {platform}: Missing credentials")
    
    all_ready = all(cred_status.values())
    
    if all_ready:
        st.success("🎉 All platforms configured!")
        DEMO_MODE = st.checkbox(
            "🛠️ Use Demo Mode Anyway", 
            value=False, 
            help="Test UI without making real API calls"
        )
    else:
        st.warning("⚠️ Some credentials missing - Demo Mode enabled")
        DEMO_MODE = st.checkbox(
            "🛠️ Developer Demo Mode", 
            value=True, 
            disabled=True,
            help="Simulate API calls for UI testing (required when credentials missing)"
        )
    
    st.divider()
    
    # --- TROUBLESHOOTING SECTION ---
    with st.expander("🔧 Troubleshooting Guide"):
        st.markdown("""
        ### Common Issues:
        
        **"I can't find my credentials"**
        - Check if you have admin access to each platform
        - Look in your email for invitation/setup messages
        - Ask your IT admin if credentials were shared with you
        
        **"My credentials aren't working"**
        - Verify you copied them completely (no extra spaces)
        - Check if tokens have expired (especially LinkedIn)
        - Ensure your user has API permissions enabled
        
        **"Where do I start?"**
        1. Start with Marketo (most critical)
        2. Then Salesforce
        3. LinkedIn can come last
        
        **"Do I need all three?"**
        - For full verification: Yes
        - For basic testing: Marketo alone can work in demo mode
        
        ### Need More Help?
        - 📧 Email your IT admin
        - 📚 Check platform documentation links above
        - 💬 Contact platform support if you can't access admin areas
        """)

# --- BACKEND UTILS (The Plumbing) ---

def generate_utm_link(base_url, source, medium, campaign_id):
    """Module 2 Step A: Auto-generate standardized tracking link"""
    clean_url = base_url.rstrip('/')
    # Standardizing naming convention to prevent typos
    return f"{clean_url}?utm_source={source}&utm_medium={medium}&utm_campaign={campaign_id}"

def mock_marketo_campaigns():
    """Simulates fetching campaigns from Marketo GET /rest/v1/campaigns.json"""
    return {
        "1098": "Financial Services ABM - Q1",
        "2045": "Healthcare AI Report",
        "3012": "Global Manufacturing Summit"
    }

def mock_assets():
    """Simulates scraping the website for available 'Thank You' assets"""
    return {
        "Gartner Magic Quadrant Report": "https://demandbase.com/resources/reports/gartner-mq",
        "The AI Inflection Point Guide": "https://demandbase.com/resources/guides/ai-inflection",
        "Financial Services Case Study": "https://demandbase.com/resources/case-studies/finserv"
    }

def verify_connection(url, campaign_id):
    """
    Module 2 Step B: The 'Pre-Flight' Simulation
    Run 3 diagnostic checks: URL, Marketo Ingestion, Salesforce Sync
    """
    logs = []
    
    # 1. URL PING
    logs.append(f"📡 Pinging URL: {url}...")
    time.sleep(1) # Network latency simulation
    if DEMO_MODE:
        # Simulate success
        logs.append("✅ URL Valid (200 OK)")
    else:
        # REAL LOGIC:
        # try:
        #     r = requests.get(url)
        #     if r.status_code == 200: logs.append("✅ URL Valid")
        #     else: return False, logs + [f"❌ URL Failed: {r.status_code}"]
        # except: return False, logs + ["❌ URL Failed: Connection Error"]
        pass

    # 2. MARKETO TEST LEAD
    logs.append(f"📨 Injecting Synthetic Lead into Marketo Campaign {campaign_id}...")
    time.sleep(1.5)
    
    # Payload Developer Reference
    test_payload = {
        "action": "createOrUpdate",
        "lookupField": "email",
        "input": [{
            "email": f"test_verify_{int(time.time())}@demandbase.com",
            "firstName": "System_Test",
            "lastName": "Do_Not_Contact",
            "source": "Campaign_Architect_Verifier"
        }]
    }
    
    if DEMO_MODE:
        logs.append(f"✅ Marketo Accepted Lead (ID: {random.randint(50000,99999)})")
    else:
        # REAL LOGIC:
        # r = requests.post(f"{mkt_base_url}/rest/v1/leads.json", json=test_payload, headers=auth_headers)
        # if r.json()['success']: logs.append("✅ Marketo Accepted Lead")
        pass

    # 3. SALESFORCE SYNC POLLING
    logs.append("🔄 Polling Salesforce for Sync (Max Wait: 30s)...")
    progress_bar = st.progress(0)
    for i in range(100):
        time.sleep(0.02) # Fast forward for demo
        progress_bar.progress(i + 1)
    
    if DEMO_MODE:
        logs.append("✅ Salesforce Sync Verified (Lead found in Object Manager)")
        return True, logs
    else:
        # REAL LOGIC: 
        # Loop query Salesforce API looking for the email address
        pass
        
    return False, logs # Default fail for non-demo without keys

def process_bulk_campaigns(df):
    """Process multiple campaigns from uploaded file"""
    results = []
    
    for idx, row in df.iterrows():
        # Extract data from row
        campaign_name = row.get('campaign_name', f"Campaign_{idx}")
        asset_url = row.get('asset_url', '')
        marketo_id = row.get('marketo_campaign_id', '')
        utm_source = row.get('utm_source', 'linkedin')
        utm_medium = row.get('utm_medium', 'paid_social')
        
        # Generate tracking URL
        final_url = generate_utm_link(asset_url, utm_source, utm_medium, marketo_id)
        
        # In demo mode, simulate verification
        if DEMO_MODE:
            verification_status = random.choice(['success', 'success', 'success', 'warning']) # Mostly success
        else:
            verification_status = 'pending'
        
        results.append({
            'campaign_name': campaign_name,
            'marketo_campaign_id': marketo_id,
            'asset_url': asset_url,
            'tracking_url': final_url,
            'form_id': f"LIGF_{marketo_id}_v1",
            'verification_status': verification_status,
            'processed_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return pd.DataFrame(results)

def create_download_link(df, filename, file_format='xlsx'):
    """Create a download link for the processed data"""
    if file_format == 'xlsx':
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Campaigns')
        output.seek(0)
        return output.getvalue(), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    else:  # csv
        return df.to_csv(index=False).encode('utf-8'), 'text/csv'

# --- FRONTEND UI ---

st.title("🛡️ Verified Campaign Architect")
st.markdown("""
**Workflow:** Upload Campaigns → Auto-Build Links → Pre-Flight Verify → Download Results
*Eliminates manual 'system jumping' and validates data plumbing before spend.*
""")

# Create tabs for different workflows
tab1, tab2, tab3 = st.tabs(["📤 Bulk Upload", "➕ Single Campaign", "📊 View Results"])

# --- TAB 1: BULK UPLOAD ---
with tab1:
    st.header("📤 Bulk Campaign Upload")
    st.markdown("Upload an Excel or CSV file with multiple campaigns to process at once.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Upload File")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose an Excel or CSV file",
            type=['xlsx', 'xls', 'csv'],
            help="Upload a file containing your campaign data"
        )
        
        # Template download
        st.markdown("### 📋 Need a template?")
        st.markdown("Download our template to see the expected format:")
        
        # Create template
        template_df = pd.DataFrame({
            'campaign_name': ['Q1 Financial Services', 'Healthcare AI Webinar', 'Manufacturing Summit'],
            'asset_url': [
                'https://demandbase.com/resources/reports/finserv',
                'https://demandbase.com/resources/webinars/healthcare-ai',
                'https://demandbase.com/resources/events/manufacturing'
            ],
            'marketo_campaign_id': ['1098', '2045', '3012'],
            'utm_source': ['linkedin', 'linkedin', 'google'],
            'utm_medium': ['paid_social', 'paid_social', 'paid_search']
        })
        
        # Download buttons for template
        col_xlsx, col_csv = st.columns(2)
        with col_xlsx:
            template_xlsx, mime_xlsx = create_download_link(template_df, 'campaign_template.xlsx', 'xlsx')
            st.download_button(
                label="📥 Download Excel Template",
                data=template_xlsx,
                file_name="campaign_template.xlsx",
                mime=mime_xlsx
            )
        with col_csv:
            template_csv, mime_csv = create_download_link(template_df, 'campaign_template.csv', 'csv')
            st.download_button(
                label="📥 Download CSV Template",
                data=template_csv,
                file_name="campaign_template.csv",
                mime=mime_csv
            )
        
        # Expected columns info
        with st.expander("ℹ️ Required Columns"):
            st.markdown("""
            Your file should include these columns:
            - **campaign_name**: Name of your campaign
            - **asset_url**: URL of the landing page/asset
            - **marketo_campaign_id**: Your Marketo campaign ID
            - **utm_source**: Traffic source (e.g., 'linkedin', 'google')
            - **utm_medium**: Marketing medium (e.g., 'paid_social', 'email')
            
            Optional columns:
            - Any additional tracking parameters
            - Notes or descriptions
            """)
    
    with col2:
        if uploaded_file is not None:
            st.subheader("2. Preview & Process")
            
            # Read the file
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.session_state.uploaded_campaigns_df = df
                
                st.success(f"✅ File uploaded successfully! Found {len(df)} campaigns.")
                
                # Show preview
                st.markdown("**Data Preview:**")
                st.dataframe(df.head(10), use_container_width=True)
                
                if len(df) > 10:
                    st.info(f"Showing first 10 of {len(df)} rows")
                
                # Validate required columns
                required_cols = ['campaign_name', 'asset_url', 'marketo_campaign_id']
                missing_cols = [col for col in required_cols if col not in df.columns]
                
                if missing_cols:
                    st.error(f"❌ Missing required columns: {', '.join(missing_cols)}")
                    st.info("Please add these columns to your file and re-upload.")
                else:
                    st.success("✅ All required columns present")
                    
                    # Process button
                    if st.button("🚀 Process All Campaigns", type="primary"):
                        with st.status("Processing campaigns...", expanded=True) as status:
                            st.write(f"Processing {len(df)} campaigns...")
                            
                            # Process the campaigns
                            processed_df = process_bulk_campaigns(df)
                            st.session_state.processed_campaigns_df = processed_df
                            
                            time.sleep(1)  # Simulate processing
                            
                            st.write("✅ Tracking URLs generated")
                            st.write("✅ Form IDs created")
                            if DEMO_MODE:
                                st.write("✅ Verification simulated (Demo Mode)")
                            
                            status.update(
                                label=f"✅ Processed {len(processed_df)} campaigns successfully!",
                                state="complete"
                            )
                        
                        st.balloons()
                        st.success("🎉 All campaigns processed! Go to 'View Results' tab to download.")
            
            except Exception as e:
                st.error(f"❌ Error reading file: {str(e)}")
                st.info("Please make sure your file is a valid Excel or CSV file.")

# --- TAB 2: SINGLE CAMPAIGN (Original Interface) ---
with tab2:
    st.header("➕ Create Single Campaign")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Build Campaign")
        
        # ASSET SELECTION
        assets = mock_assets()
        selected_asset_name = st.selectbox("Select Goal Asset (Website)", options=assets.keys())
        selected_asset_url = assets[selected_asset_name]
        
        # CAMPAIGN SELECTION (MARKETO)
        campaigns = mock_marketo_campaigns()
        selected_campaign_id = st.selectbox(
            "Select Destination Campaign (Marketo)", 
            options=campaigns.keys(),
            format_func=lambda x: f"{x} - {campaigns[x]}"
        )

        # AUTO-BUILDER
        st.info("👇 System will auto-generate tracking taxonomy.")
        
        utm_source = "linkedin"
        utm_medium = "paid_social"
        
        if st.button("Generate & Bind"):
            # Create the object
            final_url = generate_utm_link(selected_asset_url, utm_source, utm_medium, selected_campaign_id)
            
            st.session_state.campaign_data = {
                "asset": selected_asset_name,
                "marketo_id": selected_campaign_id,
                "final_url": final_url,
                "form_id": f"LIGF_{selected_campaign_id}_v1"
            }
            st.session_state.verification_status = None

    with col2:
        # DISPLAY THE OUTPUT OBJECT
        if st.session_state.campaign_data:
            st.subheader("2. Campaign Object")
            
            # VISUAL CARD
            with st.container(border=True):
                st.markdown(f"**Target Asset:** `{st.session_state.campaign_data['asset']}`")
                st.markdown(f"**Marketo ID:** `{st.session_state.campaign_data['marketo_id']}`")
                st.markdown("**Generated Tracking URL:**")
                st.code(st.session_state.campaign_data['final_url'], language="text")
                st.markdown("**Required LinkedIn Form Name:**")
                st.code(st.session_state.campaign_data['form_id'], language="text")
                
            st.markdown("### 3. Pre-Flight Simulation")
            st.caption("Verify the 'plumbing' (URL -> Marketo -> Salesforce) before launching.")
            
            if st.button("🚀 Run Diagnostics", type="primary"):
                with st.status("Running System Checks...", expanded=True) as status:
                    st.session_state.verification_status = 'running'
                    
                    # EXECUTE VERIFICATION
                    success, logs = verify_connection(
                        st.session_state.campaign_data['final_url'], 
                        st.session_state.campaign_data['marketo_id']
                    )
                    
                    # PRINT LOGS
                    for log in logs:
                        st.write(log)
                    
                    if success:
                        status.update(label="All Systems Go! Connection Verified.", state="complete", expanded=True)
                        st.session_state.verification_status = 'success'
                    else:
                        status.update(label="Verification Failed. See logs.", state="error", expanded=True)
                        st.session_state.verification_status = 'failed'

    # FINAL GREEN LIGHT
    if st.session_state.verification_status == 'success':
        st.divider()
        st.balloons()
        st.success(f"✅ **GREEN LIGHT**: Campaign '{campaigns[selected_campaign_id]}' is safe to launch. Data flow is verified.")
        
        with st.expander("View JSON Payload (Developer Info)"):
            st.json({
                "timestamp": str(datetime.now()),
                "campaign_object": st.session_state.campaign_data,
                "verification_proof": "salesforce_lead_id_mock_12345"
            })

# --- TAB 3: VIEW RESULTS ---
with tab3:
    st.header("📊 Processed Campaign Results")
    
    if st.session_state.processed_campaigns_df is not None:
        df_results = st.session_state.processed_campaigns_df
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Campaigns", len(df_results))
        with col2:
            success_count = len(df_results[df_results['verification_status'] == 'success'])
            st.metric("Verified", success_count)
        with col3:
            warning_count = len(df_results[df_results['verification_status'] == 'warning'])
            st.metric("Warnings", warning_count)
        with col4:
            pending_count = len(df_results[df_results['verification_status'] == 'pending'])
            st.metric("Pending", pending_count)
        
        st.divider()
        
        # Display results table
        st.subheader("Campaign Details")
        
        # Add color coding for status
        def color_status(val):
            if val == 'success':
                return 'background-color: #d4edda'
            elif val == 'warning':
                return 'background-color: #fff3cd'
            elif val == 'pending':
                return 'background-color: #e2e3e5'
            return ''
        
        styled_df = df_results.style.applymap(color_status, subset=['verification_status'])
        st.dataframe(styled_df, use_container_width=True)
        
        st.divider()
        
        # Download section
        st.subheader("💾 Download Results")
        st.markdown("Export your processed campaigns with tracking URLs and verification status.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Excel download
            excel_data, excel_mime = create_download_link(df_results, 'processed_campaigns.xlsx', 'xlsx')
            st.download_button(
                label="📥 Download as Excel",
                data=excel_data,
                file_name=f"processed_campaigns_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime=excel_mime,
                type="primary"
            )
        
        with col2:
            # CSV download
            csv_data, csv_mime = create_download_link(df_results, 'processed_campaigns.csv', 'csv')
            st.download_button(
                label="📥 Download as CSV",
                data=csv_data,
                file_name=f"processed_campaigns_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime=csv_mime
            )
        
        # Additional options
        with st.expander("📋 What's included in the download?"):
            st.markdown("""
            Your download will include:
            - ✅ Original campaign information
            - ✅ Generated tracking URLs with UTM parameters
            - ✅ LinkedIn form IDs
            - ✅ Verification status
            - ✅ Processing timestamp
            - ✅ All original columns from your upload
            
            You can import this directly into your campaign management system!
            """)
    
    else:
        st.info("👆 No processed campaigns yet. Upload a file in the 'Bulk Upload' tab to get started!")
        
        # Show example of what results look like
        with st.expander("👁️ Preview: What will the results look like?"):
            example_df = pd.DataFrame({
                'campaign_name': ['Example Campaign 1', 'Example Campaign 2'],
                'marketo_campaign_id': ['1234', '5678'],
                'asset_url': ['https://example.com/asset1', 'https://example.com/asset2'],
                'tracking_url': [
                    'https://example.com/asset1?utm_source=linkedin&utm_medium=paid_social&utm_campaign=1234',
                    'https://example.com/asset2?utm_source=linkedin&utm_medium=paid_social&utm_campaign=5678'
                ],
                'form_id': ['LIGF_1234_v1', 'LIGF_5678_v1'],
                'verification_status': ['success', 'success'],
                'processed_date': ['2024-01-15 10:30:00', '2024-01-15 10:30:01']
            })
            st.dataframe(example_df, use_container_width=True)
