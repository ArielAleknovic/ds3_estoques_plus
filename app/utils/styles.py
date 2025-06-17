def styles(img_base64: str) -> str:
    return f"""
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(255, 255, 255, 0.6), rgba(255, 255, 255, 0.6)), url("{img_base64}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #1a1a1a !important;
    }}

    section[data-testid="stSidebar"] > div:first-child {{
        background-color: rgba(255, 255, 255, 0.85);
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid #ddd;
    }}

    .css-1d391kg, .css-qri22k, .css-1v3fvcr {{
        color: #4a2c2a !important;
        font-weight: 600;
    }}

    .stRadio > label {{
        color: #4a2c2a !important;
        font-weight: bold;
    }}

    .stRadio > div > label[data-baseweb="radio"] {{
        background-color: #d4bdae;
        padding: 0.5em 1em;
        border-radius: 10px;
        margin-bottom: 5px;
        color: #1a1a1a !important;
    }}

    .stRadio > div > label[data-selected="true"] {{
        background-color: #8b5e3c !important;
        color: #ffffff !important;
    }}

    .stButton > button {{
        background-color: #4a2c2a;
        color: white;
        font-weight: bold;
        border-radius: 8px;
    }}

    h1, h2, h3, h4, h5, h6 {{
        color: #1a1a1a !important;
    }}
    </style>
    """
