
import uuid
import streamlit as st

from sales_agent import chat_with_sales_agent


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Oak & Ember Interiors",
    page_icon="🪑",
    layout="wide"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .oak-header {
        text-align: center;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
    }

    .oak-title {
        font-size: 34px;
        font-weight: 800;
        font-style: italic;
        margin-bottom: 5px;
    }

    .oak-subtitle {
        font-size: 15px;
        opacity: 0.75;
    }

    .disclosure {
        padding: 10px;
        border-radius: 8px;
        font-size: 13px;
        margin-bottom: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SESSION STATE
# =========================================================

if "thread_id" not in st.session_state:

    st.session_state.thread_id = str(
        uuid.uuid4()
    )


if "messages" not in st.session_state:

    st.session_state.messages = []


# =========================================================
# HEADER
# =========================================================

st.markdown(
    "<h1 style='text-align: center; font-style: italic;'>"
    "Oak & Ember Interiors - Sales Genie"
    "</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align: center; font-size: 16px;'>"
    "Intelligent Furniture Recommendations"
    "</p>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align: center; font-size: 18px;'>"
    "Please provide your furniture requirements below, specify "
    "furniture category, budget, and any specific features you desire. Kindly share your name," 
     "email address and contact number for further communication."
    "</p>",
    unsafe_allow_html=True
)


# =========================================================
# AI DISCLOSURE
# =========================================================

st.info(
    "AI assistance: Recommendations are generated from "
    "the approved Oak & Ember product catalog. "
    "Please verify current price and availability."
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        "### Oak & Ember Interiors - Sales Genie"
    )

    st.markdown(
        "Your AI furniture sales assistant."
    )

    st.divider()

    st.markdown(
        "### Conversation"
    )

    st.caption(
        f"Session ID: "
        f"{st.session_state.thread_id}"
    )

    if st.button(
        "Clear Conversation",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.session_state.thread_id = str(
            uuid.uuid4()
        )

        st.rerun()


# =========================================================
# DISPLAY CHAT HISTORY
# =========================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# =========================================================
# CHAT INPUT
# =========================================================

user_message = st.chat_input(
    "Tell me what furniture you're looking for..."
)


# =========================================================
# PROCESS MESSAGE
# =========================================================

if user_message:

    # -----------------------------------------------------
    # 1. SAVE USER MESSAGE
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )


    # -----------------------------------------------------
    # 2. DISPLAY USER MESSAGE IMMEDIATELY
    # -----------------------------------------------------

    with st.chat_message("user"):

        st.markdown(
            user_message
        )


    # -----------------------------------------------------
    # 3. CALL SALES AGENT
    # -----------------------------------------------------

    try:

        with st.chat_message("assistant"):

            with st.spinner(
                "Finding the best products for you..."
            ):

                response = chat_with_sales_agent(
                    user_message,
                    st.session_state.thread_id
                )


            # -------------------------------------------------
            # 4. DISPLAY RESPONSE IMMEDIATELY
            # -------------------------------------------------
            #
            # IMPORTANT:
            # This fixes the issue where the response only
            # appeared after entering the next message.
            #

            st.markdown(
                response
            )


    except Exception as e:

        response = f"Error: {e}"

        with st.chat_message("assistant"):

            st.error(
                response
            )

            st.exception(
                e
            )


    # -----------------------------------------------------
    # 5. SAVE ASSISTANT RESPONSE
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )

