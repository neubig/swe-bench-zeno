import ast
import textwrap

from pydantic import BaseModel

class Metrics(BaseModel):
    """Base class for all metric models.
    
    Provides utility functions for adding, subtracting, and taking absolute values of models.
    """

    def __add__[T: Metrics](self: T, other: T) -> T:
        """Add corresponding fields from two models of the same type."""
        if not isinstance(other, type(self)):
            raise TypeError(f"Cannot add {type(self).__name__} with {type(other).__name__}")
        
        new_values = {}
        for field_name in self.model_fields:
            self_value = getattr(self, field_name)
            other_value = getattr(other, field_name)
            
            # Skip None values
            if self_value is None or other_value is None:
                new_values[field_name] = None
                continue
                
            try:
                new_values[field_name] = self_value + other_value
            except TypeError as e:
                raise TypeError(f"Cannot add field '{field_name}': {str(e)}")
        
        return type(self)(**new_values)

    def __sub__[T: Metrics](self: T, other: T) -> T:
        """Subtract corresponding fields from two models of the same type."""
        if not isinstance(other, type(self)):
            raise TypeError(f"Cannot subtract {type(self).__name__} with {type(other).__name__}")
        
        new_values = {}
        for field_name in self.model_fields:
            self_value = getattr(self, field_name)
            other_value = getattr(other, field_name)
            
            # Skip None values
            if self_value is None or other_value is None:
                new_values[field_name] = None
                continue
                
            try:
                new_values[field_name] = self_value - other_value
            except TypeError as e:
                raise TypeError(f"Cannot subtract field '{field_name}': {str(e)}")
        
        return type(self)(**new_values)

    def __abs__[T: Metrics](self: T) -> T:
        """Return a new model with absolute values of all fields."""
        new_values = {}
        for field_name in self.model_fields:
            value = getattr(self, field_name)
            
            # Skip None values
            if value is None:
                new_values[field_name] = None
                continue
                
            try:
                new_values[field_name] = abs(value)
            except TypeError as e:
                raise TypeError(f"Cannot take absolute value of field '{field_name}': {str(e)}")
        
        return type(self)(**new_values)

    def to_dict(self, prefix: str | None = None, suffix: str | None = None) -> dict[str, int | float]:
        """Convert model to dictionary."""
        def update_field_name(field_name: str, separator: str = "/") -> str:
            if prefix is not None:
                field_name = f"{prefix}{separator}{field_name}"
            if suffix is not None:
                field_name = f"{field_name}{separator}{suffix}"
            return field_name
        
        return {
            update_field_name(field_name): getattr(self, field_name)
            for field_name in self.model_fields
        }

def normalize_indentation(code: str) -> str:
    """Remove any common leading indentation from every line in code."""
    if not code:
        return code
    
    # Filter out empty lines for dedent calculation
    lines = [line for line in code.splitlines() if line.strip()]
    if not lines:
        return code
    
    # Dedent the code
    return textwrap.dedent(code)

def parse_code_fragment(code: str) -> ast.AST:
    """Try parsing code with various indentation fixes."""
    # List of transformations to try
    attempts = [
        lambda x: x,  # Try as-is
        normalize_indentation,  # Try with normalized indentation
        lambda x: "if True:\n" + textwrap.indent(x, '    '),  # Try wrapping in if block
        lambda x: "def dummy():\n" + textwrap.indent(x, '    ')  # Try wrapping in function
    ]
    
    for transform in attempts:
        try:
            transformed_code = transform(code)
            return ast.parse(transformed_code)
        except (SyntaxError, IndentationError):
            continue
    
    # If full parsing fails, try line by line
    valid_nodes = []
    lines = code.splitlines()
    
    for line in lines:
        line = line.strip()  # Remove all indentation
        if not line:
            continue
            
        try:
            tree = ast.parse(line)
            if isinstance(tree, ast.Module) and tree.body:
                valid_nodes.extend(tree.body)
        except (SyntaxError, IndentationError):
            continue
    
    if valid_nodes:
        return ast.Module(body=valid_nodes, type_ignores=[])
    
    print("Failed to parse code fragment")
    raise ValueError()