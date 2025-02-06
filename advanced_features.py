"""
Advanced feature extraction for code analysis.
"""
import ast
from typing import Dict, List, Set, Optional
from dataclasses import dataclass
import networkx as nx

@dataclass
class TypeFeatures:
    n_type_annotations: int = 0
    n_generic_types: int = 0
    n_union_types: int = 0
    n_optional_types: int = 0
    n_callable_types: int = 0
    n_custom_types: int = 0
    type_complexity: float = 0.0

@dataclass
class ErrorFeatures:
    n_try_blocks: int = 0
    n_except_handlers: int = 0
    n_finally_blocks: int = 0
    n_raise_statements: int = 0
    max_except_depth: int = 0
    n_broad_except: int = 0  # except: or except Exception:
    n_specific_except: int = 0  # except SpecificError:
    error_handling_complexity: float = 0.0

@dataclass
class DependencyFeatures:
    n_function_calls: int = 0
    n_unique_calls: int = 0
    max_call_depth: int = 0
    n_circular_deps: int = 0
    import_depth: int = 0
    n_internal_deps: int = 0
    n_external_deps: int = 0
    dep_complexity: float = 0.0

class AdvancedVisitor(ast.NodeVisitor):
    """AST visitor for extracting advanced code features."""
    
    def __init__(self):
        self.type_features = TypeFeatures()
        self.error_features = ErrorFeatures()
        self.dependency_features = DependencyFeatures()
        self.current_except_depth = 0
        self.function_calls = set()
        self.call_graph = nx.DiGraph()
        self.current_function = None
        
    def visit_AnnAssign(self, node):
        """Visit type annotations in assignments."""
        self.type_features.n_type_annotations += 1
        if hasattr(node.annotation, 'id'):
            if node.annotation.id in ['List', 'Dict', 'Set', 'Tuple']:
                self.type_features.n_generic_types += 1
            elif node.annotation.id == 'Optional':
                self.type_features.n_optional_types += 1
            elif node.annotation.id == 'Union':
                self.type_features.n_union_types += 1
            elif node.annotation.id == 'Callable':
                self.type_features.n_callable_types += 1
            else:
                self.type_features.n_custom_types += 1
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        """Visit function definitions."""
        prev_function = self.current_function
        self.current_function = node.name
        
        # Check return type annotation
        if node.returns:
            self.type_features.n_type_annotations += 1
        
        # Check argument type annotations
        for arg in node.args.args:
            if arg.annotation:
                self.type_features.n_type_annotations += 1
        
        self.generic_visit(node)
        self.current_function = prev_function
    
    def visit_Try(self, node):
        """Visit try blocks."""
        self.error_features.n_try_blocks += 1
        self.current_except_depth += 1
        self.error_features.max_except_depth = max(
            self.error_features.max_except_depth,
            self.current_except_depth
        )
        
        # Analyze except handlers
        for handler in node.handlers:
            self.error_features.n_except_handlers += 1
            if handler.type is None or (
                hasattr(handler.type, 'id') and 
                handler.type.id == 'Exception'
            ):
                self.error_features.n_broad_except += 1
            else:
                self.error_features.n_specific_except += 1
        
        if node.finalbody:
            self.error_features.n_finally_blocks += 1
        
        self.generic_visit(node)
        self.current_except_depth -= 1
    
    def visit_Raise(self, node):
        """Visit raise statements."""
        self.error_features.n_raise_statements += 1
        self.generic_visit(node)
    
    def visit_Call(self, node):
        """Visit function calls."""
        self.dependency_features.n_function_calls += 1
        
        # Get function name
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
        else:
            func_name = "unknown"
        
        self.function_calls.add(func_name)
        
        # Add to call graph
        if self.current_function and func_name != "unknown":
            self.call_graph.add_edge(self.current_function, func_name)
        
        self.generic_visit(node)

def calculate_type_complexity(features: TypeFeatures) -> float:
    """Calculate type system complexity score."""
    return (
        features.n_type_annotations * 1.0 +
        features.n_generic_types * 1.5 +
        features.n_union_types * 2.0 +
        features.n_optional_types * 1.2 +
        features.n_callable_types * 1.8 +
        features.n_custom_types * 1.3
    )

def calculate_error_complexity(features: ErrorFeatures) -> float:
    """Calculate error handling complexity score."""
    return (
        features.n_try_blocks * 1.0 +
        features.n_except_handlers * 1.2 +
        features.n_finally_blocks * 1.5 +
        features.n_raise_statements * 0.8 +
        features.max_except_depth * 2.0 +
        features.n_broad_except * 0.5 +
        features.n_specific_except * 1.5
    )

def calculate_dependency_complexity(features: DependencyFeatures) -> float:
    """Calculate dependency complexity score."""
    return (
        features.n_function_calls * 0.5 +
        features.n_unique_calls * 1.0 +
        features.max_call_depth * 2.0 +
        features.n_circular_deps * 3.0 +
        features.import_depth * 1.5 +
        features.n_internal_deps * 1.0 +
        features.n_external_deps * 1.2
    )

def analyze_dependencies(call_graph: nx.DiGraph) -> DependencyFeatures:
    """Analyze dependency graph properties."""
    features = DependencyFeatures()
    
    # Basic metrics
    features.n_unique_calls = len(call_graph.nodes())
    
    # Calculate max call depth
    try:
        features.max_call_depth = max(
            len(nx.shortest_path(call_graph, source=source, target=target))
            for source in call_graph.nodes()
            for target in call_graph.nodes()
            if nx.has_path(call_graph, source, target)
        ) - 1  # Subtract 1 as path length includes start node
    except ValueError:
        features.max_call_depth = 0
    
    # Find circular dependencies
    try:
        features.n_circular_deps = len(list(nx.simple_cycles(call_graph)))
    except nx.NetworkXNoCycle:
        features.n_circular_deps = 0
    
    return features

def extract_advanced_features(code: str) -> dict:
    """Extract advanced features from Python code."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return {
            'type_features': vars(TypeFeatures()),
            'error_features': vars(ErrorFeatures()),
            'dependency_features': vars(DependencyFeatures())
        }
    
    visitor = AdvancedVisitor()
    visitor.visit(tree)
    
    # Calculate type complexity
    visitor.type_features.type_complexity = calculate_type_complexity(
        visitor.type_features
    )
    
    # Calculate error handling complexity
    visitor.error_features.error_handling_complexity = calculate_error_complexity(
        visitor.error_features
    )
    
    # Analyze dependencies
    dep_analysis = analyze_dependencies(visitor.call_graph)
    visitor.dependency_features.max_call_depth = dep_analysis.max_call_depth
    visitor.dependency_features.n_circular_deps = dep_analysis.n_circular_deps
    visitor.dependency_features.n_unique_calls = dep_analysis.n_unique_calls
    visitor.dependency_features.dep_complexity = calculate_dependency_complexity(
        visitor.dependency_features
    )
    
    return {
        'type_features': vars(visitor.type_features),
        'error_features': vars(visitor.error_features),
        'dependency_features': vars(visitor.dependency_features)
    }