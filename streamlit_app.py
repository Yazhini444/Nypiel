import io
import os
import sys
from pathlib import Path

import streamlit as st
from PIL import Image
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

# ---------------------------------------------------------
# PATH SETUP
# ---------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from backend.app.inference import (
    load_models,
    predict_skin_concerns,
    predict_skin_type,
    validate_model_files,
)
from backend.app.recommendations import build_recommendations


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="nypiel — skin, but better",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)


@st.cache_resource(show_spinner="Loading trained skin models on CPU...")
def cached_models():
    return load_models()


missing_models, lfs_model_pointers = validate_model_files()
model_error = None
if missing_models:
    model_error = (
        "Required model file(s) are missing: "
        + ", ".join(missing_models)
        + ". Add the trained files to the repository before deploying."
    )
elif lfs_model_pointers:
    model_error = (
        "Required model file(s) are Git LFS pointers rather than downloaded "
        "weights: " + ", ".join(lfs_model_pointers) + ". Pull the LFS objects before deploying."
    )
else:
    try:
        cached_models()
    except Exception as exc:
        model_error = f"Trained models could not be loaded on CPU: {exc}"


# ---------------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------------
st.markdown(
    """
    <style>

    .stApp {
        background: #F8F4EC;
        color: #3E3027;
    }

    .main-title {
        text-align: center;
        font-size: 64px;
        font-weight: 700;
        letter-spacing: -2px;
        color: #4B392D;
        margin-top: 20px;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        font-size: 20px;
        color: #756557;
        margin-bottom: 40px;
    }

    .section-title {
        font-size: 30px;
        font-weight: 650;
        color: #4B392D;
        margin-top: 25px;
        margin-bottom: 15px;
    }

    .result-card {
        background: #FFFDF8;
        border: 1px solid #DED4C6;
        border-radius: 22px;
        padding: 25px;
        margin-bottom: 18px;
        box-shadow: 0 5px 18px rgba(75, 57, 45, 0.06);
    }

    .skin-type {
        font-size: 32px;
        font-weight: 700;
        color: #5B6B43;
    }

    .concern {
        display: inline-block;
        background: #EEE7D8;
        color: #4B392D;
        border-radius: 20px;
        padding: 8px 15px;
        margin: 5px;
        font-size: 15px;
    }

    .recommendation {
        background: #F3EFE6;
        border-left: 4px solid #7A8055;
        padding: 15px 18px;
        border-radius: 10px;
        margin-bottom: 12px;
    }

    .footer {
        text-align: center;
        color: #8A7A6B;
        margin-top: 60px;
        padding: 20px;
        font-size: 14px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.markdown(
    '<div class="main-title">nypiel</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">skin, but better.</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div style="text-align:center;color:#756557;font-size:17px;">
    Understand your skin. Discover your concerns. Build a routine around you.
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")


# ---------------------------------------------------------
# UPLOAD
# ---------------------------------------------------------
st.markdown(
    '<div class="section-title">🔍 Analyze your skin</div>',
    unsafe_allow_html=True,
)

if model_error:
    st.error(model_error)

uploaded_file = st.file_uploader(
    "Upload a clear face image",
    type=["jpg", "jpeg", "png"],
    help="Use a clear, well-lit image with your face visible.",
)


# ---------------------------------------------------------
# ANALYSIS
# ---------------------------------------------------------
if uploaded_file is not None:

    image_bytes = uploaded_file.getvalue()

    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception:
        st.error("The uploaded file is not a valid image. Please choose a JPEG or PNG file.")
        st.stop()

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:

        st.markdown(
            '<div class="section-title">Your image</div>',
            unsafe_allow_html=True,
        )

        st.image(
            image,
        )

    with col2:

        st.markdown(
            '<div class="section-title">Analysis</div>',
            unsafe_allow_html=True,
        )

        analyze = st.button(
            "✨ Analyze My Skin",
            type="primary",
        )

        if analyze and not model_error:

            with st.spinner(
                "Analyzing your skin..."
            ):

                try:

                    # -----------------------------------------
                    # SKIN TYPE
                    # -----------------------------------------
                    skin_result = predict_skin_type(
                        image_bytes
                    )

                    skin_type = skin_result["label"]
                    skin_confidence = skin_result["confidence"]

                    # -----------------------------------------
                    # CONCERNS
                    # -----------------------------------------
                    concerns = predict_skin_concerns(
                        image_bytes
                    )

                    # -----------------------------------------
                    # RECOMMENDATIONS
                    # -----------------------------------------
                    recommendations = build_recommendations(
                        skin_type,
                        concerns,
                    )

                    # Save results
                    st.session_state["skin_type"] = skin_type
                    st.session_state[
                        "skin_confidence"
                    ] = skin_confidence

                    st.session_state[
                        "concerns"
                    ] = concerns

                    st.session_state[
                        "recommendations"
                    ] = recommendations

                    st.session_state[
                        "analyzed"
                    ] = True

                except Exception as e:

                    st.error(
                        f"Analysis failed: {e}"
                    )


# ---------------------------------------------------------
# RESULTS
# ---------------------------------------------------------
if st.session_state.get(
    "analyzed",
    False,
):

    skin_type = st.session_state[
        "skin_type"
    ]

    confidence = st.session_state[
        "skin_confidence"
    ]

    concerns = st.session_state[
        "concerns"
    ]

    recommendations = st.session_state[
        "recommendations"
    ]

    st.divider()

    st.markdown(
        '<div class="section-title">Your skin profile</div>',
        unsafe_allow_html=True,
    )

    # -----------------------------------------
    # SKIN TYPE
    # -----------------------------------------
    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            f"""
            <div class="result-card">
                <div style="font-size:15px;color:#8A7A6B;">
                    DETECTED SKIN TYPE
                </div>

                <div class="skin-type">
                    {skin_type.title()}
                </div>

                <div style="margin-top:10px;color:#756557;">
                    Confidence: {confidence * 100:.0f}%
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # -----------------------------------------
    # CONCERNS
    # -----------------------------------------
    with col2:

        concern_html = ""

        if concerns:

            for concern in concerns:

                label = concern["label"]
                conf = concern["confidence"]

                concern_html += (
                    f'<span class="concern">'
                    f'{label.replace("_", " ").title()} '
                    f'· {conf * 100:.0f}%'
                    f'</span>'
                )

        else:

            concern_html = (
                "<p>No major concerns detected.</p>"
            )

        st.markdown(
            f"""
            <div class="result-card">

                <div style="font-size:15px;color:#8A7A6B;">
                    DETECTED CONCERNS
                </div>

                <div style="margin-top:12px;">
                    {concern_html}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    # -----------------------------------------
    # RECOMMENDATIONS
    # -----------------------------------------
    st.markdown(
        '<div class="section-title">🌿 Personalized recommendations</div>',
        unsafe_allow_html=True,
    )

    if recommendations:

        for rec in recommendations:

            st.markdown(
                f"""
                <div class="recommendation">

                    <strong>
                        {rec["ingredient"]}
                    </strong>

                    <br>

                    <span style="color:#756557;">
                        {rec["why"]}
                    </span>

                    <br><br>

                    <small>
                        <strong>When:</strong>
                        {rec["use"]}
                        &nbsp;&nbsp;·&nbsp;&nbsp;

                        <strong>Frequency:</strong>
                        {rec["frequency"]}
                    </small>

                </div>
                """,
                unsafe_allow_html=True,
            )

    else:

        st.info(
            "No specific recommendations available."
        )


# ---------------------------------------------------------
# GEMINI CHATBOT
# ---------------------------------------------------------
GEMINI_MODEL = "gemini-2.5-flash-lite"
GEMINI_MISSING_KEY_MESSAGE = (
    "Gemini API key is not configured. Please add GEMINI_API_KEY to your "
    "environment or Streamlit Secrets."
)
GEMINI_ERROR_MESSAGE = (
    "Sorry, I couldn't connect to the Gemini service right now. Please try again."
)
GEMINI_SYSTEM_INSTRUCTION = """
You are Nypiel, a practical skincare assistant. Answer questions about acne,
pimples, dark spots, pigmentation, acne marks, wrinkles, fine lines, pores,
blackheads, whiteheads, dry skin, oily skin, combination skin, normal skin,
sensitive skin, niacinamide, salicylic acid, hyaluronic acid, vitamin C,
retinol, ceramides, azelaic acid, glycolic acid, sunscreen, SPF, cleansers,
moisturizers, and skincare routines.

Keep responses practical and easy to understand. You do not diagnose medical
conditions. For serious, painful, worsening, or persistent skin concerns,
recommend consulting a dermatologist. Do not claim that Nypiel provides a
medical diagnosis.
"""


def get_gemini_api_key():
    try:
        secret_key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        secret_key = None
    return secret_key or os.getenv("GEMINI_API_KEY")


@st.cache_resource
def get_gemini_client(api_key):
    from google import genai

    return genai.Client(api_key=api_key)


def build_analysis_context():
    if not st.session_state.get("analyzed"):
        return "No Nypiel image analysis is available for this conversation."

    skin_type = st.session_state.get("skin_type", "Unknown").title()
    concerns = st.session_state.get("concerns", [])
    recommendations = st.session_state.get("recommendations", [])
    concern_labels = ", ".join(
        concern.get("label", "").replace("_", " ").title()
        for concern in concerns
    ) or "None detected"
    recommendation_names = ", ".join(
        recommendation.get("ingredient", "")
        for recommendation in recommendations
    ) or "None available"
    return (
        f"Skin type: {skin_type}\n"
        f"Detected concerns: {concern_labels}\n"
        f"Recommendations: {recommendation_names}"
    )


def generate_gemini_reply(client, chat_history):
    from google.genai import types

    contents = [
        types.Content(
            role=message["role"],
            parts=[types.Part.from_text(text=message["content"])],
        )
        for message in chat_history
    ]
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=(
                GEMINI_SYSTEM_INSTRUCTION
                + "\n\nCurrent Nypiel analysis context:\n"
                + build_analysis_context()
            ),
        ),
    )
    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")
    return response.text


st.divider()
st.markdown(
    '<div class="section-title">💬 Ask nypiel</div>',
    unsafe_allow_html=True,
)

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

for message in st.session_state["chat_history"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("Ask Nypiel about your skincare routine")
if question:
    st.session_state["chat_history"].append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    api_key = get_gemini_api_key()
    if not api_key:
        reply = GEMINI_MISSING_KEY_MESSAGE
    else:
        try:
            client = get_gemini_client(api_key)
            reply = generate_gemini_reply(client, st.session_state["chat_history"])
        except Exception:
            reply = GEMINI_ERROR_MESSAGE

    st.session_state["chat_history"].append({"role": "model", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)


# ---------------------------------------------------------
# DISCLAIMER
# ---------------------------------------------------------
st.divider()

st.markdown(
    """
    <div class="footer">
        nypiel provides AI-assisted skincare insights for
        informational purposes only.<br>
        It is not a medical diagnosis or a substitute for
        professional dermatological advice.
    </div>
    """,
    unsafe_allow_html=True,
)