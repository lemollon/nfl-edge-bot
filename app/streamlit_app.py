# app/streamlit_app.py
import os, re, json, html
import streamlit as st

# --- relative imports (this file lives inside app/) ---
from rag import SimpleRAG                      # BM25 RAG (no FAISS/Torch)
from feeds import fetch_news                   # team/league RSS (ESPN/NFL + SB Nation)
from player_news import fetch_player_news      # Google News RSS for players
from prompts import SYSTEM_PROMPT, EDGE_INSTRUCTIONS
from model import LLMBackend                   # HF Inference with open-model fallbacks
from pdf_export import export_edge_sheet_pdf   # Edge Sheet PDF export
from config import SEASON, is_submission_open
from state_store import add_plan, add_leaderboard_entry, leaderboard, ladder
from ownership_scoring import normalize_roster, market_delta_by_position, delta_scalar
from badges import award_badges
from opponent_ai import generate_ai_plan
from whatif import score_archetypes
from narrative_events import surprise_event

# =============================================================================
# Brand / App config
# =============================================================================
st.set_page_config(page_title="GRIT — NFL Edge Coach", page_icon="🏈", layout="wide")
st.title("🏈 GRIT — Market Value × Narrative Pressure")

# =============================================================================
# Utilities
# =============================================================================
TAG_RE = re.compile(r"<[^>]+>")

def clean_html(txt: str | None) -> str:
    """Remove HTML tags/attrs from RSS summaries and unescape entities."""
    if not txt:
        return ""
    return html.unescape(TAG_RE.sub("", txt)).strip()

# =============================================================================
# RAG + Model (cached)
# =============================================================================
@st.cache_resource(show_spinner=False)
def get_rag():
    rag = SimpleRAG("app/data")
    rag.build()
    return rag

@st.cache_resource(show_spinner=False)
def get_model(backend: str, model_name: str):
    # backend kept for UI completeness; LLMBackend routes to HF Inference
    return LLMBackend(backend=backend, model_name=model_name)

rag = get_rag()

# -----------------------------------------------------------------------------
# Sidebar (global controls)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.subheader("Model & Context")
    backend = st.selectbox("Backend (HF Inference under the hood)", ["hf_inference"], index=0)
    model_name = st.text_input("Model name", value="HuggingFaceH4/zephyr-7b-beta")
    st.caption("Tip: open models like Zephyr, Qwen2.5-7B-Instruct, Phi-3-mini are ungated.")
    k_ctx = st.slider("RAG passages (k)", 3, 10, 5)

    st.divider()
    include_news = st.checkbox("Include headlines", True)
    team_codes = st.text_input("Focus teams (comma-separated)", "PHI, DAL")
    players_raw = st.text_area("Players (comma-separated)", "Jalen Hurts, CeeDee Lamb")
    st.session_state["team_codes"] = team_codes

    st.divider()
    want_pdf = st.checkbox("Enable Edge Sheet PDF export", True)

    st.divider()
    if st.button("Rebuild Edge Corpus (reload app/data/*.txt)"):
        st.cache_resource.clear()
        st.success("Rebuilt corpus. Reloading…")
        st.rerun()

# Create model after sidebar selections
llm = get_model(backend, model_name)

# =============================================================================
# Tabs
# =============================================================================
tab_coach, tab_game, tab_news = st.tabs(["📋 Coach Mode", "🎮 Game Mode", "📰 Headlines"])

# --------------------------------------------------------------------------------------
# Coach Mode
# --------------------------------------------------------------------------------------
with tab_coach:
    st.subheader("Edge Sheet Generator")

    coach_q = st.text_input(
        "Ask a strategic question",
        "What are the primary edges for PHI vs DAL if CB2 is vulnerable?"
    )

    if st.button("Generate Edge Sheet", key="coach_generate"):
        # retrieve context
        ctx = rag.search(coach_q, k=k_ctx)
        ctx_text = "\n\n".join([f"[{i+1}] {c['text']}" for i,(_,c) in enumerate(ctx)])

        # news context
        teams = [t.strip() for t in team_codes.split(",") if t.strip()]
        news_text = ""
        player_news_text = ""
        if include_news:
            try:
                news_items = fetch_news(max_items=10, teams=teams)
                news_text = "\n".join([f"- {n['title']} — {clean_html(n.get('summary',''))}" for n in news_items])
            except Exception as e:
                news_text = f"(news unavailable: {e})"

            players_list = [p.strip() for p in players_raw.split(",") if p.strip()]
            try:
                pitems = fetch_player_news(players_list, team_hint=teams[0] if teams else "", max_items_per_player=3) if players_list else []
                player_news_text = "\n".join([f"- ({it['player']}) {it['title']} — {clean_html(it.get('summary',''))}" for it in pitems])
            except Exception as e:
                player_news_text = f"(player headlines unavailable: {e})"

        user_msg = f"""{EDGE_INSTRUCTIONS}

Coach question:
{coach_q}

Context (Edge System doc):
{ctx_text}

Recent NFL headlines:
{news_text if include_news else 'N/A'}

Player headlines:
{player_news_text if include_news else 'N/A'}
"""
        try:
            ans = llm.chat(SYSTEM_PROMPT, user_msg)
        except Exception as e:
            ans = f"**Model error:** {e}\n\nTry a different open model in the sidebar (e.g., HuggingFaceH4/zephyr-7b-beta)."

        st.markdown(ans)

        if want_pdf:
            from datetime import datetime
            fn = f"edge_sheet_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            tldr = ans.split("\n")[0][:250]
            bullets = [line for line in ans.split("\n") if line.strip().startswith(('-', '*','•'))][:12]
            try:
                export_edge_sheet_pdf(fn, "GRIT — Edge Sheet", tldr, bullets)
                with open(fn, "rb") as f:
                    st.download_button("Download Edge Sheet PDF", data=f, file_name=fn, mime="application/pdf")
            except Exception as e:
                st.caption(f"(PDF export unavailable: {e})")

    # Optional debug: how many passages are loaded
    with st.expander("Corpus status (debug)"):
        try:
            st.write(f"Loaded passages: {len(rag.chunks)}")
            src = {}
            for c in rag.chunks:
                src[c["source"]] = src.get(c["source"], 0) + 1
            st.json(src)
        except Exception:
            st.caption("Corpus not available.")

# --------------------------------------------------------------------------------------
# Game Mode
# --------------------------------------------------------------------------------------
with tab_game:
    st.subheader("Weekly Challenge")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        username = st.text_input("Username", value="guest")
    with c2:
        week = st.number_input("Week", min_value=1, max_value=18, value=1, step=1)
    with c3:
        usage_hint = st.slider("Confidence in plan", 0.0, 1.0, 0.6, 0.05)
    with c4:
        underdog = st.checkbox("Underdog Plan?", value=False)

    open_now = is_submission_open(int(week))
    st.info("Submissions open ✅" if open_now else "Submissions closed ⛔ for this week")

    st.markdown("**Upload Rosters (CSV)** — optional but recommended  \n"
                "_Columns: Player, Pos, % Rostered_")
    a_file = st.file_uploader("Your Team Roster (CSV)", type=["csv"], key="a_csv")
    b_file = st.file_uploader("Opponent Roster (CSV)", type=["csv"], key="b_csv")

    delta_val = 0.0
    if a_file and b_file:
        import pandas as pd
        try:
            a_df = normalize_roster(pd.read_csv(a_file))
            b_df = normalize_roster(pd.read_csv(b_file))
            dpos = market_delta_by_position(a_df, b_df)
            st.write("Positional Market Delta (B − A):")
            st.dataframe(dpos, hide_index=True, use_container_width=True)
            delta_val = float(delta_scalar(dpos))
            st.success(f"Scalar Market Delta: {delta_val:.3f}")
        except Exception as e:
            st.warning(f"Roster parsing error: {e}")

    st.markdown("**Your Edge Plan**")
    team_focus = st.text_input("Your team code (e.g., PHI)", value="PHI")
    opponent = st.text_input("Opponent team code (e.g., DAL)", value="DAL")
    picks = st.text_area(
        "Your 2–3 key calls (one per line)",
        "1) 1st & 10, 12P — PA flood to TE seam — vs single-high — LB bites on run keys\n"
        "2) 3rd & medium, 11P — WR2 deep cross from stack — attack CB2 leverage\n"
        "3) Red zone — RB screen constraint — vs pressure tendency"
    )
    rationale = st.text_area("Why this works (market vs pressure)", "WR2 undervalued; CB2 leverage issues; positive sentiment.")

    if st.button("Generate Market/Pressure Summary (LLM)"):
        q = f"Summarize market vs narrative edges for {team_focus} vs {opponent} in one paragraph."
        ctx = rag.search(q, k=4)
        ctx_text = "\n\n".join([c['text'] for _,c in ctx])
        user_msg = "Return JSON only with keys delta_market_hint ([-2..+2]), sentiment_boost ([-2..+2]), reason."
        try:
            ans = llm.chat("You are a JSON generator.", f"{user_msg}\nContext:\n{ctx_text}")
            st.code(ans, language="json")
            st.session_state["_last_summary"] = ans
        except Exception as e:
            st.error(f"Model error: {e}")

    if st.button("Score My Plan (locks when deadline passes)"):
        if not open_now:
            st.error("Submissions are closed for this week.")
        else:
            hint = st.session_state.get("_last_summary", '{"delta_market_hint":0,"sentiment_boost":0,"reason":"n/a"}')
            try:
                js = json.loads(hint)
            except Exception:
                js = {"delta_market_hint": 0, "sentiment_boost": 0, "reason": "n/a"}

            delta_market = (delta_val + float(js.get("delta_market_hint", 0))) / (2 if a_file and b_file else 1)
            score = int(max(0, min(100,
                50 + (delta_market * 22.0) + (float(js.get('sentiment_boost', 0)) * 20.0) + (usage_hint * 8.0) + (5.0 if underdog else 0.0)
            )))
            st.success(f"Your Plan Score: {score}/100")

            bs = award_badges(score, float(delta_market), float(js.get("sentiment_boost", 0)), underdog,
                              len([p for p in picks.splitlines() if p.strip()]))
            if bs:
                st.write("**Badges earned:**")
                for b in bs:
                    st.write(f"{b['emoji']} **{b['name']}** — {b['desc']}")

            from time import time as now
            add_plan({
                "id": f"{username}-{int(now())}",
                "score": score,
                "summary": js,
                "season": SEASON,
                "plan": {
                    "user": username, "season": SEASON, "week": int(week),
                    "team_focus": team_focus, "opponent": opponent,
                    "picks": [p.strip('0123456789). ').strip() for p in picks.splitlines() if p.strip()],
                    "rationale": rationale, "tstamp": now()
                }
            })
            add_leaderboard_entry({"user": username, "week": int(week), "team": team_focus, "opp": opponent, "score": score, "reason": js.get("reason","")})

    st.subheader("🏆 Weekly Leaderboard")
    try:
        st.dataframe(leaderboard(week=int(week)), use_container_width=True, hide_index=True)
    except Exception:
        st.caption("(leaderboard unavailable yet)")

    st.subheader("📈 Ladder (Cumulative)")
    try:
        st.dataframe(ladder(), use_container_width=True, hide_index=True)
    except Exception:
        st.caption("(ladder unavailable yet)")

    st.divider()
    st.subheader("🎲 Fun Modes")
    f1, f2 = st.columns(2)

    with f1:
        st.markdown("**Opponent AI Coach**")
        last_user = f"Analyze {team_focus} vs {opponent} edges."  # seed if no chat
        ctx = rag.search(last_user, k=5)
        ctx_text_for_ai = "\n\n".join([c['text'] for _, c in ctx])
        if st.button("Generate AI Counter-Plan"):
            try:
                ai_plan = generate_ai_plan(llm, ctx_text_for_ai, last_user)
                st.json(ai_plan)
            except Exception as e:
                st.error(f"AI Coach error: {e}")

    with f2:
        st.markdown("**What-if Strategy Scorer**")
        if st.button("Score Common Archetypes"):
            try:
                scores = score_archetypes(llm, ctx_text_for_ai)
                st.json({"scores": scores})
            except Exception as e:
                st.error(f"What-if error: {e}")

    st.markdown("**Surprise Narrative Event**")
    if st.button("Roll Surprise Event"):
        teams = [t.strip() for t in team_codes.split(",") if t.strip()]
        try:
            news = fetch_news(max_items=12, teams=teams)
            ev = surprise_event(news)
            if ev:
                st.write(f"Event: **{ev['title']}**")
                st.write(clean_html(ev["summary"]))
                st.write(f"Impact hint: {ev['impact']:+.1f}")
            else:
                st.write("No events found.")
        except Exception as e:
            st.caption(f"(surprise event unavailable: {e})")

# --------------------------------------------------------------------------------------
# Headlines tab
# --------------------------------------------------------------------------------------
with tab_news:
    st.subheader("Latest Headlines")
    teams_for_news = [t.strip() for t in team_codes.split(",") if t.strip()]
    players_list = [p.strip() for p in players_raw.split(",") if p.strip()]
    col_team, col_player = st.columns(2)

    with col_team:
        st.markdown("**Team / League**")
        try:
            news_items = fetch_news(max_items=12, teams=teams_for_news)
            if not news_items:
                st.caption("No headlines found (check team codes or refresh).")
            for n in news_items:
                st.write(f"**{n['title']}**")
                if n.get("summary"):
                    st.caption(clean_html(n["summary"]))
                if n.get("link"):
                    st.markdown(f"[source]({n['link']})")
                st.write("---")
        except Exception as e:
            st.caption(f"(news error: {e})")

    with col_player:
        st.markdown("**Player Notes**")
        if not players_list:
            st.caption("Add player names in the sidebar to see player-specific items.")
        else:
            try:
                pitems = fetch_player_news(players_list, team_hint=teams_for_news[0] if teams_for_news else "", max_items_per_player=3)
                if not pitems:
                    st.caption("No player news right now.")
                for it in pitems:
                    st.write(f"**({it['player']}) {it['title']}**")
                    if it.get("summary"):
                        st.caption(clean_html(it["summary"]))
                    if it.get("link"):
                        st.markdown(f"[source]({it['link']})")
                    st.write("---")
            except Exception as e:
                st.caption(f"(player news error: {e})")
