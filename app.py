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
]

# Initialize all session state variables
if 'story_history' not in st.session_state:
    st.session_state.story_history = []
if 'first_turn' not in st.session_state:
    st.session_state.first_turn = True
if 'intro_message' not in st.session_state:
    st.session_state.intro_message = ""
if 'current_genre' not in st.session_state:
    st.session_state.current_genre = ""
if 'current_tone' not in st.session_state:
    st.session_state.current_tone = ""
if 'show_story_controls' not in st.session_state:
    st.session_state.show_story_controls = False
if 'story_started' not in st.session_state:
    st.session_state.story_started = False

# Function to create the story prompt with word limit
def create_interactive_prompt(user_input, story_history=[]):
    prompt = "Here are some examples of excellent short stories:\n\n"
    for example in few_shot_examples:
        prompt += f"{example['type']}: {example['value']}\nStory: {example['story']}\n\n"

    if story_history:
        prompt += f"The story so far:\n{' '.join(story_history)}\n\n"

    prompt += f"""Now, generate a new story segment based on the following input:
    
    {user_input}
    
    Important instructions:
    - Limit the story segment to exactly 150 words
    - Count the words and ensure strict adherence
    - Maintain the story's flow and quality
    - End with a natural stopping point
    
    Story:"""
    return prompt

# Get API key
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]

# Main app logic
def main():
    # Get user name
    user_name = st.text_input("Please share your name:", key="user_name").strip()

    if user_name:
        client = genai.Client(api_key=GOOGLE_API_KEY)
        chat = client.chats.create(model="gemini-2.0-flash")
        
        # Display introduction if it exists
        if st.session_state.intro_message:
            st.markdown("---")
            st.subheader("Your Storytelling Companion Says:")
            st.markdown(st.session_state.intro_message)
        
        # Start session button (only shown first time)
        if st.session_state.first_turn and not st.session_state.story_started:
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button("Weave A Story"):
                    introduction_prompt = f"""
                    Introduce yourself to {user_name} as they will be using your capabilities 
                    to create an interactive story. Use their name in the explanation.
                    Be friendly and enthusiastic about storytelling!
                    Keep your introduction under 100 words.
                    """
                    
                    with st.spinner("Getting the storyteller ready..."):
                        response = chat.send_message(introduction_prompt)
                    
                    st.session_state.intro_message = response.text
                    st.session_state.first_turn = False
                    st.session_state.story_started = True
                    st.session_state.show_story_controls = True
                    st.rerun()
            with col2:
                if st.button("Quit Session"):
                    st.session_state.story_started = False
                    st.session_state.first_turn = True
                    st.session_state.intro_message = ""
                    st.rerun()
        
        # Story creation controls
        if st.session_state.show_story_controls:
            if not st.session_state.story_history:  # Show initial story setup
                st.markdown("---")
                st.subheader("Let's Create a Story Together!")
                
                col1, col2 = st.columns(2)
                with col1:
                    genre = st.selectbox(
                        "Choose a genre:",
                        ["Fantasy", "Sci-Fi", "Mystery", "Adventure", "Romance", "Horror"],
                        key="genre_select"
                    )
                with col2:
                    emotion_options = [ex["value"] for ex in few_shot_examples if ex["type"] == "Core Emotion"]
                    tone = st.selectbox(
                        "Choose a core emotion or tone:",
                        ["Whimsical", "Dark", "Humorous", "Serious", "Suspenseful"] + emotion_options,
                        key="tone_select"
                    )
                    
                character = st.text_input("Who should be the main character?", key="character_input")
                setting = st.text_input("Where should the story take place?", key="setting_input")
                special_element = st.text_input("Add a special element (optional):", 
                                            placeholder="e.g., a magical object, a secret, etc.",
                                            key="special_element_input")
                
                if st.button("Generate Story"):
                    if not character or not setting:
                        st.warning("Please provide both a character and a setting")
                    else:
                        user_input = f"""
                        Create a story beginning with these parameters:
                        - Genre: {genre}
                        - Tone/Emotion: {tone}
                        - Main Character: {character}
                        - Setting: {setting}
                        {f"- Special Element: {special_element}" if special_element else ""}
                        
                        Important:
                        - Exactly 150 words
                        - Engaging opening
                        - Sets up for future developments
                        """
                        
                        prompt = create_interactive_prompt(
                            user_input=user_input,
                            story_history=st.session_state.story_history
                        )
                        
                        with st.spinner("Crafting your story..."):
                            story_response = chat.send_message(prompt)
                        
                        st.session_state.story_history.append(story_response.text)
                        st.session_state.current_genre = genre
                        st.session_state.current_tone = tone
                        st.rerun()
            
            # Display full story history without part numbers
            if st.session_state.story_history:
                st.markdown("---")
                st.subheader("Your Story")
                for part in st.session_state.story_history:
                    st.markdown(part)
                    st.markdown("---")
                
                # Word count display
                current_word_count = len(" ".join(st.session_state.story_history).split())
                # st.caption(f"Total story length: {current_word_count} words")
                
                # Continuation options with quit button
                st.subheader("What happens next?")
                
                # Dynamic continuation choices
                tab1, tab2 = st.tabs(["Choose from Options", "Provide Your Own"])
                
                with tab1:
                    if "Dread" in st.session_state.current_tone or "Dark" in st.session_state.current_tone or "Horror" in st.session_state.current_genre:
                        choices = [
                            "Continue building suspense",
                            "Introduce a terrifying revelation",
                            "Have the character discover something disturbing"
                        ]
                    elif "Romance" in st.session_state.current_genre:
                        choices = [
                            "Develop the romantic tension",
                            "Introduce a complication",
                            "Add a tender moment"
                        ]
                    else:
                        choices = [
                            "Continue the story naturally", 
                            "Add a surprising twist",
                            "Introduce a new character"
                        ]
                    
                    next_action = st.radio(
                        "Choose how to continue:",
                        choices,
                        index=None,
                        key="continuation_choice"
                    )
                    
                    if next_action and st.button("Continue Story"):
                        continuation_prompt = create_interactive_prompt(
                            user_input=f"""
                            Continue the existing story with this direction:
                            {next_action}
                            
                            Requirements:
                            - Exactly 150 words
                            - Maintain {st.session_state.current_tone.lower()} tone
                            - Keep {st.session_state.current_genre.lower()} genre
                            - Consistent with existing characters/setting
                            - Natural stopping point
                            """,
                            story_history=st.session_state.story_history
                        )
                        
                        with st.spinner("Developing the next chapter ..."):
                            continuation_response = chat.send_message(continuation_prompt)
                        
                        st.session_state.story_history.append(continuation_response.text)
                        st.rerun()
                
                with tab2:
                    custom_situation = st.text_area(
                        "Describe what should happen next:",
                        placeholder="e.g., 'The character finds a mysterious letter under the door...'",
                        height=100,
                        key="custom_situation"
                    )
                    
                    if custom_situation and st.button("Continue with My Idea"):
                        continuation_prompt = create_interactive_prompt(
                            user_input=f"""
                            Continue the story with this custom situation:
                            {custom_situation}
                            
                            Requirements:
                            - Exactly 150 words
                            - Maintain {st.session_state.current_tone.lower()} tone
                            - Keep {st.session_state.current_genre.lower()} genre
                            - Consistent with existing characters/setting
                            - Natural stopping point
                            """,
                            story_history=st.session_state.story_history
                        )
                        
                        with st.spinner("Developing your custom continuation ..."):
                            continuation_response = chat.send_message(continuation_prompt)
                        
                        st.session_state.story_history.append(continuation_response.text)
                        st.rerun()
                
                # Quit button
                if st.button("Quit Session"):
                    st.session_state.story_history = []
                    st.session_state.first_turn = True
                    st.session_state.intro_message = ""
                    st.session_state.show_story_controls = False
                    st.session_state.story_started = False
                    st.rerun()

# Reset button (only shown if story has been generated)
if st.session_state.story_history:
    if st.button("Reset Story"):
        st.session_state.story_history = []
        st.session_state.first_turn = True
        st.session_state.intro_message = ""
        st.session_state.current_genre = ""
        st.session_state.current_tone = ""
        st.session_state.show_story_controls = False
        st.session_state.story_started = False
        st.rerun()

if __name__ == "__main__":
    main()
