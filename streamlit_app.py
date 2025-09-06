import streamlit as st

st.set_page_config(page_title="NFL Edge Coach", page_icon="🏈", layout="wide")
st.title("🏈 NFL Edge Coach — Market Value × Narrative Pressure")

# ---- Safety imports (work even if some modules are missing) ----
def _try_import(path, alias=None):
    try:
        mod = __import__(path, fromlist=['*'])
        if alias:
            globals()[alias] = mod
        else:
            globals()[path.split('.')[-1]] = mod
        return True
    except Exception as e:
        st.warning(f"Optional module not found: {path} — {e}")
        return False

_have = {}
for m in ["app.rag", "app.model", "app.feeds", "app.player_news",
          "app.prompts", "app.pdf_export", "app.config",
          "app.state_store", "app.ownership_scoring",
          "app.badges", "app.opponent_ai", "app.whatif", "app.narrative_events"]:
    _have[m] = _try_import(m)

st.success("App loaded. If you see lots of yellow warnings, push the rest of the app files from the bundle.")

st.header("Quick Sanity Check")
st.write("• Python + Streamlit are installed ✅")
st.write("• This is the main file Streamlit Cloud needs: `app/streamlit_app.py`.")
st.write("• Once the rest of the modules are present, the full game features will appear here.")

st.divider()
st.subheader("What to do next")
st.write("""
1) Upload the remaining files from the bundle to your repo (if you haven't already).  
2) Rerun this app on Streamlit Cloud.  
3) You should see: Chat, Game Mode, Leaderboard, Fun Modes.  
""")

st.caption("Need help? Ping me here and paste any error from the Streamlit logs.")
