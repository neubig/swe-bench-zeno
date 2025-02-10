from swe_bench.models import Instance
from analysis.metrics.metrics import Metrics

class InstanceMetrics(Metrics):
    problem_statement_length: int = 0

    @staticmethod
    def from_instance(instance: Instance) -> 'InstanceMetrics':
        """Create instance metrics from an instance."""
        metrics = InstanceMetrics()
        metrics.problem_statement_length = len(instance.problem_statement)
        return metrics