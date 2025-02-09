from pathlib import Path
import click

from swe_bench.models import Split
from analysis.models.data import Data


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
    """Compute features for the downloaded data."""
    with open("data.json") as f:
        data = Data.model_validate_json(f.read())

    df = compute_features(data.dataset.instances)
    df.to_csv("features.csv", index=False)


if __name__ == "__main__":
    cli()
