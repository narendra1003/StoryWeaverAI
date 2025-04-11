import streamlit as st
from google import genai
from google.genai import types

# --- API Key Setup ---
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY")  # Access the API key from Streamlit secrets
if not GOOGLE_API_KEY:
    st.error("Please set the GOOGLE_API_KEY in Streamlit's secrets.")
    st.stop()

# Initialize genai client
client = genai.Client(api_key=GOOGLE_API_KEY)

# Title of the application
st.title('StoryWeaverAI')

# --- Initialize Session State ---
if "user_name" not in st.session_state:
    st.session_state["user_name"] = ""
if "story_history" not in st.session_state:
    st.session_state["story_history"] = ""
if "first_turn" not in st.session_state:
    st.session_state["first_turn"] = True
if "generated_story_parts" not in st.session_state:
    st.session_state["generated_story_parts"] = []

# --- Helper Function ---
def create_interactive_prompt(user_input, few_shot_examples, story_history=""):
    prompt = "Here are some examples of short stories based on a core emotion or a brief situation, often with a psychological twist:\n\n"
    for example in few_shot_examples:
        prompt += f"{example['type']}: {example['value']}\nStory: {example['story']}\n\n"

    if story_history:
        prompt += f"The story so far:\n{story_history}\n\n"

    prompt += f"Now, generate a short story based on the following user input:\n\n{user_input}\nStory:"
    return prompt

# --- Few-Shot Examples ---
few_shot_examples = [
    {
        "type": "Core Emotion",
        "value": "Dread",
        "story": "The silence in the house stretched, not peaceful, but taut like a wire about to snap. Every shadow seemed to lengthen, to whisper unseen threats. He knew, with a certainty that chilled him to the bone, that something was waiting. Something just beyond the edge of his perception."
    },
    {
        "type": "Core Emotion",
        "value": "Obsession",
        "story": "Her face filled every waking moment, and even bled into his dreams. He collected every discarded receipt, every stray hair, each a tiny fragment of her existence he could hold onto. It wasn't love, he told himself. It was… understanding."
    },
    {
        "type": "Brief Situation",
        "value": "Locked door",
        "story": "She rattled the handle again, a growing unease tightening her chest. It was her apartment. Her lock. But the bolt wouldn't budge. A faint scratching sound came from the other side. Not wood against metal. Something softer."
    },
    # Add more examples here...
]

# --- Initial greeting and name input ---
if not st.session_state["user_name"]:
    st.write("Hello, Welcome to the StoryWeaverAI. Please tell me how should I address you?")
    user_name_input = st.text_input("Your Name:", "")
    if st.button("Submit Name"):
        st.session_state["user_name"] = user_name_input.strip()
        introduction_prompt = f"Introduce yourself to {st.session_state['user_name']} as they will be using your capabilities to create an interactive story. Use their name in the explanation."
        response = client.chat.send_message(introduction_prompt) #changed from chat.send_message to client.chat.send_message
        st.markdown(response.text)  # Display the introduction
        st.session_state["first_turn"] = True  # Reset first turn

# --- Main Interaction ---
else:
    if st.session_state["first_turn"]:
        interaction_type = st.radio("Start with an 'emotion' or a 'situation'?", ("emotion", "situation"))
        if interaction_type:
            st.session_state["interaction_type"] = interaction_type
            st.session_state["first_turn"] = False

    else:
        continue_story = st.radio("Do you want to continue the story?", ("yes", "no"))
        if continue_story == "no":
            st.write("=" * 30)
            st.write("This is the story which you have generated:")
            st.write("=" * 30)
            st.write("\n".join(st.session_state['generated_story_parts']).strip())
            st.stop()  # Stop further execution
        elif continue_story == "yes":
            interaction_type = st.radio("Enter an 'emotion' or a 'situation' to guide the next part of the story:",
                                        ("emotion", "situation"))
            if interaction_type:
                st.session_state["interaction_type"] = interaction_type

    if "interaction_type" in st.session_state:
        if st.session_state["interaction_type"] == "emotion":
            core_emotion = st.text_input("Enter a core emotion (e.g., fear, joy, mystery):")
            if core_emotion:
                user_input = f"User guides with emotion: {core_emotion}"
                st.write(user_input)
                st.session_state["story_history"] += f"{user_input}\n"
                interactive_prompt = create_interactive_prompt(user_input, few_shot_examples,
                                                             st.session_state["story_history"])
                response = client.chat.send_message(interactive_prompt) #changed from chat.send_message to client.chat.send_message
                generated_text = response.text.replace("Story:", "").strip()
                st.write("\nGenerated Story:")
                st.write(generated_text)
                st.session_state["story_history"] += f"AI continues: {generated_text}\n"
                st.session_state["generated_story_parts"].append(generated_text)
                st.session_state["interaction_type"] = None  # Clear interaction type
        elif st.session_state["interaction_type"] == "situation":
            brief_situation = st.text_input("Enter a brief situation (e.g., empty swing set, whisper in the dark):")
            if brief_situation:
                user_input = f"User guides with situation: {brief_situation}"
                st.write(user_input)
                st.session_state["story_history"] += f"{user_input}\n"
                interactive_prompt = create_interactive_prompt(user_input, few_shot_examples,
                                                             st.session_state["story_history"])
                response = client.chat.send_message(interactive_prompt) #changed from chat.send_message to client.chat.send_message
                generated_text = response.text.replace("Story:", "").strip()
                st.write("\nGenerated Story:")
                st.write(generated_text)
                st.session_state["story_history"] += f"AI continues: {generated_text}\n"
                st.session_state["generated_story_parts"].append(generated_text)
                st.session_state["interaction_type"] = None  # Clear interaction type
                
