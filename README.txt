AI Lecturer (Final Project for Generative AI)
Author: Hank Zhong

Introduction
This is an AI-powered lectuer that aims to 'teach' the user (student) on given project. 
Given an overview of a course as input. The tool will automatically generate course plans and teach each class accordingly.

NOTICE:
to use this package, please replace api keys in utils.py with yours to access ai resources.

Model:
GPT-4o-mini (because of budget)

File struture:
-class_log: stores logs of each class. There's one sample of a class (unfinished) named ap_calculus_class_001.json
-class_material: stores user inputs, which are expected to be JSON files of course material overviews. There's a sample plan for the first course of AP Calculus, which is about introduction of derivatives.
-src
    -classroom.py: UI for virtual classroom
    -feedback_giver.py: check if answers for the exercises are correct
    -lecturer.py: the ai lectuer that use prompt engineering and other class to interact with the student
    -memory.py: store logs and provide reference to the lectuer during class
    -teaching_assistant.py: integrate class materials into readable course plans for ai lecturer
    -utils.py: stores api keys

Run the code:
Go to the directory of the root folder, run python -m streamlit src\classroom.py . A webpage should open in your default browser.

If you have any questions or suggestions, please contact Hank Zhong at hanquan@uchicago.edu
Thank you for using this package.