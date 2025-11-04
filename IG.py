import streamlit as st
import google.generativeai as genai

# -------------------- SETUP --------------------
st.set_page_config(page_title="ImpactGuru AI Chatbot", page_icon="💸", layout="centered")

# Configure Gemini 2.5 model
GEMINI_API_KEY = "AIzaSyAD1qMzqHvojkO70dmZxly3dKnGYqxEaxw"  # 🔑 Replace with your key
genai.configure(api_key=GEMINI_API_KEY)

try:
    model = genai.GenerativeModel("models/gemini-2.5-flash")  # Fast + capable
    st.sidebar.success("✅ Gemini API connected successfully!")
except Exception as e:
    st.sidebar.error(f"⚠️ Gemini connection failed: {e}")

# -------------------- SESSION --------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "campaigns" not in st.session_state:
    st.session_state.campaigns = {}

# -------------------- STYLES --------------------
st.markdown("""
<style>
    .stTextInput input {
        font-size: 1.1rem;
        border-radius: 10px;
        padding: 8px;
    }
    .stButton>button {
        background-color: #00BFA6;
        color: white;
        border-radius: 10px;
        font-size: 1.1rem;
        padding: 8px 16px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #008f7a;
    }
    .chat-bubble-user {
        background-color: #DCF8C6;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
    }
    .chat-bubble-bot {
        background-color: #E7E7E7;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# -------------------- HEADER --------------------
st.title("💸 ImpactGuru Crowdfunding Assistant")
st.caption("🤖 Chatbot + Campaign Setup + Donations — powered by Gemini 2.5")

# -------------------- SIDEBAR NAVIGATION --------------------
choice = st.radio("Select an action:", ["🤖 Chat with ImpactBot", "📁 Set up a Campaign", "💖 Donate to a Campaign"])

# -------------------- STREAMING RESPONSE FUNCTION --------------------
def stream_gemini_response(prompt):
    """Stream Gemini response as it’s generated"""
    response_text = ""
    placeholder = st.empty()
    for chunk in model.generate_content(prompt, stream=True):
        if chunk.text:
            response_text += chunk.text
            placeholder.markdown(f"🤖 **ImpactBot:** {response_text}▌")
    placeholder.markdown(f"🤖 **ImpactBot:** {response_text}")
    return response_text.strip()

# -------------------- CHATBOT SECTION --------------------
if choice == "🤖 Chat with ImpactBot":
    st.header("🤖 ImpactBot — Your Smart Crowdfunding Assistant")
    st.caption("💬 Ask about campaigns, donations, 80G benefits, or medical fundraisers!")

    chat_container = st.container()
    with chat_container:
        for chat in st.session_state.chat_history:
            if chat["role"] == "user":
                st.markdown(f"<div class='chat-bubble-user'>🧑‍💬 <b>You:</b> {chat['message']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-bubble-bot'>🤖 <b>ImpactBot:</b> {chat['message']}</div>", unsafe_allow_html=True)

    user_input = st.text_input("Type your message:", key="chat_input")

    if st.button("Send"):
        if user_input:
            # Add user message
            st.session_state.chat_history.append({"role": "user", "message": user_input})

            # Add short context memory (last 5 exchanges)
            context = "\n".join([f"{m['role']}: {m['message']}" for m in st.session_state.chat_history[-5:]])
            prompt = f"""
            You are ImpactBot, an AI assistant for ImpactGuru — a crowdfunding platform for healthcare and social causes.
            Be empathetic and concise. Guide users on:
            - Creating or verifying campaigns (especially for pregnant women, premature babies, etc.)
            - Donation process, trust & transparency
            - 80G tax benefits
            - Platform policies & verification steps
            Chat history:
            {context}
            User: {user_input}
            """

            with st.spinner("ImpactBot is thinking... 🤖"):
                bot_reply = stream_gemini_response(prompt)

            # Add bot reply
            st.session_state.chat_history.append({"role": "bot", "message": bot_reply})

            st.rerun()

# -------------------- CAMPAIGN CREATION SECTION --------------------
elif choice == "📁 Set up a Campaign":
    st.header("🛠️ Create a New Campaign")

    name = st.text_input("👤 Campaign Creator Name")
    campaign_name = st.text_input("📌 Campaign Title", "Help Baby Aarav Recover from Premature Birth")
    goal = st.number_input("🎯 Goal Amount (₹)", min_value=1000, step=500)
    description = st.text_area("📝 Campaign Description")
    uploaded_doc = st.file_uploader("📎 Upload Verification Document", type=["pdf", "jpg", "png"])

    if st.button("Verify & Create"):
        if name and campaign_name and goal and uploaded_doc:
            st.session_state.campaigns[campaign_name] = {
                "creator": name,
                "goal": goal,
                "raised": 0,
                "verified": True,
                "donors": []
            }
            st.success(f"✅ '{campaign_name}' verified and created successfully!")
        else:
            st.warning("⚠️ Please fill all details and upload a document.")

# -------------------- DONATION SECTION --------------------
elif choice == "💖 Donate to a Campaign":
    st.header("🎁 Make a Donation")

    if st.session_state.campaigns:
        selected = st.selectbox("Choose a Verified Campaign", list(st.session_state.campaigns.keys()))
        donor = st.text_input("💌 Your Name")
        amount = st.number_input("💰 Donation Amount (₹)", min_value=100)

        if st.button("Donate"):
            if donor and amount > 0:
                campaign = st.session_state.campaigns[selected]
                campaign["raised"] += amount
                campaign["donors"].append((donor, amount))
                st.success(f"🎉 Thank you {donor}! You donated ₹{amount} to '{selected}'.")
            else:
                st.warning("Please enter your name and a valid amount.")

        campaign = st.session_state.campaigns[selected]
        st.write(f"**Goal:** ₹{campaign['goal']} | **Raised:** ₹{campaign['raised']}")
        st.progress(min(campaign["raised"] / campaign["goal"], 1.0))

        st.subheader("💞 Donor List")
        if campaign["donors"]:
            for d, a in campaign["donors"]:
                st.write(f"- {d} donated ₹{a}")
        else:
            st.write("No donors yet — be the first!")
    else:
        st.info("No verified campaigns available. Please create one first.")
