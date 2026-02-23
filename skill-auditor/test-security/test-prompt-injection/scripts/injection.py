"""
Test script with prompt injection patterns
"""
import ai_client

def direct_user_input_in_prompt(user_query):
    """HIGH: Direct user input in prompts"""
    prompt = f"You are a helpful assistant. {user_query}"
    return ai_client.generate(prompt)

def string_concatenation(user_message):
    """HIGH: String concatenation with user input"""
    system_prompt = "You are a helpful assistant."
    full_prompt = system_prompt + " " + user_message
    return ai_client.generate(full_prompt)

def unvalidated_prompt_modifications(base_prompt, user_modifications):
    """HIGH: Unvalidated prompt modifications"""
    modified = base_prompt + " " + user_modifications
    return ai_client.generate(modified)

def role_manipulation(role, query):
    """HIGH: Role manipulation"""
    prompt = f"You are {role}. {query}"
    return ai_client.generate(prompt)

def instruction_override(user_input):
    """HIGH: Instruction override pattern"""
    prompt = f"Follow these instructions: {user_input}"
    return ai_client.generate(prompt)

def system_prompt_injection(user_query):
    """HIGH: System prompt injection"""
    prompt = f"System: {user_query}\nUser: Help me"
    return ai_client.generate(prompt)
