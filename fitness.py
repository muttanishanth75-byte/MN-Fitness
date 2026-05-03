import streamlit as st
import pandas as pd
from datetime import date
import os

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="FitTrack Pro",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  GLOBAL STYLES
# ─────────────────────────────────────────────
st.markdown(
    """
    <style>
        /* ---------- sidebar ---------- */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f0c29, #302b63, #24243e);
        }
        [data-testid="stSidebar"] * { color: #e0e0ff !important; }

        /* ---------- nav radio ---------- */
        div[role="radiogroup"] label {
            font-size: 1.05rem;
            padding: 0.45rem 0.9rem;
            border-radius: 8px;
            margin-bottom: 4px;
            transition: background 0.2s;
        }
        div[role="radiogroup"] label:hover {
            background: rgba(255,255,255,0.12);
        }

        /* ---------- cards ---------- */
        .card {
            background: #1e1e2f;
            border: 1px solid #3a3a5c;
            border-radius: 14px;
            padding: 1.4rem 1.6rem;
            margin-bottom: 1rem;
            color: #e0e0ff;
        }
        .card h3 { margin-top: 0; color: #a78bfa; }

        /* ---------- badge ---------- */
        .badge {
            display: inline-block;
            background: #7c3aed;
            color: #fff;
            border-radius: 20px;
            padding: 2px 12px;
            font-size: 0.78rem;
            font-weight: 600;
            margin-right: 6px;
        }

        /* ---------- page title ---------- */
        .page-title {
            font-size: 2rem;
            font-weight: 800;
            color: #a78bfa;
            margin-bottom: 0.2rem;
        }
        .page-sub {
            color: #9ca3af;
            margin-bottom: 1.5rem;
        }

        /* ---------- metric row ---------- */
        .metric-box {
            background: #1e1e2f;
            border: 1px solid #3a3a5c;
            border-radius: 12px;
            padding: 1rem;
            text-align: center;
            color: #e0e0ff;
        }
        .metric-val { font-size: 2rem; font-weight: 800; color: #a78bfa; }
        .metric-label { font-size: 0.82rem; color: #9ca3af; }

        /* ---------- table styling ---------- */
        thead tr th { background: #2d2d4e !important; color: #a78bfa !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
#  SESSION STATE  (initialise once, never reset)
# ─────────────────────────────────────────────
def _init_state():
    defaults = {
        "log_entries": [],          # list[dict]  – Progress Log rows
        "current_page": "Weekly Schedule",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

_init_state()

# ─────────────────────────────────────────────
#  DATA – EXERCISES  (images under assets/)
# ─────────────────────────────────────────────
EXERCISES = {
    "Superman": {
        "muscles": ["Lower Back", "Glutes", "Shoulders"],
        "difficulty": "Beginner",
        "sets": "3 × 12 reps",
        "steps": [
            "Lie face down on the floor with arms extended overhead.",
            "Lift your arms, chest, and legs off the floor simultaneously.",
            "Hold for 2 seconds, then slowly lower back down.",
        ],
        "images": ["assets/superman_step1.jpg.png"],
    
        
    },
    "Squat": {
        "muscles": ["Quads", "Glutes", "Hamstrings"],
        "difficulty": "Beginner",
        "sets": "4 × 15",
        "steps": [
            "Stand with feet shoulder-width apart, toes slightly out.",
            "Hinge at the hips and bend the knees to lower down.",
            "Drive through your heels to stand back up.",
        ],
        "images": [
            "assets/squat_step1.jpg.png",
            "assets/squat_step2.jpg.png",
        ],
    },
    "Plank": {
        "muscles": ["Core", "Shoulders", "Glutes"],
        "difficulty": "Beginner",
        "sets": "3 × 30–60 s",
        "steps": [
            "Place forearms on the floor, elbows under shoulders.",
            "Lift your hips so your body forms a straight line.",
            "Hold, squeezing abs and glutes throughout.",
        ],
        "images": [
            "assets/plank_step1.jpg.png",
        ],
    },
    "Pull-Up": {
        "muscles": ["Lats", "Biceps", "Rear Delts"],
        "difficulty": "Intermediate",
        "sets": "3 × 6–10",
        "steps": [
            "Hang from a bar with an overhand grip, arms fully extended.",
            "Pull your chest toward the bar by driving elbows down.",
            "Lower under control to a full hang.",
        ],
        "images": [
            "assets/pullup_step1.jpg.png",
            "assets/pullup_step2.jpg.png",
        ],
    },
    "Bird-Dog": {
        "muscles": ["Core", "Glutes", "Lower Back"],
        "difficulty": "Beginner",
        "sets": "3 × 10 each side",
        "steps": [
            "Start on all fours with a flat back.",
            "Extend your opposite arm and leg (e.g., right arm, left leg).",
            "Keep your hips level and hold for a second before switching.",
        ],
        "images": ["assets/birddog_step1.jpg.png"],
        
    },
    "Lunge": {
        "muscles": ["Quads", "Glutes", "Hamstrings"],
        "difficulty": "Beginner",
        "sets": "3 × 12 each leg",
        "steps": [
            "Stand tall, step one foot forward.",
            "Lower your back knee toward the floor.",
            "Push through your front heel to return to standing.",
        ],
        "images": [
            "assets/lunge_step1.jpg.png",
        ],
    },
}

# ─────────────────────────────────────────────
#  DATA – WEEKLY SCHEDULE
# ─────────────────────────────────────────────
WEEKLY_SCHEDULE = {
    "Monday":    {"focus": "Chest & Triceps",      "exercises": ["Push-Up", "Plank"],             "rest": False},
    "Tuesday":   {"focus": "Legs",                 "exercises": ["Squat", "Lunge"],               "rest": False},
    "Wednesday": {"focus": "Active Recovery",      "exercises": [],                               "rest": True},
    "Thursday":  {"focus": "Back & Biceps",        "exercises": ["Pull-Up", "Deadlift"],          "rest": False},
    "Friday":    {"focus": "Full Body",            "exercises": ["Push-Up", "Squat", "Plank"],    "rest": False},
    "Saturday":  {"focus": "Core & Conditioning",  "exercises": ["Plank", "Lunge"],               "rest": False},
    "Sunday":    {"focus": "Rest Day",             "exercises": [],                               "rest": True},
}

DIFFICULTY_COLOR = {
    "Beginner":     "#22c55e",
    "Intermediate": "#f59e0b",
    "Advanced":     "#ef4444",
}

# ─────────────────────────────────────────────
#  SIDEBAR  –  NAVIGATION
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💪 FitTrack Pro")
    st.markdown("---")

    # Exact string matching – no fuzzy comparison
    NAV_OPTIONS = ["Weekly Schedule", "Exercise Guide", "Progress Log"]

    selected_page = st.radio(
        "Navigate",
        options=NAV_OPTIONS,
        index=NAV_OPTIONS.index(st.session_state["current_page"]),
        key="nav_radio",
    )
    # Keep session_state in sync so the selection survives re-runs
    st.session_state["current_page"] = selected_page

    # ... (lines 231 to 234)
    st.markdown("---")
    st.markdown(
        "<small style='color:#6b7280'>v1.0 · Built with Streamlit</small>",
        unsafe_allow_html=True,
    )

    # PASTE YOUR BRANDING HERE:
    st.markdown(
        """
        <div style="margin-top: 20px; padding: 10px; border-radius: 10px; background: rgba(167, 139, 250, 0.1); border: 1px solid #a78bfa;">
            <p style="margin:0; font-size:0.7rem; color:#a78bfa; text-transform: uppercase;">Owner & Developer</p>
            <p style="margin:0; font-size:1rem; font-weight:bold; color:#ffffff;">Mutta Nishanth</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

# ─────────────────────────────────────────────
#  HELPER – safe image loader
# ─────────────────────────────────────────────
def show_image(path: str, caption: str = ""):
    """Display an image if the file exists, otherwise show a placeholder."""
    if os.path.isfile(path):
        st.image(path, caption=caption, width=None, use_container_width=True)
    else:
        st.info(f"📷 Image not found: `{path}`  \nAdd the file to your `assets/` folder.")

# ─────────────────────────────────────────────
#  PAGE 1 – WEEKLY SCHEDULE
# ─────────────────────────────────────────────
def page_weekly_schedule():
    st.markdown('<p class="page-title">🗓️ Weekly Schedule</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">Your 7-day training plan at a glance.</p>', unsafe_allow_html=True)

    today = date.today().strftime("%A")  # e.g. "Monday"

    cols = st.columns(2)
    for i, (day, info) in enumerate(WEEKLY_SCHEDULE.items()):
        col = cols[i % 2]
        with col:
            is_today = day == today
            border_color = "#a78bfa" if is_today else "#3a3a5c"
            highlight = "⭐ Today · " if is_today else ""

            if info["rest"]:
                st.markdown(
                    f"""<div class="card" style="border-color:{border_color}">
                        <h3>{highlight}{day}</h3>
                        <p>😴 <strong>{info['focus']}</strong></p>
                        <p style="color:#6b7280;font-size:0.85rem">No exercises – let your body recover.</p>
                    </div>""",
                    unsafe_allow_html=True,
                )
            else:
                ex_list = "".join(
                    f'<span class="badge">{ex}</span>' for ex in info["exercises"]
                )
                st.markdown(
                    f"""<div class="card" style="border-color:{border_color}">
                        <h3>{highlight}{day}</h3>
                        <p><strong>{info['focus']}</strong></p>
                        <p>{ex_list}</p>
                    </div>""",
                    unsafe_allow_html=True,
                )

# ─────────────────────────────────────────────
#  PAGE 2 – EXERCISE GUIDE
# ─────────────────────────────────────────────
def page_exercise_guide():
    st.markdown('<p class="page-title">📖 Exercise Guide</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">Step-by-step instructions for every movement.</p>', unsafe_allow_html=True)

    # Filter controls
    col_search, col_diff = st.columns([3, 1])
    with col_search:
        search = st.text_input("🔍 Search exercise", placeholder="e.g. squat")
    with col_diff:
        diff_filter = st.selectbox("Difficulty", ["All", "Beginner", "Intermediate", "Advanced"])

    filtered = {
        name: info
        for name, info in EXERCISES.items()
        if (search.lower() in name.lower() or not search)
        and (diff_filter == "All" or info["difficulty"] == diff_filter)
    }

    if not filtered:
        st.warning("No exercises match your filters.")
        return

    for name, info in filtered.items():
        diff_color = DIFFICULTY_COLOR.get(info["difficulty"], "#a78bfa")
        with st.expander(f"**{name}** — {info['sets']}", expanded=False):
            col_info, col_img = st.columns([1, 1])

            with col_info:
                st.markdown(
                    f'<span style="color:{diff_color};font-weight:700">'
                    f'● {info["difficulty"]}</span>',
                    unsafe_allow_html=True,
                )
                st.markdown(f"**Muscles:** {', '.join(info['muscles'])}")
                st.markdown(f"**Sets / Reps:** {info['sets']}")
                st.markdown("**Steps:**")
                for step_i, step in enumerate(info["steps"], 1):
                    st.markdown(f"{step_i}. {step}")

            with col_img:
                for img_path in info["images"]:
                    # Paths are already relative: "assets/filename.jpg"
                    show_image(img_path, caption=f"{name} – step image")

# ─────────────────────────────────────────────
#  PAGE 3 – PROGRESS LOG
# ─────────────────────────────────────────────
def page_progress_log():
    st.markdown('<p class="page-title">📊 Progress Log</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">Track your workouts and watch your progress grow.</p>', unsafe_allow_html=True)

    # ── Add new entry ──────────────────────────────
    with st.form("log_form", clear_on_submit=True):
        st.markdown("#### ➕ Log a Workout")
        c1, c2, c3 = st.columns(3)
        with c1:
            log_date = st.date_input("Date", value=date.today())
        with c2:
            log_exercise = st.selectbox("Exercise", list(EXERCISES.keys()))
        with c3:
            log_sets = st.number_input("Sets completed", min_value=1, max_value=20, value=3)

        c4, c5 = st.columns(2)
        with c4:
            log_reps = st.number_input("Reps per set", min_value=1, max_value=100, value=10)
        with c5:
            log_weight = st.number_input("Weight (kg, 0 = bodyweight)", min_value=0.0, step=2.5, value=0.0)

        log_notes = st.text_input("Notes (optional)")
        submitted = st.form_submit_button("💾 Save Entry")

    if submitted:
        st.session_state["log_entries"].append({
            "Date":     str(log_date),
            "Exercise": log_exercise,
            "Sets":     log_sets,
            "Reps":     log_reps,
            "Weight (kg)": log_weight if log_weight > 0 else "BW",
            "Notes":    log_notes,
        })
        st.success(f"✅ Logged **{log_exercise}** on {log_date}!")

    # ── Summary metrics ────────────────────────────
    entries = st.session_state["log_entries"]

    if entries:
        df = pd.DataFrame(entries)

        total_sessions = len(df)
        unique_exercises = df["Exercise"].nunique()
        # Count only numeric weights
        numeric_weights = pd.to_numeric(
            df["Weight (kg)"].replace("BW", None), errors="coerce"
        ).dropna()
        max_weight = numeric_weights.max() if not numeric_weights.empty else 0

        st.markdown("#### 📈 Summary")
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(
                f'<div class="metric-box"><div class="metric-val">{total_sessions}</div>'
                f'<div class="metric-label">Total Sessions</div></div>',
                unsafe_allow_html=True,
            )
        with m2:
            st.markdown(
                f'<div class="metric-box"><div class="metric-val">{unique_exercises}</div>'
                f'<div class="metric-label">Unique Exercises</div></div>',
                unsafe_allow_html=True,
            )
        with m3:
            st.markdown(
                f'<div class="metric-box"><div class="metric-val">{max_weight:.1f} kg</div>'
                f'<div class="metric-label">Max Weight Logged</div></div>',
                unsafe_allow_html=True,
            )

        st.markdown("#### 🗂️ All Entries")
        st.dataframe(df, use_container_width=True, hide_index=True)

        # ── Simple bar chart: sessions per exercise ──
        if len(df) >= 2:
            st.markdown("#### 📊 Sessions per Exercise")
            chart_data = df.groupby("Exercise").size().reset_index(name="Sessions")
            st.bar_chart(chart_data.set_index("Exercise"))

        # ── Clear log ──
        if st.button("🗑️ Clear All Entries", type="secondary"):
            st.session_state["log_entries"] = []
            st.rerun()
    else:
        st.info("No entries yet. Log your first workout above! 🏋️")

# ─────────────────────────────────────────────
#  ROUTER  –  exact string matching
# ─────────────────────────────────────────────
page = st.session_state["current_page"]

if page == "Weekly Schedule":
    page_weekly_schedule()
elif page == "Exercise Guide":
    page_exercise_guide()
elif page == "Progress Log":
    page_progress_log()
else:
    st.error(f"Unknown page: '{page}'. Please select a valid option from the sidebar.")