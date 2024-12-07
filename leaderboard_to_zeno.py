"""
Convert the current SWE-bench leaderboard to a Zeno project.
"""

from datetime import datetime

import pandas as pd
import click
import zeno_client
from swe_bench.models import Split, Dataset, Evaluation
from swe_bench.utilities import get_all_entries


@click.command()
@click.option(
    "--split",
    type=click.Choice(["lite", "verified", "test"]),
    default="verified",
    callback=lambda _ctx, _param, value: Split.from_str(value),
)
@click.option("--zeno-api-key", type=str, envvar="ZENO_API_KEY")
def main(split: Split, zeno_api_key: str | None) -> None:
    """
    Convert the current leaderboard entries to a Zeno project.
    """
    # Build the Zeno client.
    assert zeno_api_key, "No Zeno API key found."
    viz_client = zeno_client.ZenoClient(zeno_api_key)

    # Create a new project.
    current_time = datetime.now()
    viz_project = viz_client.create_project(
        name=f"SWE-bench Leaderboard ({current_time})",
        view={
            "data": {"type": "markdown"},
            "label": {"type": "text"},
            "output": {"type": "code"},
        },
        description=f"SWE-bench leaderboard (as of {current_time}) performance analysis, by entry.",
        public=True,
        metrics=[
            zeno_client.ZenoMetric(name="resolved", type="mean", columns=["resolved"])
        ],
    )

    # Build and upload the dataset.
    dataset = Dataset.from_split(split)
    viz_project.upload_dataset(
        pd.DataFrame([instance.model_dump() for instance in dataset.instances]),
        id_column="instance_id",
        data_column="problem_statement",
    )

    # Get all entries for the split.
    entries = get_all_entries(split)

    for entry in entries:
        print(f"Processing system {entry}...")
        try:
            system = Evaluation.from_github(split, entry)
        except ValueError as e:
            print(f"Skipping {entry}: {e}")
            continue

        data = pd.DataFrame(
            [
                {
                    **prediction.model_dump(),
                    "resolved": system.results.is_resolved(prediction.instance_id),
                }
                for prediction in system.predictions
            ]
        )

        # Some systems have duplicated entries, which Zeno doesn't like.
        if len(data["instance_id"].unique()) != len(data["instance_id"]):
            print(f"{entry} has duplicated entries.")
            data.drop_duplicates("instance_id", inplace=True)

        viz_project.upload_system(
            data,
            name=entry,
            id_column="instance_id",
            output_column="patch",
        )


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
