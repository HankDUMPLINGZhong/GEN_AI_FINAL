import datetime
import json
import os
from pathlib import Path

class MemoryEvent:
    """ Represents a single event in the AI Lecturer's memory (lecture progress, student interactions). """
    def __init__(self, event_type, content, timestamp=None):
        """
        :param event_type: Type of event (lecture, question, feedback, explanation, etc.)
        :param content: Textual content of the event
        :param timestamp: When the event occurred
        """
        self.event_type = event_type
        self.content = content
        self.timestamp = timestamp or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        """ Convert the event to a dictionary for easy storage. """
        return {
            "type": self.event_type,
            "content": self.content,
            "timestamp": self.timestamp
        }

class AILecturerMemory:
    """ AI Lecturer Memory system for tracking lecture progress in real-time. """

    def __init__(self, subject, classNum):
        self.memory_stream = []  # Stores sequence of events
        self.subject = subject
        self.classNum = classNum
        self.log_path = Path(__file__).parent.parent / "class_log" / self.subject / f"{self.subject}_class_{self.classNum}_log.json"

    def log_event(self, event_type, content):
        """
        Logs an event into the memory stream.

        :param event_type: Category of event (e.g., 'lecture', 'question', 'feedback', 'explanation')
        :param content: The actual content of the event
        """
        event = MemoryEvent(event_type, content)
        self.memory_stream.append(event)
        print(f"[Memory Log] ({event.timestamp}) {event_type.upper()}: {content}")
        self.save_memory()

    def get_recent_events(self, n=5):
        """ Retrieves the last 'n' events from the memory. """
        return [event.to_dict() for event in self.memory_stream[-n:]]

    def save_memory(self):
        """ Saves the memory stream to a file. """
        with open(self.log_path, "w") as f:
            json.dump([event.to_dict() for event in self.memory_stream], f, indent=4)
        print(f"Memory saved to {self.log_path}")
