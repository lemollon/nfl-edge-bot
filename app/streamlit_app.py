# app/streamlit_app.py
import os, re, html, json
import streamlit as st

# --- local modules (this file lives inside app/) ---
from rag import SimpleRAG                              # BM25 RAG (no FAISS/Torch)
from feeds import fetch_news                           # team/league RSS (ESPN/NFL + SB Nation)
from player_news import fetch_player_news              # Google News RSS for players
from prompts import SYSTEM_PROMPT, EDGE_INSTRUCTIONS
from model import LLMBackend                           # HF Inference with open-model fallbacks
from pdf_export import export_edge_sheet_pdf           # Edge Sheet PDF export
from config import SEASON, is_submission_open
from state_store import add_plan, add_leaderboard_entry, leaderboard, ladder
from ownership_scoring import normalize_roster, market_delta_by_position, delta_scalar
from badges import award_badges
from opponent_ai import generate_ai_plan
from whatif import score_archetypes
from narrative_events import surprise_event

# =============================================================================
# Branding / Page
# =============================================================================
st.set_page_config(page_title="GRIT — NFL Edge Coach", page_icon="🏈", layout="wide")
st.title("🏈 GRIT — Market Value × Narrative Pressure")

# =============================================================================
# Helpers
# =============================================================================
TAG_RE = re.compile(r"<[^>]+>")

def clean_html(txt: str | None) -> str:
    """Strip tags and unescape entities from RSS summaries."""
    if not txt:
        return ""
    return html.unescape(TAG_RE.sub("", txt)).strip()

# AI Backend choices
AI_BACKEND_CHOICES = {
    "OpenAI GPT-3.5 Turbo (Recommended)": "openai-gpt35",
    "OpenAI GPT-4 (Premium)": "openai-gpt4", 
    "Bypass Mode (Reliable)": "bypass",
    "HuggingFace (Experimental)": "huggingface"
}
DEFAULT_AI_BACKEND = "OpenAI GPT-3.5 Turbo (Recommended)"

# =============================================================================
# OpenAI Integration
# =============================================================================
def openai_chat(system_prompt: str, user_prompt: str, max_tokens: int = 512, temperature: float = 0.7, model: str = "gpt-3.5-turbo") -> str:
    """OpenAI Chat Completion with error handling"""
    try:
        import openai
        
        # Get API key from environment
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            return "❌ OpenAI API key not found. Please set OPENAI_API_KEY in your environment variables."
        
        # Set up client
        client = openai.OpenAI(api_key=openai_key)
        
        # Make API call
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=0.9
        )
        
        return response.choices[0].message.content.strip()
        
    except ImportError:
        return "❌ OpenAI library not installed. Run: pip install openai"
    except Exception as e:
        error_msg = str(e)
        if "api_key" in error_msg.lower():
            return "❌ Invalid OpenAI API key. Please check your OPENAI_API_KEY environment variable."
        elif "rate_limit" in error_msg.lower():
            return "❌ OpenAI rate limit exceeded. Please try again in a moment."
        elif "insufficient_quota" in error_msg.lower():
            return "❌ OpenAI quota exceeded. Please check your billing settings."
        else:
            return f"❌ OpenAI error: {error_msg}"

# =============================================================================
# Enhanced Error Handling for Model Issues (FEATURE 8)
# =============================================================================
def safe_llm_answer(system_prompt: str, user_prompt: str, max_tokens: int = 512, temperature: float = 0.35, backend: str = "openai-gpt35") -> str:
    """Enhanced LLM answer with fallback handling for model errors"""
    
    if backend == "openai-gpt35":
        return openai_chat(system_prompt, user_prompt, max_tokens, temperature, "gpt-3.5-turbo")
    
    elif backend == "openai-gpt4":
        return openai_chat(system_prompt, user_prompt, max_tokens, temperature, "gpt-4")
    
    elif backend == "huggingface":
        try:
            # Try HuggingFace as fallback
            llm = get_model("hf_inference", "distilgpt2")
            return llm.chat(system_prompt, user_prompt, max_new_tokens=max_tokens, temperature=temperature)
        except Exception as e:
            return f"❌ HuggingFace failed: {e}. Try OpenAI or Bypass mode."
    
    elif backend == "bypass":
        return generate_bypass_response(user_prompt)
    
    else:
        return generate_bypass_response(user_prompt)

def generate_bypass_response(user_prompt: str) -> str:
    """Bypass response system (same as before)"""
    prompt_lower = user_prompt.lower()
    
    if any(word in prompt_lower for word in ['qb', 'quarterback']):
        return """🏈 **QB Strategy Analysis:**

**Elite Tier (High Floor + Ceiling):**
• Josh Allen - Rushing upside, strong arm, elite in any weather
• Lamar Jackson - Unique rushing floor (15+ points), improved passing
• Patrick Mahomes - Consistent target distribution, clutch performer

**Value Tier (Leverage Opportunities):**
• Geno Smith - Low ownership, strong target share to DK/Tyler
• Derek Carr - Underpriced, decent floor in favorable matchups
• Justin Herbert - Bounce-back candidate, elite arm talent

**Weather Considerations:**
• Heavy wind (15+ MPH): Fade deep passers, target rushing QBs
• Cold/Rain: Favor QBs with experience in elements
• Dome games: Normal passing efficiency expected

**Game Script Analysis:**
• Teams favored by 7+: QB likely to have safe floor
• Underdogs: Higher ceiling potential, but riskier floor
• High totals (47+): Both QBs in play for GPP

**Ownership Strategy:**
• Cash games: Prioritize floor (20+ point potential)
• Tournaments: Target ceiling + low ownership combination"""
    
    else:
        return f"""🤖 **Strategic Analysis:**

Your question: "{user_prompt}"

Based on the Market Value × Narrative Pressure framework:

**Key Considerations:**
• Identify players with elite metrics but low ownership
• Look for pricing inefficiencies 
• Consider narrative bias creating opportunities

**Recommendation:** Check your Edge System documents for specific insights.

*Using bypass mode for reliable responses.*"""

# =============================================================================
# Cached resources (FEATURES 47)
# =============================================================================
@st.cache_resource(show_spinner=False)
def get_rag():
    rag = SimpleRAG("app/data")
    rag.build()
    return rag

@st.cache_resource(show_spinner=False)
def get_model(backend: str, model_name: str):
    return LLMBackend(backend=backend, model_name=model_name)

# Cache RSS fetches briefly to cut latency on repeated calls
@st.cache_data(ttl=120, show_spinner=False)
def cached_news(max_items: int, teams_tuple: tuple[str, ...]):
    teams = list(teams_tuple)
    return fetch_news(max_items=max_items, teams=teams)

@st.cache_data(ttl=120, show_spinner=False)
def cached_player_news(players_tuple: tuple[str, ...], team_hint: str, max_items_per_player: int):
    players = list(players_tuple)
    return fetch_player_news(players, team_hint=team_hint, max_items_per_player=max_items_per_player)

rag = get_rag()

# =============================================================================
# Sidebar controls (FEATURES 9-20)
# =============================================================================
with st.sidebar:
    st.subheader("🤖 AI Backend")
    
    # OpenAI API Key check
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        st.success(f"OpenAI API Key found: {openai_key[:8]}...")
    else:
        st.warning("⚠️ OPENAI_API_KEY not set")
        st.caption("Add your OpenAI API key to environment variables for AI features")
    
    # FEATURE 9: AI Backend Selection (Enhanced Model Selection)
    ai_backend_label = st.selectbox(
        "AI Backend",
        options=list(AI_BACKEND_CHOICES.keys()),
        index=list(AI_BACKEND_CHOICES.keys()).index(DEFAULT_AI_BACKEND),
        help="AI Assistant uses GPT-3.5 for dynamic responses. Expert Mode uses proven fantasy strategies."
    )
    ai_backend = AI_BACKEND_CHOICES[ai_backend_label]
    
    if ai_backend.startswith("openai") and not openai_key:
        st.error("OpenAI backend selected but no API key found!")
        ai_backend = "bypass"
        st.info("Falling back to Bypass mode")
    
    # FEATURE 20: Model Caption Display
    if ai_backend == "openai-gpt35":
        st.caption("**Selected:** `gpt-3.5-turbo` — Fast, reliable, cost-effective")
    elif ai_backend == "openai-gpt4":
        st.caption("**Selected:** `gpt-4` — Highest quality responses")
    elif ai_backend == "bypass":
        st.caption("**Selected:** `bypass` — Expert-written responses")
    else:
        st.caption("**Selected:** `huggingface` — Experimental fallback")
    
    st.divider()
    st.subheader("Model & Retrieval")

    # Legacy backend setting (no longer actively used)
    backend = "openai"  # Simplified since we're using OpenAI primarily

    # FEATURE 10: Turbo Mode Toggle
    turbo = st.toggle("Turbo Mode (fastest)", value=False, help="Forces fastest settings + Short + k=3 and disables headlines for max speed.")
    if turbo:
        ai_backend = "bypass"  # Force bypass in turbo mode

    # FEATURE 11: Response Length Control
    resp_len = st.select_slider(
        "Response length", options=["Short","Medium","Long"],
        value=("Short" if turbo else "Medium"),
        help="Short≈256 tokens, Medium≈512, Long≈800."
    )
    MAX_TOKENS = {"Short": 256, "Medium": 512, "Long": 800}[resp_len]

    # FEATURE 42: Temperature Control
    temperature = st.slider(
        "AI Creativity", 0.1, 1.0, (0.3 if turbo else 0.7), 0.1,
        help="Lower = more focused, Higher = more creative"
    )

    # FEATURE 12: Latency Mode Selection
    latency_mode = st.selectbox(
        "Latency mode", ["Fast","Balanced","Thorough"],
        index=(0 if turbo else 1),
        help="Controls default RAG k. Fast=3, Balanced=5, Thorough=8."
    )
    default_k = {"Fast": 3, "Balanced": 5, "Thorough": 8}[latency_mode]
    
    # FEATURE 13: RAG Passage Control
    k_ctx = st.slider(
        "RAG passages (k)", 3, 10, (3 if turbo else default_k),
        help="How many passages from your Edge docs are added to the prompt. Lower = faster."
    )

    st.divider()
    
    # FEATURE 14: Headlines Toggle
    include_news = st.checkbox(
        "Include headlines in prompts", (False if turbo else True),
        help="Pulls team + player headlines into context (slower but richer)."
    )
    
    # FEATURE 15: Team Focus Input
    team_codes = st.text_input("Focus teams (comma-separated)", "PHI, DAL")
    
    # FEATURE 16: Player Focus Input
    players_raw = st.text_area("Players (comma-separated)", "Jalen Hurts, CeeDee Lamb")
    st.session_state["team_codes"] = team_codes

    st.divider()
    
    # FEATURE 17: Corpus Rebuild Button
    if st.button("Rebuild Edge Corpus (reload app/data/*.txt)"):
        st.cache_resource.clear()
        st.cache_data.clear()
        st.success("Rebuilt corpus. Reloading…")
        st.rerun()

# Create model after selections (for HuggingFace fallback)
llm = get_model(backend, "distilgpt2")

# FEATURE 19: Turbo Banner
if turbo:
    st.info("**Turbo Mode enabled** — Bypass mode + Short responses + k=3 + headlines off for maximum speed.")

# Main AI function
def llm_answer(system_prompt: str, user_prompt: str, max_tokens: int = 512, temperature_val: float = 0.35) -> str:
    return safe_llm_answer(system_prompt, user_prompt, max_tokens, temperature_val, ai_backend)

# =============================================================================
# FEATURE 51: Tab-based Navigation
# =============================================================================
tab_coach, tab_game, tab_news = st.tabs(["📋 Coach Mode", "🎮 Game Mode", "📰 Headlines"])

# --------------------------------------------------------------------------------------
# 📋 Coach Mode (FEATURES 21-25)
# --------------------------------------------------------------------------------------
with tab_coach:
    # FEATURE 21: Coach Chat Interface
    st.subheader("Coach Chat")
    st.caption(f"AI Backend: {ai_backend_label}")

    # FEATURE 22: Chat History Persistence
    if "coach_chat" not in st.session_state:
        st.session_state.coach_chat = []

    for role, msg in st.session_state.coach_chat:
        st.chat_message(role).markdown(msg)

    coach_q = st.chat_input("Ask a strategic question…")
    if coach_q:
        st.session_state.coach_chat.append(("user", coach_q))
        st.chat_message("user").markdown(coach_q)

        # FEATURE 23: RAG Context Integration
        ctx = rag.search(coach_q, k=k_ctx)
        ctx_text = "\n\n".join([f"[{i+1}] {c['text']}" for i,(_,c) in enumerate(ctx)])

        # FEATURE 24: News Integration in Prompts
        teams = [t.strip() for t in team_codes.split(",") if t.strip()]
        news_text = ""
        player_news_text = ""
        if include_news:
            try:
                news_items = cached_news(8, tuple(teams))
                news_text = "\n".join([f"- {n['title']} — {clean_html(n.get('summary',''))}" for n in news_items])
            except Exception as e:
                news_text = f"(news unavailable: {e})"

            players_list = [p.strip() for p in players_raw.split(",") if p.strip()]
            try:
                pitems = cached_player_news(tuple(players_list), teams[0] if teams else "", 2) if players_list else []
                player_news_text = "\n".join([f"- ({it['player']}) {it['title']} — {clean_html(it.get('summary',''))}" for it in pitems])
            except Exception as e:
                player_news_text = f"(player headlines unavailable: {e})"

        # FEATURE 49: Dynamic Context Building
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
        with st.chat_message("assistant"):
            ans = llm_answer(SYSTEM_PROMPT, user_msg, max_tokens=MAX_TOKENS, temperature_val=temperature)
            st.markdown(ans)
            st.session_state.coach_chat.append(("assistant", ans))
            st.session_state["last_coach_answer"] = ans

    # FEATURE 25: PDF Generation from Last Answer
    st.divider()
    st.caption("Create a PDF from the **last** assistant answer:")
    if st.button("Generate Edge Sheet PDF"):
        if not st.session_state.get("last_coach_answer"):
            st.warning("Ask a question first.")
        else:
            ans = st.session_state["last_coach_answer"]
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

# --------------------------------------------------------------------------------------
# 🎮 Game Mode (FEATURES 26-40)
# --------------------------------------------------------------------------------------
with tab_game:
    # FEATURE 26: Weekly Challenge System
    st.subheader("Weekly Challenge")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        # FEATURE 27: Username Input
        username = st.text_input("Username", value="guest")
    with c2:
        # FEATURE 28: Week Selection
        week = st.number_input("Week", min_value=1, max_value=18, value=1, step=1)
    with c3:
        # FEATURE 29: Confidence Slider
        usage_hint = st.slider("Confidence in plan", 0.0, 1.0, 0.6, 0.05)
    with c4:
        # FEATURE 30: Underdog Checkbox
        underdog = st.checkbox("Underdog Plan?", value=False)

    # FEATURE 31: Submission Status Display
    open_now = is_submission_open(int(week))
    st.info("Submissions open ✅" if open_now else "Submissions closed ⛔ for this week")

    # FEATURE 32: CSV Roster Upload (Team A & B)
    st.markdown("**Upload Rosters (CSV)** — optional but recommended  \n"
                "_Columns: Player, Pos, % Rostered_")
    a_file = st.file_uploader("Your Team Roster (CSV)", type=["csv"], key="a_csv")
    b_file = st.file_uploader("Opponent Roster (CSV)", type=["csv"], key="b_csv")

    # FEATURE 33: Market Delta Analysis & Display
    delta_val = 0.0
    roster_context_str = ""
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
            roster_context_str = f"Scalar market delta (B−A): {delta_val:.3f}\n\n{dpos.to_csv(index=False)}"
        except Exception as e:
            st.warning(f"Roster parsing error: {e}")

    # FEATURE 34: Edge Plan Input (Team, Opponent, Picks, Rationale)
    st.markdown("**Your Edge Plan**")
    team_focus = st.text_input("Your team code (e.g., PHI)", value="PHI")
    opponent = st.text_input("Opponent team code (e.g., DAL)", value="DAL")
    picks = st.text_area(
        "Your 2–3 key calls (one per line)",
        "1) 1st & 10, 12P — PA flood to TE seam — vs single-high — LB bites on run keys\n"
        "2) 3rd & medium, 11P — WR2 deep cross from stack — attack CB2 leverage\n"
        "3) Red zone — RB screen constraint — vs pressure tendency"
    )
    rationale = st.text_area(
        "Why this works (market vs pressure)",
        "WR2 undervalued; CB2 leverage issues; positive sentiment."
    )

    # FEATURE 35: LLM Market/Pressure Summary Generation
    if st.button("Generate Market/Pressure Summary (LLM)"):
        q = f"Summarize market vs narrative edges for {team_focus} vs {opponent} in one paragraph."
        ctx = rag.search(q, k=4)
        ctx_text = "\n\n".join([c['text'] for _,c in ctx])
        user_msg = "Return JSON only with keys delta_market_hint ([-2..+2]), sentiment_boost ([-2..+2]), reason."
        ans = llm_answer("You are a JSON generator.", f"{user_msg}\nContext:\n{ctx_text}", max_tokens=256, temperature_val=0.3)
        st.code(ans, language="json")
        st.session_state["_last_summary"] = ans

    # FEATURE 36: Plan Scoring Algorithm
    if st.button("Score My Plan (locks when deadline passes)"):
        if not open_now:
            st.error("Submissions are closed for this week.")
        else:
            hint = st.session_state.get("_last_summary", '{"delta_market_hint":0,"sentiment_boost":0,"reason":"n/a"}')
            try:
                # FEATURE 41: JSON Response Parsing
                js = json.loads(hint)
            except Exception:
                js = {"delta_market_hint": 0, "sentiment_boost": 0, "reason": "n/a"}

            delta_market = (delta_val + float(js.get("delta_market_hint", 0))) / (2 if a_file and b_file else 1)
            score = int(max(0, min(100,
                50 + (delta_market * 22.0) + (float(js.get('sentiment_boost', 0)) * 20.0) + (usage_hint * 8.0) + (5.0 if underdog else 0.0)
            )))
            st.success(f"Your Plan Score: {score}/100")

            # FEATURE 37: Badge Award System
            bs = award_badges(score, float(delta_market), float(js.get("sentiment_boost", 0)), underdog,
                              len([p for p in picks.splitlines() if p.strip()]))
            if bs:
                st.write("**Badges earned:**")
                for b in bs:
                    st.write(f"{b['emoji']} **{b['name']}** — {b['desc']}")

            # FEATURE 48: Session State Management
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

    # FEATURE 38: Weekly Leaderboard Display
    st.subheader("🏆 Weekly Leaderboard")
    try:
        st.dataframe(leaderboard(week=int(week)), use_container_width=True, hide_index=True)
    except Exception:
        st.caption("(leaderboard unavailable yet)")

    # FEATURE 39: Cumulative Ladder Display
    st.subheader("📈 Ladder (Cumulative)")
    try:
        st.dataframe(ladder(), use_container_width=True, hide_index=True)
    except Exception:
        st.caption("(ladder unavailable yet)")

    # FEATURE 40: Game Mode Chat Interface
    st.divider()
    st.subheader("Game Mode Chat")

    if "game_chat" not in st.session_state:
        st.session_state.game_chat = []

    for role, msg in st.session_state.game_chat:
        st.chat_message(role).markdown(msg)

    game_q = st.chat_input("Ask about lineup, matchups, or scoring assumptions…", key="gm_chat")
    if game_q:
        st.session_state.game_chat.append(("user", game_q))
        st.chat_message("user").markdown(game_q)

        # Build context: RAG + roster summary + picks/rationale
        ctx = rag.search(game_q, k=k_ctx)
        ctx_text = "\n\n".join([f"[{i+1}] {c['text']}" for i,(_,c) in enumerate(ctx)])

        plan_text = f"Team: {team_focus} vs {opponent}\nPicks:\n{picks}\nRationale:\n{rationale}"
        user_msg = f"""Use the context to advise fantasy lineup or game strategy.

Question:
{game_q}

Roster/market context:
{roster_context_str or '(no roster uploaded)'} 

Plan context:
{plan_text}

Edge System context:
{ctx_text}
"""
        with st.chat_message("assistant"):
            ans = llm_answer(SYSTEM_PROMPT, user_msg, max_tokens=MAX_TOKENS, temperature_val=temperature)
            st.markdown(ans)
            st.session_state.game_chat.append(("assistant", ans))

# --------------------------------------------------------------------------------------
# 📰 Headlines Mode (FEATURES 41-46)
# --------------------------------------------------------------------------------------
with tab_news:
    # FEATURE 41: Team News Display
    st.subheader("Latest Headlines")

    teams_for_news = [t.strip() for t in team_codes.split(",") if t.strip()]
    players_list = [p.strip() for p in players_raw.split(",") if p.strip()]
    
    # FEATURE 43: Two-Column Layout
    col_team, col_player = st.columns(2)

    # Gather feeds once for chat + display (cached)
    news_items, pitems = [], []
    try:
        news_items = cached_news(12, tuple(teams_for_news))
    except Exception as e:
        st.caption(f"(team/league news error: {e})")

    try:
        if players_list:
            pitems = cached_player_news(tuple(players_list), teams_for_news[0] if teams_for_news else "", 3)
    except Exception as e:
        st.caption(f"(player news error: {e})")

    # FEATURE 41: Team News Display
    with col_team:
        st.markdown("**Team / League**")
        if not news_items:
            st.caption("No headlines found (check team codes or refresh).")
        for n in news_items:
            st.write(f"**{n['title']}**")
            if n.get("summary"):
                # FEATURE 45: HTML Content Cleaning
                st.caption(clean_html(n["summary"]))
            if n.get("link"):
                # FEATURE 44: News Source Links
                st.markdown(f"[source]({n['link']})")
            st.write("---")

    # FEATURE 42: Player News Display
    with col_player:
        st.markdown("**Player Notes**")
        if not players_list:
            st.caption("Add player names in the sidebar to see player-specific items.")
        elif not pitems:
            st.caption("No player news right now.")
        else:
            for it in pitems:
                st.write(f"**({it['player']}) {it['title']}**")
                if it.get("summary"):
                    st.caption(clean_html(it["summary"]))
                if it.get("link"):
                    st.markdown(f"[source]({it['link']})")
                st.write("---")

    # FEATURE 46: Headlines Chat Interface
    st.divider()
    st.subheader("Headlines Chat")

    if "news_chat" not in st.session_state:
        st.session_state.news_chat = []

    for role, msg in st.session_state.news_chat:
        st.chat_message(role).markdown(msg)

    news_q = st.chat_input("Ask about injuries, narratives, or pressure angles…", key="news_chat_input")
    if news_q:
        st.session_state.news_chat.append(("user", news_q))
        st.chat_message("user").markdown(news_q)

        # Build news context text
        team_news_txt = "\n".join([f"- {n['title']} — {clean_html(n.get('summary',''))}" for n in news_items[:10]])
        player_news_txt = "\n".join([f"- ({it['player']}) {it['title']} — {clean_html(it.get('summary',''))}" for it in pitems[:10]])
        ctx = rag.search(news_q, k=max(3, k_ctx//2))  # smaller RAG here
        rag_txt = "\n\n".join([f"[{i+1}] {c['text']}" for i,(_,c) in enumerate(ctx)])

        user_msg = f"""Answer using headlines + Edge System context.

Question:
{news_q}

Team/League headlines:
{team_news_txt or '(none)'}

Player headlines:
{player_news_txt or '(none)'}

Edge System context:
{rag_txt or '(none)'}
"""
        with st.chat_message("assistant"):
            # FEATURE 50: Error Handling with Fallbacks
            ans = llm_answer(SYSTEM_PROMPT, user_msg, max_tokens=MAX_TOKENS, temperature_val=temperature)
            st.markdown(ans)
            st.session_state.news_chat.append(("assistant", ans))
