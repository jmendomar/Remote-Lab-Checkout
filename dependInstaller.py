import os
import subprocess

# Define the path to the dependencies file
dependencies_file = os.path.join("Assets", "dependencies.txt")

# Check if the dependencies file exists
if not os.path.isfile(dependencies_file):
    print(f"Dependencies file '{dependencies_file}' not found.")
    exit(1)

# Read the dependencies from the file
with open(dependencies_file, "r") as file:
    dependencies = file.readlines()

# Ask the user if they want to use a proxy
use_proxy = input("Do you want to use a proxy? (y/n): ").lower().strip()
proxy_param = []

if use_proxy == "y":
    # Get the proxy details from the user
    proxy_host = input("Proxy host: ")
    proxy_port = input("Proxy port: ")

    # Construct the proxy parameter for pip
    proxy_param = [
        "--proxy",
        f"http://{proxy_host}:{proxy_port}"
    ]

# Install each dependency using pip
for dependency in dependencies:
    # Remove leading/trailing whitespaces and newlines
    dependency = dependency.strip()

    # Skip empty lines and comments
    if not dependency or dependency.startswith("#"):
        continue

    # Install the dependency using pip with or without proxy
    print(f"Installing '{dependency}'...")
    command = ["pip", "install"] + proxy_param + [dependency]
    subprocess.run(command, check=True)

print("All dependencies installed successfully.")
