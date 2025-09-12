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

# =============================================================================
# OpenAI GPT-3.5 Integration (ONLY MODEL AVAILABLE)
# =============================================================================
def openai_chat(system_prompt: str, user_prompt: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
    """OpenAI GPT-3.5 Turbo Chat Completion"""
    try:
        import openai
        
        # Get API key from environment
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            return generate_fallback_response(user_prompt)
        
        # Set up client
        client = openai.OpenAI(api_key=openai_key)
        
        # Make API call to GPT-3.5 Turbo only
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
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
        st.error("OpenAI library not installed. Please add 'openai>=1.0.0' to requirements.txt")
        return generate_fallback_response(user_prompt)
    except Exception as e:
        error_msg = str(e)
        if "api_key" in error_msg.lower():
            st.warning("OpenAI API key not configured. Using fallback responses.")
            return generate_fallback_response(user_prompt)
        elif "rate_limit" in error_msg.lower():
            st.warning("OpenAI rate limit exceeded. Please try again in a moment.")
            return generate_fallback_response(user_prompt)
        else:
            st.warning("OpenAI temporarily unavailable. Using fallback responses.")
            return generate_fallback_response(user_prompt)

def generate_fallback_response(user_prompt: str) -> str:
    """High-quality fallback responses when OpenAI is unavailable"""
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

    elif any(word in prompt_lower for word in ['rb', 'running back']):
        return """🏃 **RB Strategic Framework:**

**Target Criteria:**
• 15+ carries + positive game script (team favored)
• Teams with 25+ rush attempts per game average
• Opponents allowing 4.5+ YPC or 120+ rush yards

**Weather Advantage Scenarios:**
• Heavy wind/rain = increased rushing attempts
• Cold weather = possession-based offense prioritized
• Snow conditions = major ground game advantage

**Leverage Play Identification:**
• Backup RBs with starter questionable/out
• RBs with receiving upside (8+ targets possible)
• Low-owned workhorses in favorable matchup spots

**Red Flags to Avoid:**
• RBs vs top-5 run defenses (success rate <40%)
• Negative game script situations (7+ point underdogs)
• Timeshare backfields without clear lead back"""

    elif any(word in prompt_lower for word in ['wr', 'receiver', 'wide receiver']):
        return """🎯 **WR Analysis Framework:**

**Target Priority Metrics:**
• 8+ targets per game average (volume foundation)
• Red zone usage (goal line fades, corner routes)
• Air yards per target >10 (big play potential)

**Stacking Strategy:**
• Pair with same-team QB for correlation upside
• Target WR1s in high-total games (O/U 47+)
• Avoid WRs vs elite cornerback shadows

**Weather Impact Guidelines:**
• 15+ MPH wind: Fade deep threats, target possession receivers
• Rain/Snow: Prioritize slot receivers, avoid boundary deep balls
• Dome games: Full passing game efficiency expected

**Leverage Spot Identification:**
• WR2s with WR1 questionable (target bump)
• Slot receivers vs linebacker coverage mismatches
• Volume receivers on trailing teams (garbage time)"""

    elif any(word in prompt_lower for word in ['te', 'tight end']):
        return """🏈 **TE Strategic Approach:**

**Elite Tier (Matchup Proof):**
• Travis Kelce - Target share leader, red zone magnet
• Mark Andrews - Elite when healthy, target hog
• T.J. Hockenson - Consistent volume, TD upside

**Value Target Criteria:**
• TEs vs bottom-10 defenses against TEs
• TEs with 6+ targets per game average
• Red zone specialists in positive game scripts

**Streaming Opportunities:**
• Backup TEs with starter injured/out
• TEs in high-total games (shootout potential)
• TEs with established QB chemistry"""

    elif any(word in prompt_lower for word in ['strategy', 'edge', 'market']):
        return """📊 **Strategic Edge Framework:**

**Market Value Identification:**
• Players with elite production but low ownership (<15%)
• Pricing inefficiencies (underpriced relative to projection)
• Narrative bias creating opportunity (injury return, tough matchup perception)

**Narrative Pressure Analysis:**
• Public overreaction to recent performance trends
• Media storylines driving ownership patterns
• Weather/injury concerns creating leverage spots

**Tournament Strategy Core:**
• Stack correlations (QB+WR, RB+DEF)
• Contrarian plays in fundamentally good spots
• Ceiling-focused lineup construction approach

**Cash Game Foundation:**
• Floor prioritization (70%+ of projection hit rate)
• Injury/weather risk avoidance
• Consistent target share reliability metrics"""

    elif any(word in prompt_lower for word in ['lineup', 'build', 'construction']):
        return """🏗️ **Lineup Construction Guide:**

**Cash Game Foundation:**
• QB: High floor, 20+ point potential
• RB1/RB2: 15+ carry workhorses
• WR1/WR2: 8+ target reliable options
• TE: Consistent 5+ targets
• FLEX: Best available value
• DEF: Home favorites or vs backup QB

**Tournament Approach:**
• QB: Ceiling + low ownership combination
• RB: Leverage spots or elite with room
• WR: Correlation plays or contrarian value
• TE: Either elite or punt with upside
• FLEX: Highest ceiling available
• DEF: Upside matchups or salary relief

**Stacking Strategies:**
• Primary: QB + WR/TE from same team
• Bring-back: Add opposing skill position
• Defense: Same team as RB for script correlation"""

    elif any(word in prompt_lower for word in ['weather', 'wind', 'rain']):
        return """🌦️ **Weather Impact Analysis:**

**High Wind (15+ MPH):**
• Fade passing games, especially deep routes
• Target rushing attacks and short passing
• Consider game total unders
• Avoid kickers for long attempts

**Rain/Precipitation:**
• Fumble risk increases significantly
• Ball control offenses favored
• Target TEs and slot receivers
• Fade outdoor passing attacks

**Cold Weather (<32°F):**
• Favor teams used to cold conditions
• Ball handling becomes more difficult
• Kickers lose accuracy on 45+ yard attempts
• Dome teams struggle in elements

**Strategy Adjustments:**
• Pivot from WRs to RBs in bad weather
• Target indoor games for passing
• Stack teams in dome environments
• Fade chalk plays affected by weather"""

    else:
        return f"""🤖 **GRIT Strategic Analysis:**

**Your Question:** {user_prompt}

**Market Value × Narrative Pressure Framework Applied:**

**Key Analytical Angles:**
• Identify players with elite underlying metrics but low public exposure
• Analyze pricing inefficiencies in salary vs projection gaps
• Assess narrative bias creating market opportunities

**Strategic Recommendations:**
• Look for contrarian plays in fundamentally sound spots
• Consider correlation stacking for tournament leverage
• Balance ceiling plays with floor reliability

**Next Steps:**
Review your Edge System documents for position-specific insights and current market dynamics.

*This analysis uses the strategic framework principles developed for competitive advantage.*"""

# =============================================================================
# Cached resources
# =============================================================================
@st.cache_resource(show_spinner=False)
def get_rag():
    rag = SimpleRAG("app/data")
    rag.build()
    return rag

@st.cache_resource(show_spinner=False)
def get_model(backend: str, model_name: str):
    # Only used for legacy compatibility, not actually needed with OpenAI-only setup
    try:
        return LLMBackend(backend=backend, model_name=model_name)
    except:
        return None  # Gracefully handle HuggingFace issues

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
# Sidebar controls
# =============================================================================
with st.sidebar:
    st.subheader("AI Assistant Settings")
    
    # Show AI status
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        st.success("AI Assistant: Ready")
        st.caption("Using OpenAI GPT-3.5 Turbo for intelligent responses")
    else:
        st.info("AI Assistant: Offline")
        st.caption("Using expert-written responses (still very effective)")

    st.divider()
    st.subheader("Response Settings")

    # Response length control
    resp_len = st.select_slider(
        "Response length", options=["Short","Medium","Long"],
        value="Medium",
        help="Short≈256 tokens, Medium≈512, Long≈800."
    )
    MAX_TOKENS = {"Short": 256, "Medium": 512, "Long": 800}[resp_len]

    # AI creativity control
    temperature = st.slider(
        "AI Creativity", 0.1, 1.0, 0.7, 0.1,
        help="Lower = more focused, Higher = more creative"
    )

    # RAG retrieval settings
    latency_mode = st.selectbox(
        "Analysis depth", ["Quick","Balanced","Thorough"],
        index=1,
        help="Controls how much context from your Edge documents is used."
    )
    default_k = {"Quick": 3, "Balanced": 5, "Thorough": 8}[latency_mode]
    k_ctx = st.slider(
        "Context passages", 3, 10, default_k,
        help="How many relevant document sections are included for context."
    )

    st.divider()
    st.subheader("News & Context")
    
    include_news = st.checkbox(
        "Include current headlines", True,
        help="Adds relevant NFL news to responses for better context."
    )
    team_codes = st.text_input("Focus teams (comma-separated)", "PHI, DAL")
    players_raw = st.text_area("Focus players (comma-separated)", "Jalen Hurts, CeeDee Lamb")
    st.session_state["team_codes"] = team_codes

    st.divider()
    if st.button("Refresh Knowledge Base"):
        st.cache_resource.clear()
        st.cache_data.clear()
        st.success("Knowledge base refreshed!")
        st.rerun()

# Main AI function - ONLY uses GPT-3.5 Turbo
def llm_answer(system_prompt: str, user_prompt: str, max_tokens: int = 512, temperature_val: float = 0.7) -> str:
    return openai_chat(system_prompt, user_prompt, max_tokens, temperature_val)

# =============================================================================
# Tabs
# =============================================================================
tab_coach, tab_game, tab_news = st.tabs(["📋 Coach Mode", "🎮 Game Mode", "📰 Headlines"])

# --------------------------------------------------------------------------------------
# 📋 Coach Mode (chat + on-demand PDF)
# --------------------------------------------------------------------------------------
with tab_coach:
    st.subheader("Coach Chat")
    st.caption("AI-powered fantasy football strategy analysis")

    if "coach_chat" not in st.session_state:
        st.session_state.coach_chat = []

    for role, msg in st.session_state.coach_chat:
        st.chat_message(role).markdown(msg)

    coach_q = st.chat_input("Ask a strategic question…")
    if coach_q:
        st.session_state.coach_chat.append(("user", coach_q))
        st.chat_message("user").markdown(coach_q)

        # RAG context
        ctx = rag.search(coach_q, k=k_ctx)
        ctx_text = "\n\n".join([f"[{i+1}] {c['text']}" for i,(_,c) in enumerate(ctx)])

        # optional news
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

    # On-demand PDF export
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
# 🎮 Game Mode (upload + scoring + chat)
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

    if st.button("Generate Market/Pressure Summary (AI)"):
        q = f"Summarize market vs narrative edges for {team_focus} vs {opponent} in one paragraph."
        ctx = rag.search(q, k=4)
        ctx_text = "\n\n".join([c['text'] for _,c in ctx])
        user_msg = "Return JSON only with keys delta_market_hint ([-2..+2]), sentiment_boost ([-2..+2]), reason."
        ans = llm_answer("You are a JSON generator.", f"{user_msg}\nContext:\n{ctx_text}", max_tokens=256, temperature_val=0.3)
        st.code(ans, language="json")
        st.session_state["_last_summary"] = ans

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

    # Game Mode Chat
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
# 📰 Headlines tab (feeds + chat)
# --------------------------------------------------------------------------------------
with tab_news:
    st.subheader("Latest Headlines")

    teams_for_news = [t.strip() for t in team_codes.split(",") if t.strip()]
    players_list = [p.strip() for p in players_raw.split(",") if p.strip()]
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

    with col_team:
        st.markdown("**Team / League**")
        if not news_items:
            st.caption("No headlines found (check team codes or refresh).")
        for n in news_items:
            st.write(f"**{n['title']}**")
            if n.get("summary"):
                st.caption(clean_html(n["summary"]))
            if n.get("link"):
                st.markdown(f"[source]({n['link']})")
            st.write("---")

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

    # Headlines Chat
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
            ans = llm_answer(SYSTEM_PROMPT, user_msg, max_tokens=MAX_TOKENS, temperature_val=temperature)
            st.markdown(ans)
            st.session_state.news_chat.append(("assistant", ans))
