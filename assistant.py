import sys
import cmd
from core.llm_client import call_groq
from core.memory import MemoryStore
from core.stack_manager import load_stack, update_topic_status, add_topic, merge_external_updates
from core.interview import generate_interview_questions, quiz

memory = MemoryStore()

class LearningAssistant(cmd.Cmd):
    intro = "Welcome to your AI Learning Assistant. Type 'help' for commands.\n"
    prompt = "(you) "
    
    def __init__(self):
        super().__init__()
        self.current_topic = None
    
    def do_discuss(self, arg):
        "discuss <topic> - Start discussing a topic (e.g., discuss RAG)"
        self.current_topic = arg.strip()
        prompt = f"Let's learn about {self.current_topic}. Explain core concepts in simple terms and ask me if I have questions."
        response = call_groq(prompt, system="You are a friendly tutor. Keep explanations concise.")
        print(f"\nAssistant: {response}\n")
        memory.add_chat_message(f"Start discussing {self.current_topic}", response, self.current_topic)
    
    def default(self, line):
        # Any normal conversation – treat as follow-up
        if not self.current_topic:
            print("Please set a topic first using 'discuss <topic>'")
            return
        # Retrieve relevant past conversation
        past = memory.retrieve_similar(line, n_results=2)
        context = "\n".join(past) if past else ""
        prompt = f"Current topic: {self.current_topic}\nPrevious relevant discussion: {context}\nUser: {line}\nAssistant:"
        response = call_groq(prompt, system="Continue the learning conversation. Be helpful and concise.")
        print(f"\nAssistant: {response}\n")
        memory.add_chat_message(line, response, self.current_topic)
    
    def do_status(self, arg):
        "Show current learning progress"
        stack = load_stack()
        print("\n--- Learning Progress ---")
        for t in stack['topics']:
            print(f"{t['name']}: {t['status']}")
        print()
    
    def do_mark(self, arg):
        "mark <topic> as <status> - e.g., mark RAG as completed"
        parts = arg.split(" as ")
        if len(parts) != 2:
            print("Usage: mark <topic> as <status> (status: not_started, discussing, interview_ready, completed)")
            return
        topic, status = parts[0].strip(), parts[1].strip()
        if update_topic_status(topic, status):
            print(f"Updated {topic} to {status}")
        else:
            print("Topic not found")
    
    def do_generate(self, arg):
        "generate interview for <topic>"
        topic = arg.replace("interview for ", "").strip()
        result = generate_interview_questions(topic)
        print(result)
    
    def do_quiz(self, arg):
        "quiz <topic> - Start a quiz on the topic"
        topic = arg.strip()
        quiz(topic)
    
    def do_add_topic(self, arg):
        "add_topic <name> : subtopic1, subtopic2 - Add new main topic"
        if " : " in arg:
            name, subs = arg.split(" : ")
            subtopics = [s.strip() for s in subs.split(",")]
        else:
            name = arg
            subtopics = []
        if add_topic(name, subtopics):
            print(f"Topic '{name}' added.")
    
    def do_merge_stack(self, arg):
        "merge_stack <json_file> - Merge external tech_stack.json edits"
        filepath = arg.strip()
        import json
        with open(filepath) as f:
            new_data = json.load(f)
        merge_external_updates(new_data)
        print("Stack merged successfully")
    
    def do_export_mermaid(self, arg):
        "Generate Mermaid diagram from current stack"
        stack = load_stack()
        lines = ["graph TD"]
        for t in stack['topics']:
            node_id = t['name'].replace(" ", "_")
            lines.append(f"    {node_id}[\"{t['name']}\"]")
            # Simple grouping – you can enhance
        with open("exported_stack.mmd", "w") as f:
            f.write("\n".join(lines))
        print("Exported to exported_stack.mmd")
    
    def do_exit(self, arg):
        "Exit the assistant"
        print("Goodbye!")
        return True

if __name__ == "__main__":
    LearningAssistant().cmdloop()