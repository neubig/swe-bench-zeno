from __future__ import annotations

import ast
from pydantic import BaseModel

class ErrorMetrics(BaseModel):
    n_try_blocks: int = 0
    n_except_handlers: int = 0
    n_finally_blocks: int = 0
    n_raise_statements: int = 0
    max_except_depth: int = 0
    n_broad_except: int = 0  # except: or except Exception:
    n_specific_except: int = 0  # except SpecificError:

    def complexity(self) -> float:
        """Calculate error handling complexity score.
        
        Weights chosen by OpenHands.
        """
        return (
            self.n_try_blocks * 1.0 +
            self.n_except_handlers * 1.2 +
            self.n_finally_blocks * 1.5 +
            self.n_raise_statements * 0.8 +
            self.max_except_depth * 2.0 +
            self.n_broad_except * 0.5 +
            self.n_specific_except * 1.5
        )

    def __add__(self, other: ErrorMetrics) -> ErrorMetrics:
        return ErrorMetrics(
            n_try_blocks=self.n_try_blocks + other.n_try_blocks,
            n_except_handlers=self.n_except_handlers + other.n_except_handlers,
            n_finally_blocks=self.n_finally_blocks + other.n_finally_blocks,
            n_raise_statements=self.n_raise_statements + other.n_raise_statements,
            max_except_depth=max(self.max_except_depth, other.max_except_depth),
            n_broad_except=self.n_broad_except + other.n_broad_except,
            n_specific_except=self.n_specific_except + other.n_specific_except
        )


class ErrorMetricsVisitor(ast.NodeVisitor):
    """AST visitor for extracting advanced code features."""
    
    def __init__(self):
        self.error_metrics = ErrorMetrics()
        self.current_except_depth = 0

    def visit_Try(self, node):
        """Visit try blocks."""
        self.error_metrics.n_try_blocks += 1
        self.current_except_depth += 1
        self.error_metrics.max_except_depth = max(
            self.error_metrics.max_except_depth,
            self.current_except_depth
        )
        
        # Analyze except handlers
        for handler in node.handlers:
            self.error_metrics.n_except_handlers += 1
            if handler.type is None or (
                hasattr(handler.type, 'id') and 
                handler.type.id == 'Exception'
            ):
                self.error_metrics.n_broad_except += 1
            else:
                self.error_metrics.n_specific_except += 1
        
        if node.finalbody:
            self.error_metrics.n_finally_blocks += 1
        
        self.generic_visit(node)
        self.current_except_depth -= 1
    
    def visit_Raise(self, node):
        """Visit raise statements."""
        self.error_metrics.n_raise_statements += 1
        self.generic_visit(node)


def extract_error_metrics(code: str) -> ErrorMetrics:
    """Extract advanced features from Python code."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return ErrorMetrics()
    
    visitor = ErrorMetricsVisitor()
    visitor.visit(tree)

    return visitor.error_metrics

ErrorMetrics.from_str = extract_error_metrics