from teaching_assistant import TeachingAssistant
from feedback_giver import FeedbackGiver
from utils import client
from memory import *
import json
import re

class AILecturer:
    def __init__(self, subject, class_num):
        self.subject = subject
        self.class_num = class_num
        self.ta = TeachingAssistant(subject, class_num)
        self.feedback_giver = FeedbackGiver(isOPENAI=True)
        self.ta.convert_prompt(isPrint=False)
        self.class_info = self.ta.get_classinfo()
        self.phase = "warm_up"  # Phases: warm_up → core_lesson → guided_practice → wrap_up → done
        self.current_step = 0
        self.current_topic_index = 0
        self.memory = AILecturerMemory(subject, class_num)
        self.current_problem_index = 0

    def call_ai_teacher(self, system_message, user_message):
        """Generate AI responses using OpenAI API."""
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()

    def get_next_step(self):
        """Move forward through the lesson plan step by step."""
        if self.phase == "warm_up":
            return self.deliver_warm_up()
        elif self.phase == "core_lesson":
            return self.deliver_core_lesson()
        elif self.phase == "guided_practice":
            return self.deliver_guided_practice()
        elif self.phase == "wrap_up":
            return self.deliver_wrap_up()
        else:
            return "🎉 The class has finished!"

    def deliver_warm_up(self):
        """Engage students with introductory discussions."""
        knowledge = self.memory.get_recent_events(n=10)
        warm_up = self.class_info["warm_up"]
        self.update_memory("system",f"current stage:{self.phase};current task:{self.current_step}")
        if self.current_step < len(warm_up["tasks"]):
            task = warm_up["tasks"][self.current_step]
            prompt = f'''
            You are in the warm_up stages of a class in {self.subject}. Play the role of the lecturer. You are having a one-to-one class, with the user as the student.
            You have been given the task of {task}.
            Complete the task by returning a meaning question or response that you think could help make progresses on the task.
            If there are some previous conversations in records: {knowledge}, you could reflect on some of them if necessary.
            Control the length of your response so that it's acceptable for a conversation in class.
            Do not expression confirmation of receiving this message. Play the role.
            Be noticed that student may not understand concepts related to {self.subject} yet, so avoid professional terms while delivering materials.
            '''
            sys_message = f"You are an engaging and highly knowledgeable AI lecturer specializing in {self.subject}. Your role is to teach students interactively while keeping them engaged."
            response = self.call_ai_teacher(sys_message, prompt)
            self.current_step += 1
            self.update_memory("warm up opening remark", response)
            return response
        else:
            self.phase = "core_lesson"
            self.current_step = 0
            return self.get_next_step()

    def deliver_core_lesson(self):
        """Teach key concepts in a structured manner."""
        self.update_memory("system",f"current stage:{self.phase};current task:{self.current_step}")
        knowledge = self.memory.get_recent_events(n=30)
        core_lesson = self.class_info["core_lesson"]
        if self.current_topic_index < len(core_lesson):
            topic = core_lesson[self.current_topic_index]
            self.current_topic_index += 1
            concepts = "\n".join([f"- {c}" for c in topic["concepts"]])
            examples = "\n".join([f"🔹 Example: {e}" for e in topic.get("examples", [])])
            prompt = f'''
            You are in the core lesson stages of a class in {self.subject}.
            You need to let the student understand the concepts: {concepts} using provided example: {examples}.
            Based on the conversation history: {knowledge}, identify the concept that is the next on the list that is not taught yet. Start teaching with that concept.
            Keep in mind to play the role of a lecturer.
            '''
            sys_message = f"You are an engaging and highly knowledgeable AI lecturer specializing in {self.subject}. Your role is to teach students interactively while keeping them engaged."
            response = self.call_ai_teacher(sys_message, prompt)
            return response
        else:
            self.phase = "guided_practice"
            self.current_topic_index = 0
            return self.get_next_step()

    def deliver_guided_practice(self):
        """Ask students to solve problems and provide feedback."""
        knowledge = self.memory.get_recent_events(n=10)
        self.update_memory("system",f"current stage:{self.phase};current task:{self.current_step}")
        problems = self.class_info["guided_practice"]
        prompt = f'''
You are teaching a student (the user) on the subject: {self.subject}
Now you have entered the pratice stage of the class, where the problems to be praticed are: {problems}
Provide a natural transition from the last part of class based on this record of 10 most recent conversation logs: {knowledge}.
You do not have to tell the problem to the student: it will be presented to the student later. 
Just play the role of the teacher and tell the student it's time for practice.
        '''
        sys_message = f"You are an engaging and highly knowledgeable AI lecturer specializing in {self.subject}. Your role is to teach students interactively while keeping them engaged."
        response = self.call_ai_teacher(sys_message, prompt)
        if self.current_problem_index < len(problems):
            problem = problems[self.current_problem_index]
            self.current_problem_index += 1
            return response + f"🛠️ **Exercise:** {problem['question']}"
        else:
            self.phase = "wrap_up"
            self.current_problem_index = 0
            return self.get_next_step()

    def check_student_answer(self, student_answer):
        """Evaluate student responses using `FeedbackGiver`."""
        problems = self.class_info["guided_practice"]
        problem = problems[self.current_problem_index - 1]  # Get last problem asked

        correct_answer = self.feedback_giver.get_correct_answer(problem["question"])
        evaluation = self.feedback_giver.evaluate_answer(correct_answer, student_answer)
        feedback = self.feedback_giver.give_feedback(problem["question"], evaluation)

        return feedback

    def deliver_wrap_up(self):
        """Summarize the class and give homework."""
        self.update_memory("system",f"current stage:{self.phase};current task:{self.current_step}")
        wrap_up = self.class_info["wrap_up"]
        summary = wrap_up["summary"]
        homework = wrap_up["homework"]
        sys_message = f"You are an engaging and highly knowledgeable AI lecturer specializing in {self.subject}. Your role is to teach students interactively while keeping them engaged."
        prompt = f'''
You are wrapping up class in {self.subject}.
You are given an intended summary: {summary} and homework to be released {homework}.
Play the role of the lecturer and wrap up the course. Tell the student what he/she needs to do for homework.        
        '''
        response = self.call_ai_teacher(sys_message,prompt)
        self.phase = "done"
        return response
    
    def interact(self, student_message):
        knowledge = self.memory.get_recent_events(n=10)
        sys_message = f"You are an engaging and highly knowledgeable AI lecturer specializing in {self.subject}. Your role is to teach students interactively while keeping them engaged."
        prompt = f'''
        You are in the middle of the class teaching a high school student, current class_stage is {self.phase}.
        The whole class plan is as follow: {self.class_info}.
        Your student is studying {self.subject}, so while talking and giving examples please picturing yourself as communicating with people at that age.
        Here are records of your recent interactions with the student: {knowledge}.
        You received the student response: {student_message}.
        Based on your recent interactions and the student response, check if it is suitable to continue to the next topic or staying on the current topic.
        
        Reasons to stay on the current topic might include the following:
        1. the student is asking about something
        2. the student does not understand something you just covered (you could refer to your recent interactions for clues)

        Reasons to move to the next topic might include the following:
        1. the student has understand your inquiry by providing suitbale examples or explanations. For example, if you ask for some real-world examples, and the students named a few as the response. You should move to the next topic if the examples provided are reasonable.
        2. the response does not have to be perfect, as long as it answers your question, you should move on. Especially in the warm-up session.
        
        You are talking to the student, so do not include your decision of staying in your response if you decide to stay. 
        When you are responding to the student, be sure to refer to the knowledge given to you.
        Since the student is studying the subject, do not talk about concepts that you deduced they have nor learned yet. For instance, if they are learning derivatives, do not talk to them about solving integrals, since they must have not learned that.
        Cover one core topic at a time.

        **EXAMPLE**
        AI Lectuer: How do you think calculus helps us understand the behavior of objects in motion, and can you think of a real-world example where this is applied?
        Student: measuring runner's running capability in races
        In the above example, the student has demosntrated sufficient understanding by giving a reasonable example. In that case, you should return "True", which means you are determined to continue to the next topic.

        **OUTPUT FORMAT**
        If you determine it suitable to continue to the next topic, return only the word "True". Do not provide any explanations, clarifications, or additional output.
        If you determine it necessary to stay on the current topic, directly return a response that you think would be helpful to promote the conversation
        '''
        response = self.call_ai_teacher(sys_message,prompt)
        status = self.evaluate()
        print(status)
        if status:
            self.update_memory("system", f"a task has been finished, move to the next one")
            return self.get_next_step()
        else:
            self.update_memory("system", f"unresolved - staying on current topic")
            return response
    
    def evaluate(self):
        knowledge = self.memory.get_recent_events(n=20)
        sys_message = f"You are a class log analyzer that determines if a topic could be closed up."
        prompt = f'''
Given a record of recent conversations between an AI lectuer and a student: {knowledge}. The current stage of the class is: {self.phase}. 
1. Locate the most recent topic the lecturer and the student are talking about
2. Determine if that topic is sufficiently discussed and covered, so that they could move to next topic.

Definition of 'sufficiently discussed' include:
1. student's confusion regarding that topic is answered
2. student has provided reasonable answers to the AL lecturer's question on that topic
3. the discussion of the topic is reasonably long, and the final student response is not a question
4. the content of the discussion begin to deviate from the current stage. For instance, discussing exercises in warm-up section.

If it's sufficient to move on to next topic, return only the word "yes"; if not, return only the word "no".
Do not return any other thing.
        '''
        response = self.call_ai_teacher(sys_message,prompt)
        if response == 'yes':
            return True
        else:
            return False

    def update_memory(self, agent, message):
        prompt = f'''
        You are an AI memory assistant responsible for logging interactions between a student and an AI Lecturer.
        Your job is to analyze each message tuple and categorize it correctly before storing it in memory.
        ## **Input Format:**
        You will be given two values, an agent: {agent}, and the message the agent is sending: {message}.
        For the variable agent:
        - value "system" indicates that 'message' will be a progress check to see the phase of the class
        - value `"student"` indicates that 'message' will be an interaction from the student
        - value `"teacher"` indicates that 'message' will be a response or teaching prgress by the AI lecturer
        ## **Expected Output:**
        Determine the type of the event based on the agent and the message, then return only the type of the event that you think this message belongs to.
        '''
        sys_message = "You are an AI memory assistant responsible for logging interactions between a student and an AI Lecturer."
        event_type = self.call_ai_teacher(sys_message, prompt)
        #print(f"{event_type}:{message}")
        if event_type and message:
            self.memory.log_event(event_type, message)
            return True
        else:
            return False

# **Usage Example**
if __name__ == "__main__":
    subject = "ap_calculus"
    classNum = "001"
    lecturer = AILecturer(subject, classNum)
    lecturer.prepare_lesson()
    lecturer.start_class()


