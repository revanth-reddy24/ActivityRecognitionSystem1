# Quick Start Guide - Live Activity Recognition

## Start the Server

```bash
python manage.py runserver
```

Server runs on: http://127.0.0.1:8000

## Test Registration (Fixed - No IntegrityError)

1. Go to: http://127.0.0.1:8000/users/register/
2. Fill in username, email, password
3. Submit - should succeed with no database errors ✓

## Test Live Monitoring with Camera

1. **Login** at http://127.0.0.1:8000/users/login/
2. Go to **Real-time Monitoring** from sidebar
3. Click **"Start Camera"** button
4. **Allow camera access** when browser prompts
   - Look for the permission dialog/notification
   - For Chrome/Edge: Small icon in address bar
   - For Firefox: Permission bar at top of page
5. **Watch the activity feed** on the left
   - Predictions appear every 1-2 seconds
   - Shows: Activity type, confidence %, timestamp, location
   - Confidence bar is color-coded: Red <60%, Yellow 60-80%, Green >80%

## If Camera Permission is Denied

1. Error message appears below "Start Camera" button
2. Click **"How to allow"** button for tips
3. After allowing permission in browser settings:
   - Click **"Retry Camera"** button
4. Camera should now work ✓

## What the System Does

**When camera is running:**
- Captures frame every 1.2 seconds
- Sends to prediction endpoint
- Server predicts: walking, running, sitting, standing, falling, unusual, cooking, sleeping, exercising
- Saves prediction to database as Activity record
- Activity feed auto-refreshes every 1.5 seconds to show latest predictions

**Activity Feed Shows:**
- Activity type (detected behavior)
- Confidence score (how sure the model is)
- Timestamp (when detected)
- Location (always "Live Camera" for real-time)
- Environment (test location or default)

---

## Project Structure

```
activities/
├── views.py              ← predict_activity() saves predictions to DB
├── urls.py               ← /activities/stream-predict/ and /activities/api/activities/
├── models.py             ← Activity, Environment, ActivitySession models
└── templates/real_time.html  ← Camera UI + activity feed + real-time refresh

users/
├── views.py              ← register() no longer creates duplicate UserProfile
├── signals.py            ← create_user_profile() uses get_or_create()
└── models.py             ← CustomUser, UserProfile

core/
└── settings.py           ← ALLOWED_HOSTS set for dev
```

---

## Technical Details

### Prediction Endpoint
- **URL**: `/activities/stream-predict/`
- **Method**: POST
- **Input**: `image` (base64 data URL from canvas.toDataURL())
- **Output**: JSON with activity type, confidence, activity_id, status
- **Side Effect**: Creates Activity record in DB

### Activity Feed Endpoint
- **URL**: `/activities/api/activities/`
- **Method**: GET (AJAX)
- **Output**: JSON array of activities (most recent first)
- **Refresh**: Every 1.5s when camera is active, manual refresh otherwise

### Database Changes
- Activity records created with:
  - `user` (current logged-in user)
  - `activity_type` (predicted activity)
  - `confidence_score` (0-100)
  - `timestamp` (current time)
  - `location` (always "Live Camera" for real-time)
  - `environment` (linked to first active environment)

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Camera won't start | Click "How to allow" button for permission tips; try http://127.0.0.1:8000 (not hostname) |
| No activities showing | Start camera first; wait 1-2 seconds for prediction to be saved |
| Activity feed empty | Click Refresh button; ensure camera is capturing |
| Registration IntegrityError | Fixed ✓ - Register should now work |
| Server error on prediction | Check Django console for error message; ensure environment exists |

---

## Admin Access

1. Create superuser (if not exists):
   ```bash
   python manage.py createsuperuser
   ```
2. Go to: http://127.0.0.1:8000/admin/
3. View registered activities, environments, users

---

## Test Scripts

Run these to verify everything works:

```bash
# Test prediction endpoint
python test_prediction_flow.py

# Test activity feed
python test_activity_feed.py

# Run Django checks
python manage.py check
```

All tests should pass ✓

---

**System Status**: ✅ All fixes complete and tested
