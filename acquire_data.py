import json
import os
import random
import subprocess
import argparse
import datasets


def acquire_data(data_dir):
    # OpenDevin data
    od_eval_dir = os.path.join(data_dir, "od_eval")
    if not os.path.exists(od_eval_dir):
        os.makedirs(od_eval_dir, exist_ok=True)
        subprocess.run(
            [
                "git",
                "clone",
                "https://huggingface.co/spaces/OpenDevin/evaluation",
                od_eval_dir,
            ],
            check=True,
        )
        subprocess.run(["git", "lfs", "pull"], cwd=od_eval_dir, check=True)
    else:
        print(f"Directory {od_eval_dir} already exists. Skipping cloning.")
    # SWE-Bench leaderboard data
    swe_eval_dir = os.path.join(data_dir, "swe_eval")
    if not os.path.exists(swe_eval_dir):
        os.makedirs(swe_eval_dir, exist_ok=True)
        subprocess.run(
            [
                "git",
                "clone",
                "https://github.com/swe-bench/experiments.git",
                swe_eval_dir,
            ],
            check=True,
        )
        subprocess.run(["git", "lfs", "pull"], cwd=swe_eval_dir, check=True)
        # Create a map from id to problem statement using the princeton-nlp/SWE-bench
        # dataset
        swe_bench_dataset = datasets.load_dataset("princeton-nlp/SWE-bench")
        problem_statements = {}
        for split in ["train", "dev", "test"]:
            for data in swe_bench_dataset[split]:
                problem_statements[data["instance_id"]] = data["problem_statement"]
        # Convert SWE-bench data to a similar format as OpenDevin
        for split in ["lite", "test"]:
            for experiment in os.listdir(
                os.path.join(swe_eval_dir, "evaluation", split)
            ):
                experiment_dir = os.path.join(
                    swe_eval_dir, "evaluation", split, experiment
                )
                all_data = []
                with open(
                    os.path.join(experiment_dir, "results/results.json"), "r"
                ) as f:
                    json_data = json.load(f)
                    all_instances = {}
                    for result, instance_ids in json_data.items():
                        for instance_id in instance_ids:
                            all_instances[instance_id] = (
                                1
                                if result == "resolved"
                                else all_instances.get(instance_id, 0)
                            )
                    for instance_id, resolved in all_instances.items():
                        problem_statement = problem_statements[instance_id]
                        data = {
                            "instance_id": instance_id,
                            "swe_instance": {"problem_statement": problem_statement},
                            "test_result": {"result": {"resolved": resolved}},
                        }
                        all_data.append(data)
                    random.seed(42)
                    random.shuffle(all_data)
                with open(
                    os.path.join(experiment_dir, "results/od_results.jsonl"), "w"
                ) as f:
                    for data in all_data:
                        print(json.dumps(data), file=f)
    else:
        print(f"Directory {swe_eval_dir} already exists. Skipping cloning.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data_dir",
        type=str,
        default="data",
        help="Directory to download the data into",
    )
    args = parser.parse_args()
    acquire_data(data_dir=args.data_dir)
