import os
import json
import logging
from core.utils import load_json, save_json

logger = logging.getLogger(__name__)

STACK_FILE = "data/tech_stack.json"

def load_stack():
    logger.debug(f"Loading stack from {STACK_FILE}")
    try:
        stack = load_json(STACK_FILE)
        logger.info(f"Loaded {len(stack['topics'])} topics from stack")
        return stack
    except Exception as e:
        logger.error(f"Failed to load stack: {e}")
        raise

def save_stack(stack):
    logger.debug(f"Saving stack to {STACK_FILE}")
    save_json(STACK_FILE, stack)
    logger.info(f"Stack saved with {len(stack['topics'])} topics")

def update_topic_status(topic_name, status):
    logger.debug(f"Updating status for '{topic_name}' to '{status}'")
    stack = load_stack()
    for topic in stack['topics']:
        if topic['name'] == topic_name:
            old = topic['status']
            topic['status'] = status
            save_stack(stack)
            logger.info(f"Status changed from '{old}' to '{status}' for topic '{topic_name}'")
            return True
    logger.warning(f"Topic '{topic_name}' not found")
    return False

def add_topic(topic_name, subtopics=None, category=None):
    logger.info(f"Adding new topic '{topic_name}' with subtopics: {subtopics}")
    stack = load_stack()
    new_topic = {
        "name": topic_name,
        "status": "not_started",
        "subtopics": subtopics or [],
        "notes": "",
        "interview_file": f"interviews/{topic_name.replace(' ', '_')}.md"
    }
    stack['topics'].append(new_topic)
    save_stack(stack)
    os.makedirs("data/interviews", exist_ok=True)
    logger.debug("Interview directory ensured")
    return True

def merge_external_updates(new_stack_filepath):
    logger.info(f"Merging external stack from {new_stack_filepath}")
    with open(new_stack_filepath, 'r') as f:
        new_stack = json.load(f)
    current = load_stack()
    current_map = {t['name']: t for t in current['topics']}
    for new_t in new_stack['topics']:
        if new_t['name'] in current_map:
            old = current_map[new_t['name']]
            new_t['status'] = old['status']
            new_t['notes'] = old['notes']
            new_t['interview_file'] = old.get('interview_file', new_t.get('interview_file'))
            logger.debug(f"Preserved progress for '{new_t['name']}': status={old['status']}")
        else:
            logger.info(f"New topic detected: '{new_t['name']}'")
    current['topics'] = new_stack['topics']
    save_stack(current)
    logger.info("Merge completed")