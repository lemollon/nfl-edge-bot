/* BUTTONS - ENHANCED VISIBILITY */
    .stButton > button {
        background: linear-gradient(90deg, #00ff41 0%, #0066cc 100%) !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.8) !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3) !important;
    }
    
    /* BUTTON TEXT VISIBILITY FIX */
    .stButton > button span,
    .stButton > button div,
    .stButton > button * {
        color: #000000 !important;
        font-weight: bold !important;
        text-shadow: none !important;
    }
    
    /* CRITICAL FIX FOR INSTANT ANALYSIS BUTTONS - DARK BACKGROUND */
    .stButton > button[kind="secondary"] {
        background: #262626 !important;
        color: #ffffff !important;
        border: 2px solid #00ff41 !important;
    }
    
    .stButton > button[kind="secondary"] span,
    .stButton > button[kind="secondary"] div,
    .stButton > button[kind="secondary"] * {
        color: #ffffff !important;
        background: transparent !important;
    }
    
    /* NUCLEAR OPTION - FORCE DARK BACKGROUNDS ON PROBLEM BUTTONS */
    .stButton button:not([kind="primary"]) {
        background: #262626 !important;
        color: #ffffff !important;
        border: 2px solid #00ff41 !important;
    }
    
    .stButton button:not([kind="primary"]) * {
        color: #ffffff !important;
        background: transparent !important;
    }
    
    /* FINAL FALLBACK - TARGET ANY REMAINING INVISIBLE TEXT */
    .stButton button[style*="background: rgb(255, 255, 255)"],
    .stButton button[style*="background-color: white"],
    .stButton button[style*="background-color: #ffffff"] {
        background: #262626 !important;
        color: #ffffff !important;
        border: 2px solid #00ff41 !important;
    }
