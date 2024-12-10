"""Perform grid search over many parameters."""

import os
import re
from data_utils import load_data, load_data_aider_bench, get_model_name_aider_bench
import argparse
import zeno_client
import pandas as pd


def visualise_swe_bench(input_files: list[str]):
    """Visualize data from multiple input files."""
    data = [load_data(input_file) for input_file in input_files]
    ids = [x[0] for x in data[0]]
    id_map = {x: i for (i, x) in enumerate(ids)}

    # Find all duplicate values in "ids"
    seen = set()
    duplicates = set()
    for x in ids:
        if x in seen:
            duplicates.add(x)
        seen.add(x)
    print(duplicates)

    vis_client, vis_project = None, None
    vis_client = zeno_client.ZenoClient(os.environ.get("ZENO_API_KEY"))

    # use zeno to visualize
    df_data = pd.DataFrame(
        {
            "id": ids,
            "problem_statement": [{"text": "", "sections": [{"title": "Problem", "content": x[1]}]} for x in data[0]],
        },
        index=ids,
    )
    df_data["statement_length"] = df_data["problem_statement"].apply(lambda x: len(x["sections"][0]["content"]))
    df_data["repo"] = df_data["id"].str.rsplit("-", n=1).str[0]
    vis_project = vis_client.create_project(
        name="OD swe-bench visualization",
        view={
            "data": {"type": "message", "content": {"type": "markdown"}, "role": "user"},
            "label": {"type": "text"},
            "output": {"type": "message", "content": {"type": "markdown"}, "role": "assistant"},
        },
        description="OD issue prediction",
        public=False,
        metrics=[
            zeno_client.ZenoMetric(name="resolved", type="mean", columns=["resolved"]),
        ],
    )
    vis_project.upload_dataset(
        df_data,
        id_column="id",
        data_column="problem_statement",
    )

    # Do evaluation
    for input_file, data_entry in zip(input_files, data):
        resolved = [0] * len(data[0])
        for entry in data_entry:
            resolved[id_map[entry[0]]] = entry[2]
        df_system = pd.DataFrame(
            {
                "id": ids,
                "resolved": resolved,
            },
            index=ids,
        )
        model_name = re.sub(r"data/.*lite/", "", input_file)
        model_name = re.sub(r"(od_output|output).jsonl", "", model_name)
        model_name = model_name.replace("/", "_")
        vis_project.upload_system(
            df_system, name=model_name, id_column="id", output_column="resolved"
        )

def visualize_aider_bench(input_files: list[str]):
    """Visualize data from multiple input files."""
    data = [load_data_aider_bench(input_file) for input_file in input_files]
    ids = [x[0] for x in data[0]]
    id_map = {x: i for (i, x) in enumerate(ids)}

    # Find all duplicate values in "ids"
    seen = set()
    duplicates = set()
    for x in ids:
        if x in seen:
            duplicates.add(x)
        seen.add(x)
    print(duplicates)

    vis_client, vis_project = None, None
    print(os.environ.get("ZENO_API_KEY"))
    vis_client = zeno_client.ZenoClient(os.environ.get("ZENO_API_KEY"))

    # use zeno to visualize
    df_data = pd.DataFrame(
        {
            "id": ids,
            "instruction": [{"text": x[1]} for x in data[0]],
        },
        index=ids,
    )
    df_data["instruction_length"] = df_data["instruction"].apply(lambda x: len(x["text"]))
    #df_data["repo"] = df_data["id"].str.rsplit("-", n=1).str[0]
    vis_project = vis_client.create_project(
        name="Aider Bench Code Editing Visualization",
        view={
            "data": {"type": "message", "content": {"type": "markdown"}, "role": "user"},
            "label": {"type": "text"},
            "output": {"type": "message", "content": {"type": "markdown"}, "role": "assistant"}
        },
        description="Aider Bench Code Editing",
        public=False,
        metrics=[
            zeno_client.ZenoMetric(name="resolved", type="mean", columns=["resolved"]),
        ],
    )
    vis_project.upload_dataset(
        df_data,
        id_column="id",
        data_column="instruction"
    )

    # Do evaluation
    for input_file, data_entry in zip(input_files, data):
        output = []
        resolved = [0] * len(data[0])
        for entry in data_entry:
            resolved[id_map[entry[0]]] = entry[2]
            trajectory = {
                "text": "",
                "sections": [
                    {"title": "Resolved", "content": str(entry[2])},
                    {"title": "Test Cases", "content": str(entry[3])},
                    {"title": "Tests", "content": str(entry[4])},
                    {"title": "Agent Trajectory", "content": ""}
                ]
            }
            for i, step in enumerate(entry[5]):
                trajectory["sections"][3]["content"] += f'### Step {i+1}\n'
                trajectory["sections"][3]["content"] += f'Action: {step["action"]}\n'
                trajectory["sections"][3]["content"] += f'Code: {step["code"]}\n'
                trajectory["sections"][3]["content"] += f'Thought: {step["thought"]}\n'
                trajectory["sections"][3]["content"] += f'Observation: {step["observation"]}\n'
            output.append(trajectory)


        df_system = pd.DataFrame(
            {
                "id": ids,
                "agent output": output,
                "resolved": resolved
            },
            index=ids,
        )

        vis_project.upload_system(
            df_system, name=get_model_name_aider_bench(input_file), id_column="id", output_column="agent output"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Visualize results from SWE-bench experiments."
    )
    parser.add_argument("input_files", help="Path to multiple input files", nargs="+")
    parser.add_argument("benchmark", help="Benchmark to visualize", type=str, choices=["swe-bench", "aider-bench"], default="swe-bench")
    args = parser.parse_args()
    if args.benchmark == "swe-bench":
        visualise_swe_bench(args.input_files)
    else:
        visualize_aider_bench(args.input_files)