import configparser

import requests
import os 

from text_utils import parse_list
from findLLM import get_active_llm_from_config

def load_config(file_path=None):
    if file_path is None:
        # Get the directory of the current script (findLLM.py)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct the path to settings.cfg relative to the script
        file_path = os.path.join(script_dir, 'settings.cfg')

    config = configparser.ConfigParser()
    
    print(f"Attempting to read config from: {os.path.abspath(file_path)}")
    
    if not os.path.exists(file_path):
        print(f"Error: Config file not found at {file_path}")
        return {}

    try:
        with open(file_path, 'r') as f:
            config.read_file(f)
    except Exception as e:
        print(f"Error reading config file: {e}")
        return {}

    sections = config.sections()
    print(f"Sections found in config: {sections}")

    if not sections:
        print("Warning: No sections found in the config file.")

    config_dict = {section: dict(config[section]) for section in sections}
    
    return config


def check_llm(name, url, endpoint):
    try:
        full_url = f"{url}{endpoint}"
        print(f"Checking {name} at {full_url}")
        response = requests.get(full_url, timeout=2)
        if response.status_code == 200:
            print(f"{name} is available")
            return name
        else:
            print(f"{name} returned status code {response.status_code}")
    except requests.RequestException as e:
        print(f"Error checking {name}: {e}")
    return None


def build_payload(prompt, settings):
    payload = {}
    payload_structure = eval(settings.get("payload_structure", "{}"))

    for key, value in payload_structure.items():
        if isinstance(value, str):
            payload[key] = prompt if value == "prompt" else settings.get(value, "")
        elif isinstance(value, list):
            payload[key] = [
                {
                    sub_key: (
                        prompt if sub_value == "prompt" else settings.get(sub_value, "")
                    )
                    for sub_key, sub_value in item.items()
                }
                for item in value
                if isinstance(item, dict)
            ]
    return payload


def query_llm(prompt, active_llm, config=None):
    config = config or load_config()

    if not active_llm:
        print("Error: No active LLM specified")
        return None

    # print(f"Active LLM: {active_llm}")
    # print(f"Config Sections: {config.sections()}")

    if active_llm not in config:
        print(f"Error: {active_llm} not found in config")
        return None

    settings = {**config["DEFAULT"], **config[active_llm]}
    #print(f"Settings: {settings}")

    url = settings["url"]
    endpoint = settings.get("endpoint", "")
    full_url = f"{url}{endpoint}"

    headers = {"Content-Type": "application/json"}
    payload = {
        "model": settings.get("model", "mistral:latest"),
        "prompt": prompt,
        "stream": settings.get("stream", "false").lower() == "true",
    }

    print(f"URL: {full_url}")
    print(f"Payload: {payload}")

    try:
        response = requests.post(full_url, json=payload, headers=headers)
        response.raise_for_status()
        print(f"Response status code: {response.status_code}")
        print(f"Response content text: {response.text}")
        return response.json()
    except requests.RequestException as e:
        print(f"Error querying {active_llm}: {e}")
        if e.response:
            print(f"Response status code: {e.response.status_code}")
            print(f"Response content: {e.response.text}")
        else:
            print("No response received")
        return None


def extract_response(response, response_key):
    keys = response_key.split(".")
    for key in keys:
        if key.isdigit():
            response = response[int(key)]
        else:
            response = response.get(key, {})
    return response


def get_response(response, active_llm, config=None):
    config = config or load_config()
    settings = {**config["DEFAULT"], **config[active_llm]}
    response_key = settings.get("response_key", "")
    return extract_response(response, response_key)


def get_llm_response(prompt):
    # applies segmentation filtering to response
    config = load_config()
    active_llm = get_active_llm_from_config()

    if active_llm:
        response = query_llm(prompt, active_llm, config)
        if response:
            content = get_response(response, active_llm, config)
            return parse_list(content)  # only if it's a list item!
        return "Error: Failed to get a response from the LLM"
    return "Error: No active Local LLM found"


def get_clean_llm_response(prompt):
    # raw response
    config = load_config()
    active_llm = get_active_llm_from_config()

    if active_llm:
        response = query_llm(prompt, active_llm, config)
        if response:
            content = get_response(response, active_llm, config)
            return content  # only if it's a NOT list item, aka a Riff!
        return "Error: Failed to get a response from the LLM"
    return "Error: No active Local LLM found"
