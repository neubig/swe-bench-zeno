import json
import os


def load_data(file_path):
    data_list = []
    directory_name = os.path.dirname(file_path)
    print("Directory name: ", directory_name)
    with open(os.path.join(directory_name, "report.json"), "r") as report_file:
        data = json.load(report_file)
        resolved_ids = data.get("resolved_ids", [])
    with open(file_path, "r") as file:
        for line in file:
            data = json.loads(line)
            instance = data.get("instance_id")
            problem_statement = data.get("instance", {}).get("problem_statement")
            resolved = 1 if instance in resolved_ids else 0
            data_list.append((instance, problem_statement, resolved))
    return data_list
