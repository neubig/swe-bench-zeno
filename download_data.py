"""
Download and store SWE-bench data locally.
"""
import json
from pathlib import Path
from swe_bench.models import Split, Dataset, Evaluation
from swe_bench.utilities import get_all_entries

def main():
    # Create data directory
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Download verified split data
    split = Split.from_str("verified")
    dataset = Dataset.from_split(split)
    
    # Save dataset instances
    instances = [{
        'instance_id': instance.instance_id,
        'problem_statement': instance.problem_statement,
        'repo': instance.repo,
        'base_commit': instance.base_commit,
    } for instance in dataset.instances]
    
    with open(data_dir / "instances.json", "w") as f:
        json.dump(instances, f)
    
    # Get all entries and their evaluations
    entries = get_all_entries(split)
    systems_data = {}
    
    for entry in entries:
        print(f"Processing system {entry}...")
        try:
            system = Evaluation.from_github(split, entry)
            systems_data[entry] = {
                "predictions": [
                    {
                        "instance_id": pred.instance_id,
                        "patch": pred.patch,
                        "resolved": system.results.is_resolved(pred.instance_id)
                    }
                    for pred in system.predictions
                ]
            }
        except ValueError as e:
            print(f"Skipping {entry}: {e}")
            continue
    
    with open(data_dir / "systems.json", "w") as f:
        json.dump(systems_data, f)

if __name__ == "__main__":
    main()