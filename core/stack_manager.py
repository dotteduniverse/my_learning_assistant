import os
import json
from core.utils import load_json, save_json

STACK_FILE = "data/tech_stack.json"

def load_stack():
    return load_json(STACK_FILE)

def save_stack(stack):
    save_json(STACK_FILE, stack)

def update_topic_status(topic_name, status):
    stack = load_stack()
    for topic in stack['topics']:
        if topic['name'] == topic_name:
            topic['status'] = status
            save_stack(stack)
            return True
    return False

def add_topic(topic_name, subtopics=None, category=None):
    stack = load_stack()
    # If category given, find parent? For simplicity, we add as new main topic
    new_topic = {
        "name": topic_name,
        "status": "not_started",
        "subtopics": subtopics or [],
        "notes": "",
        "interview_file": f"interviews/{topic_name.replace(' ', '_')}.md"
    }
    stack['topics'].append(new_topic)
    save_stack(stack)
    # Ensure interview file folder exists
    os.makedirs("data/interviews", exist_ok=True)
    return True

# Merge external JSON edits (preserve progress)
def merge_external_updates(new_stack_json):
    current = load_stack()
    # Map name -> current topic
    current_map = {t['name']: t for t in current['topics']}
    for new_t in new_stack_json['topics']:
        if new_t['name'] in current_map:
            # keep old status, notes, interview_file if present
            old = current_map[new_t['name']]
            new_t['status'] = old['status']
            new_t['notes'] = old['notes']
            new_t['interview_file'] = old.get('interview_file', new_t.get('interview_file'))
        else:
            # new topic, ensure interview file path
            if 'interview_file' not in new_t:
                new_t['interview_file'] = f"interviews/{new_t['name'].replace(' ', '_')}.md"
    current['topics'] = new_stack_json['topics']
    save_stack(current)