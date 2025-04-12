# StoryWeaverAI

## Overview

StoryWeaverAI is a Streamlit application that uses the Gemini API to create interactive short stories. Users can guide the story generation by providing a core emotion or a brief situation as input. The application then uses these inputs to generate a story, offering a unique and engaging storytelling experience.

## Features

* **Interactive Story Generation:** Users can influence the direction of the story by providing emotional or situational prompts.
* **Gemini API Integration:** The application leverages the Google Gemini API to generate creative and contextually relevant story content.
* **Customizable User Experience:** The application greets the user, remembers their name, and allows them to continue the story in an interactive way.
* **Story History:** The application keeps track of the generated story parts.

## How to Use

1.  **Initial Setup:**
    * The application will greet you and ask for your name. This is used to personalize the interaction.
2.  **Story Generation:**
    * You can choose to start the story with either an "emotion" or a "situation".
    * Provide a specific emotion (e.g., fear, joy, mystery) or a brief situation (e.g., empty swing set, whisper in the dark).
    * The AI will generate a part of the story based on your input.
3.  **Continuing the Story:**
    * You will be asked if you want to continue the story.
    * If you choose to continue, you can again provide an "emotion" or a "situation" to guide the next part of the story.
4.  **Ending the Story:**
    * If you choose not to continue, the application will display the complete story generated so far.

## Technical Details

* **Python:** The application is written in Python.
* **Streamlit:** The user interface is built using the Streamlit framework.
* **Google Gemini API:** The application uses the Google Gemini API for story generation.
* **Session State:** Streamlit's session state is used to manage user data and story history.
