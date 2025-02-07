import os
import subprocess
import re
import shutil
import platform

from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

import logger

# Delete the directory ./generated_code if it exists
generated_code_dir = "./generated_code"
if os.path.exists(generated_code_dir):
    shutil.rmtree(generated_code_dir)
    logger.log_message("INFO", f"Deleted directory: {generated_code_dir}")
else:
    logger.log_message("INFO", f"Directory does not exist: {generated_code_dir}")

logger.log_message("INFO", "Program started")

system_details = {
    "machine": "",
    "version": "",
    "architecture": "",
    "compiler_version": ""
}

def getSystemArchitecture():
    # Get the machine architecture
    machine = platform.machine().lower()
    if 'arm' in machine:
        system_details["machine"] = 'ARM'
    elif 'x86' in machine or 'amd64' in machine or 'i386' in machine:
        system_details["machine"] = 'x86'
    else:
        logger.log_message("ERROR", f"Unsupported architecture: {machine}")
        raise ValueError(f"Unsupported architecture: {machine}")
    logger.log_message("INFO", f"Machine : {system_details['machine']}")
    
    # Get the system architecture
    architecture = platform.architecture()
    if '64bit' in architecture[0]:
        system_details["architecture"] = '64bit'
    elif '32bit' in architecture[0]:
        system_details["architecture"] = '32bit'
    else:
        logger.log_message("ERROR", f"Unsupported architecture: {architecture[0]}")
        raise ValueError(f"Unsupported architecture: {architecture[0]}")
    logger.log_message("INFO", f"Architecture : {system_details['architecture']}")

    # Get the system version
    os_name = platform.system()
    logger.log_message("INFO", f"Operating system : {os_name}")

    # Get the system version
    os_version = platform.version()
    logger.log_message("INFO", f"OS version : {os_version}")


def getCompilerDetails():
    # Checks if the rust compiler is installed
    if shutil.which("rustc") is None:
        logger.log_message("ERROR", "Rust compiler found")
        raise ValueError("rust compiler not found")

    # Get the version of the rust compiler
    output = subprocess.run(["rustc", "--version"], stdout=subprocess.PIPE)
    version = output.stdout.decode().strip().split(' ')[1]
    if not re.match(r'^\d+\.\d+\.\d+$', version):
        logger.log_message("ERROR", f"Cannot get the version of the compiler: {version}")
        raise ValueError(f"Cannot get the version of the compiler: {version}")
    system_details["compiler_version"] = version
    logger.log_message("INFO", f"Compiler version : {system_details['compiler_version']}")


getSystemArchitecture()
getCompilerDetails()

# Project ideas
projects = [
    "a function that calculates the factorial of a number",
    "Implement a basic calculator that can perform addition, subtraction, multiplication, and division",
    "Create a simple text-based adventure game",
    "Develop a program to convert temperatures between Celsius and Fahrenheit",
    "Build a command-line todo list manager",
    "Write a program to generate and print the Fibonacci sequence",
    "Implement a basic encryption/decryption tool using Caesar cipher",
    "Create a simple guessing game where the computer picks a random number",
    "Develop a program to check if a given string is a palindrome",
    "Build a basic text editor that can create, read, and modify files",
    "Implement a simple sorting algorithm (e.g., bubble sort, insertion sort) and visualize its steps"
]

selected_project = projects[1]

logger.log_message("INFO", f"Selected project: {selected_project}")

# Initialize Ollama model
model = 'codellama'
llm = Ollama(base_url='http://localhost:11434', 
             model=model)
logger.log_message("INFO", f"Chain: Ollama model {model} initialized")

# Create prompt template
prompt_template = PromptTemplate.from_template(
    "Generate rust main.rs file for {task}. Provide the full code, without any explanations or comments:"
)

# Function to extract code between "```" markers
def extract_code(output):
    start = output.find("```") + 3
    end = output.find("```", start)
    code = output[start:end]
    if code[:4] == "rust":
        code = code[4:]
    if output == "":
        logger.log_message("ERROR", "Chain: RAG chain didn't return any code")
        raise ValueError("RAG chain didn't return any code")
    logger.log_message("INFO", "Chain: Code extracted")
    return output[start:end].strip()

# Create chain
chain = prompt_template | llm | StrOutputParser() | extract_code

ittr = 1
num_errors_per_ittr = []
# Invoke the chain
response = chain.invoke({
    "task": f"{selected_project}"
})
logger.log_message("INFO", "Chain invoked")

if response == "":
    logger.log_message("ERROR", "Chain: RAG chain didn't return any code")
    raise ValueError("RAG chain didn't return any code")
logger.log_message("INFO", "Chain: Response generated")

os.makedirs("generated_code", exist_ok=True)
os.chdir("generated_code")
try:
    with open(f"main_{ittr}.rs", "w") as f:
        f.write(response + "\n")
        logger.log_message("INFO", "Chain: File generated")
except Exception as e:
    logger.log_message("ERROR", f"Chain: Failed to write file: {e}")
    raise ValueError(f"Failed to write file: {e}")

# Compile the Rust code
compiler_output = subprocess.run(["rustc", f"main_{ittr}.rs"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
# Checking complier output
if compiler_output.returncode == 0:
    logger.log_message("INFO", "Chain: Code compiled")
    logger.log_message("INFO", "Chain: Compilation successful with 0 warnings and 0 errors")
    run_loop = False
else:
    error_match = re.search(r"aborting due to (\d+) previous error", str(compiler_output))
    if error_match:
        num_errors = error_match.group(1)
        num_errors_per_ittr.append(num_errors)
        logger.log_message("ERROR", f"Chain: Compilation failed with {num_errors} errors")
    else:
        logger.log_message("ERROR", "Chain: Compilation failed with an unknown number of errors")
    run_loop = True


# Correct the code
while run_loop:
    ittr += 1
    logger.log_message("INFO", "Chain: Trying to correct the code")

    # Prompt to correct the code
    prompt_template = PromptTemplate.from_template(
        "Correct the following Rust code for " + selected_project + " provide the corrected code. Provide the full code, without any explanations or comments:\n\n{code}\n\nErrors\n\n{errors}"
    )

    chain = prompt_template | llm | StrOutputParser() | extract_code
    # Invoke the chain
    response = chain.invoke({
        "code": response,
        "errors": compiler_output.stderr
    })

    if response == "":
        logger.log_message("ERROR", "Chain: RAG chain didn't return any code")
        raise ValueError("RAG chain didn't return any code")

    logger.log_message("INFO", "Chain: Response generated")
    try:
        with open(f"main_{ittr}.rs", "w") as f:
            f.write(response + "\n")
            logger.log_message("INFO", "Chain: File generated")
    except Exception as e:
        logger.log_message("ERROR", f"Chain: Failed to write file: {e}")
        raise ValueError(f"Failed to write file: {e}")

    # Compile the Rust code
    compiler_output = subprocess.run(["rustc", f"main_{ittr}.rs"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # Checking complier output
    if compiler_output.returncode == 0:
        logger.log_message("INFO", "Chain: Code compiled")
        logger.log_message("INFO", "Chain: Compilation successful with 0 warnings and 0 errors")
        run_loop = False
    else:
        error_match = re.search(r"aborting due to (\d+) previous error", str(compiler_output))
        if error_match:
            num_errors = error_match.group(1)
            num_errors_per_ittr.append(num_errors)
            logger.log_message("ERROR", f"Chain: Compilation failed with {num_errors} errors")
        else:
            logger.log_message("ERROR", "Chain: Compilation failed with an unknown number of errors")


logger.log_message("INFO", f"Program completed by correcting itself {ittr} times")

# Log the number of errors in each iteration
for i, num_errors in enumerate(num_errors_per_ittr, start=1):
    logger.log_message("INFO", f"Iteration {i}: {num_errors} errors")

logger.log_message("INFO", "Program completed")