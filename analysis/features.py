from typing import Iterable
import pandas as pd

from analysis.metrics import apply_metrics, CodeMetrics, TypeMetrics, ErrorMetrics, DependencyMetrics, PatchMetrics, InstanceMetrics
from analysis.models.patch import Patch

from swe_bench.models import Instance

def compute_features(instances: Iterable[Instance]) -> pd.DataFrame:
    """Compute features for a list of instances."""
    rows = []
    for instance in instances:
        print(f"Computing metrics for instance {instance.instance_id}...")
        # Test computing metrics
        try:
            patch = Patch.from_instance(instance)
        except:
            print(f"Failed to compute metrics for instance {instance.instance_id}")
            continue
        metrics = apply_metrics(
            patch,
            {
                "code": CodeMetrics,
                "type": TypeMetrics,
                "error": ErrorMetrics,
                "dependency": DependencyMetrics,
            },
        )


        row = pd.DataFrame([{
            **metrics, 
            **PatchMetrics.from_patch(patch).to_dict(prefix="patch"),
            **InstanceMetrics.from_instance(instance).to_dict(prefix="instance"),
            "instance_id": instance.instance_id
        }])
        rows.append(row)
    return pd.concat(rows)