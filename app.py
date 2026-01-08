import streamlit as st
import pandas as pd
import time
import requests
import json
import random
from datetime import datetime

# --- CONFIGURATION & STATE ---
st.set_page_config(page_title="Verified Campaign Architect", layout="wide", page_icon="🛡️")

# Initialize Session State
if 'campaign_data' not in st.session_state:
    st.session_state.campaign_data = {}
if 'verification_log' not in st.session_state:
    st.session_state.verification_log = []
if 'verification_status' not in st.session_state:
    st.session_state.verification_status = None # None, 'running', 'success', 'failed'

# --- SIDEBAR: AUTHENTICATION (Anthony's Job Later) ---
with st.sidebar:
    st.header("🔐 API Configuration")
    st.markdown("Enter credentials to enable real-time verification.")
    
    with st.expander("Marketo (Source of Truth)"):
        mkt_client_id = st.text_input("Client ID", type="password")
        mkt_client_secret = st.text_input("Client Secret", type="password")
        mkt_base_url = st.text_input("Munchkin Base URL")
    
    with st.expander("Salesforce (Sync Check)"):
        sf_consumer_key = st.text_input("Consumer Key", type="password")
        sf_consumer_secret = st.text_input("Consumer Secret", type="password")
    
    with st.expander("LinkedIn (Form Connector)"):
        li_access_token = st.text_input("Access Token", type="password")

    st.divider()
    # DEV TOGGLE: Allows you to show the UI flow without real keys
    DEMO_MODE = st.checkbox("🛠️ Developer Demo Mode", value=True, help="Simulate API calls for UI testing")

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

# --- FRONTEND UI ---

st.title("🛡️ Verified Campaign Architect")
st.markdown("""
**Workflow:** Select Asset $\rightarrow$ Auto-Build Links $\rightarrow$ Pre-Flight Verify $\rightarrow$ Launch.
*Eliminates manual 'system jumping' and validates data plumbing before spend.*
""")

st.divider()

# COLUMNS FOR LAYOUT
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
            "form_id": f"LIGF_{selected_campaign_id}_v1" # Simulated LinkedIn Form Name
        }
        st.session_state.verification_status = None # Reset verification on new build

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
                
                # EXECUTE VERIFICATION (Module 2, Step B)
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

# --- FINAL GREEN LIGHT ---
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
