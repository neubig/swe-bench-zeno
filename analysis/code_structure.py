"""
Extract structural features from Python code using AST analysis.
"""
import ast
import tokenize
from io import StringIO
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import difflib

@dataclass
class CodeMetrics:
    n_functions: int = 0
    n_classes: int = 0
    n_methods: int = 0
    max_nested_depth: int = 0
    n_lines: int = 0
    n_comment_lines: int = 0
    n_docstring_lines: int = 0
    n_control_statements: int = 0
    n_variables: int = 0
    avg_function_length: float = 0
    max_function_length: int = 0
    n_function_params: int = 0
    n_returns: int = 0
    n_imports: int = 0
    n_decorators: int = 0

class StructureVisitor(ast.NodeVisitor):
    """AST visitor to collect code structure metrics."""
    
    def __init__(self):
        self.metrics = CodeMetrics()
        self.current_depth = 0
        self.function_lines = []
        self.variables = set()
        
    def visit_FunctionDef(self, node):
        self.metrics.n_functions += 1
        self.metrics.n_decorators += len(node.decorator_list)
        self.metrics.n_function_params += len(node.args.args)
        
        # Count function lines
        func_lines = node.end_lineno - node.lineno + 1
        self.function_lines.append(func_lines)
        
        # Visit function body
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        self.metrics.n_classes += 1
        self.generic_visit(node)
    
    def visit_Return(self, node):
        self.metrics.n_returns += 1
        self.generic_visit(node)
    
    def visit_Import(self, node):
        self.metrics.n_imports += len(node.names)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        self.metrics.n_imports += len(node.names)
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
            self.metrics.n_control_statements += 1
            self.current_depth += 1
            self.metrics.max_nested_depth = max(
                self.metrics.max_nested_depth,
                self.current_depth
            )
            
        super().visit(node)
        
        if isinstance(node, control_flow_nodes):
            self.current_depth -= 1

def count_comments_and_docstrings(code: str) -> Tuple[int, int]:
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
    metrics.n_variables = len(visitor.variables)
    metrics.n_lines = len(code.split('\n'))
    
    if visitor.function_lines:
        metrics.avg_function_length = sum(visitor.function_lines) / len(visitor.function_lines)
        metrics.max_function_length = max(visitor.function_lines)
    
    comment_lines, docstring_lines = count_comments_and_docstrings(code)
    metrics.n_comment_lines = comment_lines
    metrics.n_docstring_lines = docstring_lines
    
    return metrics

def parse_patch(patch: str) -> Dict[str, Tuple[str, str]]:
    """Parse a git patch into a dict of {filename: (before, after)}."""
    files = {}
    current_file = None
    current_before = []
    current_after = []
    
    try:
        lines = patch.split('\n')
        for line in lines:
            if line.startswith('diff --git'):
                # Save previous file if exists
                if current_file:
                    files[current_file] = (
                        '\n'.join(current_before),
                        '\n'.join(current_after)
                    )
                # Start new file
                current_file = line.split()[-1].lstrip('b/')
                current_before = []
                current_after = []
            elif line.startswith('+++') or line.startswith('---'):
                continue
            elif line.startswith('+'):
                current_after.append(line[1:])
            elif line.startswith('-'):
                current_before.append(line[1:])
            elif line.startswith(' '):
                current_before.append(line[1:])
                current_after.append(line[1:])
        
        # Save last file
        if current_file:
            files[current_file] = (
                '\n'.join(current_before),
                '\n'.join(current_after)
            )
    except Exception:
        pass
    
    return files

def extract_patch_features(patch: str) -> dict:
    """Extract structural features from a patch."""
    if not patch:
        return {
            'files_modified': 0,
            'total_lines_changed': 0,
            'avg_function_length_before': 0,
            'avg_function_length_after': 0,
            'max_function_length_before': 0,
            'max_function_length_after': 0,
            'total_functions_before': 0,
            'total_functions_after': 0,
            'total_classes_before': 0,
            'total_classes_after': 0,
            'max_nested_depth_before': 0,
            'max_nested_depth_after': 0,
            'total_control_statements_before': 0,
            'total_control_statements_after': 0,
            'total_variables_before': 0,
            'total_variables_after': 0,
            'total_imports_before': 0,
            'total_imports_after': 0,
            'total_returns_before': 0,
            'total_returns_after': 0,
            'total_decorators_before': 0,
            'total_decorators_after': 0,
            'total_comments_before': 0,
            'total_comments_after': 0,
            'total_docstrings_before': 0,
            'total_docstrings_after': 0,
            'avg_function_params_before': 0,
            'avg_function_params_after': 0
        }
    
    files = parse_patch(patch)
    
    # Aggregate metrics across files
    total_before = CodeMetrics()
    total_after = CodeMetrics()
    
    for filename, (before, after) in files.items():
        if not filename.endswith('.py'):
            continue
            
        before_metrics = extract_file_metrics(before)
        after_metrics = extract_file_metrics(after)
        
        # Aggregate metrics
        for metric_name in CodeMetrics.__annotations__:
            before_val = getattr(before_metrics, metric_name)
            after_val = getattr(after_metrics, metric_name)
            
            setattr(total_before, metric_name, 
                   getattr(total_before, metric_name) + before_val)
            setattr(total_after, metric_name,
                   getattr(total_after, metric_name) + after_val)
    
    # Calculate averages where needed
    def safe_div(a, b):
        return a / b if b else 0
    
    return {
        'files_modified': len(files),
        'total_lines_changed': abs(total_after.n_lines - total_before.n_lines),
        'avg_function_length_before': total_before.avg_function_length,
        'avg_function_length_after': total_after.avg_function_length,
        'max_function_length_before': total_before.max_function_length,
        'max_function_length_after': total_after.max_function_length,
        'total_functions_before': total_before.n_functions,
        'total_functions_after': total_after.n_functions,
        'total_classes_before': total_before.n_classes,
        'total_classes_after': total_after.n_classes,
        'max_nested_depth_before': total_before.max_nested_depth,
        'max_nested_depth_after': total_after.max_nested_depth,
        'total_control_statements_before': total_before.n_control_statements,
        'total_control_statements_after': total_after.n_control_statements,
        'total_variables_before': total_before.n_variables,
        'total_variables_after': total_after.n_variables,
        'total_imports_before': total_before.n_imports,
        'total_imports_after': total_after.n_imports,
        'total_returns_before': total_before.n_returns,
        'total_returns_after': total_after.n_returns,
        'total_decorators_before': total_before.n_decorators,
        'total_decorators_after': total_after.n_decorators,
        'total_comments_before': total_before.n_comment_lines,
        'total_comments_after': total_after.n_comment_lines,
        'total_docstrings_before': total_before.n_docstring_lines,
        'total_docstrings_after': total_after.n_docstring_lines,
        'avg_function_params_before': safe_div(
            total_before.n_function_params,
            total_before.n_functions
        ),
        'avg_function_params_after': safe_div(
            total_after.n_function_params,
            total_after.n_functions
        )
    }