# Excel/CSV Upload & Download Guide
## Campaign Architect - Bulk Processing Feature

---

## 🎯 Overview

The enhanced Campaign Architect now supports **bulk campaign processing** through Excel and CSV files. This allows you to:
- ✅ Upload multiple campaigns at once
- ✅ Auto-generate tracking URLs for all campaigns
- ✅ Verify connections in batch
- ✅ Download processed results with all tracking details

---

## 📤 How to Upload Campaigns

### Method 1: Use Our Template (Recommended)

1. **Download the Template**
   - Go to the "📤 Bulk Upload" tab
   - Click "📥 Download Excel Template" or "📥 Download CSV Template"
   - Open the downloaded file

2. **Fill in Your Campaign Data**
   The template includes these columns:
   
   | Column Name | Description | Example |
   |------------|-------------|---------|
   | `campaign_name` | Your campaign's name | "Q1 Financial Services" |
   | `asset_url` | Landing page URL | "https://demandbase.com/resources/report" |
   | `marketo_campaign_id` | Your Marketo campaign ID | "1098" |
   | `utm_source` | Traffic source | "linkedin" or "google" |
   | `utm_medium` | Marketing medium | "paid_social" or "email" |

3. **Save and Upload**
   - Save your file (Excel or CSV format)
   - Click "Choose an Excel or CSV file" in the app
   - Select your file
   - Preview appears automatically

### Method 2: Create Your Own File

**Required Columns:**
```
campaign_name, asset_url, marketo_campaign_id, utm_source, utm_medium
```

**Example CSV:**
```csv
campaign_name,asset_url,marketo_campaign_id,utm_source,utm_medium
Q1 Financial Campaign,https://demandbase.com/resources/finserv,1098,linkedin,paid_social
Healthcare AI Webinar,https://demandbase.com/resources/healthcare,2045,linkedin,paid_social
Manufacturing Summit,https://demandbase.com/resources/manufacturing,3012,google,paid_search
```

**Example Excel:**
- Create a spreadsheet with the columns above
- Each row = one campaign
- Save as `.xlsx` or `.xls`

---

## 🔄 How to Process Campaigns

### Step-by-Step:

1. **Upload Your File**
   - Go to "📤 Bulk Upload" tab
   - Upload your Excel or CSV file
   - Wait for the preview to appear

2. **Review the Preview**
   - Check that your data looks correct
   - Verify all required columns are present
   - System will show ✅ or ❌ validation status

3. **Click "Process All Campaigns"**
   - The system will:
     - Generate tracking URLs for each campaign
     - Create LinkedIn form IDs
     - Verify connections (if credentials configured)
     - Add processing timestamps

4. **Wait for Completion**
   - Progress indicator shows status
   - Usually takes a few seconds per campaign
   - Success message appears when done

---

## 📥 How to Download Results

### Where to Find Downloads:

1. **Go to "📊 View Results" Tab**
   - See summary metrics:
     - Total campaigns processed
     - Verified campaigns
     - Warnings
     - Pending verifications

2. **Review the Results Table**
   - All campaigns listed with details
   - Color-coded status:
     - 🟢 Green = Success
     - 🟡 Yellow = Warning
     - ⚪ Gray = Pending

3. **Choose Download Format**
   - **Excel (.xlsx)** - Recommended for further editing
   - **CSV (.csv)** - Compatible with most systems

4. **Click Download Button**
   - File downloads automatically
   - Named with timestamp: `processed_campaigns_20240115_103045.xlsx`

---

## 📋 What's Included in Downloads?

Your downloaded file contains:

### Original Data:
- Campaign name
- Asset URL
- Marketo Campaign ID
- UTM source
- UTM medium

### Generated Data:
- ✅ **Tracking URL** - Complete URL with UTM parameters
- ✅ **Form ID** - LinkedIn form identifier
- ✅ **Verification Status** - success/warning/pending
- ✅ **Processing Timestamp** - When it was processed

### Example Output:

| campaign_name | marketo_campaign_id | tracking_url | form_id | verification_status |
|--------------|-------------------|--------------|---------|-------------------|
| Q1 Financial | 1098 | https://demandbase.com/resources/finserv?utm_source=linkedin&utm_medium=paid_social&utm_campaign=1098 | LIGF_1098_v1 | success |

---

## 🎯 Use Cases

### Use Case 1: Monthly Campaign Setup
**Scenario:** You have 50 new campaigns to launch this month

**Workflow:**
1. Export campaign list from your planning spreadsheet
2. Add required columns (asset_url, marketo_campaign_id, etc.)
3. Upload to Campaign Architect
4. Download processed results
5. Import tracking URLs into your ad platforms

**Time Saved:** Hours of manual URL building and verification

---

### Use Case 2: Campaign Audit
**Scenario:** Need to verify existing campaigns are properly configured

**Workflow:**
1. Export existing campaigns from Marketo
2. Upload to Campaign Architect
3. System verifies all connections
4. Download report showing which campaigns have issues
5. Fix the flagged campaigns

**Benefit:** Catch broken tracking before wasting ad spend

---

### Use Case 3: Cross-Team Collaboration
**Scenario:** Marketing ops creates campaigns, paid media team needs URLs

**Workflow:**
1. Marketing ops: Upload campaign list
2. System generates all tracking URLs
3. Download and share file with paid media team
4. Paid media team: Copy URLs directly into ad platforms
5. No back-and-forth, no errors

**Benefit:** Standardized process, fewer mistakes

---

## ✅ Best Practices

### File Preparation:
- ✅ **Use the template** - Ensures correct column names
- ✅ **Check for typos** - Especially in URLs and IDs
- ✅ **Test with small batch first** - Upload 5-10 campaigns to test
- ✅ **Keep original file** - Save your source data as backup

### Processing:
- ✅ **Review preview** - Check data before processing
- ✅ **Configure credentials** - For full verification
- ✅ **Note warnings** - Check any campaigns with warnings
- ✅ **Re-run if needed** - Can upload same file again

### Downloads:
- ✅ **Download immediately** - Session may expire
- ✅ **Save with version numbers** - `campaigns_v1.xlsx`, `campaigns_v2.xlsx`
- ✅ **Archive processed files** - Keep for reference
- ✅ **Import carefully** - Double-check URLs before using

---

## ⚠️ Common Issues & Solutions

### Issue: "Missing required columns"
**Solution:** 
- Download our template
- Copy your data into template
- Make sure column names match exactly (case-sensitive)

### Issue: "File won't upload"
**Solution:**
- Check file size (should be under 10MB)
- Verify it's .xlsx, .xls, or .csv format
- Close file in Excel before uploading
- Try converting to CSV if Excel file has issues

### Issue: "Verification shows 'pending'"
**Solution:**
- This means API credentials aren't configured yet
- URLs are still generated and valid
- Add credentials for full verification
- Or continue in Demo Mode for testing

### Issue: "Can't find downloaded file"
**Solution:**
- Check your browser's Downloads folder
- File named: `processed_campaigns_[timestamp].xlsx`
- May need to allow popup/download in browser settings

### Issue: "Some campaigns show 'warning'"
**Solution:**
- Review those specific campaigns in the results table
- Common causes:
  - Invalid URL format
  - Missing Marketo campaign ID
  - Connection timeout
- Fix in your source file and re-upload

---

## 🔄 Typical Workflow

### Weekly Campaign Launch Process:

**Monday:**
1. Marketing team creates campaign plan in Google Sheets
2. Export to CSV

**Tuesday:**
1. Upload CSV to Campaign Architect
2. System generates tracking URLs
3. Download processed file
4. Review for any warnings

**Wednesday:**
1. Import tracking URLs into LinkedIn Ads
2. Import into Google Ads
3. Set up campaigns

**Thursday:**
1. QA test - click through URLs
2. Verify Marketo is receiving test leads
3. Check Salesforce sync

**Friday:**
1. Launch campaigns
2. Archive processed file for reference

**Time Saved:** 4-6 hours per week on manual URL building and verification

---

## 📊 File Size Limits

| File Type | Max Rows | Max File Size | Notes |
|-----------|----------|---------------|-------|
| CSV | 1,000 | 5 MB | Fastest processing |
| Excel (.xlsx) | 1,000 | 10 MB | Supports formulas |
| Excel (.xls) | 500 | 5 MB | Older format |

**Need to process more?**
- Break into multiple files
- Process in batches
- Contact support for enterprise limits

---

## 🆘 Need Help?

### Documentation:
- See main CREDENTIAL_GUIDE.md for API setup
- See IMPROVEMENTS_SUMMARY.md for feature overview

### Troubleshooting:
- Check the "🔧 Troubleshooting Guide" in the sidebar
- Review validation messages in the app
- Download and compare with template

### Support:
- Contact your IT/DevOps team
- Email: [your-support-email]
- Slack: #campaign-architect-help

---

## 🎉 Quick Start Checklist

Ready to process your first batch? Follow this checklist:

- [ ] Download the Excel/CSV template
- [ ] Fill in your campaign data (at least 3-5 campaigns for testing)
- [ ] Verify all required columns are present
- [ ] Upload file to Campaign Architect
- [ ] Review the preview
- [ ] Click "Process All Campaigns"
- [ ] Go to "View Results" tab
- [ ] Review the results table
- [ ] Download processed file (Excel or CSV)
- [ ] Import tracking URLs into your ad platforms
- [ ] Test one campaign to verify tracking works
- [ ] Launch remaining campaigns
- [ ] 🎉 Celebrate time saved!

---

## 💡 Pro Tips

1. **Keep a Master Template**
   - Save a version with all your standard settings
   - utm_source, utm_medium defaults pre-filled
   - Makes future uploads faster

2. **Version Control Your Files**
   - Name files: `campaigns_2024Q1_v1.xlsx`
   - Keep history of what was processed when
   - Helps troubleshoot issues later

3. **Use Excel Formulas**
   - Auto-generate campaign names: `="Q1 " & A2`
   - Build asset URLs: `="https://yoursite.com/resources/" & B2`
   - Speeds up bulk file creation

4. **Batch by Campaign Type**
   - Separate files for LinkedIn vs Google campaigns
   - Different utm_medium values
   - Easier to manage and track

5. **Archive Processed Files**
   - Create a "Processed Campaigns" folder
   - Keep downloads for at least 90 days
   - Reference when troubleshooting tracking

---

**Ready to save hours on campaign setup? Upload your first batch today!** 🚀
