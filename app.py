import streamlit as st
from google import genai
from google.genai import types

# Set up the page
st.set_page_config(
    page_title="Interactive Story Generator",
    page_icon="📖",
    layout="centered"
)

# Title and introduction
st.title("📖 Interactive Story Generator")
st.markdown("Welcome to the Interactive Story Generator powered by Google Gemini!")

# Few Shot prompt examples for the model
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

# Get API key
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]

# Get user name
user_name = st.text_input("Please share your name:", key="user_name").strip()

if user_name:  # Only proceed if user has entered a name
    # Initialize the chat client
    client = genai.Client(api_key=GOOGLE_API_KEY)
    chat = client.chats.create(model="gemini-2.0-flash")
    
    # Introduction from the AI
    introduction_prompt = f"""
    Introduce yourself to {user_name} as they will be using your capabilities 
    to create an interactive story. Use their name in the explanation.
    Be friendly and enthusiastic about storytelling!
    """
    
    if st.button("Start Storytelling Session"):
        with st.spinner("Getting the storyteller ready..."):
            response = chat.send_message(introduction_prompt)
            
        # Display the introduction
        st.markdown("---")
        st.subheader("Your Storytelling Companion Says:")
        st.markdown(response.text)
        
        # Now add interactive story generation
        st.markdown("---")
        st.subheader("Let's Create a Story Together!")
        
        # Story parameters
        col1, col2 = st.columns(2)
        with col1:
            genre = st.selectbox(
                "Choose a genre:",
                ["Fantasy", "Sci-Fi", "Mystery", "Adventure", "Romance", "Horror"]
            )
        with col2:
            # Create emotion options from few-shot examples
            emotion_options = [ex["value"] for ex in few_shot_examples if ex["type"] == "Core Emotion"]
            tone = st.selectbox(
                "Choose a core emotion or tone:",
                ["Whimsical", "Dark", "Humorous", "Serious", "Suspenseful"] + emotion_options
            )
            
        character = st.text_input("Who should be the main character?")
        setting = st.text_input("Where should the story take place?")
        
        # Add option to use few-shot examples
        use_examples = st.checkbox("Use curated writing examples to guide the style", value=True)
        
        if st.button("Generate Story Beginning"):
            if not character or not setting:
                st.warning("Please provide both a character and a setting")
            else:
                # Prepare the prompt with few-shot examples if enabled
                if use_examples:
                    examples_text = "\n\n".join(
                        f"Example of '{ex['value']}':\n{ex['story']}" 
                        for ex in few_shot_examples
                    )
                    story_prompt = f"""
                    Below are some examples of excellent storytelling. Use them as inspiration 
                    for the style and emotional depth of the story you're about to create:
                    
                    {examples_text}
                    
                    Now create the beginning of a {tone.lower()} {genre.lower()} story for {user_name}.
                    Main character: {character}
                    Setting: {setting}
                    Make it engaging and set up for interactive choices.
                    Capture the same quality and emotional impact as the examples above.
                    """
                else:
                    story_prompt = f"""
                    Create the beginning of a {tone.lower()} {genre.lower()} story for {user_name}.
                    Main character: {character}
                    Setting: {setting}
                    Make it engaging and set up for interactive choices.
                    """
                
                with st.spinner("Crafting your story..."):
                    story_response = chat.send_message(story_prompt)
                
                st.markdown("---")
                st.subheader("Your Story Begins...")
                st.markdown(story_response.text)
                
                # Add options for continuing the story
                st.markdown("---")
                st.subheader("What happens next?")
                
                # Dynamic choices based on the selected tone
                if "Dread" in tone or "Dark" in tone or "Horror" in genre:
                    choices = [
                        "Continue building suspense",
                        "Introduce a terrifying revelation",
                        "Have the character discover something disturbing"
                    ]
                elif "Romance" in genre:
                    choices = [
                        "Develop the romantic tension",
                        "Introduce a complication",
                        "Add a tender moment"
                    ]
                else:  # Default choices
                    choices = [
                        "Continue the story as is", 
                        "Add a surprising twist",
                        "Introduce a new character"
                    ]
                
                choice = st.radio(
                    "Make a choice:",
                    choices,
                    index=None
                )
                
                if choice and st.button("Continue Story"):
                    continuation_prompt = f"""
                    {user_name} has chosen to: {choice}.
                    Continue the story accordingly, maintaining the {tone.lower()} tone
                    and {genre.lower()} genre. Make it about 2 paragraphs.
                    """
                    
                    if use_examples:
                        continuation_prompt += "\nMaintain the same quality as the examples provided earlier."
                    
                    with st.spinner("Developing the next chapter..."):
                        continuation_response = chat.send_message(continuation_prompt)
                    
                    st.markdown(continuation_response.text)

# Add section to show the few-shot examples
with st.expander("View Writing Examples Used"):
    st.write("These examples help guide the AI's writing style:")
    for example in few_shot_examples:
        st.subheader(f"{example['type']}: {example['value']}")
        st.write(example['story'])
        st.markdown("---")
