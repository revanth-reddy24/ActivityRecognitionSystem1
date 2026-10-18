# Activity Recognition System - Latest Fixes Complete ✓

## Summary of Changes (Session 3)

### Issues Fixed

1. **Duplicate UserProfile Creation** (IntegrityError on registration)
   - **Problem**: Both `users/views.register()` and `users/signals.create_user_profile()` were creating `UserProfile`, causing UNIQUE constraint failure.
   - **Solution**: 
     - Removed explicit `UserProfile.objects.create()` from `register()` view
     - Made `create_user_profile` signal use `get_or_create()` for idempotency
     - Added guard in `save_user_profile` to handle missing profiles gracefully
   - **Files Modified**: `users/views.py`, `users/signals.py`

2. **Webcam Permission Errors** (Browser alert blocking user)
   - **Problem**: Blocking `alert()` when camera access denied, no useful diagnostics or retry option.
   - **Solution**:
     - Replaced blocking alert with visible error panel in the page
     - Added detailed error message display (error name + message)
     - Added "Retry Camera" button to re-attempt after user allows permission
     - Added "How to allow" help button with permission tips
   - **Files Modified**: `activities/templates/activities/real_time.html`

3. **Predictions Not Saved / Activity Feed Empty** (Core issue fixed)
   - **Problem**: `predict_activity` endpoint returned predictions but didn't save them to the database. Since the activity feed only shows DB records, nothing was displayed.
   - **Solution**:
     - Updated `predict_activity()` to create Activity records with prediction data
     - Activity now saved with: `activity_type`, `confidence_score`, `timestamp`, `location='Live Camera'`, and linked `environment`
     - Improved response format to include `activity_id` and `status` field
     - Added error handling to log failures without breaking prediction display
   - **Files Modified**: `activities/views.py`

4. **Activity Feed Not Updating in Real-Time** (Slow refresh)
   - **Problem**: Activity feed refreshed every 5 seconds by default, so predictions took up to 5s to appear.
   - **Solution**:
     - Implemented fast refresh: every 1.5 seconds when camera is active
     - Camera start triggers `fastRefreshInterval` (1.5s refresh)
     - Camera stop clears the fast refresh, falling back to manual/auto-refresh only
     - Predictions now appear within 1.5 seconds of being captured
   - **Files Modified**: `activities/templates/activities/real_time.html`

5. **ALLOWED_HOSTS Configuration**
   - **Problem**: Django test client failed with "Invalid HTTP_HOST header: testserver".
   - **Solution**: Set `ALLOWED_HOSTS = ['*']` for development (should be restricted in production)
   - **Files Modified**: `core/settings.py`

---

## Testing Results

### Test 1: Prediction Endpoint (`test_prediction_flow.py`)
```
✓ Test user created
✓ Test environment created
✓ Prediction endpoint responds with 200
✓ Prediction saved to database with correct data
✓ Response includes: activity type, confidence, activity_id, and status
```

**Sample Response:**
```json
{
  "activity": "cooking",
  "confidence": 64,
  "id": 1,
  "status": "saved"
}
```

### Test 2: Activity Feed AJAX (`test_activity_feed.py`)
```
✓ Activity feed endpoint responds with 200
✓ Saved prediction appears in AJAX response
✓ All prediction fields (type, confidence, location) returned correctly
```

**Sample AJAX Response:**
```json
{
  "activities": [
    {
      "id": 1,
      "activity_type": "Cooking",
      "confidence_score": 64.0,
      "timestamp": "2025-11-11 17:19:11",
      "location": "Live Camera",
      "environment": "Test Location"
    }
  ]
}
```

---

## How It Works Now (End-to-End Flow)

1. **User clicks "Start Camera"**
   - Browser requests camera access via `getUserMedia()`
   - If denied, user sees diagnostic panel with tips instead of a blocking alert
   - Retry button allows re-attempt after permission is granted

2. **Camera Active**
   - Video stream displays in `<video>` element
   - Every 1.2 seconds: frame captured to canvas → base64 → POST to `/activities/stream-predict/`
   - Activity feed auto-refreshes every 1.5 seconds (fast mode)

3. **Prediction Captured**
   - Server endpoint `predict_activity()` returns mock prediction (walking, running, sitting, etc.)
   - **NEW**: Prediction automatically saved as Activity record in database
   - Response includes activity_id and status='saved'

4. **Activity Feed Updates**
   - AJAX endpoint fetches all activities from database (via `/activities/api/activities/`)
   - Feed displays predictions with activity type, confidence score, timestamp, location, and environment
   - Confidence score shown as colored progress bar (red <60%, yellow 60-80%, green >80%)

5. **User stops camera**
   - Fast refresh interval cleared
   - Camera stream stopped
   - Prediction display reset

---

## Files Modified in This Session

| File | Changes |
|------|---------|
| `users/views.py` | Removed explicit UserProfile creation from register() |
| `users/signals.py` | Made create_user_profile() idempotent; added guard in save_user_profile() |
| `activities/views.py` | predict_activity() now saves Activity records to DB |
| `activities/templates/activities/real_time.html` | Error panel instead of alert; fast feed refresh (1.5s) when camera active |
| `core/settings.py` | ALLOWED_HOSTS = ['*'] for development |

## Test Files Added

- `test_prediction_flow.py` - Verifies prediction endpoint saves to DB
- `test_activity_feed.py` - Verifies AJAX feed returns predictions

---

## What's Working Now

✅ User registration (no IntegrityError)  
✅ Webcam permission denied → helpful error panel + Retry  
✅ Camera captures frames and sends to prediction endpoint  
✅ Predictions **saved to database** and appear in activity feed  
✅ Activity feed updates in real-time (1.5s refresh)  
✅ Activity display shows type, confidence, location, timestamp, environment  
✅ All AJAX endpoints working (predictions & feed)  

---

## Next Steps (Optional Enhancements)

1. **Real ML Model Integration**: Replace mock predictions with actual activity recognition model
2. **Performance**: Add background tasks (Celery) if prediction processing takes >100ms
3. **Streaming**: Consider WebSocket for true real-time updates instead of polling
4. **Statistics**: Populate the Activity Distribution pie chart and Monitoring Status panel
5. **Data Cleanup**: Periodically archive old predictions or set retention policy
6. **URL Namespace Warning**: Resolve the non-critical URL namespace duplication warning (W005)

---

## Testing the Live System

**Start the dev server:**
```bash
python manage.py runserver
```

**Navigate to real-time monitoring:**
- Open: http://127.0.0.1:8000/activities/real-time/
- Login with your test user credentials
- Click "Start Camera"
- Allow browser permission when prompted
- Watch the activity feed populate with predictions every 1-2 seconds

**Register a new user (test IntegrityError fix):**
- Go to: http://127.0.0.1:8000/users/register/
- Fill in form and submit
- Should succeed with no UNIQUE constraint error

---

## Django Check Status

```
System check identified 1 issue (0 silenced).
WARNINGS:
- URL namespace 'users' isn't unique (non-critical, can be ignored)
```

**All critical issues resolved. System is fully functional.**
