import json

from django.shortcuts import render
from django.http import (
    JsonResponse,
    StreamingHttpResponse,
)
from django.views.decorators.http import (
    require_GET,
    require_POST,
)
from django.views.decorators.csrf import ensure_csrf_cookie

from .services import SalesSimulatorService


service = SalesSimulatorService()


# ============================================================
# DASHBOARD
# ============================================================

@require_GET
@ensure_csrf_cookie
def dashboard(request):

    return render(
        request,
        "dashboard/dashboard.html",
    )


# ============================================================
# TRAINING SETUP
# ============================================================

@require_GET
@ensure_csrf_cookie
def training_setup(request):

    return render(
        request,
        "setup/setup.html",
    )


# ============================================================
# TRAINING PAGE
# ============================================================

@require_GET
@ensure_csrf_cookie
def training(request, session_id):

    session = service.get_session(
        session_id
    )

    if not session:

        return render(
            request,
            "setup/setup.html",
        )

    return render(
        request,
        "training/training.html",
        {
            "session_id": session_id,
        },
    )


# ============================================================
# HISTORY PAGE
# ============================================================

@require_GET
@ensure_csrf_cookie
def history(request):

    sessions = service.get_recent_sessions(
        limit=50
    )

    return render(
        request,
        "history/history.html",
        {
            "sessions": sessions,
        },
    )


# ============================================================
# SESSION ANALYSIS PAGE
# ============================================================

@require_GET
@ensure_csrf_cookie
def session_analysis(
    request,
    session_id,
):

    try:

        session = service.get_session(
            session_id
        )

        if not session:

            return render(
                request,
                "analysis/session_analysis.html",
                {
                    "error": "Session not found.",
                },
            )

        if session["status"] != "completed":

            return render(
                request,
                "analysis/session_analysis.html",
                {
                    "error": (
                        "Only completed sessions "
                        "can be analyzed."
                    ),
                },
            )

        # ----------------------------------------------------
        # IMPORTANT
        #
        # DO NOT CALL OLLAMA HERE.
        #
        # Only check whether analysis already exists.
        # ----------------------------------------------------

        analysis = service.get_session_analysis(
            session_id
        )

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

        print(
            f"SESSION ANALYSIS PAGE ERROR: {exc}"
        )

        return render(
            request,
            "analysis/session_analysis.html",
            {
                "error": str(exc),
            },
        )


# ============================================================
# GENERATE SESSION ANALYSIS
# ============================================================

@require_POST
def generate_session_analysis(
    request,
    session_id,
):

    try:

        session = service.get_session(
            session_id
        )

        if not session:

            return JsonResponse(
                {
                    "error": "Session not found.",
                },
                status=404,
            )

        if session["status"] != "completed":

            return JsonResponse(
                {
                    "error": (
                        "Only completed sessions "
                        "can be analyzed."
                    ),
                },
                status=400,
            )

        # ----------------------------------------------------
        # DB FIRST
        #
        # If report already exists, NEVER call Ollama.
        # ----------------------------------------------------

        existing = service.get_session_analysis(
            session_id
        )

        if existing:

            return JsonResponse(
                {
                    "status": "completed",
                    "analysis": existing,
                }
            )

        print(
            f"[ANALYZER] Starting analysis: {session_id}"
        )

        analysis = service.analyze_session(
            session_id
        )

        print(
            f"[ANALYZER] Analysis completed: {session_id}"
        )

        return JsonResponse(
            {
                "status": "completed",
                "analysis": analysis,
            }
        )

    except Exception as exc:

        print(
            f"[ANALYZER] ERROR: {exc}"
        )

        return JsonResponse(
            {
                "status": "error",
                "error": str(exc),
            },
            status=500,
        )


# ============================================================
# SESSION ANALYSIS STATUS
# ============================================================

@require_GET
def session_analysis_status(
    request,
    session_id,
):

    try:

        analysis = service.get_session_analysis(
            session_id
        )

        if analysis:

            return JsonResponse(
                {
                    "status": "completed",
                    "analysis": analysis,
                }
            )

        return JsonResponse(
            {
                "status": "pending",
            }
        )

    except Exception as exc:

        print(
            f"[ANALYZER STATUS ERROR] {exc}"
        )

        return JsonResponse(
            {
                "status": "error",
                "error": str(exc),
            },
            status=500,
        )


# ============================================================
# GET PERSONALITIES
# ============================================================

@require_GET
def get_personalities(request):

    personalities = service.get_personalities()

    return JsonResponse(
        {
            "personalities": personalities,
        }
    )


# ============================================================
# CREATE SESSION
# ============================================================

@require_POST
def create_session(request):

    try:

        body = json.loads(
            request.body
        )

        personality = (
            body.get(
                "personality",
                "",
            )
            .strip()
            .lower()
        )

        difficulty = (
            body.get(
                "difficulty",
                "medium",
            )
            .strip()
            .lower()
        )

        focus_area = body.get(
            "focus_area"
        )

        session_length = (
            body.get(
                "session_length",
                "quick",
            )
            .strip()
            .lower()
        )

        if not personality:

            return JsonResponse(
                {
                    "error":
                        "Personality is required.",
                },
                status=400,
            )

        result = service.create_session(
            personality=personality,
            difficulty=difficulty,
            focus_area=focus_area,
            session_length=session_length,
        )

        return JsonResponse(
            result
        )

    except json.JSONDecodeError:

        return JsonResponse(
            {
                "error": "Invalid JSON.",
            },
            status=400,
        )

    except ValueError as exc:

        return JsonResponse(
            {
                "error": str(exc),
            },
            status=400,
        )

    except Exception as exc:

        print(
            f"CREATE SESSION ERROR: {exc}"
        )

        return JsonResponse(
            {
                "error":
                    "Failed to create session.",
            },
            status=500,
        )


# ============================================================
# GET SESSION DETAILS
# ============================================================

@require_GET
def get_session_details(
    request,
    session_id,
):

    session = service.get_session(
        session_id
    )

    if not session:

        return JsonResponse(
            {
                "error": "Session not found.",
            },
            status=404,
        )

    return JsonResponse(
        session
    )


# ============================================================
# GET SESSION MESSAGES
# ============================================================

@require_GET
def get_session_messages(
    request,
    session_id,
):

    messages = service.get_history(
        session_id
    )

    return JsonResponse(
        {
            "messages": messages,
        }
    )


# ============================================================
# GET RECENT SESSIONS
# ============================================================

@require_GET
def get_recent_sessions(request):

    sessions = service.get_recent_sessions(
        limit=50
    )

    return JsonResponse(
        {
            "sessions": sessions,
        }
    )


# ============================================================
# GET ACTIVE SESSIONS
# ============================================================

@require_GET
def get_active_sessions(request):

    sessions = service.get_active_sessions(
        limit=50
    )

    return JsonResponse(
        {
            "sessions": sessions,
        }
    )


# ============================================================
# CHAT
# ============================================================

@require_POST
def chat(
    request,
    session_id,
):

    try:

        body = json.loads(
            request.body
        )

        user_message = (
            body.get(
                "message",
                "",
            )
            .strip()
        )

        if not user_message:

            return JsonResponse(
                {
                    "error":
                        "Message cannot be empty.",
                },
                status=400,
            )

    except json.JSONDecodeError:

        return JsonResponse(
            {
                "error": "Invalid JSON.",
            },
            status=400,
        )

    def event_stream():

        for event in service.chat_stream(
            session_id=session_id,
            user_message=user_message,
        ):

            yield (
                json.dumps(
                    event,
                    ensure_ascii=False,
                )
                + "\n"
            )

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
def end_session(
    request,
    session_id,
):

    service.end_session(
        session_id
    )

    return JsonResponse(
        {
            "status": "completed",
        }
    )