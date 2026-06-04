import os
from core.llm_client import call_groq
from core.stack_manager import load_stack, save_stack

INTERVIEW_DIR = "data/interviews"
os.makedirs(INTERVIEW_DIR, exist_ok=True)

def generate_interview_questions(topic_name):
    stack = load_stack()
    topic = next((t for t in stack['topics'] if t['name'] == topic_name), None)
    if not topic:
        return "Topic not found."
    
    # Only call Groq if needed
    prompt = f"Generate 5 common interview questions and concise answers for the topic '{topic_name}'. Subtopics: {topic['subtopics']}. Format: Q1: ... A1: ..."
    questions_text = call_groq(prompt, system="You are an expert technical interviewer.")
    
    # Save to file
    filepath = os.path.join(INTERVIEW_DIR, f"{topic_name.replace(' ', '_')}.md")
    with open(filepath, 'w') as f:
        f.write(f"# Interview Q&A for {topic_name}\n\n{questions_text}")
    
    # Also store in ChromaDB later if needed
    return f"Interview questions generated and saved to {filepath}"

def load_interview_questions(topic_name):
    filepath = os.path.join(INTERVIEW_DIR, f"{topic_name.replace(' ', '_')}.md")
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return f.read()
    return None

def quiz(topic_name):
    qa_text = load_interview_questions(topic_name)
    if not qa_text:
        return "No interview questions found. Please generate first with 'generate interview for <topic>'."
    
    # Simple interactive quiz
    print(f"\n--- Quiz on {topic_name} ---")
    print("I'll ask you one question at a time. Type 'skip' to move to next, 'stop' to end.\n")
    # Parse Q&A from text (naive but works)
    import re
    questions = re.findall(r'Q\d+\.\s*(.*?)\s*A\d+\.\s*(.*?)(?=Q\d+\.|\Z)', qa_text, re.DOTALL)
    score = 0
    for i, (q, correct_a) in enumerate(questions, 1):
        print(f"Q{i}: {q.strip()}")
        user = input("Your answer: ")
        if user.lower() == 'stop':
            break
        if user.lower() == 'skip':
            print(f"Answer: {correct_a.strip()}\n")
            continue
        # Simple evaluation using Groq (optional, but we can use local check)
        eval_prompt = f"User answer: {user}\nCorrect answer: {correct_a}\nIs the user answer essentially correct? Reply only 'YES' or 'NO'."
        verdict = call_groq(eval_prompt, temperature=0).strip().upper()
        if 'YES' in verdict:
            print("✓ Correct!\n")
            score += 1
        else:
            print(f"✗ Not quite. The answer: {correct_a.strip()}\n")
    print(f"Quiz finished. Score: {score}/{len(questions)}")