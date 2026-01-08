# Self-Annealing System Documentation

## Overview

The Campaign Architect now implements a **self-annealing system** based on the principles from AGENTS.md. The system automatically learns from errors, tracks patterns, and improves itself over time.

---

## What is Self-Annealing?

Self-annealing is the process where the system:
1. **Detects errors** and edge cases
2. **Fixes problems** automatically when possible
3. **Learns from failures** by tracking patterns
4. **Suggests improvements** based on recurring issues
5. **Evolves** to become more reliable over time

This approach is inspired by the 3-layer architecture principle:
- **Layer 1**: Instructions (what to do)
- **Layer 2**: Orchestration (AI decision-making)
- **Layer 3**: Execution (deterministic code)

---

## Key Features

### 1. System Logger

**Purpose**: Capture all system events for analysis and improvement

**What it tracks:**
- ✅ **Success events** - Completed operations
- ❌ **Error events** - Failed operations with stack traces
- 🔧 **Improvements** - Auto-fixes and enhancements
- ℹ️ **Info events** - General system activity

**Example:**
```python
SystemLogger.log_success("generate_utm_link", {"url": final_url})
SystemLogger.log_error("validation", "Missing required field", {"field": "campaign_name"})
SystemLogger.log_improvement("url_validation", "Auto-added https:// protocol", "Prevents validation errors")
```

### 2. Auto-Fix Capabilities

**Purpose**: Automatically correct common mistakes

**Current Auto-Fixes:**

#### URL Validation
- **Problem**: User forgets "https://" in URL
- **Fix**: Automatically adds "https://" prefix
- **Impact**: Prevents validation errors and broken links

#### Double Slash Correction
- **Problem**: URLs with double slashes (e.g., `https://site.com//path`)
- **Fix**: Removes duplicate slashes in path
- **Impact**: Prevents routing errors

#### URL Trailing Slash
- **Problem**: Inconsistent trailing slashes
- **Fix**: Standardizes by removing trailing slashes
- **Impact**: Consistent URL format

**Example:**
```python
# Before
url = "demandbase.com/resources//report"

# After auto-fix
url = "https://demandbase.com/resources/report"
```

### 3. Pattern Detection

**Purpose**: Identify recurring errors and suggest fixes

**How it works:**
- Tracks error types and frequencies
- When same error occurs 3+ times, flags it
- Generates improvement suggestions
- Displays in sidebar under "System Health & Logs"

**Example Suggestions:**
- "Recurring URL validation error (5 times). Consider implementing automatic retry logic."
- "Multiple campaign ID format issues detected. Add field validation."

### 4. Validation with Learning

**Purpose**: Validate data and learn from common issues

**Validation Checks:**
- ✅ Required fields present
- ✅ URLs properly formatted
- ✅ Campaign IDs are numeric
- ✅ No duplicate entries

**Learning Process:**
```
User uploads file → System validates → Finds issues → Auto-fixes → Logs improvements → Updates patterns
```

---

## User-Visible Features

### System Health Dashboard

**Location**: Sidebar → "🔬 System Health & Logs"

**What you see:**
1. **Improvements Counter**
   - Shows total improvements made
   - Click "View Improvements" to see recent fixes
   
2. **Error Pattern Analysis**
   - Shows number of error types tracked
   - Displays suggested improvements
   
3. **Activity Log**
   - Filter by type (All, error, success, improvement)
   - Last 20 events displayed
   - Real-time updates

### Auto-Fix Notifications

**During file upload:**
- "🔧 Auto-fixed 5 issues" - Shows when system corrects problems
- "⚠️ 3 warnings" - Non-critical issues detected
- "❌ 2 errors" - Critical issues requiring attention

### Improvement Tracking

**What gets tracked:**
- URL format fixes
- Field validation improvements
- Performance optimizations
- Error handling enhancements

**View improvements:**
```
Sidebar → System Health & Logs → View Improvements
```

---

## How It Works: Example Flow

### Scenario: User Uploads File with Bad URLs

1. **Upload**: User uploads campaign file with URLs missing "https://"
   
2. **Detection**: System validates each row
   ```python
   # Detects: "demandbase.com/resource"
   ```

3. **Auto-Fix**: System corrects the URL
   ```python
   # Fixes to: "https://demandbase.com/resource"
   ```

4. **Logging**: Records the improvement
   ```python
   SystemLogger.log_improvement(
       'url_validation',
       'Auto-added https:// protocol to URL',
       'Prevents validation errors'
   )
   ```

5. **Notification**: User sees "🔧 Auto-fixed 1 issue"

6. **Pattern**: If this happens 3+ times, system suggests:
   ```
   "Recurring URL format issue. Consider adding
   format hints in the template."
   ```

7. **Evolution**: System becomes smarter about URL handling

---

## Technical Implementation

### SystemLogger Class

```python
class SystemLogger:
    @staticmethod
    def log_event(event_type, message, metadata=None):
        """Log any system event"""
        
    @staticmethod
    def log_error(error_type, error_message, context=None):
        """Log errors and track patterns"""
        
    @staticmethod
    def log_success(operation, details=None):
        """Log successful operations"""
        
    @staticmethod
    def log_improvement(improvement_type, description, impact):
        """Log system improvements"""
        
    @staticmethod
    def analyze_patterns():
        """Analyze errors and suggest improvements"""
        
    @staticmethod
    def get_recent_logs(count=50, log_type=None):
        """Retrieve filtered logs"""
```

### Auto-Fix Functions

```python
def auto_fix_url(url):
    """Automatically fix common URL issues"""
    # Add https:// if missing
    # Remove double slashes
    # Strip trailing slash
    
def validate_campaign_data(row, row_num):
    """Validate and auto-correct campaign data"""
    # Check required fields
    # Fix URL format
    # Validate campaign ID
    # Return errors, warnings, fixed_row
```

### Integration Points

1. **File Upload**: Validates and auto-fixes
2. **Campaign Generation**: Logs success/errors
3. **URL Building**: Auto-corrects format
4. **Verification**: Tracks patterns
5. **Download**: Logs completions

---

## Benefits

### For Users

1. **Fewer Errors**
   - System catches and fixes common mistakes
   - Less time debugging
   
2. **Better Reliability**
   - System learns from failures
   - Gets smarter over time
   
3. **Transparency**
   - See what's being fixed
   - Understand system improvements
   
4. **Proactive Suggestions**
   - System tells you how to prevent recurring issues

### For Developers

1. **Error Tracking**
   - Complete logs of all failures
   - Stack traces preserved
   
2. **Pattern Recognition**
   - Identify systemic issues
   - Prioritize fixes
   
3. **Impact Measurement**
   - Track improvement frequency
   - Measure system evolution
   
4. **Debugging**
   - Full activity history
   - Context for each error

---

## Configuration

### Session State Variables

```python
# Log storage
st.session_state.system_logs = []          # All events
st.session_state.error_patterns = {}       # Error frequency
st.session_state.improvements = []         # Auto-fixes made
```

### Log Retention

- **Default**: Last 1000 events
- **Display**: Last 20 events
- **Filtered**: By type (error/success/improvement)

### Pattern Threshold

- **Trigger**: 3+ occurrences of same error type
- **Action**: Generate improvement suggestion
- **Display**: In System Health dashboard

---

## Future Enhancements

### Planned Features

1. **Machine Learning Integration**
   - Learn optimal validation rules
   - Predict errors before they occur
   
2. **Automatic Retry Logic**
   - Retry failed API calls with backoff
   - Learn optimal retry strategies
   
3. **User Preferences Learning**
   - Adapt to user's specific patterns
   - Customize auto-fixes per user
   
4. **Export/Import Learnings**
   - Share improvements across teams
   - Version control for system intelligence
   
5. **Advanced Analytics**
   - Success rate trending
   - Most common error types
   - Time-to-fix metrics

### Extensibility

To add new auto-fixes:

```python
def auto_fix_my_feature(data):
    """Fix a specific issue"""
    # Detection logic
    if issue_detected:
        # Fix logic
        fixed_data = apply_fix(data)
        
        # Log improvement
        SystemLogger.log_improvement(
            'my_feature',
            'Description of fix',
            'Impact explanation'
        )
        
        return fixed_data
    return data
```

---

## Best Practices

### For Users

1. **Check System Health Regularly**
   - Review improvements
   - Read suggested enhancements
   
2. **Act on Suggestions**
   - Implement recommended changes
   - Update templates based on patterns
   
3. **Report Persistent Issues**
   - If same error keeps occurring
   - Contact support with log details

### For Developers

1. **Log Generously**
   - Log all significant operations
   - Include context in metadata
   
2. **Meaningful Messages**
   - Clear error descriptions
   - Actionable improvement descriptions
   
3. **Test Auto-Fixes**
   - Verify fixes don't break edge cases
   - Add unit tests for new fixes
   
4. **Review Patterns Weekly**
   - Check for new recurring issues
   - Implement fixes for common patterns

---

## Troubleshooting

### Logs Not Appearing

**Problem**: No logs visible in sidebar
**Solution**: 
- Check if any operations have been performed
- Try processing a campaign or uploading a file
- Logs appear after first event

### Too Many Improvements

**Problem**: Improvement counter seems high
**Solution**:
- This is actually good! System is learning
- Review improvements to see what's being fixed
- Many small fixes = better reliability

### Same Error Keeps Occurring

**Problem**: Pattern detection but no improvement
**Solution**:
- Check suggested improvements in sidebar
- May require manual code fix
- Report to development team with context

### Performance Impact

**Problem**: App seems slower
**Solution**:
- Logs limited to 1000 entries (auto-trimmed)
- Minimal performance impact
- If issues persist, check browser console

---

## Summary

The self-annealing system makes Campaign Architect:
- ✅ **Smarter** - Learns from errors
- ✅ **More Reliable** - Auto-fixes common issues
- ✅ **Transparent** - Shows what it's doing
- ✅ **Proactive** - Suggests improvements
- ✅ **Self-Improving** - Gets better over time

**Key Principle**: The system should learn from every error and become more robust with each use.

---

## References

- **AGENTS.md** - Original self-annealing architecture principles
- **System Health Dashboard** - View in app sidebar
- **Activity Logs** - Real-time event tracking
- **Improvement Log** - History of all auto-fixes
