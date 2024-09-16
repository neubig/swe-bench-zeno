import json


def load_data(file_path):
    data_list = []
    with open(file_path, "r") as file:
        for line in file:
            data = json.loads(line)
            instance = data.get("instance_id")
            problem_statement = data.get("swe_instance", {}).get("problem_statement")
            if "fine_grained_report" in data:
                resolved = 1 if data["fine_grained_report"]["resolved"] else 0
            else:
                resolved = (
                    1 if data["test_result"].get("result", {}).get("resolved", 0) else 0
                )
            data_list.append((instance, problem_statement, resolved))
    return data_list
