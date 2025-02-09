from typing import Iterable
import pandas as pd

from analysis.metrics import apply_metrics, CodeMetrics, TypeMetrics, ErrorMetrics, DependencyMetrics
from analysis.models.patch import Patch

from swe_bench.models import Instance

def compute_features(instances: Iterable[Instance]) -> pd.DataFrame:
    """Compute features for a list of instances."""
    rows = []
    for instance in instances:
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
    return pd.concat(rows)