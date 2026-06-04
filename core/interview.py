import os
import re
import logging
from core.llm_client import call_groq
from core.stack_manager import load_stack

logger = logging.getLogger(__name__)

INTERVIEW_DIR = "data/interviews"
os.makedirs(INTERVIEW_DIR, exist_ok=True)

def generate_interview_questions(topic_name):
    logger.info(f"Generating interview Q&A for '{topic_name}'")
    stack = load_stack()
    topic = next((t for t in stack['topics'] if t['name'] == topic_name), None)
    if not topic:
        logger.error(f"Topic '{topic_name}' not found in stack")
        return "Topic not found."
    
    prompt = f"Generate 5 common interview questions and concise answers for the topic '{topic_name}'. Subtopics: {topic['subtopics']}. Format: Q1: ... A1: ..."
    logger.debug(f"Prompt to Groq: {prompt[:150]}...")
    questions_text = call_groq(prompt, system="You are an expert technical interviewer.")
    
    filepath = os.path.join(INTERVIEW_DIR, f"{topic_name.replace(' ', '_')}.md")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# Interview Q&A for {topic_name}\n\n{questions_text}")
    logger.info(f"Interview Q&A saved to {filepath} (size: {len(questions_text)} chars)")
    return f"Interview questions generated and saved to {filepath}"

def load_interview_questions(topic_name):
    filepath = os.path.join(INTERVIEW_DIR, f"{topic_name.replace(' ', '_')}.md")
    if os.path.exists(filepath):
        logger.debug(f"Loading interview Q&A from {filepath}")
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        logger.debug(f"No interview file found for {topic_name}")
        return None

def quiz(topic_name):
    logger.info(f"Starting quiz for topic: {topic_name}")
    qa_text = load_interview_questions(topic_name)
    if not qa_text:
        logger.warning(f"No interview questions for {topic_name}")
        print("No interview questions found. Please generate first with 'generate interview for <topic>'.")
        return
    
    print(f"\n--- Quiz on {topic_name} ---")
    print("I'll ask you one question at a time. Type 'skip' to move to next, 'stop' to end.\n")
    
    # Parse Q&A
    questions = re.findall(r'Q\d+\.\s*(.*?)\s*A\d+\.\s*(.*?)(?=Q\d+\.|\Z)', qa_text, re.DOTALL)
    logger.debug(f"Parsed {len(questions)} Q&A pairs from file")
    score = 0
    for i, (q, correct_a) in enumerate(questions, 1):
        print(f"Q{i}: {q.strip()}")
        user = input("Your answer: ")
        if user.lower() == 'stop':
            logger.info("User stopped quiz early")
            break
        if user.lower() == 'skip':
            print(f"Answer: {correct_a.strip()}\n")
            continue
        
        # Evaluate using Groq (one API call per answer)
        eval_prompt = f"User answer: {user}\nCorrect answer: {correct_a}\nIs the user answer essentially correct? Reply only 'YES' or 'NO'."
        logger.debug(f"Evaluating answer for Q{i}")
        verdict = call_groq(eval_prompt, temperature=0).strip().upper()
        if 'YES' in verdict:
            print("✓ Correct!\n")
            score += 1
            logger.debug(f"Q{i} marked correct")
        else:
            print(f"✗ Not quite. The answer: {correct_a.strip()}\n")
            logger.debug(f"Q{i} marked incorrect")
    
    print(f"Quiz finished. Score: {score}/{len(questions)}")
    logger.info(f"Quiz completed: {score}/{len(questions)} correct")