import streamlit as st
import random
import requests
import pandas as pd

# Fetch trivia questions from Open Trivia DB API
def fetch_trivia_questions(amount=5, difficulty='easy', category=None):
    base_url = f"https://opentdb.com/api.php?amount={amount}&difficulty={difficulty}&type=multiple"
    if category:
        base_url += f"&category={category}"
    response = requests.get(base_url)
    data = response.json()
    questions = data.get('results', [])
    return questions

# Initialize session state variables
if "questions" not in st.session_state:
    st.session_state.questions = []
if "current_question" not in st.session_state:
    st.session_state.current_question = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "answers" not in st.session_state:
    st.session_state.answers = []
if "game_active" not in st.session_state:
    st.session_state.game_active = False
if "user_choice" not in st.session_state:
    st.session_state.user_choice = None
if "submitted" not in st.session_state:
    st.session_state.submitted = False  # Track whether the user has submitted their answer

# App title and description
st.title("🎲 Trivia Game App")
st.write("Test your knowledge with this trivia quiz! Answer multiple-choice questions and see how many you can get right.")

# Sidebar for game settings
st.sidebar.title("Game Settings")
num_questions = st.sidebar.slider("Number of Questions", 5, 20, 5)
difficulty = st.sidebar.selectbox("Difficulty", ['easy', 'medium', 'hard'])

# Fetch questions and start the game
if st.sidebar.button("Start Game"):
    questions = fetch_trivia_questions(amount=num_questions, difficulty=difficulty)

    if not questions:
        st.error("Failed to load questions. Try again later.")
    else:
        st.session_state.questions = questions
        st.session_state.current_question = 0
        st.session_state.score = 0
        st.session_state.answers = []
        st.session_state.game_active = True
        st.session_state.user_choice = None
        st.session_state.submitted = False

# Gameplay logic
if st.session_state.game_active:
    # Get the current question and options
    question = st.session_state.questions[st.session_state.current_question]
    question_text = question['question']
    correct_answer = question['correct_answer']
    options = question['incorrect_answers'] + [correct_answer]
    random.shuffle(options)

    # Display the question and options
    st.write(f"### Question {st.session_state.current_question + 1}: {question_text}")
    st.session_state.user_choice = st.radio(
        "Choose your answer:",
        options,
        index=0 if not st.session_state.user_choice else options.index(st.session_state.user_choice),
        key=f"question_{st.session_state.current_question}"
    )

    # Submit Answer button
    if not st.session_state.submitted:
        if st.button("Submit Answer"):
            if st.session_state.user_choice:
                st.session_state.submitted = True  # Mark as submitted
                if st.session_state.user_choice == correct_answer:
                    st.success("🎉 Correct!")
                    st.session_state.score += 1
                else:
                    st.error(f"❌ Wrong! The correct answer was: {correct_answer}")
            else:
                st.warning("Please select an answer before submitting.")

    # Next Question button
    if st.session_state.submitted:
        if st.button("Next Question"):
            # Save the user's answer and move to the next question
            st.session_state.answers.append({
                "question": question_text,
                "your_answer": st.session_state.user_choice,
                "correct_answer": correct_answer
            })
            st.session_state.current_question += 1
            st.session_state.user_choice = None  # Reset user choice for the next question
            st.session_state.submitted = False  # Reset submission status

            # End the game if no more questions
            if st.session_state.current_question >= len(st.session_state.questions):
                st.session_state.game_active = False

# End of the game
if not st.session_state.game_active and st.session_state.questions:
    st.write("## Game Over!")
    st.write(f"Your final score is: {st.session_state.score}/{len(st.session_state.questions)}")

    # Display a summary of the answers
    results_df = pd.DataFrame(st.session_state.answers)
    st.table(results_df)

    # Reset button
    if st.button("Play Again"):
        st.session_state.questions = []
        st.session_state.current_question = 0
        st.session_state.score = 0
        st.session_state.answers = []
        st.session_state.game_active = False
        st.session_state.user_choice = None
        st.session_state.submitted = False
