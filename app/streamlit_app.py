import os, streamlit as st
from dotenv import load_dotenv
from app.rag import SimpleRAG
from app.feeds import fetch_news
from app.player_news import fetch_player_news
from app.prompts import SYSTEM_PROMPT, EDGE_INSTRUCTIONS
from app.model import LLMBackend
from app.pdf_export import export_edge_sheet_pdf
from app.config import SEASON, is_submission_open
from app.state_store import add_plan, add_leaderboard_entry, leaderboard, ladder
from app.ownership_scoring import normalize_roster, market_delta_by_position, delta_scalar
from app.badges import award_badges
from app.opponent_ai import generate_ai_plan
from app.whatif import score_archetypes
from app.narrative_events import surprise_event

load_dotenv()
st.set_page_config(page_title="NFL Edge Coach", page_icon="🏈", layout="wide")
st.title("🏈 NFL Edge Coach — Market Value × Narrative Pressure")

# -------------------------
# Setup RAG and Model
# -------------------------
@st.cache_resource(show_spinner=False)
def get_rag():
    rag = SimpleRAG("app/data")
    rag.build()
    return rag
rag = get_rag()

with st.sidebar:
    st.subheader("Model Backend")
    backend = st.selectbox("Backend", ["hf_inference","local"], index=0)
    model_name = st.text_input(
        "Model name", 
        value="meta-llama/Meta-Llama-3-8B-Instruct" if backend=="hf_inference" else "Qwen/Qwen2.5-7B-Instruct"
    )
    st.caption("For hf_inference, set HUGGINGFACE_API_TOKEN in Secrets/env.")
    st.divider()
    st.subheader("Context")
    k_ctx = st.slider("RAG passages (k)", 3, 10, 5)
    use_news = st.checkbox("Include headlines", True)
    team_codes = st.text_input("Focus teams (comma-separated)", "PHI, DAL")
    players_raw = st.text_area("Players (comma-separated)", "Jalen Hurts, CeeDee Lamb")
    st.session_state["team_codes"] = team_codes
    st.divider()
    want_pdf = st.checkbox("Enable Edge Sheet PDF export", True)

@st.cache_resource(show_spinner=False)
def get_model(backend, model_name):
    return LLMBackend(backend=backend, model_name=model_name)
llm = get_model(backend, model_name)

# -------------------------
# Chat Mode
# -------------------------
if "chat" not in st.session_state:
    st.session_state.chat = []

for role, msg in st.session_state.chat:
    st.chat_message(role).markdown(msg)

prompt = st.chat_input("Ask about a team/player matchup or strategy…")
if prompt:
    st.session_state.chat.append(("user", prompt))
    st.chat_message("user").markdown(prompt)

    ctx = rag.search(prompt, k=k_ctx)
    ctx_text = "\n\n".join([f"[{i+1}] ({round(sc,3)}): {c['text']}" for i,(sc,c) in enumerate(ctx)])

    teams = [t.strip() for t in team_codes.split(",") if t.strip()]
    news_text = ""
    if use_news:
        news_items = fetch_news(max_items=12, teams=teams)
        news_text = "\n\n".join([f"- {n['title']} — {n['summary']}" for n in news_items])
    players_list = [p.strip() for p in players_raw.split(",") if p.strip()]
    player_news_items = fetch_player_news(players_list, team_hint=teams[0] if teams else "", max_items_per_player=3) if (use_news and players_list) else []
    player_news_text = "\n".join([f"- ({it['player']}) {it['title']} — {it['summary']}" for it in player_news_items])

    user_msg = f"""{EDGE_INSTRUCTIONS}

User question:
{prompt}

Context (Edge System doc):
{ctx_text}

Recent NFL headlines:
{news_text if use_news else 'N/A'}
"""
    if player_news_text:
        user_msg += f"\n\nPlayer headlines:\n{player_news_text}"

    with st.chat_message("assistant"):
        ans = llm.chat(SYSTEM_PROMPT, user_msg)
        st.markdown(ans)
        st.session_state.chat.append(("assistant", ans))

        if want_pdf:
            from datetime import datetime
            fn = f"edge_sheet_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            tldr = ans.split("\n")[0][:250]
            bullets = [line for line in ans.split("\n") if line.strip().startswith(('-', '*','•'))][:12]
            export_edge_sheet_pdf(fn, "NFL Edge Sheet", tldr, bullets)
            with open(fn, "rb") as f:
                st.download_button("Download Edge Sheet PDF", data=f, file_name=fn, mime="application/pdf")

# -------------------------
# Game Mode
# -------------------------
st.divider()
st.header("🎮 Game Mode — Weekly Challenge")
colA, colB, colC, colD = st.columns(4)
with colA:
    username = st.text_input("Username", value="guest")
with colB:
    week = st.number_input("Week", min_value=1, max_value=18, value=1, step=1)
with colC:
    usage_hint = st.slider("Confidence in plan", 0.0, 1.0, 0.6, 0.05)
with colD:
    underdog = st.checkbox("Underdog Plan?", value=False)

open_now = is_submission_open(int(week))
st.info("Submissions open ✅" if open_now else "Submissions closed ⛔ for this week")

st.subheader("Upload Rosters (CSV) — optional but recommended")
st.caption("Format: Player, Pos, % Rostered")
a_file = st.file_uploader("Your Team Roster (CSV)", type=["csv"], key="a_csv")
b_file = st.file_uploader("Opponent Roster (CSV)", type=["csv"], key="b_csv")
delta_val = 0.0
if a_file and b_file:
    import pandas as pd
    try:
        a_df = normalize_roster(pd.read_csv(a_file))
        b_df = normalize_roster(pd.read_csv(b_file))
        dpos = market_delta_by_position(a_df, b_df)
        st.write("Positional Market Delta (B - A):")
        st.dataframe(dpos, hide_index=True, use_container_width=True)
        delta_val = float(delta_scalar(dpos))
        st.success(f"Scalar Market Delta: {delta_val:.3f}")
    except Exception as e:
        st.warning(f"Roster parsing error: {e}")

st.subheader("Your Edge Plan")
team_focus = st.text_input("Your team code (e.g., PHI)", value="PHI")
opponent = st.text_input("Opponent team code (e.g., DAL)", value="DAL")
picks = st.text_area("Your 2–3 key calls (one per line)", "1) Target boundary with WR2 deep cross\n2) 12-personnel PA on early downs\n3) RB screen vs blitz")
rationale = st.text_area("Why this works (market vs pressure)", "WR2 undervalued; opponent CB2 struggles; positive sentiment.")

if st.button("Generate Market/Pressure Summary (LLM)"):
    q = f"Summarize market vs narrative edges for {team_focus} vs {opponent} in one paragraph."
    ctx = rag.search(q, k=4)
    ctx_text = "\n\n".join([c['text'] for _,c in ctx])
    user_msg = "Return JSON only with keys delta_market_hint ([-2..+2]), sentiment_boost ([-2..+2]), reason."
    ans = llm.chat("You are a JSON generator.", f"{user_msg}\nContext:\n{ctx_text}")
    st.code(ans, language="json")
    st.session_state["_last_summary"] = ans

if st.button("Score My Plan (locks when deadline passes)"):
    if not open_now:
        st.error("Submissions are closed for this week.")
    else:
        import json as _json
        hint = st.session_state.get("_last_summary", '{"delta_market_hint":0,"sentiment_boost":0,"reason":"n/a"}')
        try:
            data = _json.loads(hint)
        except Exception:
            data = {"delta_market_hint":0,"sentiment_boost":0,"reason":"n/a"}
        delta_market = (delta_val + float(data.get("delta_market_hint",0))) / (2 if a_file and b_file else 1)
        score = int(max(0, min(100, 50 + (delta_market*22.0) + (float(data.get('sentiment_boost',0))*20.0) + (usage_hint*8.0) + (5.0 if underdog else 0.0))))
        st.success(f"Your Plan Score: {score}/100")

        bs = award_badges(score, float(delta_market), float(data.get("sentiment_boost",0)), underdog, len([p for p in picks.splitlines() if p.strip()]))
        if bs:
            st.write("**Badges earned:**")
            for b in bs:
                st.write(f"{b['emoji']} **{b['name']}** — {b['desc']}")

        from time import time as now
        add_plan({
            "id": f"{username}-{int(now())}",
            "score": score,
            "summary": data,
            "season": SEASON,
            "plan": {
                "user": username, "season": SEASON, "week": int(week),
                "team_focus": team_focus, "opponent": opponent,
                "picks": [p.strip('0123456789). ').strip() for p in picks.splitlines() if p.strip()],
                "rationale": rationale, "tstamp": now()
            }
        })
        add_leaderboard_entry({"user": username, "week": int(week), "team": team_focus, "opp": opponent, "score": score, "reason": data.get("reason","")})

st.subheader("🏆 Weekly Leaderboard")
st.dataframe(leaderboard(week=int(week)), use_container_width=True, hide_index=True)

st.subheader("📈 Ladder (Cumulative)")
st.dataframe(ladder(), use_container_width=True, hide_index=True)

# -------------------------
# Fun Modes
# -------------------------
st.divider()
st.header("🎲 Fun Modes")
col_fun1, col_fun2 = st.columns(2)
with col_fun1:
    st.subheader("🤖 Opponent AI Coach")
    last_user = st.session_state.chat[-1][1] if st.session_state.get("chat") else "Analyze PHI vs DAL edges."
    ctx = rag.search(last_user, k=5)
    ctx_text_for_ai = "\n\n".join([c['text'] for _,c in ctx])
    if st.button("Generate AI Counter-Plan"):
        ai_plan = generate_ai_plan(llm, ctx_text_for_ai, last_user)
        st.json(ai_plan)

with col_fun2:
    st.subheader("🧪 What-if Strategy Scorer")
    if st.button("Score Common Archetypes"):
        scores = score_archetypes(llm, ctx_text_for_ai)
        st.json({"scores": scores})

st.subheader("🎲 Surprise Narrative Event")
if st.button("Roll Surprise Event"):
    teams = [t.strip() for t in team_codes.split(",") if t.strip()]
    news = fetch_news(max_items=12, teams=teams)
    ev = surprise_event(news)
    if ev:
        st.write(f"Event: **{ev['title']}**")
        st.write(ev["summary"])
        st.write(f"Impact hint: {ev['impact']:+.1f}")
    else:
        st.write("No events found.")

