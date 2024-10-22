import streamlit as st
import requests
import json
import base64

# Streamlit App
st.set_page_config(layout="wide")
st.title('Design Project Assistant')

# Creating columns for left and right layout
col1, col2 = st.columns(2)

# Placeholder questions in the left column
with col1:
    st.subheader("General Overview")
    if st.button("Autofill Placeholder Values"):
        st.session_state["vision_goals"] = "I’m aiming for a fresh, functional design that suits my lifestyle and personal taste."
        st.session_state["primary_function"] = "This will be a multi-purpose room used for both work and relaxation."
        st.session_state["traffic"] = "It will have moderate traffic throughout the day."
        st.session_state["children_use"] = "Yes, this space needs to be kid-friendly and safe."
        st.session_state["personal_shared"] = "This room will be shared with family and occasional guests."
        st.session_state["atmosphere"] = "I’d like it to feel serene and inviting, but also energizing."
        st.session_state["budget"] = "I’m looking to stay within a mid-range budget, but open to flexibility."
        st.session_state["existing_pieces"] = "I’d like to keep a few key pieces of furniture and some family heirlooms."

    vision_goals = st.text_area("Can you describe your vision or goals for this project?", key="vision_goals", placeholder="I’m aiming for a fresh, functional design that suits my lifestyle and personal taste.")

    st.subheader("Room Use & Function")
    primary_function = st.text_input("What is the primary function of this space?", key="primary_function", placeholder="This will be a multi-purpose room used for both work and relaxation.")
    traffic = st.text_input("How much daily traffic does this room get?", key="traffic", placeholder="It will have moderate traffic throughout the day.")
    children_use = st.text_input("Will children use this room? If so, what should be considered for them?", key="children_use", placeholder="Yes, this space needs to be kid-friendly and safe.")
    personal_shared = st.text_input("Will this space be primarily for personal use, or shared?", key="personal_shared", placeholder="This room will be shared with family and occasional guests.")

    st.subheader("Emotions")
    atmosphere = st.text_input("What feeling or atmosphere do you want this space to create?", key="atmosphere", placeholder="I’d like it to feel serene and inviting, but also energizing.")

    st.subheader("Budget")
    budget = st.text_input("Do you have a budget in mind for this project?", key="budget", placeholder="I’m looking to stay within a mid-range budget, but open to flexibility.")

    st.subheader("Existing Furniture/Items")
    existing_pieces = st.text_area("Are there any existing pieces or elements you’d like to incorporate into the design?", key="existing_pieces", placeholder="I’d like to keep a few key pieces of furniture and some family heirlooms.")

    st.subheader("Upload Images")
    uploaded_images = st.file_uploader("Upload images that represent the style and vibe you want for this project", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])

    # Setting the context for the API call
    st.subheader("API Call Setup")
    api_key = st.text_input("OpenAI API Key", type="password")
    context = st.text_area("Context for ChatGPT:", "You’re helping to interpret responses from a customer about their upcoming design project. Extract key details from their answers to display them as clear project specifications. All details are optional, so if any information is not provided, leave it blank or state \"N/A\" for that item. Highlight details such as the timeframe, budget, and any uploaded images that provide a sense of the style or vibe desired.\n\nAdditionally, provide three outputs:\n1. Extract key elements from the customer's input (timeline, budget, and the style you extract from the image they provide if any), displayed separately at the top for quick reference in a structured format.\n2. A friendly, human-like response that acknowledges the customer's design inputs and summarizes them concisely.\n3. A very short summary of the uploaded image(s) and how they influenced the design suggestions.\n\nThe customer is providing details about their design project. Your role is to extract key information, provide a friendly summary, and - in a separate section - make a very brief helpful comment / suggest additional considerations to ensure a successful collaboration between the customer and the interior designer (keep it short). The customer's preferences and requirements are fully optional, and your summary should be helpful for both the customer and the designer to move forward with the project confidently. Be concise.")
    chat_message = st.text_area("Chat Message (use {variable_name} for placeholders):", "Here’s the customer’s input:\n\nGeneral Overview: \"{vision_goals}\"\n\nRoom Use & Function:\n\nPrimary Function: \"{primary_function}\"\n\nTraffic Level: \"{traffic}\"\n\nKids: \"{children_use}\"\n\nPersonal or Shared: \"{personal_shared}\"\n\nEmotions: \"{atmosphere}\"\n\nBudget: \"{budget}\"\n\nExisting Furniture/Items: \"{existing_pieces}\"\n\nUploaded Images: {uploaded_images}\n\nUsing this information, please extract and summarize the following project specs. If any information is missing or not mentioned, simply note it as \"Unknown\"\n\nTimeframe:\n\nBudget:\n\nStyle:\n\nExpected Output Example:\n\nTimeframe: N/A (Customer hasn’t provided a specific deadline)\n\nBudget: {budget}\n\nStyle: Extracted from uploaded images\n\nSummary of Project:\n\nShort Summary of Uploaded Images:\n\"{uploaded_images}\"")

    if st.button("Submit"):
        if not api_key:
            st.warning("Please provide your API key to proceed.")
        else:
            try:
                # Convert uploaded images to base64 strings and add descriptions to include in prompt (if any images are uploaded)
                image_contents = []
                image_summary = "No images uploaded"
                style_summary = "N/A"
                if uploaded_images:
                    for img in uploaded_images:
                        img_bytes = img.read()
                        encoded_img = base64.b64encode(img_bytes).decode('utf-8')
                        image_contents.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_img}"}})
                    image_summary = "The uploaded images suggest a preference for certain colors, textures, or styles that have been incorporated into the design recommendations."
                    # Extract style summary from images
                    style_summary = "Modern, family-friendly with light tones and natural materials"  # Example extraction

                # Replace missing placeholders with "N/A" to avoid KeyError
                prompt = chat_message.format(
                    vision_goals=vision_goals if vision_goals else "N/A",
                    primary_function=primary_function if primary_function else "N/A",
                    traffic=traffic if traffic else "N/A",
                    children_use=children_use if children_use else "N/A",
                    personal_shared=personal_shared if personal_shared else "N/A",
                    atmosphere=atmosphere if atmosphere else "N/A",
                    budget=budget if budget else "N/A",
                    existing_pieces=existing_pieces if existing_pieces else "N/A",
                    uploaded_images=image_summary
                )
                prompt = f"{context}\n\n{prompt}"

                # API call to ChatGPT
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }
                data = {
                    "model": "gpt-4o",
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                }

                response = requests.post("https://api.openai.com/v1/chat/completions", json=data, headers=headers, timeout=60)

                # Handle API Response
                if response.status_code == 200:
                    chat_response = response.json().get("choices", [])[0].get("message", {}).get("content", "No response from API.")
                    if "Human-Like Summary for Customer:" in chat_response:
                        key_elements, human_summary = chat_response.split("Human-Like Summary for Customer:")
                        with col2:
                            st.subheader("Key Elements Summary")
                            st.write(f"**Timeframe**: Extracted from input or N/A")
                            st.write(f"**Budget**: {budget}")
                            st.write(f"**Style**: {style_summary}")
                            st.subheader("ChatGPT Response")
                            st.write(human_summary.strip())
                    else:
                        with col2:
                            st.write(chat_response)
                else:
                    with col2:
                        st.error(f"Error: {response.status_code}, {response.text}")

            except requests.exceptions.RequestException as e:
                st.error(f"An error occurred: {e}")

            # Display the entire request and response for debugging purposes
            with st.expander("Debugging Information"):
                st.subheader("Request Data")
                st.json(data)
                st.subheader("Response Data")
                if response.status_code == 200:
                    st.json(response.json())
                else:
                    st.text(response.text)
