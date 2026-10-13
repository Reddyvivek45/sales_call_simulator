import json
from functools import wraps

from django.shortcuts import render, redirect
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .services import SalesSimulatorService
from . import voice_service


service = SalesSimulatorService()


# ============================================================
# AUTH HELPERS
# ============================================================

def api_login_required(view_func):
    """
    Like @login_required, but returns a 401 JSON response
    instead of redirecting — for API endpoints the frontend
    reads with fetch(), where a redirect to an HTML login
    page would break JSON parsing.
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:

            return JsonResponse(
                {"error": "Authentication required."},
                status=401,
            )

        return view_func(request, *args, **kwargs)

    return wrapper


def _owns_session(request, session):
    """
    True only if the session exists and belongs to the
    current user. Returning 404 (not 403) for both "doesn't
    exist" and "belongs to someone else" avoids leaking
    which session IDs are real.
    """

    return (
        session is not None
        and session.get("user_id") == request.user.id
    )


# ============================================================
# LOGIN / LOGOUT
# ============================================================

@require_GET
@ensure_csrf_cookie
def login_page(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    return render(request, "auth/login.html")


@require_POST
def login_submit(request):

    username = request.POST.get("username", "").strip()
    password = request.POST.get("password", "")

    user = authenticate(
        request,
        username=username,
        password=password,
    )

    if user is None:

        return render(
            request,
            "auth/login.html",
            {"error": "Invalid username or password."},
        )

    login(request, user)

    return redirect("dashboard")


@require_POST
def logout_view(request):

    logout(request)

    return redirect("login")


# ============================================================
# DASHBOARD
# ============================================================

@require_GET
@login_required
@ensure_csrf_cookie
def dashboard(request):

    return render(request, "dashboard/dashboard.html")


@require_GET
@api_login_required
def dashboard_data(request):

    try:

        data = service.get_dashboard_data(
            user_id=request.user.id
        )

        return JsonResponse(data)

    except Exception as exc:

        print(f"[DASHBOARD DATA ERROR] {exc}")

        return JsonResponse(
            {"error": "Failed to load dashboard data."},
            status=500,
        )


# ============================================================
# TRAINING SETUP
# ============================================================

@require_GET
@login_required
@ensure_csrf_cookie
def training_setup(request):

    return render(request, "setup/setup.html")


# ============================================================
# TRAINING PAGE
# ============================================================

@require_GET
@login_required
@ensure_csrf_cookie
def training(request, session_id):

    session = service.get_session(session_id)

    if not _owns_session(request, session):
        return render(request, "setup/setup.html")

    return render(
        request,
        "training/training.html",
        {"session_id": session_id},
    )


# ============================================================
# HISTORY PAGE
# ============================================================

@require_GET
@login_required
@ensure_csrf_cookie
def history(request):

    sessions = service.get_history_sessions(
        user_id=request.user.id
    )

    return render(request, "history/history.html", {"sessions": sessions})


# ============================================================
# SESSION ANALYSIS PAGE
# ============================================================

@require_GET
@login_required
@ensure_csrf_cookie
def session_analysis(request, session_id):

    try:

        session = service.get_session(session_id)

        if not _owns_session(request, session):

            return render(
                request,
                "analysis/session_analysis.html",
                {"error": "Session not found."},
            )

        if session["status"] != "completed":

            return render(
                request,
                "analysis/session_analysis.html",
                {"error": "Only completed sessions can be analyzed."},
            )

        analysis = service.get_session_analysis(session_id)

        return render(
            request,
            "analysis/session_analysis.html",
            {
                "session": session,
                "analysis": analysis,
                "analysis_exists": analysis is not None,
            },
        )

    except Exception as exc:

        print(f"SESSION ANALYSIS PAGE ERROR: {exc}")

        return render(
            request,
            "analysis/session_analysis.html",
            {"error": str(exc)},
        )


# ============================================================
# GENERATE SESSION ANALYSIS
# ============================================================

@require_POST
@api_login_required
def generate_session_analysis(request, session_id):

    try:

        session = service.get_session(session_id)

        if not _owns_session(request, session):

            return JsonResponse(
                {"error": "Session not found."},
                status=404,
            )

        if session["status"] != "completed":

            return JsonResponse(
                {"error": "Only completed sessions can be analyzed."},
                status=400,
            )

        existing = service.get_session_analysis(session_id)

        if existing:

            return JsonResponse(
                {"status": "completed", "analysis": existing}
            )

        print(f"[ANALYZER] Starting analysis: {session_id}")

        analysis = service.analyze_session(session_id)

        print(f"[ANALYZER] Analysis completed: {session_id}")

        return JsonResponse(
            {"status": "completed", "analysis": analysis}
        )

    except Exception as exc:

        print(f"[ANALYZER] ERROR: {exc}")

        return JsonResponse(
            {"status": "error", "error": str(exc)},
            status=500,
        )


# ============================================================
# SESSION ANALYSIS STATUS
# ============================================================

@require_GET
@api_login_required
def session_analysis_status(request, session_id):

    try:

        session = service.get_session(session_id)

        if not _owns_session(request, session):

            return JsonResponse(
                {"error": "Session not found."},
                status=404,
            )

        analysis = service.get_session_analysis(session_id)

        if analysis:

            return JsonResponse(
                {"status": "completed", "analysis": analysis}
            )

        return JsonResponse({"status": "pending"})

    except Exception as exc:

        print(f"[ANALYZER STATUS ERROR] {exc}")

        return JsonResponse(
            {"status": "error", "error": str(exc)},
            status=500,
        )


# ============================================================
# GET PERSONALITIES
# ============================================================

@require_GET
@api_login_required
def get_personalities(request):

    personalities = service.get_personalities()

    return JsonResponse({"personalities": personalities})


# ============================================================
# CREATE SESSION
# ============================================================

@require_POST
@api_login_required
def create_session(request):

    try:

        body = json.loads(request.body)

        personality = body.get("personality", "").strip().lower()
        difficulty = body.get("difficulty", "medium").strip().lower()
        focus_area = body.get("focus_area")
        session_length = body.get("session_length", "quick").strip().lower()
        mode = body.get("mode", "chat").strip().lower() 

        if not personality:

            return JsonResponse(
                {"error": "Personality is required."},
                status=400,
            )

        result = service.create_session(
            personality=personality,
            difficulty=difficulty,
            focus_area=focus_area,
            session_length=session_length,
            user_id=request.user.id,         # NEW
            mode=mode,
        )

        return JsonResponse(result)

    except json.JSONDecodeError:

        return JsonResponse({"error": "Invalid JSON."}, status=400)

    except ValueError as exc:

        return JsonResponse({"error": str(exc)}, status=400)

    except Exception as exc:

        print(f"CREATE SESSION ERROR: {exc}")

        return JsonResponse(
            {"error": "Failed to create session."},
            status=500,
        )


# ============================================================
# GET SESSION DETAILS
# ============================================================

@require_GET
@api_login_required
def get_session_details(request, session_id):

    session = service.get_session(session_id)

    if not _owns_session(request, session):

        return JsonResponse(
            {"error": "Session not found."},
            status=404,
        )

    return JsonResponse(session)


# ============================================================
# GET SESSION MESSAGES
# ============================================================

@require_GET
@api_login_required
def get_session_messages(request, session_id):

    session = service.get_session(session_id)

    if not _owns_session(request, session):

        return JsonResponse(
            {"error": "Session not found."},
            status=404,
        )

    messages = service.get_history(session_id)

    return JsonResponse({"messages": messages})


# ============================================================
# GET RECENT SESSIONS
# ============================================================

@require_GET
@api_login_required
def get_recent_sessions(request):

    sessions = service.get_recent_sessions(
        user_id=request.user.id,
        limit=50,
    )

    return JsonResponse({"sessions": sessions})


# ============================================================
# GET ACTIVE SESSIONS
# ============================================================

@require_GET
@api_login_required
def get_active_sessions(request):

    sessions = service.get_active_sessions(
        user_id=request.user.id,
        limit=50,
    )

    return JsonResponse({"sessions": sessions})


# ============================================================
# CHAT
# ============================================================

@require_POST
@api_login_required
def chat(request, session_id):

    session = service.get_session(session_id)

    if not _owns_session(request, session):

        return JsonResponse(
            {"error": "Session not found."},
            status=404,
        )

    try:

        body = json.loads(request.body)

        user_message = body.get("message", "").strip()

        if not user_message:

            return JsonResponse(
                {"error": "Message cannot be empty."},
                status=400,
            )

    except json.JSONDecodeError:

        return JsonResponse({"error": "Invalid JSON."}, status=400)

    def event_stream():

        for event in service.chat_stream(
            session_id=session_id,
            user_message=user_message,
        ):

            yield json.dumps(event, ensure_ascii=False) + "\n"

    response = StreamingHttpResponse(
        event_stream(),
        content_type="application/x-ndjson",
    )

    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"

    return response


# ============================================================
# END SESSION
# ============================================================

@require_POST
@api_login_required
def end_session(request, session_id):

    session = service.get_session(session_id)

    if not _owns_session(request, session):

        return JsonResponse(
            {"error": "Session not found."},
            status=404,
        )

    service.end_session(session_id)

    return JsonResponse({"status": "completed"})


# ============================================================
# SIMULATION PAGE (VOICE)
# ============================================================

@require_GET
@login_required
@ensure_csrf_cookie
def simulation(request, session_id):

    session = service.get_session(session_id)

    if not _owns_session(request, session):
        return render(request, "setup/setup.html")

    return render(
        request,
        "simulation/simulation.html",
        {"session_id": session_id},
    )


# ============================================================
# VOICE MODEL STATUS / LOAD / STT / TTS
# ============================================================

@require_GET
@api_login_required
def voice_status(request):

    status = voice_service.get_model_status()

    return JsonResponse(status)


@require_POST
@api_login_required
def voice_load_models(request):

    try:

        status = voice_service.load_all_models()

        return JsonResponse(status)

    except Exception as exc:

        print(f"[VOICE LOAD ERROR] {exc}")

        return JsonResponse({"error": str(exc)}, status=500)


@require_POST
@api_login_required
def voice_stt(request):

    try:

        audio_file = request.FILES.get("audio")

        if not audio_file:

            return JsonResponse(
                {"error": "No audio file uploaded."},
                status=400,
            )

        audio_bytes = audio_file.read()

        result = voice_service.transcribe_audio(audio_bytes)

        return JsonResponse(result)

    except Exception as exc:

        print(f"[STT ERROR] {exc}")

        return JsonResponse({"error": str(exc)}, status=500)


@require_POST
@api_login_required
def voice_tts(request):

    try:

        body = json.loads(request.body)

        text = body.get("text", "").strip()

        if not text:

            return JsonResponse({"error": "No text provided."}, status=400)

        audio_bytes = voice_service.synthesize_speech(text)

        from django.http import HttpResponse

        response = HttpResponse(audio_bytes, content_type="audio/wav")

        response["Content-Disposition"] = 'inline; filename="speech.wav"'

        return response

    except json.JSONDecodeError:

        return JsonResponse({"error": "Invalid JSON."}, status=400)

    except Exception as exc:

        print(f"[TTS ERROR] {exc}")

        return JsonResponse({"error": str(exc)}, status=500)