from django.urls import path
from . import views


urlpatterns = [

    path(
        "",
        views.dashboard,
        name="dashboard",
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
]