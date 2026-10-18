# Quick Reference: Activity History & Multi-Person Updates

## What Changed

### Views (`activities/views.py`)
```
✅ activity_history()  → Now combines Activity + PersonActivity
✅ multi_person_view() → Now includes PersonActivity records  
✅ get_distribution()  → Now aggregates both sources
```

### Templates
```
✅ history.html       → Added source badges, handles both types
✅ multi_person.html  → Added PersonActivity section, real charts
```

## What Users See

### Activity History Page
- **Source badges**: 📷 Image OR 👤 Pose next to each activity
- **Combined data**: Both Activity and PersonActivity in one table
- **Proper handling**: Missing fields show as "N/A"

### Multi-Person View
- **Grouped activities**: MultiPersonActivity records
- **Pose detections**: Separate section showing last hour
- **Real charts**: Distribution pie chart loads actual data

## Data Aggregation Example

```
Activity Records:
  - WALKING (90%)
  - SITTING (85%)
  - WALKING (92%)
  
PersonActivity Records:
  - SITTING (95%)
  - RUNNING (87%)
  
Distribution Result:
  - WALKING: 2 (from Activity)
  - SITTING: 2 (1 from Activity + 1 from PersonActivity)
  - RUNNING: 1 (from PersonActivity)
```

## Key Features

| Feature | Before | After |
|---------|--------|-------|
| Historical view shows | Activity only | Activity + PersonActivity |
| Distribution includes | Activity only | Activity + PersonActivity |
| Source indication | None | Badges show source |
| Multi-person display | Images only | Images + Pose separately |
| Chart data | Hardcoded | Real/Dynamic |

## Template Fields Reference

### Activity Records (source='image')
```
- id: 'act_{id}'
- activity_type: WALKING/SITTING/etc
- confidence_score: 85.5
- timestamp: 2025-01-20 14:30:45
- location: 'Home'
- environment: Environment object (not None)
- is_verified: True/False
- duration: seconds
- source: 'image'
```

### PersonActivity Records (source='pose')
```
- id: 'pa_{id}'
- activity_type: WALKING/SITTING/etc
- confidence_score: 92.0
- timestamp: 2025-01-20 14:30:45
- location: 'Office'
- environment: None (not available)
- is_verified: False (not available)
- duration: None (not available)
- source: 'pose'
```

## Testing Commands

```bash
# Basic verification
python test_view_updates.py

# Comprehensive verification
python verify_updates.py

# System check
python manage.py check

# Start server
python manage.py runserver
```

## API Endpoint

### GET `/api/distribution/`
**Returns aggregated Activity + PersonActivity counts**

```json
{
    "distribution": {
        "WALKING": 5,
        "SITTING": 3,
        "STANDING": 2,
        "RUNNING": 1,
        "SLEEPING": 1,
        "FALLING": 1
    }
}
```

## URLs

- Activity History: `/activities/history/`
- Multi-Person View: `/activities/multi-person/`
- Distribution API: `/api/distribution/`
- Real-Time: `/activities/real-time/`

## Files to Review

1. **Backend Logic**: `activities/views.py` (lines 430-475)
2. **History Template**: `activities/templates/activities/history.html`
3. **Multi-Person Template**: `activities/templates/activities/multi_person.html`
4. **Documentation**: 
   - `ACTIVITY_HISTORY_UPDATE.md` - Detailed changes
   - `UPDATE_COMPLETE.md` - Full overview
   - `SLEEPING_DETECTION_FIX.md` - Previous sleeping improvements

## Troubleshooting

**Issue**: Charts not loading
- **Fix**: Verify `/api/distribution/` endpoint returns JSON

**Issue**: PersonActivity records not showing
- **Fix**: Check `multi_person_view()` includes `person_activities` in context

**Issue**: Source badges not displaying
- **Fix**: Verify combined data has `'source'` key in view

**Issue**: "N/A" showing for environment (PersonActivity)
- **Fix**: This is expected - PersonActivity doesn't have environment field

## Success Indicators

✅ Activity history shows mixed Activity and PersonActivity records
✅ Source badges display correctly
✅ Distribution chart shows combined counts
✅ Multi-person view has separate pose-based section
✅ No errors in browser console
✅ All tests pass

---

**Status**: ✅ Complete and Verified
**Tested**: ✅ All components tested
**Ready**: ✅ Production ready
