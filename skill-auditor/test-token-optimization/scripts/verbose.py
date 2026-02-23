"""
Test script with verbose code and redundant patterns
"""
import os
import sys
import json
import time
from datetime import datetime

def verbose_function_with_many_prints(data):
    """Verbose function with excessive print statements"""
    print("Starting to process data...")
    print(f"Data type: {type(data)}")
    print(f"Data length: {len(data)}")
    print("Step 1: Initializing...")
    print("Step 2: Processing...")
    print("Step 3: Analyzing...")
    print("Step 4: Finalizing...")
    print("Processing complete!")
    return data

def redundant_code_blocks(data):
    """Function with redundant code blocks"""
    result = []
    for item in data:
        if item is not None:
            result.append(item)
    
    result2 = []
    for item in data:
        if item is not None:
            result2.append(item)
    
    result3 = []
    for item in data:
        if item is not None:
            result3.append(item)
    
    return result

def long_function_with_deep_nesting(data):
    """Function with deep nesting and many lines"""
    if data is not None:
        if isinstance(data, list):
            if len(data) > 0:
                for item in data:
                    if item is not None:
                        if isinstance(item, dict):
                            if 'key' in item:
                                if item['key'] is not None:
                                    if isinstance(item['key'], str):
                                        if len(item['key']) > 0:
                                            print(item['key'])
                                        else:
                                            print("Empty key")
                                    else:
                                        print("Not a string")
                                else:
                                    print("Key is None")
                            else:
                                print("No key")
                        else:
                            print("Not a dict")
                    else:
                        print("Item is None")
                else:
                    print("No items")
            else:
                print("Empty list")
        else:
            print("Not a list")
    else:
        print("Data is None")

def inefficient_algorithm(data):
    """Inefficient algorithm with O(n^2) complexity"""
    result = []
    for i in range(len(data)):
        for j in range(len(data)):
            if data[i] == data[j]:
                result.append((i, j))
    return result

def duplicate_imports_and_unused():
    """Function with duplicate imports and unused variables"""
    import os
    import sys
    import json
    import time
    from datetime import datetime
    
    unused_var = "This is never used"
    another_unused = 12345
    
    print("Function executed")

def very_long_function():
    """Very long function that should be split"""
    print("Line 1")
    print("Line 2")
    print("Line 3")
    print("Line 4")
    print("Line 5")
    print("Line 6")
    print("Line 7")
    print("Line 8")
    print("Line 9")
    print("Line 10")
    print("Line 11")
    print("Line 12")
    print("Line 13")
    print("Line 14")
    print("Line 15")
    print("Line 16")
    print("Line 17")
    print("Line 18")
    print("Line 19")
    print("Line 20")
    print("Line 21")
    print("Line 22")
    print("Line 23")
    print("Line 24")
    print("Line 25")
    print("Line 26")
    print("Line 27")
    print("Line 28")
    print("Line 29")
    print("Line 30")
    print("Line 31")
    print("Line 32")
    print("Line 33")
    print("Line 34")
    print("Line 35")
    print("Line 36")
    print("Line 37")
    print("Line 38")
    print("Line 39")
    print("Line 40")
    print("Line 41")
    print("Line 42")
    print("Line 43")
    print("Line 44")
    print("Line 45")
    print("Line 46")
    print("Line 47")
    print("Line 48")
    print("Line 49")
    print("Line 50")
    print("Line 51")
    print("Line 52")
    print("Line 53")
    print("Line 54")
    print("Line 55")
    print("Line 56")
    print("Line 57")
    print("Line 58")
    print("Line 59")
    print("Line 60")
    print("Line 61")
    print("Line 62")
    print("Line 63")
    print("Line 64")
    print("Line 65")
    print("Line 66")
    print("Line 67")
    print("Line 68")
    print("Line 69")
    print("Line 70")
    print("Line 71")
    print("Line 72")
    print("Line 73")
    print("Line 74")
    print("Line 75")
    print("Line 76")
    print("Line 77")
    print("Line 78")
    print("Line 79")
    print("Line 80")
    print("Line 81")
    print("Line 82")
    print("Line 83")
    print("Line 84")
    print("Line 85")
    print("Line 86")
    print("Line 87")
    print("Line 88")
    print("Line 89")
    print("Line 90")
    print("Line 91")
    print("Line 92")
    print("Line 93")
    print("Line 94")
    print("Line 95")
    print("Line 96")
    print("Line 97")
    print("Line 98")
    print("Line 99")
    print("Line 100")

def consecutive_prints():
    """Function with consecutive print statements"""
    print("This is line 1")
    print("This is line 2")
    print("This is line 3")
    print("This is line 4")
    print("This is line 5")
    print("This is line 6")
    print("This is line 7")
    print("This is line 8")
    print("This is line 9")
    print("This is line 10")

def debug_prints():
    """Function with debug print statements"""
    x = 10
    print(f"DEBUG: x = {x}")
    y = 20
    print(f"DEBUG: y = {y}")
    z = x + y
    print(f"DEBUG: z = {z}")
    print(f"DEBUG: Result is {z}")
    return z

def redundant_string_operations():
    """Function with redundant string operations"""
    text = "hello world"
    result1 = text.upper()
    result2 = text.upper()
    result3 = text.upper()
    result4 = text.upper()
    result5 = text.upper()
    return result1
