"""
Extract structural features from Python code using AST analysis.
"""
from __future__ import annotations

import ast
import tokenize
from io import StringIO

from analysis.features.metrics import Metrics

class CodeMetrics(Metrics):
    number_of_functions: int = 0
    number_of_classes: int = 0
    number_of_methods: int = 0
    max_nested_depth: int = 0
    number_of_lines: int = 0
    number_of_comment_lines: int = 0
    number_of_docstring_lines: int = 0
    number_of_control_statements: int = 0
    number_of_variables: int = 0
    average_function_length: float = 0
    max_function_length: int = 0
    number_of_function_parameters: int = 0
    number_of_returns: int = 0
    number_of_imports: int = 0
    number_of_decorators: int = 0

class StructureVisitor(ast.NodeVisitor):
    """AST visitor to collect code structure metrics."""
    
    def __init__(self):
        self._reset()
        
    def _reset(self) -> None:
        """Reset all tracking information.
        
        When using the same visitor instance on multiple ASTs, call this method between traversals.
        """
        self.metrics = CodeMetrics()
        self.current_depth = 0
        self.function_lines = []
        self.variables = set()

    def visit_FunctionDef(self, node):
        self.metrics.number_of_functions += 1
        self.metrics.number_of_decorators += len(node.decorator_list)
        self.metrics.number_of_function_parameters += len(node.args.args)
        
        # Count function lines
        func_lines = node.end_lineno - node.lineno + 1
        self.function_lines.append(func_lines)
        
        # Visit function body
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        self.metrics.number_of_classes += 1
        self.generic_visit(node)
    
    def visit_Return(self, node):
        self.metrics.number_of_returns += 1
        self.generic_visit(node)
    
    def visit_Import(self, node):
        self.metrics.number_of_imports += len(node.names)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        self.metrics.number_of_imports += len(node.names)
        self.generic_visit(node)
    
    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            self.variables.add(node.id)
        self.generic_visit(node)
    
    def visit(self, node):
        """Track nesting depth during traversal."""
        control_flow_nodes = (
            ast.If, ast.For, ast.While, ast.Try,
            ast.With, ast.AsyncWith, ast.AsyncFor
        )
        
        if isinstance(node, control_flow_nodes):
            self.metrics.number_of_control_statements += 1
            self.current_depth += 1
            self.metrics.max_nested_depth = max(
                self.metrics.max_nested_depth,
                self.current_depth
            )
            
        super().visit(node)
        
        if isinstance(node, control_flow_nodes):
            self.current_depth -= 1

def count_comments_and_docstrings(code: str) -> tuple[int, int]:
    """Count comment and docstring lines in code."""
    comment_lines = 0
    docstring_lines = 0
    
    # Count comments using tokenize
    try:
        tokens = tokenize.generate_tokens(StringIO(code).readline)
        for token in tokens:
            if token.type == tokenize.COMMENT:
                comment_lines += 1
    except tokenize.TokenError:
        pass
    
    # Count docstrings using AST
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                if ast.get_docstring(node):
                    docstring = ast.get_docstring(node)
                    docstring_lines += len(docstring.split('\n'))
    except SyntaxError:
        pass
    
    return comment_lines, docstring_lines

def extract_file_metrics(code: str) -> CodeMetrics:
    """Extract metrics from a Python file."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return CodeMetrics()
    
    visitor = StructureVisitor()
    visitor.visit(tree)
    metrics = visitor.metrics
    
    # Update metrics that need post-processing
    metrics.number_of_variables = len(visitor.variables)
    metrics.number_of_lines = len(code.split('\n'))
    
    if visitor.function_lines:
        metrics.avg_function_length = sum(visitor.function_lines) / len(visitor.function_lines)
        metrics.max_function_length = max(visitor.function_lines)
    
    comment_lines, docstring_lines = count_comments_and_docstrings(code)
    metrics.number_of_comment_lines = comment_lines
    metrics.number_of_docstring_lines = docstring_lines
    
    return metrics

# Monkey patch the extraction into CodeMetrics
CodeMetrics.from_str = extract_file_metrics