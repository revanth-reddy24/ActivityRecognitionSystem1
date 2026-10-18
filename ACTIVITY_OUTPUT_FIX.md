# Activity Recognition System - Fixed Activity Output

## Problem
Activity outputs were not showing in the real-time monitoring UI, even though the backend was correctly:
- Receiving pose data from the client
- Classifying activities using temporal heuristics
- Saving PersonActivity records to the database
- Returning predictions in API responses

## Root Cause
The `/api/activities/` AJAX endpoint was **only querying the `Activity` model** (image-based predictions), but the new pose-based prediction endpoint (`/pose-predict/`) creates **`PersonActivity` records** instead. These are two separate models:
- `Activity`: Records from the `/stream-predict/` (image-based) endpoint
- `PersonActivity`: Records from the `/pose-predict/` (pose-based) endpoint

The activity feed was empty or only showing old image-based predictions because it wasn't fetching PersonActivity records.

## Solution Implemented

### 1. Updated `/api/activities/` Endpoint
**File**: `activities/views.py`

Modified `get_activities()` to:
- Query both `Activity` and `PersonActivity` models
- Filter by the logged-in user
- Combine results into a single sorted list
- Limit to 20 most recent records
- Include a `source` field ('image' or 'pose') to distinguish the prediction type

```python
# Now returns combined Activity + PersonActivity records
# Sorted by timestamp (newest first)
# Includes source field for debugging/UI distinction
```

### 2. Enhanced `/pose-predict/` Endpoint
**File**: `activities/views.py`

Already implemented features:
- **Client ID Support**: Accepts `id` field from client (assigned by JS tracker)
- **Smart Deduplication**: Updates recent PersonActivity records with the same client_id instead of creating duplicates
- **Per-Person Output**: Returns exactly one result per detected person
- **Multi-Person Grouping**: Groups all persons from a single request under one MultiPersonActivity

```python
# Accepts persons with client-provided IDs
# Updates existing records when client_id matches within 8-second window
# Returns client_id in response for client-side mapping
```

### 3. Client-Side Tracking
**File**: `activities/templates/activities/real_time.html`

Implemented JavaScript tracker that:
- Assigns stable small numeric IDs to detected poses based on nose position matching
- Maintains a list of tracked persons across frames
- Matches new detections to existing tracked persons (distance threshold: 60px)
- Prunes tracked entries older than 5 seconds
- Sends these IDs to the server for better matching and deduplication

## Results

### Test Outputs
All tests now pass with activity outputs visible:

1. **Single Person**
   ```
   Pose Prediction: standing (81%)
   Activity Feed shows:
     - STANDING (81.0%) @ 2025-11-11 19:20:52 [src: pose]
   ```

2. **Multiple People**
   ```
   Server input: 2 persons detected
   Server output: 2 results (one per person)
   Activity Feed shows both entries
   ```

3. **Activity Distribution**
   ```
   API returns aggregated counts across all activity types
   - walking: 16
   - running: 15
   - sitting: 15
   ```

### Accuracy Improvements

The system now correctly detects:
- **Standing**: Shoulders well above hips, knees below hips
- **Sitting**: Small shoulder-hip gap, knees near hips
- **Sleeping/Lying**: Low vertical span + wide horizontal span (bounding box)
- **Falling**: Nose well below hips, or significant downward motion
- **Walking/Running**: Hip movement across frames

## How to Test Live

### 1. Start Django Server
```bash
python manage.py runserver
```

### 2. Open Real-time Monitoring
Visit: `http://127.0.0.1:8000/activities/real-time/`

### 3. Start Camera
Click the "Start Camera" button in the Live Camera card

### 4. Observe Activity Output
The system will:
- Estimate poses using PoseNet (client-side)
- Send keypoints to `/pose-predict/` endpoint
- Display predictions in the "Persons List" (right side)
- Show recent activities in the "Live Activity Feed" (left side, updates every 1.5s)
- Update the activity distribution pie chart

### 5. Test Multiple People
Position multiple people in the camera frame:
- The system will show one row per detected person
- Each person's activity is independently classified
- The distribution chart updates accordingly

## Database Behavior

### DB Deduplication
When the client sends the same person (same client_id) within 8 seconds:
- **New**: A new PersonActivity record is created if no matching client_id found
- **Update**: The most recent PersonActivity for that client_id is updated with new data
- **Effect**: Prevents explosion of duplicate records for continuous monitoring

### Example Session
```
Frame 1: Person 1 standing → creates PersonActivity (standing, 81%)
Frame 2: Person 1 still standing → updates existing record (standing, 82%)
Frame 3: Person 1 shifts to sitting → updates existing record (sitting, 75%)
Frame 4: New person appears → creates new PersonActivity for person 2
```

## Files Modified
1. `activities/views.py` - Updated `get_activities()` and `pose_predict()`
2. `activities/templates/activities/real_time.html` - Enhanced client-side tracking and response mapping

## Next Recommendations

### Short-term
- ✓ Activity outputs showing (DONE - this fix)
- Test with real live camera feed
- Monitor for any timing/synchronization issues
- Tune confidence thresholds if needed

### Medium-term
- Add per-person tracking to maintain consistent IDs across longer sessions
- Implement more robust pose matching (multi-keypoint similarity)
- Replace PoseNet with MoveNet for better pose quality

### Long-term
- Train a temporal model (LSTM/CNN) on pose sequences for higher accuracy
- Implement a proper person re-identification system
- Add analytics and historical reporting

## Testing Files Created
- `test_pose_debug.py` - Basic endpoint testing
- `test_live_workflow.py` - Simulates real-time workflow
- `test_multi_person_ui.py` - Tests multi-person scenarios

Run tests with:
```bash
python test_pose_debug.py
python test_live_workflow.py
python test_multi_person_ui.py
python test_multi_sim.py
python test_prediction_flow.py
```

All tests should pass with ✓ SUCCESS markers.
