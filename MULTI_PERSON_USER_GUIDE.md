# 📊 MULTI-PERSON ACTIVITY MONITORING - USER GUIDE

## What Is Multi-Person View?

The Multi-Person Activity Monitoring page shows **all people detected in an environment**, including:
- ✅ Named persons (with profile pictures if available)
- ✅ Unidentified persons (detected but not logged in)
- ✅ Their detected activities (Walking, Sitting, Standing, Sleeping, etc.)
- ✅ Confidence scores for each detection
- ✅ Overall activity distribution charts

---

## 🚀 Getting Started

### Step 1: Start the Application
```bash
python manage.py runserver
```

### Step 2: Login
- Go to: `http://localhost:8000/login/`
- Enter your username and password
- Click "Login"

### Step 3: Go to Multi-Person View
- Click **Activities** in navigation menu
- Click **Multi-Person Monitoring**
- Or directly visit: `http://localhost:8000/activities/multi-person/`

---

## 📍 Page Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  MULTI-PERSON ACTIVITY MONITORING                               │
│  [Refresh Button]  [Auto-Refresh Toggle]                        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ SELECT ENVIRONMENT                                               │
├─────────────────────────────────────────────────────────────────┤
│ ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│ │ 🏢 Living    │  │ 🏢 Bedroom   │  │ 🏢 Kitchen   │            │
│ │ Room         │  │              │  │              │            │
│ │ 4 zones      │  │ 4 zones      │  │ 4 zones      │            │
│ │ ✓ Active     │  │ ✓ Active     │  │ ✓ Active     │            │
│ └──────────────┘  └──────────────┘  └──────────────┘            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ CURRENT MULTI-PERSON ACTIVITIES         ⭕ Monitoring           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ ┌──────────────────────────────────────┐                        │
│ │ 📍 Living Room - 2 minutes ago       │                        │
│ ├──────────────────────────────────────┤                        │
│ │ [Profile] John Doe                   │                        │
│ │           👤 WALKING  85.0% confidence                        │
│ │           📍 Near TV                 │                        │
│ │                                      │                        │
│ │ [?] Unidentified Person              │                        │
│ │      👤 SITTING  92.0% confidence    │                        │
│ │      📍 On Couch                     │                        │
│ └──────────────────────────────────────┘                        │
│                                                                  │
│ ┌──────────────────────────────────────┐                        │
│ │ 📍 Kitchen - 5 minutes ago           │                        │
│ ├──────────────────────────────────────┤                        │
│ │ [?] Unidentified Person              │                        │
│ │      👤 STANDING  78.0% confidence   │                        │
│ │      📍 Counter                      │                        │
│ └──────────────────────────────────────┘                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ ACTIVITY DISTRIBUTION    │ ACTIVITY TIMELINE                    │
├──────────────────────────┼──────────────────────────────────────┤
│      📊 PIE CHART        │     📈 LINE CHART                    │
│     Walking    Sitting   │     ▲ Activities                     │
│     30%        25%       │     │      ╱╲                        │
│     Sleeping   Standing  │     │    ╱  ╲╱╲                    │
│     25%        20%       │     └─────────────────►              │
│                          │     Time →                           │
└──────────────────────────┴──────────────────────────────────────┘
```

---

## 🎮 How to Use

### 1. **Select an Environment**
   - Click any environment card to view activities in that location
   - The selected environment has a **blue border**
   - Activities refresh to show detections in that environment

### 2. **View Activity Cards**
   - Each card shows one multi-person activity detection event
   - Card shows:
     - **Environment name** and **time detected**
     - **List of persons** detected in that event
     - For each person:
       - Profile picture (if logged in) or **?** (if unidentified)
       - Name or **"Unidentified Person"** badge
       - **Activity type** (WALKING, SITTING, etc.)
       - **Confidence score** (how sure the system is)
       - **Location** (where in the environment)

### 3. **Check Activity Charts**
   - **Pie Chart (left)**: Shows breakdown of all activities detected
     - Example: 30% Walking, 25% Sitting, etc.
   - **Timeline Chart (right)**: Shows activity frequency over time
     - Example: How many activities detected each hour

### 4. **Enable Auto-Refresh**
   - Click **"Auto Refresh"** button to enable auto-updating
   - Page will refresh every 5 seconds
   - Button changes to **"Pause"** when active
   - Click again to stop auto-refreshing

### 5. **Manual Refresh**
   - Click **"Refresh"** button to immediately update data
   - Useful if auto-refresh is off

---

## 🧑‍💼 Understanding Identified vs. Unidentified Persons

### Identified Person
```
✅ Has a login account in the system
✅ Has a profile picture
✅ Shows their name
✅ Example: "John Doe" with profile image
```

### Unidentified Person  
```
❓ No login account (detected by camera)
❓ No profile picture available
❓ Shows "Unidentified Person" badge
❓ May be a visitor or guest
```

---

## 📊 What the Data Means

### Activity Types
| Type | What It Means |
|------|--------------|
| **WALKING** | Person is moving around |
| **RUNNING** | Person is moving fast |
| **SITTING** | Person is seated |
| **STANDING** | Person is standing still |
| **SLEEPING** | Person is lying down/sleeping |
| **FALLING** | Person has fallen |
| **UNUSUAL** | Unexpected activity |

### Confidence Score
```
90-100% = Very confident (good detection)
70-89%  = Confident (good detection)
50-69%  = Somewhat confident (may be wrong)
<50%    = Low confidence (probably wrong)
```

**Higher is better!** ✅

### Timeline in Cards
```
"2 minutes ago"   = Detected 2 minutes ago (recent)
"1 hour ago"      = Detected 1 hour ago (less recent)
"3 hours ago"     = Detected 3 hours ago (old)
```

---

## ⚙️ Settings & Controls

### Refresh Button
- **Purpose**: Update the page immediately
- **When to use**: Want to see latest data right now
- **Time**: Updates in < 1 second

### Auto-Refresh Toggle
- **Off** = Manual refresh only
- **On** = Auto-updates every 5 seconds
- **Status indicator**: Changes color when running
  - 🟢 Green = Online/Monitoring
  - 🔴 Red = Offline/Error

### Environment Selection
- **Purpose**: Filter activities by location
- **How**: Click any environment card
- **Visual**: Selected environment gets blue border
- **Effect**: Shows only activities from that environment

---

## 🎯 Common Scenarios

### Scenario 1: Two People Detected
```
Event: Multi-Person Activity in Living Room

Person 1:  ✅ John Doe (Identified)
           Activity: WALKING
           Confidence: 87%
           Location: Near door

Person 2:  ❓ Unidentified Person
           Activity: SITTING
           Confidence: 92%
           Location: On couch

Expected: Both shown in same activity card
```

### Scenario 2: Monitoring for Safety
```
Goal: Detect if someone falls
Action: 
  1. Go to multi-person view
  2. Enable auto-refresh
  3. Watch for "FALLING" activities
  4. Act immediately if detected
```

### Scenario 3: Activity Tracking
```
Goal: Count how many people walked through
Action:
  1. Select environment
  2. Check distribution pie chart
  3. Count WALKING percentage/count
  4. Note the timeline
```

---

## 🔍 Troubleshooting

### Problem: No Activities Shown
**Cause:** No detections in that environment yet
**Solution:** 
- Try different environment
- Enable auto-refresh to wait for new detections
- Check real-time monitoring page instead

### Problem: "Unidentified Person" Everywhere
**Cause:** Camera detecting but users not logged in
**Solution:**
- Have users login to the system
- System will identify them in future detections
- Ask unidentified persons to register

### Problem: Charts Not Loading
**Cause:** No activity data available
**Solution:**
- Wait for some activities to be detected
- Go to real-time monitoring page first
- Refresh the page

### Problem: Page Not Updating
**Cause:** Auto-refresh might be off
**Solution:**
- Click "Auto-Refresh" button to turn on
- Or click "Refresh" button manually
- Check browser console for errors

### Problem: Profile Pictures Not Showing
**Cause:** User profile not fully set up
**Solution:**
- Go to Profile page
- Upload a profile picture
- Return to multi-person view (now shows picture)

---

## 📱 Mobile Use

The page is **mobile-friendly**!

✅ Use on phones and tablets
✅ Touch to select environments
✅ Swipe to scroll through activities
✅ Charts resize for smaller screens

---

## 🔐 Privacy Notes

- **Identified Persons**: Only shown if they're logged in
- **Unidentified Persons**: Shown as "Unidentified Person" (privacy protected)
- **Activity Data**: Stored securely in database
- **Profile Pictures**: Only shown if user uploaded them

---

## 💡 Tips & Tricks

### 💾 For Better Results:
1. **Keep camera aligned** - Better detections
2. **Good lighting** - More accurate predictions
3. **Clear area** - Less confusion with objects
4. **Update profiles** - Upload pictures for identification

### ⚡ For Performance:
1. **Don't leave auto-refresh on 24/7** - Save resources
2. **Limit environments selected** - Faster updates
3. **Clear old data periodically** - Keep database fast

### 🎯 For Monitoring:
1. **Set multiple environments** - Monitor whole house
2. **Check timeline chart** - See patterns
3. **Note peak times** - When most activity occurs

---

## 📞 Support

If you have questions:
1. Check the **troubleshooting** section above
2. Review **real-time monitoring** for live debugging
3. Check **admin panel** for system status
4. Look at **activity history** for past data

---

**Status: Multi-Person View Working ✅**
**Last Updated: November 2025**
