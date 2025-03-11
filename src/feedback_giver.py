from utils import client, deepseek_client

class FeedbackGiver:
    def __init__(self, isOPENAI = True, model="gpt-4o-mini",temperature = 1):
        if isOPENAI:
            self.model = model
            self.client= client
        else:
            self.model = "deepseek-chat"
            self.client = deepseek_client
        self.temperature = temperature
    
    def call_chat_completion(self, system_message: str, user_message: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ],
            temperature=self.temperature,
        )
        return response.choices[0].message.content.strip()

    def determine_topic(self, sentence):
        prompt = f'''
        You are given a sentence: {sentence}\n
        Determine whether it related to a field in mathematics. If so, only return the category.
        '''
        system_msg = "You are a mathematician."
        category = self.call_chat_completion(system_msg, prompt)
        return category

    def generate_math_problem(self, topic):
        """
        Generate a math problem using OpenAI's API.
        """
        prompt = f'''
        Generate a math problem in the field of {topic}\n for a middle school student. 
        Start directly with the problem. Do not answer the problem yourself.
        '''
        system_msg = "You are a helpful math tutor."
        problem = self.call_chat_completion(system_msg, prompt)
        return problem

    def get_correct_answer(self,problem) -> str:
        prompt = f"Given the problem: {problem}\n What should be the answer to this problem? Return only the answer."
        system_msg = "You are a helpful math tutor"
        answer = self.call_chat_completion(system_msg, prompt)
        return answer

    def evaluate_answer(self, correct_answer, user_answer):
        """
        Evaluate the user's answer and provide feedback.
        """
        prompt = f'''
        This is the correct answer to a certain question: {correct_answer}\n 
        This is the user's answer: {user_answer}\n
        Indicate whether they are equivalent. 
        If it is, just return 1. 
        If it is not, just return 0.
        If the two answers are only different by a unit name, treat them as equivalent, and return 1.
        '''
        system_msg = "You are a checker that checks if two responses are equivalent."
        eval = self. call_chat_completion(system_msg, prompt)
        return eval

    def give_feedback(self, problem, number) -> str:
        prompt = f'''
        You have been given a number:{number}\n ,and a problem: {problem}\n 
        If the number is 1, return a sentence indicating that the user has made a correct response.
        If the number is 0, return a sentence indicating that the user has made an incorrect response, then find relevant math knowledge of the problem and return it.
        If the number is 1, return the math knowledge part in a brief manner.
        If the number is 0 (which means the user is incorrect), tell them it is incorrect in a nice way.
        Do not tell the user anything about the number you have been given, since they do not represent real responses.
        Call the user as "you".
        '''
        system_msg = "You are a helpful math tutor"
        answer = self. call_chat_completion(system_msg, prompt)
        return answer

    def check_yes_no(self, sentence):
        prompt = f'''
        You are given some sentence(s):{sentence}\n
        Check if the sentence means a 'yes' or a 'no'.
        If it means yes, just return "yes"
        If it means no, just return "no"
        '''
        system_msg = "You are a meaning finder that tries to determine if a sentence means yes or no."
        atti = self. call_chat_completion(system_msg, prompt)
        return atti

    def run(self, iterate = True, topic = None):
        while iterate:
            # Step 1: Generate a math problem on a topic of user's choice
            topic = self.determine_topic(input("\nWhat kind of problem would you like to try today?"))
            if topic == None:
                topic = "random topic in mathematics"
            problem = self.generate_math_problem(topic)
            print("Problem:\n", problem)

            # Step 2: Get the user's answer
            user_answer = input("Your answer: ")

            # Step 3: Get the right answer
            correct_answer = self.get_correct_answer(problem)

            # Step 4: Evaluate the answer and provide feedback
            result = self.evaluate_answer(correct_answer, user_answer)
            feedback = self.give_feedback(problem, result)
            print("\nFeedback:\n", feedback)
            # Step 5: Ask the user if they want to continue
            if iterate:
                user_continue = input("\nDo you want to try another problem?: ")
                continue_playing = self.check_yes_no(user_continue)
                if continue_playing != "yes":
                    print("Thank you for playing! Goodbye!")
                    break
            else:
                break

if __name__ == "__main__":
    feedback_giver = FeedbackGiver(isOPENAI = False)
    feedback_giver.run()
