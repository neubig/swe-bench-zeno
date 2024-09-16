"""Perform grid search over many parameters."""

import os
import re
from data_utils import load_data
import argparse
import zeno_client
import pandas as pd


def main(input_files: list[str]):
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
            "problem_statement": [x[1] for x in data[0]],
        },
        index=ids,
    )
    df_data["statement_length"] = df_data["problem_statement"].apply(len)
    df_data["repo"] = df_data["id"].str.rsplit("-", n=1).str[0]
    vis_project = vis_client.create_project(
        name="OD swe-bench visualization",
        view={
            "data": {"type": "markdown"},
            "label": {"type": "text"},
            "output": {"type": "text"},
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Visualize results from SWE-bench experiments."
    )
    parser.add_argument("input_files", help="Path to multiple input files", nargs="+")
    args = parser.parse_args()
    main(args.input_files)
