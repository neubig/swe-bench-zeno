from pathlib import Path
import click
import pandas as pd

from swe_bench.models import Split
from analysis.models.data import Data
from analysis.metrics import apply_metrics, CodeMetrics, TypeMetrics, ErrorMetrics, DependencyMetrics
from analysis.models.patch import Patch

@click.group()
def cli():
    ...

@cli.command()
@click.argument("filepath", type=click.Path())
@click.option("--split", type=Split, default="verified", callback=lambda _ctx, _, value: Split.from_str(value))
def download(filepath: click.Path, split: Split) -> None:
    """Download and store SWE-bench data locally."""
    data = Data.download(split)
    with open(filepath, "w") as f:
        f.write(data.model_dump_json())

    # Compute size of downloaded file
    file_size = Path(filepath).stat().st_size
    click.echo(f"Downloaded {file_size} bytes to {filepath}")

@cli.command()
@click.argument("filepath", type=click.Path())
def test(filepath: click.Path) -> None:
    """Test loading a data file."""
    with open(filepath) as f:
        data = Data.model_validate_json(f.read())

    rows = []

    # Convert metrics to pandas dataframe
    for instance in data.dataset.instances:
        click.echo(f"Instance: {instance.instance_id}")

        # Test computing metrics
        patch = Patch.from_str(instance.patch)
        metrics = apply_metrics(patch, {"code": CodeMetrics, "type": TypeMetrics, "error": ErrorMetrics, "dependency": DependencyMetrics})

        row = pd.DataFrame({**metrics, "instance_id": instance.instance_id}, index=[0])
        rows.append(row)
    
    df = pd.concat(rows)

    col_sums = df.sum()
    nonzero_cols = col_sums[col_sums > 0].index.tolist()
    print(nonzero_cols)

if __name__ == "__main__":
    cli()