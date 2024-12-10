import json
import os
import re


def load_data(file_path):
    data_list = []
    with open(file_path, "r") as file:
        for line in file:
            data = json.loads(line)
            instance = data.get("id")
            problem_statement = data.get("problem_statement")
            resolved = data.get("resolved", 0)
            data_list.append((instance, problem_statement, resolved))
    return data_list

def load_data_aider_bench(file_path):
    data_list = []
    with open(file_path, "r") as file:
        for line in file:
            data = json.loads(line)
            instance_id = data.get("id")
            instruction = data.get("instruction")
            resolved = data.get("resolved", 0)
            test_cases = data.get("test_cases")
            tests = data.get("tests")
            trajectory = data.get("trajectory", [])
            data_list.append((instance_id, instruction, resolved, test_cases, tests, trajectory))

    return data_list

def get_model_name_aider_bench(file_path):
    with open(file_path, "r") as file:
        first_line = file.readline()
        data = json.loads(first_line)
        model = data.get("metadata", {}).get("llm_config", {}).get("model")
        return model.split("/")[-1] if model else "unknown"