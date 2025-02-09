from pathlib import Path
import click

from swe_bench.models import Split
from analysis.models.data import Data

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

if __name__ == "__main__":
    cli()