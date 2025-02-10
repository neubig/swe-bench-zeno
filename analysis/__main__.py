from pathlib import Path
import click

import pandas as pd
import requests
import unidiff

from swe_bench.models import Split
from analysis.models.data import Data
from analysis.performance_gap import top_performers, unresolved_instances
from analysis import features

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report


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

    df = features.compute_features(data.dataset.instances)
    df.to_csv("features.csv", index=False)

@cli.command()
@click.option("--top-k", "-k", default=3, help="Number of top models to consider.")
def feature_corr(top_k: int) -> None:
    """Compute correlation between features and performance gap."""
    # Load the dataset and the features
    with open("data.json") as f:
        data = Data.model_validate_json(f.read())
    
    df = pd.read_csv("features.csv")

    metrics = list(df.columns)
    metrics.remove("instance_id")

    print(f"Evaluating {len(metrics)} features over {len(df)} instances...\n")

    # Source model is always OpenHands
    source = data.systems[data.closest_system("OpenHands")]
    targets = top_performers(data.systems.values(), k=top_k)

    print(f"Source model: {source.metadata.name}\n")
    print(f"Target models: \n{'\n'.join(['\t- ' + t.metadata.name for t in targets])}\n")

    # Compute the performance gap
    gap = unresolved_instances(source, targets)
    df['gap'] = df['instance_id'].apply(lambda instance_id: 1 if instance_id in gap else 0)

    # One-hot encode categorical features
    X = df[metrics]
    y = df['gap']
    
    # Split data
     # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Scale numerical features
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    
    # Train model
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    
    # Print classification report
    y_pred = clf.predict(X_test)
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Get feature importance
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': clf.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\nTop 10 Most Important Features:")
    print(feature_importance.head(10))
    
    basic_features = feature_importance.head(10)['feature'].values
    gap_stats = df[df['gap'] == 1][basic_features].corr()
    print(gap_stats)

@cli.command()
def diff():
    with open("data.json") as f:
        data = Data.model_validate_json(f.read())

    for instance in data.dataset.instances:
        patch = unidiff.PatchSet(instance.patch)
        for patch in unidiff.PatchSet(instance.patch):
            path = patch.path
            
            url = f"https://raw.githubusercontent.com/{instance.repo}/{instance.base_commit}/{path}"
        
            response = requests.get(url)
            response.raise_for_status()

            lines = response.text.splitlines(keepends=True)

            for hunk in patch:
                # Calculate hunk position
                start = hunk.target_start - 1
            
                # Remove lines
                del lines[start:start + hunk.target_length]
            
                # Insert new lines
                lines[start:start] = [line[1:] for line in hunk.target_lines() if line.value.startswith('+')]


            print("BEFORE")
            print("\n".join(lines))

            print("AFTER")
            print("".join(lines))

            break
        # url = f"https://raw.githubusercontent.com/{owner}/{repo}/{commit}/{path}"
        # print(instance)

if __name__ == "__main__":
    cli()
