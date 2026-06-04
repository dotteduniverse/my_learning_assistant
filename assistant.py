#!/usr/bin/env python3
"""
AI Learning Assistant – CLI with detailed logging
"""

import cmd
import logging
import sys
from pathlib import Path

# Configure logging first
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
logging.basicConfig(
    level=logging.DEBUG,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler("assistant.log", mode="a", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("assistant")

# Import core modules after logging is configured
from core.llm_client import call_groq
from core.memory import MemoryStore
from core.stack_manager import load_stack, update_topic_status, add_topic, merge_external_updates
from core.interview import generate_interview_questions, quiz

logger.info("=" * 60)
logger.info("AI Learning Assistant started")
logger.info("=" * 60)

memory = MemoryStore()

class LearningAssistant(cmd.Cmd):
    intro = "Welcome to your AI Learning Assistant. Type 'help' for commands.\n"
    prompt = "(you) "
    
    def __init__(self):
        super().__init__()
        self.current_topic = None
        logger.debug("CLI instance created")
    
    def do_discuss(self, arg):
        """discuss <topic> - Start discussing a topic (e.g., discuss RAG)"""
        if not arg:
            logger.warning("discuss command called without topic")
            print("Usage: discuss <topic>")
            return
        self.current_topic = arg.strip()
        logger.info(f"Starting discussion on topic: {self.current_topic}")
        
        prompt = f"Let's learn about {self.current_topic}. Explain core concepts in simple terms and ask me if I have questions."
        logger.debug(f"Groq prompt: {prompt[:100]}...")
        response = call_groq(prompt, system="You are a friendly tutor. Keep explanations concise.")
        logger.debug(f"Groq response length: {len(response)} chars")
        
        print(f"\nAssistant: {response}\n")
        memory.add_chat_message(f"Start discussing {self.current_topic}", response, self.current_topic)
        logger.info(f"Discussion on {self.current_topic} started, chat saved to memory")
    
    def default(self, line):
        """Any normal conversation – treat as follow-up"""
        if not self.current_topic:
            logger.warning("User sent message without active topic")
            print("Please set a topic first using 'discuss <topic>'")
            return
        
        logger.debug(f"User message: {line[:50]}... (topic: {self.current_topic})")
        
        # Retrieve relevant past conversation
        past = memory.retrieve_similar(line, n_results=2)
        logger.info(f"Retrieved {len(past)} similar past messages from ChromaDB")
        context = "\n".join(past) if past else ""
        
        prompt = f"Current topic: {self.current_topic}\nPrevious relevant discussion: {context}\nUser: {line}\nAssistant:"
        logger.debug(f"Sending to Groq (context length: {len(context)})")
        response = call_groq(prompt, system="Continue the learning conversation. Be helpful and concise.")
        logger.debug(f"Response received, length: {len(response)}")
        
        print(f"\nAssistant: {response}\n")
        memory.add_chat_message(line, response, self.current_topic)
        logger.debug("Conversation turn saved")
    
    def do_status(self, arg):
        """Show current learning progress"""
        logger.info("Status command executed")
        stack = load_stack()
        print("\n--- Learning Progress ---")
        for t in stack['topics']:
            print(f"{t['name']}: {t['status']}")
        print()
        logger.debug(f"Status displayed for {len(stack['topics'])} topics")
    
    def do_mark(self, arg):
        """mark <topic> as <status> - e.g., mark RAG as completed"""
        parts = arg.split(" as ")
        if len(parts) != 2:
            logger.warning("Invalid mark command format")
            print("Usage: mark <topic> as <status> (status: not_started, discussing, interview_ready, completed)")
            return
        topic, status = parts[0].strip(), parts[1].strip()
        logger.info(f"Marking topic '{topic}' as '{status}'")
        if update_topic_status(topic, status):
            print(f"Updated {topic} to {status}")
            logger.debug(f"Status updated successfully")
        else:
            logger.error(f"Topic '{topic}' not found in stack")
            print("Topic not found")
    
    def do_generate(self, arg):
        """generate interview for <topic>"""
        topic = arg.replace("interview for ", "").strip()
        if not topic:
            logger.warning("Generate command missing topic")
            print("Usage: generate interview for <topic>")
            return
        logger.info(f"Generating interview Q&A for topic: {topic}")
        result = generate_interview_questions(topic)
        print(result)
        logger.debug(f"Generation result: {result[:100]}...")
    
    def do_quiz(self, arg):
        """quiz <topic> - Start a quiz on the topic"""
        topic = arg.strip()
        if not topic:
            logger.warning("Quiz command missing topic")
            print("Usage: quiz <topic>")
            return
        logger.info(f"Starting quiz on topic: {topic}")
        quiz(topic)
        logger.debug("Quiz finished")
    
    def do_add_topic(self, arg):
        """add_topic <name> : sub1, sub2 - Add new main topic"""
        if " : " in arg:
            name, subs = arg.split(" : ")
            subtopics = [s.strip() for s in subs.split(",")]
        else:
            name = arg
            subtopics = []
        name = name.strip()
        if not name:
            logger.warning("Add_topic missing name")
            print("Usage: add_topic <name> : subtopic1, subtopic2")
            return
        logger.info(f"Adding new topic: '{name}' with subtopics {subtopics}")
        if add_topic(name, subtopics):
            print(f"Topic '{name}' added.")
            logger.debug("Topic added successfully")
        else:
            logger.error("Failed to add topic")
    
    def do_merge_stack(self, arg):
        """merge_stack <json_file> - Merge external tech_stack.json edits"""
        filepath = arg.strip()
        if not filepath:
            logger.warning("Merge_stack missing filepath")
            print("Usage: merge_stack data/tech_stack.json")
            return
        logger.info(f"Merging external stack from {filepath}")
        merge_external_updates(filepath)
        print("Stack merged successfully")
        logger.debug("Merge completed")
    
    def do_export_mermaid(self, arg):
        """Generate Mermaid diagram from current stack"""
        logger.info("Exporting stack to Mermaid format")
        stack = load_stack()
        lines = ["graph TD"]
        for t in stack['topics']:
            node_id = t['name'].replace(" ", "_")
            lines.append(f"    {node_id}[\"{t['name']}\"]")
        with open("exported_stack.mmd", "w") as f:
            f.write("\n".join(lines))
        print("Exported to exported_stack.mmd")
        logger.debug(f"Exported {len(stack['topics'])} nodes to exported_stack.mmd")
    
    def do_exit(self, arg):
        """Exit the assistant"""
        logger.info("Assistant exiting")
        print("Goodbye!")
        return True

if __name__ == "__main__":
    LearningAssistant().cmdloop()