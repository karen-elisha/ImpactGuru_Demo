import streamlit as st

st.set_page_config(page_title="ImpactGuru Crowdfunding Demo", page_icon="💸")
st.title("💸 ImpactGuru Crowdfunding Prototype")
st.subheader("Choose to set up or donate to a crowdfunding campaign")

# --- Option selection ---
choice = st.radio("Select an action:", ["📁 Set up a Campaign", "💖 Donate to a Campaign"])

# Initialize session
if "campaigns" not in st.session_state:
    st.session_state.campaigns = {}

# --- Campaign Setup and Verification ---
if choice == "📁 Set up a Campaign":
    st.header("🛠️ Campaign Setup")

    name = st.text_input("Campaign Creator Name")
    campaign_name = st.text_input("Campaign Title", "Help Rahul's Cancer Treatment")
    goal = st.number_input("Goal Amount (₹)", min_value=1000, step=500)
    description = st.text_area("Campaign Description")

    uploaded_doc = st.file_uploader("Upload Verification Document (PDF/JPG/PNG)", type=["pdf", "jpg", "png"])

    if st.button("Verify & Create Campaign"):
        if name and campaign_name and goal and uploaded_doc:
            st.session_state.campaigns[campaign_name] = {
                "creator": name,
                "goal": goal,
                "raised": 0,
                "verified": True,
                "donors": [],
                "active": True  # ✅ Track if campaign is still accepting donations
            }
            st.success(f"✅ Campaign '{campaign_name}' verified and created successfully!")
        else:
            st.warning("Please fill in all details and upload a verification document.")

# --- Donation Section ---
elif choice == "💖 Donate to a Campaign":
    st.header("🎁 Make a Donation")

    if st.session_state.campaigns:
        selected = st.selectbox("Select a Verified Campaign", list(st.session_state.campaigns.keys()))
        campaign = st.session_state.campaigns[selected]

        # Check if campaign is still active
        if campaign["active"]:
            donor = st.text_input("Your Name")
            amount = st.number_input("Donation Amount (₹)", min_value=100)

            if st.button("Donate"):
                if donor and amount > 0:
                    if campaign["raised"] + amount <= campaign["goal"]:
                        campaign["raised"] += amount
                        campaign["donors"].append((donor, amount))
                        st.success(f"🎉 Thank you {donor}! You donated ₹{amount} to '{selected}'.")
                    else:
                        # If this donation exceeds the goal
                        st.warning("🚫 This campaign has already reached its goal. Donations are closed.")
                        campaign["active"] = False
                else:
                    st.warning("Please enter your name and donation amount.")

            # Show campaign progress
            st.write(f"**Goal:** ₹{campaign['goal']} | **Raised:** ₹{campaign['raised']}")
            st.progress(min(campaign["raised"] / campaign["goal"], 1.0))

            # If goal reached
            if campaign["raised"] >= campaign["goal"]:
                campaign["active"] = False
                st.success(f"🎯 Goal achieved! ₹{campaign['raised']} raised successfully.")
                st.info(f"💰 Funds are being transferred securely to beneficiary **{campaign['creator']}**.")
        else:
            st.warning(f"🚫 Campaign '{selected}' has ended. Goal achieved or donations closed.")

        # Show donor list
        st.subheader("💞 Donor List")
        if campaign["donors"]:
            for d, a in campaign["donors"]:
                st.write(f"- {d} donated ₹{a}")
        else:
            st.write("No donors yet. Be the first to contribute!")

    else:
        st.info("No verified campaigns available. Please create one first.")

