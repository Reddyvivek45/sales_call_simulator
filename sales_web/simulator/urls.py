from django.urls import path
from . import views


urlpatterns = [
    path(
        "login/",
        views.login_page,
        name="login",
    ),

    path(
        "login/submit/",
        views.login_submit,
        name="login_submit",
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout",
    ),

    path(
        "",
        views.dashboard,
        name="dashboard",
    ),
    path(
        "dashboard/data/",
        views.dashboard_data,
        name="dashboard_data",
    ),


    path(
        "training/setup/",
        views.training_setup,
        name="training_setup",
    ),

    path(
        "training/<str:session_id>/",
        views.training,
        name="training",
    ),

    path(
        "history/",
        views.history,
        name="history",
    ),

    # ========================================================
    # ANALYSIS
    # ========================================================

    path(
        "analysis/<str:session_id>/",
        views.session_analysis,
        name="session_analysis",
    ),

    path(
        "analysis/<str:session_id>/generate/",
        views.generate_session_analysis,
        name="generate_session_analysis",
    ),

    path(
        "analysis/<str:session_id>/status/",
        views.session_analysis_status,
        name="session_analysis_status",
    ),
   

    # ========================================================
    # APIs
    # ========================================================

    path(
        "api/personalities/",
        views.get_personalities,
        name="get_personalities",
    ),

    path(
        "api/sessions/",
        views.create_session,
        name="create_session",
    ),

    path(
        "api/sessions/active/",
        views.get_active_sessions,
        name="get_active_sessions",
    ),

    path(
        "api/sessions/<str:session_id>/",
        views.get_session_details,
        name="get_session_details",
    ),

    path(
        "api/sessions/<str:session_id>/messages/",
        views.get_session_messages,
        name="get_session_messages",
    ),

    path(
        "api/sessions/<str:session_id>/end/",
        views.end_session,
        name="end_session",
    ),

    path(
        "api/chat/<str:session_id>/",
        views.chat,
        name="chat",
    ),

    path(
        "api/recent-sessions/",
        views.get_recent_sessions,
        name="get_recent_sessions",
    ),


    # ========================================================
    # VOICE SIMULATION
    # ========================================================

    path(
        "simulation/<str:session_id>/",
        views.simulation,
        name="simulation",
    ),

    path(
        "api/voice/status/",
        views.voice_status,
        name="voice_status",
    ),

    path(
        "api/voice/load-models/",
        views.voice_load_models,
        name="voice_load_models",
    ),

    path(
        "api/voice/stt/",
        views.voice_stt,
        name="voice_stt",
    ),

    path(
        "api/voice/tts/",
        views.voice_tts,
        name="voice_tts",
    ),

]