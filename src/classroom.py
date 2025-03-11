import streamlit as st
from lecturer import AILecturer

st.title("🎓 Virtual Classroom - AI Lecturer")

st.sidebar.header("Select a Subject")
subject = st.sidebar.selectbox("Choose a subject:", ["ap_calculus"])
class_number = st.sidebar.text_input("Enter Class Number", "001")

if "class_started" not in st.session_state:
    st.session_state.class_started = False  # Controls when UI elements appear

if "lecturer" not in st.session_state:
    st.session_state.lecturer = AILecturer(subject, class_number)

if "conversation" not in st.session_state:
    st.session_state.conversation = []
if "blackboard_content" not in st.session_state:
    st.session_state.blackboard_content = "" 

if "student_input" not in st.session_state:
    st.session_state.student_input = ""  

if "waiting_for_exercise_answer" not in st.session_state:
    st.session_state.waiting_for_exercise_answer = False

if not st.session_state.class_started:
    if st.button("Start Class"):
        st.session_state.class_started = True
        first_step = st.session_state.lecturer.get_next_step() 
        st.session_state.conversation.append(("assistant", first_step))
        st.rerun()

if st.session_state.class_started:
    st.subheader("📢 AI Lecturer:")

    chat_container = st.container()
    with chat_container:
        for role, message in st.session_state.conversation:
            with st.chat_message(role):
                st.markdown(message)

    student_input = st.text_input("🗣️ You:", value=st.session_state.student_input, key="student_input")

    if st.button("Submit to AI Lecturer"):
        if student_input.strip():
            st.session_state.conversation.append(("user", student_input))
            st.session_state.lecturer.update_memory("student", student_input)
            if st.session_state.waiting_for_exercise_answer:
                feedback = st.session_state.lecturer.check_student_answer(student_input)
                st.session_state.conversation.append(("assistant", feedback))
                st.session_state.waiting_for_exercise_answer = False 
            else:
                response = st.session_state.lecturer.interact(student_input)

                if "**🛠️ Exercise**" in response:
                    st.session_state.waiting_for_exercise_answer = True

                st.session_state.conversation.append(("assistant", response))

            st.rerun() 

    with st.expander("📝 Blackboard (Click to Expand)"):
        st.session_state.blackboard_content = st.text_area(
            "Write or view markdown formulas here:",
            st.session_state.blackboard_content,
            height=200
        )
        st.markdown(st.session_state.blackboard_content, unsafe_allow_html=True)



#python -m streamlit run src\classroom.py