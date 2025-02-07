from __future__ import annotations

import ast
from pydantic import BaseModel

class TypeMetrics(BaseModel):
    number_of_type_annotations: int = 0
    number_of_generic_types: int = 0
    number_of_union_types: int = 0
    number_of_optional_types: int = 0
    number_of_callable_types: int = 0
    number_of_custom_types: int = 0

    def __add__(self, other: TypeMetrics) -> TypeMetrics:
        return TypeMetrics(
            number_of_type_annotations=self.number_of_type_annotations + other.number_of_type_annotations,
            number_of_generic_types=self.number_of_generic_types + other.number_of_generic_types,
            number_of_union_types=self.number_of_union_types + other.number_of_union_types,
            number_of_optional_types=self.number_of_optional_types + other.number_of_optional_types,
            number_of_callable_types=self.number_of_callable_types + other.number_of_callable_types,
            number_of_custom_types=self.number_of_custom_types + other.number_of_custom_types,
        )

    def complexity(self) -> float:
        """Type system complexity score.
        
        Weights chosen by OpenHands.
        """
        return (
            self.number_of_type_annotations * 1.0 +
            self.number_of_generic_types * 1.5 +
            self.number_of_union_types * 2.0 +
            self.number_of_optional_types * 1.2 +
            self.number_of_callable_types * 1.8 +
            self.number_of_custom_types * 1.3
        )
    
class TypeMetricsVisitor(ast.NodeVisitor):
    """AST visitor for extracting advanced code features."""
    
    def __init__(self):
        self.type_metrics = TypeMetrics()
        
    def visit_AnnAssign(self, node):
        """Visit type annotations in assignments."""
        self.type_metrics.number_of_type_annotations += 1
        if hasattr(node.annotation, 'id'):
            if node.annotation.id in ['List', 'Dict', 'Set', 'Tuple']:
                self.type_metrics.number_of_generic_types += 1
            elif node.annotation.id == 'Optional':
                self.type_metrics.number_of_optional_types += 1
            elif node.annotation.id == 'Union':
                self.type_metrics.number_of_union_types += 1
            elif node.annotation.id == 'Callable':
                self.type_metrics.number_of_callable_types += 1
            else:
                self.type_metrics.number_of_custom_types += 1
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        """Visit function definitions."""
        # Check return type annotation
        if node.returns:
            self.type_metrics.number_of_type_annotations += 1
        
        # Check argument type annotations
        for arg in node.args.args:
            if arg.annotation:
                self.type_metrics.number_of_type_annotations += 1
        
        self.generic_visit(node)

def extract_type_metrics(code: str) -> TypeMetrics:
    """Extract type metrics from Python code."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return TypeMetrics()
    
    visitor = TypeMetricsVisitor()
    visitor.visit(tree)
    
    return visitor.type_metrics

TypeMetrics.from_str = extract_type_metrics