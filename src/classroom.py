import streamlit as st
from lecturer import AILecturer

# Streamlit App Title
st.title("🎓 Virtual Classroom - AI Lecturer")

# Sidebar for Subject Selection
st.sidebar.header("Select a Subject")
subject = st.sidebar.selectbox("Choose a subject:", ["ap_calculus"])
class_number = st.sidebar.text_input("Enter Class Number", "001")

# Initialize session state variables
if "class_started" not in st.session_state:
    st.session_state.class_started = False  # Controls when UI elements appear

if "lecturer" not in st.session_state:
    st.session_state.lecturer = AILecturer(subject, class_number)

if "conversation" not in st.session_state:
    st.session_state.conversation = []  # Stores chat history

if "blackboard_content" not in st.session_state:
    st.session_state.blackboard_content = ""  # Stores blackboard content

if "student_input" not in st.session_state:
    st.session_state.student_input = ""  # Track input field value

if "waiting_for_exercise_answer" not in st.session_state:
    st.session_state.waiting_for_exercise_answer = False  # Track exercise response state

# Start Class Button
if not st.session_state.class_started:
    if st.button("Start Class"):
        st.session_state.class_started = True
        first_step = st.session_state.lecturer.get_next_step()  # Start the class
        st.session_state.conversation.append(("assistant", first_step))
        st.rerun()

# Show Conversation & Blackboard only if class has started
if st.session_state.class_started:
    st.subheader("📢 AI Lecturer:")

    # Scrollable chat history
    chat_container = st.container()
    with chat_container:
        for role, message in st.session_state.conversation:
            with st.chat_message(role):
                st.markdown(message)

    # Student Input Section
    student_input = st.text_input("🗣️ You:", value=st.session_state.student_input, key="student_input")

    if st.button("Submit to AI Lecturer"):
        if student_input.strip():
            # Store student's question
            st.session_state.conversation.append(("user", student_input))
            st.session_state.lecturer.update_memory("student", student_input)
            if st.session_state.waiting_for_exercise_answer:
                # AI is expecting an answer to an exercise
                feedback = st.session_state.lecturer.check_student_answer(student_input)
                st.session_state.conversation.append(("assistant", feedback))
                st.session_state.waiting_for_exercise_answer = False  # Reset exercise state
            else:
                # Continue lesson
                response = st.session_state.lecturer.interact(student_input)

                # If AI asks an exercise, enable the response waiting state
                if "**🛠️ Exercise**" in response:
                    st.session_state.waiting_for_exercise_answer = True

                # Store AI's response
                st.session_state.conversation.append(("assistant", response))

            st.rerun()  # Forces UI to update and clears the field

    # Blackboard Section (Retains Content)
    with st.expander("📝 Blackboard (Click to Expand)"):
        st.session_state.blackboard_content = st.text_area(
            "Write or view markdown formulas here:",
            st.session_state.blackboard_content,
            height=200
        )
        st.markdown(st.session_state.blackboard_content, unsafe_allow_html=True)



#python -m streamlit run src\classroom.py