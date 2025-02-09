"""
Download and store SWE-bench data locally.
"""
from __future__ import annotations

import json
from pathlib import Path
from swe_bench.models import Split, Dataset, Evaluation
from swe_bench.utilities import get_all_entries

from pydantic import BaseModel

class Data(BaseModel):
    dataset: Dataset
    systems: dict[str, Evaluation]

    @staticmethod
    def download(split: Split) -> Data:
        dataset = Dataset.from_split(split)
        entries = get_all_entries(split)
        systems: dict[str, Evaluation] = {}

        for entry in entries:
            try:
                system = Evaluation.from_github(split, entry)
                systems[entry] = system
            except ValueError as e:
                print(f"Skipping {entry}: {e}")
                continue
        
        return Data(dataset=dataset, systems=systems)
