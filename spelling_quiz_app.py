import streamlit as st
import random
from gtts import gTTS
import os
from pathlib import Path

# --------------------------
# Streamlit App Configuration
# --------------------------
st.set_page_config(page_title="🐹 Isaac Spelling Quiz", page_icon="🐹")
st.title("🐹 Isaac Spelling Quiz")

# --------------------------
# Load Words from File
# --------------------------
file_path = "week_4.txt"
if not Path(file_path).exists():
    st.error(f"❌ {file_path} not found. Please add your word list file in the same folder.")
    st.stop()

with open(file_path) as f:
    word_list = [line.strip() for line in f if line.strip()]

# --------------------------
# Initialize session state
# --------------------------
if "words" not in st.session_state:
    random.shuffle(word_list)
    st.session_state.words = word_list
    st.session_state.current = 0
    st.session_state.correct = 0
    st.session_state.incorrect_words = []
    st.session_state.last_feedback = None  # Persistent feedback

# Ensure last_feedback exists on reruns
if "last_feedback" not in st.session_state:
    st.session_state.last_feedback = None

# --------------------------
# Utility: Generate TTS
# --------------------------
def make_tts(word, idx):
    filename = f"quiz_word_{idx}.mp3"
    tts = gTTS(text=word, lang="en")
    tts.save(filename)
    return filename

# --------------------------
# Show last feedback message
# --------------------------
if st.session_state.last_feedback:
    feedback_type = st.session_state.last_feedback["type"]
    feedback_msg = st.session_state.last_feedback["msg"]
    if feedback_type == "success":
        st.success(feedback_msg)
    else:
        st.error(feedback_msg)
    st.session_state.last_feedback = None  # Clear after displaying

# --------------------------
# Quiz Logic
# --------------------------
if st.session_state.current < len(st.session_state.words):
    word = st.session_state.words[st.session_state.current]
    filename = make_tts(word, st.session_state.current)

    st.subheader(f"Word {st.session_state.current + 1} of {len(st.session_state.words)}")

    # Play button for audio
    st.audio(filename)

    # Input form
    with st.form(key=f"form_{st.session_state.current}"):
        user_input = st.text_input("✍️ Type your spelling:")
        submitted = st.form_submit_button("Submit")

        if submitted:
            # Remove all spaces from input and answer before comparing
            cleaned_input = user_input.lower().replace(" ", "")
            cleaned_word = word.lower().replace(" ", "")

            if cleaned_input == cleaned_word:
                st.session_state.correct += 1
                st.session_state.last_feedback = {
                    "type": "success",
                    "msg": f"✅ \"{user_input}\" is correct! 🐹🐹"
                }
            else:
                st.session_state.incorrect_words.append(word)
                st.session_state.last_feedback = {
                    "type": "error",
                    "msg": f"❌ Incorrect. The correct spelling is: **{word}**"
                }

            # Clean up audio file
            os.remove(filename)

            st.session_state.current += 1
            st.rerun()

# --------------------------
# Final Results
# --------------------------
else:
    total = len(st.session_state.words)
    st.success(f"🎉 You got {st.session_state.correct} out of {total} correct!")

    # Perfect score: display hamster pyramid
    if st.session_state.correct == total:
        st.markdown("🐹🐹🐹 Perfect score! 🎉")
        a = [1, 2, 3, 4, 3, 2, 1]
        pyramid_lines = []
        for i in a:
            spaces = "&nbsp;" * 2 * (4 - i)
            hamsters = "🐹&nbsp;&nbsp;" * i
            pyramid_lines.append(spaces + hamsters)
        pyramid_html = "<br>".join(pyramid_lines)
        st.markdown(f"<div style='text-align:center; font-size:24px;'>{pyramid_html}</div>", unsafe_allow_html=True)

    # Show incorrect words
    if st.session_state.incorrect_words:
        st.warning("Here are the words you got wrong:")
        for w in st.session_state.incorrect_words:
            st.write("-", w)

        # Practice incorrect words button
        if st.button("🔁 Practice incorrect words"):
            random.shuffle(st.session_state.incorrect_words)
            st.session_state.words = st.session_state.incorrect_words
            st.session_state.current = 0
            st.session_state.correct = 0
            st.session_state.incorrect_words = []
            st.session_state.last_feedback = None
            st.rerun()
    else:
        st.balloons()
        st.info("✅ Practice session complete!")
