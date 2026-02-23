"""
Test script with malicious eval/exec/compile patterns
"""
import subprocess

def dangerous_eval(user_input):
    """CRITICAL: Direct eval with user input"""
    result = eval(user_input)
    return result

def dangerous_exec(user_script):
    """CRITICAL: Direct exec with user input"""
    exec(user_script)

def dangerous_compile(user_code):
    """CRITICAL: Compile and exec with user input"""
    code_obj = compile(user_code, '<string>', 'exec')
    exec(code_obj)

def dangerous_subprocess(user_command):
    """CRITICAL: Subprocess with shell=True and user input"""
    subprocess.run(user_command, shell=True)

def dangerous_os_system(user_command):
    """CRITICAL: os.system with user input"""
    import os
    os.system(user_command)

def dangerous_eval_math(expression):
    """CRITICAL: eval for math expressions"""
    return eval(expression)

def dangerous_exec_globals(user_code):
    """CRITICAL: exec with custom globals"""
    exec(user_code, {'__builtins__': {}})
