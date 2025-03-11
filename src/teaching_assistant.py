import json
import os

class TeachingAssistant:
    def __init__(self, subject, classNum):
        self.subject = subject
        self.classNum = classNum
        self.prompt = ""
        self.classinfo = {}

    def get_json_path(self):
        """
        Constructs the relative path to the JSON file from the src folder.
        Returns the absolute path for flexibility.
        """
        return os.path.join("class_material", self.subject, f"ap_calculus_class_{self.classNum}.json")

    def load_class_data(self, json_path):
        """
        Reads and loads the class data from the JSON file.
        
        Args:
            json_path (str): Path to the JSON file.
        
        Returns:
            dict: Parsed JSON data.
        """
        try:
            with open(json_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            print(f"Error: File not found at {json_path}")
            return None
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON format in {json_path}")
            return None


    def extract_class_info(self, class_data):
        """
        Extracts and organizes key information from the class JSON data.
        
        Args:
            class_data (dict): The loaded JSON data.

        Returns:
            dict: Organized class details.
        """
        if not class_data:
            return 0

        self.classinfo = {
            "class_title": class_data.get("class_title", "Unknown Title"),
            "teaching_goals": class_data.get("teaching_goal", []),
            "warm_up": class_data.get("class_structure", {}).get("warm_up", {}),
            "core_lesson": class_data.get("class_structure", {}).get("core_lesson", {}).get("topics", []),
            "guided_practice": class_data.get("class_structure", {}).get("guided_practice", {}).get("problems", []),
            "wrap_up": class_data.get("class_structure", {}).get("wrap_up", {})
        }
        return 1


    def summarize_class_info(self): # to_str
        """
        Prints a structured summary of the extracted class information.
        
        Args:
            class_info (dict): Extracted class details.
        """
        if self.classinfo == {}:
            print("No class information available.")
            return
        
        print(f"\nClass Title: {self.classinfo['class_title']}\n")
        print("Teaching Goals:")
        for goal in self.classinfo["teaching_goals"]:
            print(f"- {goal}")

        print("\nWarm-Up (Duration: {}):".format(self.classinfo["warm_up"].get("duration", "N/A")))
        for task in self.classinfo["warm_up"].get("tasks", []):
            print(f"- {task}")

        print("\nCore Lesson:")
        for topic in self.classinfo["core_lesson"]:
            print(f"\n  {topic['title']} ({topic['duration']})")
            print("  Concepts:")
            for concept in topic.get("concepts", []):
                print(f"    - {concept}")
            print("  Examples:")
            for example in topic.get("examples", []):
                print(f"    - {example}")

        print("\nGuided Practice:")
        for problem in self.classinfo["guided_practice"]:
            print(f"  - {problem['question']} (Type: {problem['type']})")

        print("\nWrap-Up Summary:")
        for point in self.classinfo["wrap_up"].get("summary", []):
            print(f"- {point}")

        print("\nHomework:")
        for hw in self.classinfo["wrap_up"].get("homework", []):
            print(f"- {hw}")

    def generate_ai_teacher_prompt(self):
        """
        Generates a structured AI teaching prompt based on any extracted class information.

        Args:
            class_info (dict): Extracted class details.

        Returns:
            str: AI teaching prompt.
        """
        if not self.classinfo:
            return "Error: No class information provided."

        prompt = f"""You are an expert teacher of the subject {self.subject}, and you are conducting a lesson on "{self.classinfo['class_title']}". 
    Your goal is to engage students, explain concepts clearly, and guide them through exercises. 
    Below is the structured plan for the lesson:

    ---

    ### **Teaching Goals:**
    """
        for goal in self.classinfo["teaching_goals"]:
            prompt += f"- {goal}\n"

        # Warm-Up Section
        warm_up = self.classinfo.get("warm_up", {})
        prompt += f"""\n### **Warm-Up** (Duration: {warm_up.get('duration', 'N/A')}):
    Begin by introducing the topic and engaging students with the following discussion prompts:\n"""
        for task in warm_up.get("tasks", []):
            prompt += f"- {task}\n"

        # Core Lesson (Flexible for Any Subject)
        prompt += "\n### **Core Lesson:**\n"
        for topic in self.classinfo.get("core_lesson", []):
            prompt += f"\n#### {topic['title']} ({topic['duration']}):\n"
            prompt += "**Key Concepts:**\n"
            for concept in topic.get("concepts", []):
                prompt += f"- {concept}\n"
            prompt += "\n**Examples or Case Studies:**\n"
            for example in topic.get("examples", []):
                prompt += f"- {example}\n"

        # Guided Practice (Adaptable to Any Subject)
        prompt += "\n### **Guided Practice:**\n"
        prompt += "Now, guide students through the following exercises:\n"
        for problem in self.classinfo.get("guided_practice", []):
            prompt += f"- {problem['question']} (Type: {problem['type']})\n"

        # Wrap-Up
        wrap_up = self.classinfo.get("wrap_up", {})
        prompt += f"""\n### **Wrap-Up** (Duration: {wrap_up.get('duration', 'N/A')}):
    Summarize the lesson by reinforcing key takeaways:\n"""
        for point in wrap_up.get("summary", []):
            prompt += f"- {point}\n"

        # Homework
        prompt += "\n### **Homework Assignment:**\nAssign students the following practice exercises:\n"
        for hw in wrap_up.get("homework", []):
            prompt += f"- {hw}\n"

        prompt += "\nEncourage student participation, discussion, and active learning throughout the session."

        return prompt

    def convert_prompt(self, isPrint = False):
        json_path = self.get_json_path()  # Get JSON file path
        class_data = self.load_class_data(json_path)  # Load JSON data
        self.extract_class_info(class_data)  # Extract key information
        ai_teacher_prompt = self.generate_ai_teacher_prompt()
        if isPrint:
            print(ai_teacher_prompt)
        self.prompt = ai_teacher_prompt
        return ai_teacher_prompt
    
    def get_prompt(self):
        return self.prompt
    
    def get_classinfo(self):
        return self.classinfo

# **Usage Example**
if __name__ == "__main__":
    subject = "ap_calculus"
    classNum = "001"
    # Generate AI teacher prompt (subject-independent)
    ta = TeachingAssistant(subject, classNum)
    ta.convert_prompt(isPrint=True)

