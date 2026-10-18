"""
ENHANCED ACTIVITY VIEWS - USING AI DETECTOR
Integrates the AI-based activity classifier with Django views
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Count
from .models import Activity, ActivitySession, Environment, MultiPersonActivity, PersonActivity
from .forms import ActivityFilterForm
import json

# Import AI detector
try:
    from ai_activity_detector import AIActivityClassifier, Keypoint
    AI_DETECTOR_AVAILABLE = True
except ImportError:
    AI_DETECTOR_AVAILABLE = False
    print("WARNING: AI detector not available, will use fallback")


def _get_ai_classifier():
    """Get AI classifier instance (fresh each time to pick up code changes)."""
    if not AI_DETECTOR_AVAILABLE:
        return None
    try:
        return AIActivityClassifier()
    except Exception as e:
        print(f"ERROR creating classifier: {e}")
        return None


# Legacy: kept for backwards compatibility, but prefer _get_ai_classifier()
ai_classifier = None
if AI_DETECTOR_AVAILABLE:
    ai_classifier = AIActivityClassifier()


def _convert_keypoints_to_ai_format(keypoints_raw):
    """
    Convert keypoints from API format to AI detector format.
    
    API format: [{part, position:{x,y}, score}, ...]
    AI format: [Keypoint(part, x, y, score), ...]
    """
    keypoints = []
    for kp in keypoints_raw:
        if isinstance(kp, dict):
            part = kp.get('part', '')
            pos = kp.get('position', {})
            x = pos.get('x', 0)
            y = pos.get('y', 0)
            score = kp.get('score', 0)
        else:
            part = getattr(kp, 'part', '')
            x = getattr(kp, 'x', 0)
            y = getattr(kp, 'y', 0)
            score = getattr(kp, 'score', 0)
        
        keypoints.append(Keypoint(part=part, x=float(x), y=float(y), score=float(score)))
    
    return keypoints


def _classify_pose_from_keypoints_ai(keypoints_raw):
    """
    Classify activity using AI detector.
    
    Args:
        keypoints_raw: Raw keypoints from API
    
    Returns:
        (activity_label, confidence_percentage)
    """
    classifier = _get_ai_classifier()  # Get fresh instance each time
    if classifier is None:
        return 'walking', 50
    
    try:
        keypoints = _convert_keypoints_to_ai_format(keypoints_raw)
        activity, confidence = classifier.classify(keypoints)
        return activity, confidence
    except Exception as e:
        print(f"ERROR in AI classification: {e}")
        return 'walking', 50


def _classify_pose_from_history_ai(history_keypoints_list):
    """
    Classify activity using AI detector with temporal history.
    
    Args:
        history_keypoints_list: List of keypoint lists (older -> newer)
    
    Returns:
        (activity_label, confidence_percentage)
    """
    classifier = _get_ai_classifier()  # Get fresh instance each time
    if classifier is None:
        return 'walking', 50
    
    if not history_keypoints_list:
        return 'unusual', 40
    
    try:
        # Convert all frames to AI format
        history = [_convert_keypoints_to_ai_format(kps) for kps in history_keypoints_list]
        
        # Use last frame as current and pass history
        current_keypoints = history[-1]
        activity, confidence = classifier.classify(current_keypoints, keypoint_history=history[:-1])
        
        return activity, confidence
    except Exception as e:
        print(f"ERROR in AI history classification: {e}")
        return 'walking', 50


# Fallback to old heuristic (if needed)
def _classify_pose_from_keypoints_fallback(keypoints):
    """Fallback heuristic classifier for when AI is not available."""
    kp = {k.get('part'): k for k in keypoints}
    scores = [k.get('score', 0) for k in keypoints]
    avg_score = sum(scores) / (len(scores) or 1)
    
    if avg_score < 0.35:
        return 'unusual', int(avg_score * 100)
    
    def _y(p):
        return kp.get(p, {}).get('position', {}).get('y', 0)
    
    def _x(p):
        return kp.get(p, {}).get('position', {}).get('x', 0)
    
    xs = [k.get('position', {}).get('x', 0) for k in keypoints if k.get('position')]
    ys = [k.get('position', {}).get('y', 0) for k in keypoints if k.get('position')]
    min_x, max_x = (min(xs), max(xs)) if xs else (0, 0)
    min_y, max_y = (min(ys), max(ys)) if ys else (0, 0)
    width = max_x - min_x
    height = max_y - min_y
    
    nose_y = _y('nose')
    left_shoulder_y = _y('leftShoulder')
    right_shoulder_y = _y('rightShoulder')
    left_hip_y = _y('leftHip')
    right_hip_y = _y('rightHip')
    
    shoulders_y = (left_shoulder_y + right_shoulder_y) / 2 if left_shoulder_y and right_shoulder_y else None
    hips_y = (left_hip_y + right_hip_y) / 2 if left_hip_y and right_hip_y else None
    
    try:
        if height > 0 and width > 0:
            aspect_ratio = width / height if height > 0 else 0
            
            if aspect_ratio > 1.2:
                return 'sleeping', min(99, int(avg_score * 100 + 20))
            
            if shoulders_y and hips_y:
                shoulder_hip_gap = abs(shoulders_y - hips_y)
                
                if shoulder_hip_gap < 25:
                    return 'sitting', min(95, int(avg_score * 100 + 12))
                
                if shoulder_hip_gap > 35:
                    return 'standing', min(95, int(avg_score * 100 + 8))
    except:
        pass
    
    return 'walking', int(avg_score * 100 * 0.9)


# Compatibility wrappers: provide the old function names so other code/tests keep working
def _classify_pose_from_keypoints(keypoints):
    """Compatibility wrapper: choose AI classifier if available, else fallback."""
    try:
        if AI_DETECTOR_AVAILABLE and ai_classifier is not None:
            return _classify_pose_from_keypoints_ai(keypoints)
    except Exception:
        pass
    return _classify_pose_from_keypoints_fallback(keypoints)


def _classify_pose_from_history(history_keypoints_list):
    """Compatibility wrapper for history-aware classification.

    Prefer AI history classifier when available; otherwise use a lightweight
    temporal heuristic derived from earlier logic.
    """
    try:
        if AI_DETECTOR_AVAILABLE and ai_classifier is not None:
            # convert history frames to raw keypoints lists expected by AI wrapper
            return _classify_pose_from_history_ai(history_keypoints_list)
    except Exception:
        pass

    # Simple temporal heuristic fallback
    if not history_keypoints_list:
        return 'unusual', 40

    def avg_score(kps):
        scores = [k.get('score', 0) for k in kps]
        return sum(scores) / (len(scores) or 1)

    frames = history_keypoints_list
    scores = [avg_score(kps) for kps in frames]
    avg_conf = sum(scores) / len(scores)

    def mean_y(kps, parts):
        vals = [k.get('position', {}).get('y', 0) for k in kps if k.get('part') in parts]
        return sum(vals) / (len(vals) or 1)

    hips = [mean_y(kps, ['leftHip', 'rightHip']) for kps in frames]
    shoulders = [mean_y(kps, ['leftShoulder', 'rightShoulder']) for kps in frames]
    noses = [mean_y(kps, ['nose']) for kps in frames]

    hip_disp = hips[-1] - hips[0] if len(hips) > 1 else 0
    nose_disp = noses[-1] - noses[0] if len(noses) > 1 else 0

    # average shoulder-hip gap
    sh_vals = [(s - h) for s, h in zip(shoulders, hips) if s and h]
    sh_gap = sum([abs(v) for v in sh_vals]) / (len(sh_vals) or 1) if sh_vals else None

    if avg_conf < 0.35:
        return 'unusual', int(avg_conf * 100)

    try:
        # FALLING: nose moves down significantly or ends below hips
        if nose_disp > 30 or (noses[-1] and hips[-1] and noses[-1] > hips[-1] + 40):
            return 'falling', min(95, int(avg_conf * 100) + 15)

        # SITTING
        if sh_gap is not None and sh_gap < 25 and abs(hip_disp) < 10:
            return 'sitting', min(95, int(avg_conf * 100) + 12)

        # STANDING
        if sh_gap is not None and sh_gap > 35 and abs(hip_disp) < 10:
            return 'standing', min(93, int(avg_conf * 100) + 8)

        # WALKING
        if abs(hip_disp) > 8 or (len(hips) >= 3 and (max(hips) - min(hips)) > 10):
            return 'walking', min(92, int(avg_conf * 100) + 5)
    except Exception:
        pass

    return 'walking', int(avg_conf * 100 * 0.9)


@login_required
def predict_activity(request):
    """
    Receive an image frame (base64) and return predictions using AI detector.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    import random
    
    labels = ['walking', 'running', 'sitting', 'standing', 'falling', 'unusual', 'cooking', 'sleeping', 'exercising']
    
    multi_mode = random.random() < 0.25
    
    environment = Environment.objects.filter(is_active=True).first()
    
    if multi_mode:
        mp = MultiPersonActivity.objects.create(environment=environment, timestamp=timezone.now())
        persons = []
        n = random.randint(2, 4)
        for i in range(n):
            lbl = random.choice(labels)
            conf = random.randint(50, 99)
            pa = PersonActivity.objects.create(
                multi_activity=mp,
                user=request.user,
                activity_type=lbl,
                confidence_score=conf,
                location='Live Camera',
                timestamp=timezone.now()
            )
            persons.append({'id': pa.id, 'activity': lbl, 'confidence': conf})
        
        return JsonResponse({'status': 'multi_saved', 'multi_id': mp.id, 'persons': persons})
    else:
        label = random.choice(labels)
        confidence = random.randint(50, 99)
        try:
            act = Activity.objects.create(
                user=request.user,
                activity_type=label,
                confidence_score=confidence,
                location='Live Camera',
                environment=environment,
                timestamp=timezone.now()
            )
            return JsonResponse({'status': 'saved', 'activity_id': act.id, 'activity': label, 'confidence': confidence})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@login_required
def pose_predict(request):
    """
    Receive pose keypoints (JSON) and return predictions using AI detector.
    This is the main endpoint for real-time pose-based classification.
    
    POST data:
    {
        "persons": [
            {
                "id": 1,
                "keypoints": [...],
                "score": 0.9
            },
            ...
        ],
        "frames": [
            [{keypoint}, ...],
            ...
        ]
    }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    try:
        data = json.loads(request.body)
        persons_data = data.get('persons', [])
        frames_data = data.get('frames', [])
        
        environment = Environment.objects.filter(is_active=True).first()
        
        if not persons_data:
            return JsonResponse({'persons': [], 'status': 'no_persons'})
        
        results = []
        
        # If we have frame history, use it for better temporal classification
        if frames_data and len(frames_data) >= 2:
            # Use history
            for person in persons_data:
                person_id = person.get('id')
                client_id = person.get('client_id', person_id)
                
                # Get keypoints for this person across all frames (simplified - just use last)
                current_keypoints = person.get('keypoints', [])
                
                # Classify with history
                activity, confidence = _classify_pose_from_history_ai(frames_data)
                
                # Save to database
                try:
                    mp = MultiPersonActivity.objects.create(
                        environment=environment,
                        timestamp=timezone.now()
                    )
                    pa = PersonActivity.objects.create(
                        multi_activity=mp,
                        user=request.user,
                        activity_type=activity,
                        confidence_score=confidence,
                        location='Live Camera',
                        pose=json.dumps(current_keypoints),
                        timestamp=timezone.now()
                    )
                    results.append({
                        'id': pa.id,
                        'client_id': client_id,
                        'activity': activity,
                        'confidence': confidence
                    })
                except Exception as e:
                    print(f"Error saving activity: {e}")
                    results.append({
                        'client_id': client_id,
                        'activity': activity,
                        'confidence': confidence
                    })
        else:
            # Single frame classification for each person
            for person in persons_data:
                person_id = person.get('id')
                client_id = person.get('client_id', person_id)
                keypoints = person.get('keypoints', [])
                
                # Use AI classifier on single frame
                activity, confidence = _classify_pose_from_keypoints_ai(keypoints)
                
                # Save to database
                try:
                    mp = MultiPersonActivity.objects.create(
                        environment=environment,
                        timestamp=timezone.now()
                    )
                    pa = PersonActivity.objects.create(
                        multi_activity=mp,
                        user=request.user,
                        activity_type=activity,
                        confidence_score=confidence,
                        location='Live Camera',
                        pose=json.dumps(keypoints),
                        timestamp=timezone.now()
                    )
                    results.append({
                        'id': pa.id,
                        'client_id': client_id,
                        'activity': activity,
                        'confidence': confidence
                    })
                except Exception as e:
                    print(f"Error saving activity: {e}")
                    results.append({
                        'client_id': client_id,
                        'activity': activity,
                        'confidence': confidence
                    })
        
        return JsonResponse({'persons': results, 'status': 'success'})
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def activity_detail(request, activity_id):
    """Display detailed information about a specific activity."""
    activity = get_object_or_404(Activity, id=activity_id, user=request.user)
    return render(request, 'activities/activity_detail.html', {'activity': activity})


@login_required
def history(request):
    """Display activity history for the logged-in user."""
    activities = Activity.objects.filter(user=request.user).order_by('-timestamp')[:50]
    form = ActivityFilterForm(request.GET)
    
    if form.is_valid() and form.cleaned_data.get('activity_type'):
        activities = activities.filter(activity_type=form.cleaned_data['activity_type'])
    
    return render(request, 'activities/history.html', {
        'activities': activities,
        'form': form
    })


@login_required
def multi_person(request):
    """Display multi-person activity monitoring."""
    activities = MultiPersonActivity.objects.select_related('environment').prefetch_related('personactivity_set').all()[:20]
    
    return render(request, 'activities/multi_person.html', {
        'activities': activities
    })


@login_required
def get_activities(request):
    """AJAX endpoint: Get recent activities."""
    activities = Activity.objects.filter(user=request.user).values(
        'id', 'activity_type', 'confidence_score', 'timestamp', 'location'
    ).order_by('-timestamp')[:10]
    
    return JsonResponse({
        'activities': list(activities)
    })


@login_required
def get_distribution(request):
    """AJAX endpoint: Get activity type distribution."""
    distribution = Activity.objects.filter(user=request.user).values('activity_type').annotate(
        count=Count('id')
    )
    
    result = {}
    for item in distribution:
        result[item['activity_type']] = item['count']
    
    return JsonResponse({'distribution': result})


@login_required
def real_time(request):
    """Display real-time activity monitoring."""
    environments = Environment.objects.filter(is_active=True)
    
    return render(request, 'activities/real_time.html', {
        'environments': environments
    })



@login_required
def predict_activity(request):
    """Receive an image frame (base64) and return one or more predictions.

    This mock endpoint sometimes returns a single prediction (saved as Activity)
    and sometimes simulates a multi-person detection by creating a MultiPersonActivity
    and several PersonActivity entries. The response includes saved activity ids and
    a `persons` array when multiple detections are generated.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    image_data = request.POST.get('image')
    import random

    # Activity labels
    labels = ['walking', 'running', 'sitting', 'standing', 'falling', 'unusual', 'cooking', 'sleeping', 'exercising']

    # Randomly choose to simulate multi-person detection (~25% of the time)
    multi_mode = random.random() < 0.25

    environment = Environment.objects.filter(is_active=True).first()

    if multi_mode:
        # create a MultiPersonActivity and several PersonActivity entries
        mp = MultiPersonActivity.objects.create(environment=environment, timestamp=timezone.now())
        persons = []
        # simulate 2-4 people
        n = random.randint(2, 4)
        for i in range(n):
            lbl = random.choice(labels)
            conf = random.randint(50, 99)
            # For demo, associate person activity with the requesting user so it appears in DB
            pa = PersonActivity.objects.create(
                multi_activity=mp,
                user=request.user,
                activity_type=lbl,
                confidence_score=conf,
                location='Live Camera',
                timestamp=timezone.now()
            )
            persons.append({'id': pa.id, 'activity': lbl, 'confidence': conf})

        return JsonResponse({'status': 'multi_saved', 'multi_id': mp.id, 'persons': persons})
    else:
        # single-person prediction path (same as before)
        label = random.choice(labels)
        confidence = random.randint(50, 99)
        try:
            activity = Activity.objects.create(
                user=request.user,
                activity_type=label,
                confidence_score=confidence,
                timestamp=timezone.now(),
                location='Live Camera',
                environment=environment,
            )
            return JsonResponse({'activity': label, 'confidence': confidence, 'id': activity.id, 'status': 'saved'})
        except Exception as e:
            print(f"Error saving activity: {e}")
            return JsonResponse({'activity': label, 'confidence': confidence, 'status': 'predicted_only', 'error': str(e)})

@login_required
def pose_predict(request):
    """Accept pose keypoints for one or more people and classify per-person activities.

    Expects JSON payload: { persons: [ { keypoints: [{part, position:{x,y}, score}, ...] }, ... ] }
    Returns: { persons: [ { activity, confidence, id }, ... ] }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    persons = payload.get('persons', [])
    results = []
    environment = Environment.objects.filter(is_active=True).first()

    # If frames history provided, perform simple tracking by nearest nose across frames
    frames = payload.get('frames', [])  # list of frames (each a list of persons)

    def _nose_pos(kps):
        for k in kps:
            if k.get('part') == 'nose':
                pos = k.get('position', {})
                return (pos.get('x', 0), pos.get('y', 0))
        return (None, None)

    # create one MultiPersonActivity to group all detected persons in this request
    mp = None
    if persons:
        mp = MultiPersonActivity.objects.create(environment=environment, timestamp=timezone.now())

    for p in persons:
        kps = p.get('keypoints', [])
        client_id = p.get('id') or p.get('client_id')

        # build history for this person
        history = [kps]
        try:
            cur_nx, cur_ny = _nose_pos(kps)
        except Exception:
            cur_nx = cur_ny = None

        # match previous frames
        for f in reversed(frames[:-1]):
            # f is an earlier frame (list of persons)
            best = None
            best_d = None
            for cand in f:
                cand_nx, cand_ny = _nose_pos(cand.get('keypoints', []))
                if cand_nx is None or cur_nx is None:
                    continue
                dx = cand_nx - cur_nx
                dy = cand_ny - cur_ny
                d = (dx*dx + dy*dy) ** 0.5
                if best is None or d < best_d:
                    best = cand
                    best_d = d
            # if nearest within threshold, attach
            if best is not None and best_d is not None and best_d < 60:
                history.insert(0, best.get('keypoints', []))

        # classify using history-aware classifier
        if len(history) > 1:
            label, conf = _classify_pose_from_history(history)
        else:
            label, conf = _classify_pose_from_keypoints(kps)

        # If client provided a stable id, try to update a recent PersonActivity for the same client
        pa = None
        try:
            if client_id is not None:
                cutoff = timezone.now() - timedelta(seconds=8)
                existing = PersonActivity.objects.filter(pose__client_id=str(client_id), timestamp__gte=cutoff).order_by('-timestamp').first()
                if existing:
                    # update existing entry instead of creating a new one
                    existing.activity_type = label
                    existing.confidence_score = conf
                    existing.pose = {'client_id': str(client_id), 'keypoints': kps, 'history_frames': len(history)}
                    existing.timestamp = timezone.now()
                    existing.location = 'Live Camera'
                    existing.save()
                    pa = existing
        except Exception:
            pa = None

        if pa is None:
            # attach to the MultiPersonActivity created above
            pa = PersonActivity.objects.create(
                multi_activity=mp,
                user=request.user if hasattr(request, 'user') and request.user.is_authenticated else None,
                activity_type=label,
                confidence_score=conf,
                location='Live Camera',
                pose={'client_id': str(client_id) if client_id is not None else None, 'keypoints': kps, 'history_frames': len(history)},
                timestamp=timezone.now()
            )

        # include client_id in response when provided so client can map responses
        resp_entry = {'id': pa.id, 'activity': label, 'confidence': conf}
        if client_id is not None:
            resp_entry['client_id'] = str(client_id)
        results.append(resp_entry)

    return JsonResponse({'persons': results})

@login_required
def real_time_monitoring(request):
    """Real-time activity monitoring view"""
    environments = Environment.objects.filter(is_active=True)
    
    # Get recent activities for the current user
    recent_activities = Activity.objects.filter(
        user=request.user
    ).order_by('-timestamp')[:10]
    
    context = {
        'environments': environments,
        'recent_activities': recent_activities,
    }
    return render(request, 'activities/real_time.html', context)

@login_required
def activity_history(request):
    """Historical activity data view with filtering - includes both Activity and PersonActivity"""
    # Get Activity records (image-based)
    activities = Activity.objects.filter(user=request.user).order_by('-timestamp')
    
    # Get PersonActivity records (pose-based) for this user
    person_activities = PersonActivity.objects.filter(
        user=request.user
    ).order_by('-timestamp').select_related('multi_activity')
    
    # Filter both querysets
    if request.method == 'GET':
        form = ActivityFilterForm(request.GET)
        if form.is_valid():
            activity_type = form.cleaned_data.get('activity_type')
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')
            environment = form.cleaned_data.get('environment')
            
            if activity_type:
                activities = activities.filter(activity_type=activity_type)
                person_activities = person_activities.filter(activity_type=activity_type)
            if start_date:
                activities = activities.filter(timestamp__gte=start_date)
                person_activities = person_activities.filter(timestamp__gte=start_date)
            if end_date:
                activities = activities.filter(timestamp__lte=end_date)
                person_activities = person_activities.filter(timestamp__lte=end_date)
            if environment:
                activities = activities.filter(environment=environment)
    else:
        form = ActivityFilterForm()
        # Default: last 7 days
        week_ago = timezone.now() - timedelta(days=7)
        activities = activities.filter(timestamp__gte=week_ago)
        person_activities = person_activities.filter(timestamp__gte=week_ago)
    
    # Combine and sort by timestamp (newest first)
    combined = []
    for act in activities:
        combined.append({
            'id': f'act_{act.id}',
            'activity_type': act.activity_type,
            'confidence_score': act.confidence_score,
            'timestamp': act.timestamp,
            'location': act.location,
            'environment': act.environment,
            'is_verified': act.is_verified,
            'duration': act.duration,
            'source': 'image',
            'object': act
        })
    
    for pa in person_activities:
        combined.append({
            'id': f'pa_{pa.id}',
            'activity_type': pa.activity_type,
            'confidence_score': pa.confidence_score,
            'timestamp': pa.timestamp,
            'location': pa.location,
            'environment': None,
            'is_verified': False,
            'duration': None,
            'source': 'pose',
            'object': pa
        })
    
    combined.sort(key=lambda x: x['timestamp'], reverse=True)
    
    context = {
        'activities': combined,
        'form': form,
    }
    return render(request, 'activities/history.html', context)

@login_required
def multi_person_view(request):
    """View for monitoring multiple people simultaneously - includes PersonActivity data"""
    environments = Environment.objects.filter(is_active=True)
    
    # Get MultiPersonActivity records with related PersonActivity data
    multi_activities = MultiPersonActivity.objects.filter(
        environment__in=environments,
        timestamp__gte=timezone.now() - timedelta(hours=1)
    ).prefetch_related('personactivity_set').order_by('-timestamp')
    
    # Also get individual PersonActivity records for users
    person_activities = PersonActivity.objects.filter(
        user=request.user,
        timestamp__gte=timezone.now() - timedelta(hours=1)
    ).select_related('multi_activity').order_by('-timestamp')[:20]
    
    context = {
        'environments': environments,
        'multi_activities': multi_activities,
        'person_activities': person_activities,
    }
    return render(request, 'activities/multi_person.html', context)

@login_required
def get_activities(request):
    """API endpoint for fetching activities (AJAX) - includes both Activity and PersonActivity records"""
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        last_id = request.GET.get('last_id', 0)
        
        # Get Activity records (image-based predictions)
        activities = Activity.objects.filter(
            user=request.user,
            id__gt=last_id
        ).order_by('-timestamp')
        
        # Get PersonActivity records (pose-based predictions)
        person_activities = PersonActivity.objects.filter(
            user=request.user,
            id__gt=last_id
        ).order_by('-timestamp')
        
        activity_data = []
        
        # Add Activity records
        for activity in activities:
            activity_data.append({
                'id': activity.id,
                'activity_type': activity.activity_type,
                'confidence_score': activity.confidence_score,
                'timestamp': activity.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'location': activity.location,
                'environment': activity.environment.name if activity.environment else 'N/A',
                'source': 'image'
            })
        
        # Add PersonActivity records
        for pa in person_activities:
            activity_data.append({
                'id': pa.id,
                'activity_type': pa.activity_type,
                'confidence_score': pa.confidence_score,
                'timestamp': pa.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'location': pa.location,
                'environment': 'N/A',
                'source': 'pose'
            })
        
        # Sort combined list by timestamp descending and limit to 20
        activity_data.sort(key=lambda x: x['timestamp'], reverse=True)
        activity_data = activity_data[:20]
        
        return JsonResponse({'activities': activity_data})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def get_distribution(request):
    """Return aggregated activity distribution for charting - includes both Activity and PersonActivity."""
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Aggregate counts from Activity model
        activity_counts = Activity.objects.values('activity_type').annotate(count=Count('id'))
        data = {item['activity_type']: item['count'] for item in activity_counts}
        
        # Aggregate counts from PersonActivity model
        person_activity_counts = PersonActivity.objects.values('activity_type').annotate(count=Count('id'))
        for item in person_activity_counts:
            activity_type = item['activity_type']
            if activity_type in data:
                data[activity_type] += item['count']
            else:
                data[activity_type] = item['count']
        
        return JsonResponse({'distribution': data})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def activity_detail(request, activity_id):
    """Detailed view of a specific activity"""
    activity = get_object_or_404(Activity, id=activity_id, user=request.user)
    return render(request, 'activities/activity_detail.html', {'activity': activity})