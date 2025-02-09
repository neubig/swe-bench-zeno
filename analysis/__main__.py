from pathlib import Path
import click
import pandas as pd

from swe_bench.models import Split
from analysis.models.data import Data
from analysis.metrics import (
    apply_metrics,
    CodeMetrics,
    TypeMetrics,
    ErrorMetrics,
    DependencyMetrics,
)
from analysis.models.patch import Patch


@click.group()
def cli(): ...


@cli.command()
@click.option(
    "--split",
    type=Split,
    default="verified",
    callback=lambda _ctx, _, value: Split.from_str(value),
)
def download(split: Split) -> None:
    """Download and store SWE-bench data locally."""
    data = Data.download(split)
    with open("data.json", "w") as f:
        f.write(data.model_dump_json())

    # Compute size of downloaded file
    file_size = Path("data.json").stat().st_size
    click.echo(f"Downloaded {file_size} bytes to data.json")


@cli.command()
def compute_features() -> None:
    """Test loading a data file."""
    with open("data.json") as f:
        data = Data.model_validate_json(f.read())

    # Convert metrics to pandas dataframe
    rows = []
    for instance in data.dataset.instances:
        # Test computing metrics
        patch = Patch.from_str(instance.patch)
        metrics = apply_metrics(
            patch,
            {
                "code": CodeMetrics,
                "type": TypeMetrics,
                "error": ErrorMetrics,
                "dependency": DependencyMetrics,
            },
        )

        row = pd.DataFrame([{**metrics, "instance_id": instance.instance_id}])
        rows.append(row)

    df = pd.concat(rows)

    # Save to CSV
    df.to_csv("features.csv", index=False)


if __name__ == "__main__":
    cli()
