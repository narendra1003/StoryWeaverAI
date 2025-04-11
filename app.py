# Import the modules and libraries
import streamlit as st
import os
from google import genai
from google.genai import types

# Force use of pysqlite3-binary work around, specific for streamlit purpose.
# Streamlit is using older version of pysqllite3
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import chromadb

# Import API key stored in secret
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]

# Title of the application
st.title('StoryWeaverAI')

# Initializ varibles, lists and strings to store the generated story later on
# Initialize variables using st.session_state
# Initialized the story to maintain long context window
if "story_history" not in st.session_state:
    st.session_state["story_history"] = ""

# to handel the initial prompt
if "first_turn" not in st.session_state:
    st.session_state["first_turn"] = True

# A list to store generated story segments
if "generated_story_parts" not in st.session_state:
    st.session_state["generated_story_parts"] = []

# LLM model selection
client = genai.Client(api_key=GOOGLE_API_KEY)
chat = client.chats.create(model="gemini-2.0-flash")

# --- Initial greeting and name input ---
if not st.session_state["user_name"]:
    st.write('Hello, Welcome to the StoryWeaverAI. Please tell me how should I address you?')
    user_name_input = st.text_input("Your Name:", "")
    if st.button("Submit Name"):
        st.session_state["user_name"] = user_name_input.strip()
        introduction_prompt = f"Introduce yourself to {st.session_state['user_name']} as they will be using your capabilities to create an interactive story. Use their name in the explanation."
        response = chat.send_message(introduction_prompt)
        st.markdown(response.text)

elif st.session_state["first_turn"]:
    start_choice = st.radio("Start with:", ("Emotion", "Situation", "Quit"))
    if start_choice == "Emotion":
        core_emotion = st.text_input("Enter a core emotion:")
        if st.button("Start with Emotion"):
            st.session_state["interaction_type"] = "emotion"
            st.session_state["user_input"] = f"User guides with emotion: {core_emotion}"
            st.session_state["first_turn"] = False
    elif start_choice == "Situation":
        brief_situation = st.text_input("Enter a brief situation:")
        if st.button("Start with Situation"):
            st.session_state["interaction_type"] = "situation"
            st.session_state["user_input"] = f"User guides with situation: {brief_situation}"
            st.session_state["first_turn"] = False
    elif start_choice == "Quit":
        st.write("Thanks for playing, {}!".format(st.session_state.get("user_name", "User")))
        st.stop()

# --- Story continuation ---
elif st.session_state["first_turn"] == False:
    st.write("Current Story:")
    for part in st.session_state["generated_story_parts"]:
        st.write(part)

    continue_choice = st.radio("Continue?", ("Yes", "No", "Quit"))
    if continue_choice == "Yes":
        next_interaction_type = st.radio("Guide the next part with:", ("Emotion", "Situation"))
        if next_interaction_type == "Emotion":
            next_emotion = st.text_input("Enter a core emotion for the next part:")
            if st.button("Continue with Emotion"):
                st.session_state["interaction_type"] = "emotion"
                st.session_state["user_input"] = f"User guides with emotion: {next_emotion}"
                # --- RAG and LLM Call ---
                user_input = st.session_state["user_input"]
                user_input_embedding = client.models.embed_content(model="models/text-embedding-004", contents=[user_input]).embeddings[0].values
                query_results = collection.query(query_embeddings=[user_input_embedding], n_results=2)
                retrieved_documents = query_results['documents'][0] if query_results and query_results['documents'] else []
                retrieved_context = "\n".join(retrieved_documents)
                interactive_prompt = create_interactive_prompt_rag(user_input, few_shot_examples, st.session_state["story_history"], retrieved_context)
                response = chat.send_message(interactive_prompt)
                generated_text = response.text.replace("Story:", "").strip()
                st.write("Generated Story:", generated_text)
                st.session_state["story_history"] += f"{user_input}\nAI continues: {generated_text}\n"
                st.session_state["generated_story_parts"].append(generated_text)
        elif next_interaction_type == "Situation":
            next_situation = st.text_input("Enter a brief situation for the next part:")
            if st.button("Continue with Situation"):
                st.session_state["interaction_type"] = "situation"
                st.session_state["user_input"] = f"User guides with situation: {next_situation}"
                # --- RAG and LLM Call ---
                user_input = st.session_state["user_input"]
                user_input_embedding = client.models.embed_content(model="models/text-embedding-004", contents=[user_input]).embeddings[0].values
                query_results = collection.query(query_embeddings=[user_input_embedding], n_results=2)
                retrieved_documents = query_results['documents'][0] if query_results and query_results['documents'] else []
                retrieved_context = "\n".join(retrieved_documents)
                interactive_prompt = create_interactive_prompt_rag(user_input, few_shot_examples, st.session_state["story_history"], retrieved_context)
                response = chat.send_message(interactive_prompt)
                generated_text = response.text.replace("Story:", "").strip()
                st.write("Generated Story:", generated_text)
                st.session_state["story_history"] += f"{user_input}\nAI continues: {generated_text}\n"
                st.session_state["generated_story_parts"].append(generated_text)
    elif continue_choice == "No" or continue_choice == "Quit":
        st.write("Final Story:")
        for part in st.session_state["generated_story_parts"]:
            st.write(part)
        st.write("Thanks for playing, {}!".format(st.session_state.get("user_name", "User")))
        st.stop()


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
    {
        "type": "Core Emotion",
        "value": "Euphoria",
        "story": "The world snapped into crystalline focus - every color vibrating, every sound a symphony. She laughed as raindrops hung suspended around her, each one a liquid diamond containing entire universes. This wasn't just happiness; it was revelation. The warning label on the pill bottle ('Do not operate heavy machinery') seemed hilariously inadequate now that she could see the machinery of existence itself."
    },
    {
        "type": "Core Emotion",
        "value": "Betrayal",
        "story": "The handwriting was unmistakable. Those looping g's, the dramatic cross on the t. His fingers trembled as they traced the words that dismantled twelve years of marriage. The note was signed with her pet name for him - the final twist of the knife. He'd always wondered what was in the locked drawer of her nightstand. Now he wished he'd never found the key."
    },
    {
        "type": "Core Emotion", 
        "value": "Awe",
        "story": "The canyon didn't just stretch below him - it pulled at his soul. His breath came in shallow gasps as vertigo warred with wonder. A single misstep would send him tumbling into that magnificent void. His fingers dug into the sandstone as some primal part of his brain screamed that he wasn't meant to see things this beautiful and survive."
    },
    {
        "type": "Brief Situation",
        "value": "Unexpected package",
        "story": "The box on his doorstep bore no postmark, no address - just his name written in what looked like charcoal. Inside, nestled in black velvet, was a childhood toy he distinctly remembered burning in his family's fireplace. The attached note read: 'You should have kept better track of your things.'"
    },
    {
        "type": "Brief Situation",
        "value": "Broken mirror",
        "story": "Seven years bad luck was the least of her worries. The cracks in the bathroom mirror didn't just distort her reflection - they showed versions of herself she'd never been. One reflection mouthed words she'd never say; another had scars she'd never received. The most disturbing one simply stared back, smiling with teeth that were just slightly too sharp."
    },
    {
        "type": "Brief Situation",
        "value": "Late-night phone call",
        "story": "The phone rang at 3:17 AM. A voice she hadn't heard in twenty years said, 'I'm outside.' Her childhood best friend had drowned at summer camp. Yet when she pulled back the curtain, there she stood on the lawn - dripping wet, wearing the same swimsuit from that final day, holding out a sodden friendship bracelet."
    },
    {
        "type": "Brief Situation",
        "value": "Wrong number text",
        "story": "'The body is hidden where we agreed,' read the message meant for someone else. She stared at the grainy photo attached - her own backyard shed. When she called the number, a familiar voice answered on the first ring: 'See? I told you you'd notice eventually.'"
    },
    {
        "type": "Brief Situation", 
        "value": "Stuck elevator",
        "story": "The emergency call button sparked when he pressed it. In the sudden darkness, the elevator began moving - downward. The floor display showed B3, B4, B5... though the building only had two basement levels. A whisper came through the vents: 'You should've taken the stairs.'"
    }
]

# Retrieval-Augmented Generation, RAG setup

# Our simple knowledge base
knowledge_base = [
    "The old house stood on a windswept hill, its windows like vacant eyes staring out at the stormy sea.",
    "A feeling of intense paranoia washed over him as he realized he was the only one who remembered the missing photograph.",
    "The ancient prophecy spoke of a hidden key that would unlock a forgotten power.",
    "Despite the joyous celebration, a subtle undercurrent of sadness lingered in her smile.",
    "The mirror reflected not his own face, but a distorted and menacing visage.",
]

# Select embedding model
embeddings = client.models.embed_content(model="models/text-embedding-004", contents = knowledge_base) 

# Access the 'embeddings' attribute
embedded_list = [embedding.values for embedding in embeddings.embeddings]


# Set up ChromaDB in-memory
client_rag = chromadb.Client()
collection = client_rag.create_collection("story_knowledge")

# Add embeddings and documents to the collection
ids = [f"doc_{i}" for i in range(len(knowledge_base))]
collection.add(
    embeddings=embedded_list,
    documents=knowledge_base,
    ids=ids)


# Function to create the prompt which will be used to generate the story

def create_interactive_prompt_rag(user_input, few_shot_examples, story_history="", retrieved_context=""):
    prompt_parts = [
        "Here are some examples of short stories based on a core emotion or a brief situation, often with a psychological twist:\n\n"
    ]
    for example in few_shot_examples:
        prompt_parts.append(f"{example['type']}: {example['value']}\nStory: {example['story']}\n\n")

    if story_history:
        prompt_parts.append(f"The story so far:\n{story_history}\n\n")

    if retrieved_context:
        prompt_parts.append(f"Consider this retrieved knowledge to enrich the story:\n{retrieved_context}\n\n")

    prompt_parts.append(f"Now, continue the story based on the user's input: {user_input}\nStory:")
    return "".join(prompt_parts)


# # With Retrieval-Augmented Generation, RAG

# while True:
#     if first_turn:
#         interaction_type = input("\nStart with an 'emotion' or a 'situation' (or 'quit'): ").lower()
#         first_turn = False
#     else:
#         continue_story = input("\nDo you want to continue the story? (yes/no/quit): ").lower()
#         if continue_story == 'no' or continue_story == 'quit':
#             print("=="*70)
#             print("This is the story which you have generated with retrieved knowledge:")
#             print("=="*70 + "\n")
#             print("\n".join(generated_story_parts).strip())
#             break
            
#         # Prompt sent to llm
#         interaction_type = input("\nEnter an 'emotion' or a 'situation' to guide the next part of the story: ").lower()

#     if interaction_type == 'emotion':
#         core_emotion = input("Enter a core emotion (e.g., fear, joy, mystery): ")
#         user_input = f"User guides with emotion: {core_emotion}"
#         print(user_input)
#         story_history += f"{user_input}\n"

#         # Retrieve relevant knowledge
#         # Generate embeddings for the user input using the same model used for the collection
#         user_input_embedding = client.models.embed_content(model="models/text-embedding-004", contents=[user_input]).embeddings[0].values

#         query_results = collection.query(
#             query_embeddings=[user_input_embedding],  # Pass the generated embedding
#             n_results=2) # Retrieve top 2 relevant documents

#         retrieved_documents = query_results['documents'][0] if query_results and query_results['documents'] else []
#         retrieved_context = "\n".join(retrieved_documents)

#         # Final Prompt generated for llm
#         interactive_prompt = create_interactive_prompt_rag(user_input, few_shot_examples, story_history, retrieved_context)
        
#         # Final prompt sent to llm
#         response = chat.send_message(interactive_prompt)
#         generated_text = response.text.replace("Story:", "").strip()
#         print("\nGenerated Story:")
#         print(generated_text)
#         story_history += f"AI continues: {generated_text}\n"
#         generated_story_parts.append(generated_text)

#     elif interaction_type == 'situation':
#         brief_situation = input("Enter a brief situation (e.g., empty swing set, whisper in the dark): ")
#         user_input = f"User guides with situation: {brief_situation}"
#         print(user_input)
#         story_history += f"{user_input}\n"

#         # Retrieve relevant knowledge
#         # Generate embeddings for the user input using the same model used for the collection
#         user_input_embedding = client.models.embed_content(model="models/text-embedding-004", contents=[user_input]).embeddings[0].values

#         query_results = collection.query(
#             query_embeddings=[user_input_embedding],  # Pass the generated embedding
#             n_results=2) # Retrieve top 2 relevant documents
            
#         retrieved_documents = query_results['documents'][0] if query_results and query_results['documents'] else []
#         retrieved_context = "\n".join(retrieved_documents)

#          # Final prompt generated for llm
#         interactive_prompt = create_interactive_prompt_rag(user_input, few_shot_examples, story_history, retrieved_context)

#          # Final prompt sent to llm
#         response = chat.send_message(interactive_prompt)
#         generated_text = response.text.replace("Story:", "").strip()
#         print("\nGenerated Story:")
#         print(generated_text)
#         story_history += f"AI continues: {generated_text}\n"
#         generated_story_parts.append(generated_text)

#     elif interaction_type == 'quit':
#         print("=="*70)
#         print("This is the story which you have generated:")
#         print("=="*70 + "\n")
#         print("\n".join(generated_story_parts).strip())
#         break

#     else:
#         print("Invalid input. Please enter 'emotion', 'situation', or 'quit'.")
