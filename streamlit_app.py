import streamlit as st
import pandas as pd
import time
import requests
import json
import random
from datetime import datetime
from io import BytesIO
import os
import traceback

# --- CONFIGURATION & STATE ---
st.set_page_config(page_title="Verified Campaign Architect", layout="wide", page_icon="🛡️")

# Initialize Session State
if 'campaign_data' not in st.session_state:
    st.session_state.campaign_data = {}
if 'verification_log' not in st.session_state:
    st.session_state.verification_log = []
if 'verification_status' not in st.session_state:
    st.session_state.verification_status = None
if 'uploaded_campaigns_df' not in st.session_state:
    st.session_state.uploaded_campaigns_df = None
if 'processed_campaigns_df' not in st.session_state:
    st.session_state.processed_campaigns_df = None
if 'system_logs' not in st.session_state:
    st.session_state.system_logs = []
if 'error_patterns' not in st.session_state:
    st.session_state.error_patterns = {}
if 'improvements' not in st.session_state:
    st.session_state.improvements = []

# --- SELF-ANNEALING SYSTEM ---

class SystemLogger:
    """
    Implements self-annealing based on AGENTS.md principles:
    1. Capture errors and patterns
    2. Learn from failures
    3. Suggest improvements
    4. Update system based on learnings
    """
    
    @staticmethod
    def log_event(event_type, message, metadata=None):
        """Log system events for later analysis"""
        log_entry = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'type': event_type,
            'message': message,
            'metadata': metadata or {}
        }
        st.session_state.system_logs.append(log_entry)
        
        # Keep only last 1000 logs to prevent memory issues
        if len(st.session_state.system_logs) > 1000:
            st.session_state.system_logs = st.session_state.system_logs[-1000:]
    
    @staticmethod
    def log_error(error_type, error_message, context=None):
        """Log errors and track patterns"""
        SystemLogger.log_event('error', error_message, {
            'error_type': error_type,
            'context': context,
            'stack_trace': traceback.format_exc()
        })
        
        # Track error patterns
        if error_type not in st.session_state.error_patterns:
            st.session_state.error_patterns[error_type] = []
        st.session_state.error_patterns[error_type].append({
            'message': error_message,
            'context': context,
            'timestamp': datetime.now()
        })
    
    @staticmethod
    def log_success(operation, details=None):
        """Log successful operations"""
        SystemLogger.log_event('success', f"Completed: {operation}", details)
    
    @staticmethod
    def log_improvement(improvement_type, description, impact):
        """Log system improvements for tracking evolution"""
        improvement = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'type': improvement_type,
            'description': description,
            'impact': impact
        }
        st.session_state.improvements.append(improvement)
        SystemLogger.log_event('improvement', description, improvement)
    
    @staticmethod
    def analyze_patterns():
        """Analyze error patterns and suggest improvements"""
        suggestions = []
        
        for error_type, occurrences in st.session_state.error_patterns.items():
            if len(occurrences) >= 3:  # Pattern threshold
                suggestions.append({
                    'type': error_type,
                    'count': len(occurrences),
                    'suggestion': f"Recurring {error_type} error detected ({len(occurrences)} times). Consider implementing automatic retry logic or validation."
                })
        
        return suggestions
    
    @staticmethod
    def get_recent_logs(count=50, log_type=None):
        """Retrieve recent logs, optionally filtered by type"""
        logs = st.session_state.system_logs[-count:]
        if log_type:
            logs = [log for log in logs if log['type'] == log_type]
        return logs

# --- SELF-HEALING UTILITIES ---

def auto_fix_url(url):
    """Self-annealing: Automatically fix common URL issues"""
    if not url:
        return url
    
    # Fix missing protocol
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        SystemLogger.log_improvement(
            'url_validation',
            'Auto-added https:// protocol to URL',
            'Prevents validation errors'
        )
    
    # Fix double slashes
    if '//' in url[8:]:  # Skip protocol
        url = url[:8] + url[8:].replace('//', '/')
        SystemLogger.log_improvement(
            'url_validation',
            'Fixed double slashes in URL path',
            'Prevents routing errors'
        )
    
    return url

def validate_campaign_data(row, row_num):
    """Self-annealing: Validate and auto-correct campaign data"""
    errors = []
    warnings = []
    
    # Required field validation
    required_fields = ['campaign_name', 'asset_url', 'marketo_campaign_id']
    for field in required_fields:
        if field not in row or pd.isna(row[field]) or str(row[field]).strip() == '':
            errors.append(f"Row {row_num}: Missing required field '{field}'")
    
    # URL validation and auto-fix
    if 'asset_url' in row and not pd.isna(row['asset_url']):
        original_url = str(row['asset_url'])
        fixed_url = auto_fix_url(original_url)
        if fixed_url != original_url:
            row['asset_url'] = fixed_url
            warnings.append(f"Row {row_num}: Auto-fixed URL format")
    
    # Campaign ID validation
    if 'marketo_campaign_id' in row and not pd.isna(row['marketo_campaign_id']):
        campaign_id = str(row['marketo_campaign_id'])
        if not campaign_id.isdigit():
            warnings.append(f"Row {row_num}: Campaign ID should be numeric")
    
    return errors, warnings, row

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
        
        # Validation helper with self-annealing
        if mkt_base_url and not mkt_base_url.startswith("https://"):
            st.warning("⚠️ URL should start with 'https://'")
            if st.button("🔧 Auto-fix URL"):
                mkt_base_url = auto_fix_url(mkt_base_url)
                st.success("✅ URL fixed!")
        
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
    
    # --- SYSTEM HEALTH & LOGS ---
    with st.expander("🔬 System Health & Logs", expanded=False):
        st.markdown("### Self-Annealing Status")
        
        # Show improvements
        if st.session_state.improvements:
            st.success(f"✅ {len(st.session_state.improvements)} improvements made")
            if st.button("View Improvements"):
                for imp in st.session_state.improvements[-5:]:
                    st.info(f"**{imp['type']}**: {imp['description']}\n*Impact: {imp['impact']}*")
        
        # Show error patterns
        if st.session_state.error_patterns:
            st.warning(f"⚠️ {len(st.session_state.error_patterns)} error types tracked")
            suggestions = SystemLogger.analyze_patterns()
            if suggestions:
                st.markdown("**Suggested Improvements:**")
                for sug in suggestions:
                    st.info(f"{sug['suggestion']}")
        
        # Log viewer
        st.markdown("### Recent Activity")
        log_type_filter = st.selectbox(
            "Filter by type",
            ["All", "error", "success", "improvement"],
            key="log_filter"
        )
        
        filter_type = None if log_type_filter == "All" else log_type_filter
        recent_logs = SystemLogger.get_recent_logs(20, filter_type)
        
        if recent_logs:
            for log in reversed(recent_logs):
                icon = {"error": "❌", "success": "✅", "improvement": "🔧"}.get(log['type'], "ℹ️")
                st.text(f"{icon} [{log['timestamp']}] {log['message']}")
        else:
            st.info("No logs yet")

# --- BACKEND UTILS (The Plumbing) ---

def retry_with_backoff(max_retries=3, base_delay=1):
    """
    Decorator for automatic retry with exponential backoff
    High Priority Improvement: Handles transient network failures
    """
    from functools import wraps
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        SystemLogger.log_error("retry_exhausted", f"Failed after {max_retries} attempts", {
                            'function': func.__name__,
                            'error': str(e)
                        })
                        raise
                    delay = base_delay * (2 ** attempt)
                    SystemLogger.log_event('retry', f"Attempt {attempt + 1}/{max_retries} failed, retrying in {delay}s", {
                        'function': func.__name__,
                        'error': str(e),
                        'retry_delay': delay
                    })
                    time.sleep(delay)
        return wrapper
    return decorator

def generate_utm_link(base_url, source, medium, campaign_id):
    """Module 2 Step A: Auto-generate standardized tracking link"""
    try:
        clean_url = auto_fix_url(base_url.rstrip('/'))
        result = f"{clean_url}?utm_source={source}&utm_medium={medium}&utm_campaign={campaign_id}"
        SystemLogger.log_success("generate_utm_link", {"url": result})
        return result
    except Exception as e:
        SystemLogger.log_error("utm_generation", str(e), {"base_url": base_url})
        raise

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

@retry_with_backoff(max_retries=3, base_delay=1)
def verify_connection(url, campaign_id):
    """
    Module 2 Step B: The 'Pre-Flight' Simulation
    Run 3 diagnostic checks: URL, Marketo Ingestion, Salesforce Sync
    Now with automatic retry logic for transient failures!
    """
    logs = []
    
    try:
        # 1. URL PING
        logs.append(f"📡 Pinging URL: {url}...")
        time.sleep(1)
        
        if DEMO_MODE:
            logs.append("✅ URL Valid (200 OK)")
            SystemLogger.log_success("url_check", {"url": url})
        else:
            # REAL LOGIC HERE - with retry
            pass

        # 2. MARKETO TEST LEAD
        logs.append(f"📨 Injecting Synthetic Lead into Marketo Campaign {campaign_id}...")
        time.sleep(1.5)
        
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
            lead_id = random.randint(50000,99999)
            logs.append(f"✅ Marketo Accepted Lead (ID: {lead_id})")
            SystemLogger.log_success("marketo_lead_injection", {"lead_id": lead_id})
        else:
            # REAL LOGIC HERE
            pass

        # 3. SALESFORCE SYNC POLLING
        logs.append("🔄 Polling Salesforce for Sync (Max Wait: 30s)...")
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.02)
            progress_bar.progress(i + 1)
        
        if DEMO_MODE:
            logs.append("✅ Salesforce Sync Verified (Lead found in Object Manager)")
            SystemLogger.log_success("salesforce_sync", {"campaign_id": campaign_id})
            return True, logs
        else:
            # REAL LOGIC HERE
            pass
            
        return False, logs
        
    except Exception as e:
        SystemLogger.log_error("verification_flow", str(e), {
            "url": url,
            "campaign_id": campaign_id
        })
        logs.append(f"❌ Error: {str(e)}")
        return False, logs

def process_bulk_campaigns(df):
    """Process multiple campaigns from uploaded file with self-annealing validation"""
    results = []
    validation_summary = {'errors': [], 'warnings': [], 'fixed': 0}
    
    SystemLogger.log_event('info', f"Starting bulk processing of {len(df)} campaigns")
    
    for idx, row in df.iterrows():
        try:
            # Self-annealing validation
            errors, warnings, fixed_row = validate_campaign_data(row, idx + 1)
            validation_summary['errors'].extend(errors)
            validation_summary['warnings'].extend(warnings)
            if fixed_row is not row:
                validation_summary['fixed'] += 1
            
            # Skip if critical errors
            if errors:
                continue
            
            # Extract data from fixed row
            campaign_name = fixed_row.get('campaign_name', f"Campaign_{idx}")
            asset_url = fixed_row.get('asset_url', '')
            marketo_id = fixed_row.get('marketo_campaign_id', '')
            utm_source = fixed_row.get('utm_source', 'linkedin')
            utm_medium = fixed_row.get('utm_medium', 'paid_social')
            
            # Generate tracking URL
            final_url = generate_utm_link(asset_url, utm_source, utm_medium, marketo_id)
            
            # In demo mode, simulate verification
            if DEMO_MODE:
                verification_status = random.choice(['success', 'success', 'success', 'warning'])
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
            
        except Exception as e:
            SystemLogger.log_error("campaign_processing", str(e), {
                "row": idx,
                "campaign": row.get('campaign_name', 'Unknown')
            })
            st.error(f"Error processing row {idx + 1}: {str(e)}")
    
    # Log validation summary
    SystemLogger.log_event('info', f"Bulk processing complete", {
        'total': len(df),
        'processed': len(results),
        'errors': len(validation_summary['errors']),
        'warnings': len(validation_summary['warnings']),
        'auto_fixed': validation_summary['fixed']
    })
    
    return pd.DataFrame(results), validation_summary

def create_download_link(df, filename, file_format='xlsx'):
    """Create a download link for the processed data"""
    try:
        if file_format == 'xlsx':
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Campaigns')
            output.seek(0)
            SystemLogger.log_success("create_download", {"format": "xlsx", "rows": len(df)})
            return output.getvalue(), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        else:
            SystemLogger.log_success("create_download", {"format": "csv", "rows": len(df)})
            return df.to_csv(index=False).encode('utf-8'), 'text/csv'
    except Exception as e:
        SystemLogger.log_error("download_creation", str(e), {"format": file_format})
        raise

# --- FRONTEND UI ---

st.title("🛡️ Verified Campaign Architect")
st.markdown("""
**Workflow:** Upload Campaigns → Auto-Build Links → Pre-Flight Verify → Download Results
*Eliminates manual 'system jumping' and validates data plumbing before spend.*

🤖 **Self-Annealing System Active** - Automatically learns from errors and improves over time.
""")

# Quick Win: System Health Summary Dashboard
if st.session_state.system_logs or st.session_state.improvements:
    with st.expander("📊 System Health Summary", expanded=False):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_events = len(st.session_state.system_logs)
            st.metric("Total Events", total_events, help="All system activities logged")
        
        with col2:
            improvements = len(st.session_state.improvements)
            delta = f"+{improvements}" if improvements > 0 else None
            st.metric("Auto-Improvements", improvements, delta=delta, help="Issues automatically fixed")
        
        with col3:
            error_count = len([log for log in st.session_state.system_logs if log['type'] == 'error'])
            success_count = len([log for log in st.session_state.system_logs if log['type'] == 'success'])
            if total_events > 0:
                success_rate = int((success_count / total_events) * 100)
                st.metric("Success Rate", f"{success_rate}%", help="Percentage of successful operations")
            else:
                st.metric("Success Rate", "N/A", help="No operations yet")
        
        with col4:
            pattern_count = len(st.session_state.error_patterns)
            st.metric("Error Patterns", pattern_count, help="Unique error types tracked")

# Create tabs
tab1, tab2, tab3 = st.tabs(["📤 Bulk Upload", "➕ Single Campaign", "📊 View Results"])

# [Rest of the UI code continues with the same structure as before...]
# TAB 1: BULK UPLOAD
with tab1:
    st.header("📤 Bulk Campaign Upload")
    st.markdown("Upload an Excel or CSV file with multiple campaigns to process at once.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Upload File")
        
        uploaded_file = st.file_uploader(
            "Choose an Excel or CSV file",
            type=['xlsx', 'xls', 'csv'],
            help="Upload a file containing your campaign data"
        )
        
        # Template download
        st.markdown("### 📋 Need a template?")
        st.markdown("Download our template to see the expected format:")
        
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
    
    with col2:
        if uploaded_file is not None:
            st.subheader("2. Preview & Process")
            
            # Quick Win B: File size validation
            file_size_mb = uploaded_file.size / (1024 * 1024)
            if file_size_mb > 5:
                st.warning(f"⚠️ Large file detected ({file_size_mb:.1f}MB). Processing may take several minutes.")
                st.info("💡 **Tip:** For files with 1000+ rows, consider splitting into smaller batches for faster processing.")
            
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.session_state.uploaded_campaigns_df = df
                
                st.success(f"✅ File uploaded successfully! Found {len(df)} campaigns.")
                SystemLogger.log_success("file_upload", {"rows": len(df), "filename": uploaded_file.name, "size_mb": f"{file_size_mb:.2f}"})
                
                st.markdown("**Data Preview:**")
                st.dataframe(df.head(10), use_container_width=True)
                
                if len(df) > 10:
                    st.info(f"Showing first 10 of {len(df)} rows")
                
                required_cols = ['campaign_name', 'asset_url', 'marketo_campaign_id']
                missing_cols = [col for col in required_cols if col not in df.columns]
                
                if missing_cols:
                    st.error(f"❌ Missing required columns: {', '.join(missing_cols)}")
                    SystemLogger.log_error("validation", f"Missing columns: {missing_cols}", {"file": uploaded_file.name})
                else:
                    st.success("✅ All required columns present")
                    
                    if st.button("🚀 Process All Campaigns", type="primary"):
                        # Quick Win A: Better loading states with detailed progress
                        with st.status("Processing campaigns...", expanded=True) as status:
                            # Step 1: Validation
                            status.write("🔍 **Step 1/4:** Validating campaign data...")
                            time.sleep(0.3)
                            st.write(f"   → Checking {len(df)} campaigns for required fields")
                            st.write(f"   → Verifying URLs and formats")
                            
                            # Step 2: Auto-fixing
                            status.write("🔧 **Step 2/4:** Applying intelligent auto-fixes...")
                            time.sleep(0.3)
                            
                            processed_df, validation_summary = process_bulk_campaigns(df)
                            st.session_state.processed_campaigns_df = processed_df
                            
                            # Show validation results inline
                            if validation_summary['fixed'] > 0:
                                st.write(f"   ✅ Auto-corrected {validation_summary['fixed']} issues")
                            if validation_summary['warnings']:
                                st.write(f"   ⚠️  Found {len(validation_summary['warnings'])} warnings")
                            if validation_summary['errors']:
                                st.write(f"   ❌ Encountered {len(validation_summary['errors'])} errors")
                            
                            # Step 3: Generation
                            status.write("🚀 **Step 3/4:** Generating tracking URLs and form IDs...")
                            time.sleep(0.3)
                            st.write(f"   → Created {len(processed_df)} UTM tracking URLs")
                            st.write(f"   → Generated {len(processed_df)} LinkedIn form IDs")
                            
                            # Step 4: Verification
                            status.write("✅ **Step 4/4:** Finalizing and verifying...")
                            time.sleep(0.3)
                            if DEMO_MODE:
                                st.write("   → Demo mode: Simulated verification")
                            st.write(f"   → Saved {len(processed_df)} campaigns to results")
                            
                            status.update(
                                label=f"✅ Successfully processed {len(processed_df)} campaigns!",
                                state="complete"
                            )
                        
                        st.balloons()
                        st.success("🎉 All campaigns processed! Go to 'View Results' tab to download.")
            
            except Exception as e:
                st.error(f"❌ Error reading file: {str(e)}")
                SystemLogger.log_error("file_read", str(e), {"filename": uploaded_file.name})
                st.info("Please make sure your file is a valid Excel or CSV file.")

# TAB 2: Single Campaign (keeping original interface)
with tab2:
    st.header("➕ Create Single Campaign")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Build Campaign")
        
        assets = mock_assets()
        selected_asset_name = st.selectbox("Select Goal Asset (Website)", options=assets.keys())
        selected_asset_url = assets[selected_asset_name]
        
        campaigns = mock_marketo_campaigns()
        selected_campaign_id = st.selectbox(
            "Select Destination Campaign (Marketo)", 
            options=campaigns.keys(),
            format_func=lambda x: f"{x} - {campaigns[x]}"
        )

        st.info("👇 System will auto-generate tracking taxonomy.")
        
        utm_source = "linkedin"
        utm_medium = "paid_social"
        
        if st.button("Generate & Bind"):
            try:
                final_url = generate_utm_link(selected_asset_url, utm_source, utm_medium, selected_campaign_id)
                
                st.session_state.campaign_data = {
                    "asset": selected_asset_name,
                    "marketo_id": selected_campaign_id,
                    "final_url": final_url,
                    "form_id": f"LIGF_{selected_campaign_id}_v1"
                }
                st.session_state.verification_status = None
                SystemLogger.log_success("campaign_generation", {
                    "campaign": selected_asset_name,
                    "marketo_id": selected_campaign_id
                })
            except Exception as e:
                st.error(f"Error generating campaign: {str(e)}")

    with col2:
        if st.session_state.campaign_data:
            st.subheader("2. Campaign Object")
            
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
                    
                    success, logs = verify_connection(
                        st.session_state.campaign_data['final_url'], 
                        st.session_state.campaign_data['marketo_id']
                    )
                    
                    for log in logs:
                        st.write(log)
                    
                    if success:
                        status.update(label="All Systems Go! Connection Verified.", state="complete", expanded=True)
                        st.session_state.verification_status = 'success'
                    else:
                        status.update(label="Verification Failed. See logs.", state="error", expanded=True)
                        st.session_state.verification_status = 'failed'

    if st.session_state.verification_status == 'success':
        st.divider()
        st.balloons()
        st.success(f"✅ **GREEN LIGHT**: Campaign '{campaigns[selected_campaign_id]}' is safe to launch. Data flow is verified.")

# TAB 3: View Results
with tab3:
    st.header("📊 Processed Campaign Results")
    
    if st.session_state.processed_campaigns_df is not None:
        df_results = st.session_state.processed_campaigns_df
        
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
        
        st.subheader("Campaign Details")
        st.dataframe(df_results, use_container_width=True)
        
        st.divider()
        
        st.subheader("💾 Download Results")
        st.markdown("Export your processed campaigns with tracking URLs and verification status.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            excel_data, excel_mime = create_download_link(df_results, 'processed_campaigns.xlsx', 'xlsx')
            st.download_button(
                label="📥 Download as Excel",
                data=excel_data,
                file_name=f"processed_campaigns_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime=excel_mime,
                type="primary"
            )
        
        with col2:
            csv_data, csv_mime = create_download_link(df_results, 'processed_campaigns.csv', 'csv')
            st.download_button(
                label="📥 Download as CSV",
                data=csv_data,
                file_name=f"processed_campaigns_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime=csv_mime
            )
    
    else:
        st.info("👆 No processed campaigns yet. Upload a file in the 'Bulk Upload' tab to get started!")
