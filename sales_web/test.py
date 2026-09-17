import json
import sys
import os

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)

from database.connection import SessionLocal
from database.models import (
    SalesSession,
    SessionAnalysis,
)


CLIENT_NAME = "KLM Fashion Mall"


def main():

    db = SessionLocal()

    try:

        print("\n" + "=" * 80)
        print("DASHBOARD DATABASE TEST")
        print("=" * 80)

        # ==================================================
        # 1. ALL COMPLETED SESSIONS
        # ==================================================

        completed_sessions = (
            db.query(SalesSession)
            .filter(
                SalesSession.client_name == CLIENT_NAME,
                SalesSession.status == "completed",
            )
            .order_by(
                SalesSession.started_at.asc()
            )
            .all()
        )

        print("\n" + "-" * 80)
        print("1. COMPLETED SESSIONS")
        print("-" * 80)

        print(
            "Total completed sessions:",
            len(completed_sessions)
        )

        for index, session in enumerate(
            completed_sessions,
            start=1,
        ):
            print(
                f"{index}. "
                f"ID={session.id} | "
                f"Started={session.started_at} | "
                f"Status={session.status}"
            )

        # ==================================================
        # 2. ANALYZED SESSIONS
        # ==================================================

        analyzed_sessions = (
            db.query(
                SalesSession,
                SessionAnalysis,
            )
            .join(
                SessionAnalysis,
                SessionAnalysis.session_id
                == SalesSession.id,
            )
            .filter(
                SalesSession.client_name == CLIENT_NAME,
                SalesSession.status == "completed",
            )
            .order_by(
                SalesSession.started_at.asc()
            )
            .all()
        )

        print("\n" + "-" * 80)
        print("2. ANALYZED SESSIONS")
        print("-" * 80)

        print(
            "Total analyzed sessions:",
            len(analyzed_sessions)
        )

        # ==================================================
        # 3. SHOW EVERY ANALYSIS
        # ==================================================

        for index, (
            session,
            analysis,
        ) in enumerate(
            analyzed_sessions,
            start=1,
        ):

            print("\n" + "=" * 80)
            print(f"ANALYZED SESSION {index}")
            print("=" * 80)

            print("Session ID:")
            print(session.id)

            print("\nStarted At:")
            print(session.started_at)

            print("\nOverall Score:")
            print(analysis.overall_score)

            print("\nAnalysis JSON RAW:")
            print(analysis.analysis_json)

            # ----------------------------------------------
            # Try parsing JSON
            # ----------------------------------------------

            try:

                analysis_data = json.loads(
                    analysis.analysis_json
                )

                print("\nParsed JSON:")
                print(
                    json.dumps(
                        analysis_data,
                        indent=4,
                    )
                )

                print("\nTop-level JSON keys:")
                print(
                    list(
                        analysis_data.keys()
                    )
                )

                # ------------------------------------------
                # Check "scores"
                # ------------------------------------------

                scores = analysis_data.get(
                    "scores"
                )

                print("\n'scores' field:")
                print(scores)

                if isinstance(scores, dict):

                    print("\nIndividual skill scores:")

                    for key, value in scores.items():
                        print(
                            f"  {key}: {value}"
                        )

            except (
                json.JSONDecodeError,
                TypeError,
            ):

                print(
                    "\nERROR: analysis_json "
                    "is not valid JSON."
                )

        # ==================================================
        # 4. LATEST ANALYZED SESSION
        # ==================================================

        if analyzed_sessions:

            latest_session, latest_analysis = (
                analyzed_sessions[-1]
            )

            print("\n" + "=" * 80)
            print("3. LATEST ANALYZED SESSION")
            print("=" * 80)

            print(
                "Session ID:",
                latest_session.id,
            )

            print(
                "Started At:",
                latest_session.started_at,
            )

            print(
                "Overall Score:",
                latest_analysis.overall_score,
            )

            print("\nRaw analysis_json:")
            print(
                latest_analysis.analysis_json
            )

            try:

                latest_data = json.loads(
                    latest_analysis.analysis_json
                )

                print("\nParsed latest JSON:")
                print(
                    json.dumps(
                        latest_data,
                        indent=4,
                    )
                )

                print("\nDashboard expects:")

                latest_scores = (
                    latest_data.get(
                        "scores",
                        {},
                    )
                )

                print(
                    "product_knowledge =",
                    latest_scores.get(
                        "product_knowledge",
                        0,
                    ),
                )

                print(
                    "needs_discovery =",
                    latest_scores.get(
                        "needs_discovery",
                        0,
                    ),
                )

                print(
                    "objection_handling =",
                    latest_scores.get(
                        "objection_handling",
                        0,
                    ),
                )

                print(
                    "value_selling =",
                    latest_scores.get(
                        "value_selling",
                        0,
                    ),
                )

                print(
                    "communication =",
                    latest_scores.get(
                        "communication",
                        0,
                    ),
                )

                print(
                    "closing =",
                    latest_scores.get(
                        "closing",
                        0,
                    ),
                )

            except (
                json.JSONDecodeError,
                TypeError,
            ):

                print(
                    "Could not parse latest analysis JSON."
                )

        else:

            print(
                "\nNo analyzed sessions found."
            )

        print("\n" + "=" * 80)
        print("TEST COMPLETE")
        print("=" * 80)


    finally:

        db.close()


if __name__ == "__main__":
    main()