"""
Analyze features that predict OpenHands performance gaps.
"""
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report


def analyze_code_structure_changes(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze how code structure changes correlate with performance gaps."""
    metrics = {
        'Function Length': ('avg_function_length_before', 'avg_function_length_after'),
        'Max Function Length': ('max_function_length_before', 'max_function_length_after'),
        'Number of Functions': ('total_functions_before', 'total_functions_after'),
        'Number of Classes': ('total_classes_before', 'total_classes_after'),
        'Nesting Depth': ('max_nested_depth_before', 'max_nested_depth_after'),
        'Control Statements': ('total_control_statements_before', 'total_control_statements_after'),
        'Variables': ('total_variables_before', 'total_variables_after'),
        'Imports': ('total_imports_before', 'total_imports_after'),
        'Returns': ('total_returns_before', 'total_returns_after'),
        'Decorators': ('total_decorators_before', 'total_decorators_after'),
        'Comments': ('total_comments_before', 'total_comments_after'),
        'Docstrings': ('total_docstrings_before', 'total_docstrings_after'),
        'Function Parameters': ('avg_function_params_before', 'avg_function_params_after')
    }
    
    results = []
    for metric_name, (before_col, after_col) in metrics.items():
        # Calculate change statistics
        df['change'] = df[after_col] - df[before_col]
        
        # Calculate correlations and statistics
        change_corr = df['change'].corr(df['performance_gap'])
        mean_change_success = df[df['performance_gap'] == 0]['change'].mean()
        mean_change_fail = df[df['performance_gap'] == 1]['change'].mean()
        
        results.append({
            'Metric': metric_name,
            'Correlation': change_corr,
            'Mean Change (Success)': mean_change_success,
            'Mean Change (Failure)': mean_change_fail,
            'Difference': mean_change_fail - mean_change_success
        })
    
    return pd.DataFrame(results).sort_values('Correlation', key=abs, ascending=False)

def main():
    # Load features
    df = pd.DataFrame(pd.read_csv("data/features.csv"))
    
    # Create binary target: 1 if top models significantly outperform OpenHands
    df['performance_gap'] = (df['top_model_success_rate'] > 0.6).astype(int)
    
    # Prepare features
    numerical_features = [
        # Basic metrics
        'patch_size', 
        'files_modified', 
        'problem_desc_length',
        'problem_patch_similarity',
        
        # Code structure metrics - before
        'avg_function_length_before',
        'max_function_length_before',
        'total_functions_before',
        'total_classes_before',
        'max_nested_depth_before',
        'total_control_statements_before',
        'total_variables_before',
        'total_imports_before',
        'total_returns_before',
        'total_decorators_before',
        'total_comments_before',
        'total_docstrings_before',
        'avg_function_params_before',
        
        # Code structure metrics - after
        'avg_function_length_after',
        'max_function_length_after',
        'total_functions_after',
        'total_classes_after',
        'max_nested_depth_after',
        'total_control_statements_after',
        'total_variables_after',
        'total_imports_after',
        'total_returns_after',
        'total_decorators_after',
        'total_comments_after',
        'total_docstrings_after',
        'avg_function_params_after',
        
        # Derived metrics
        'total_lines_changed'
    ]
    
    # One-hot encode categorical features
    X = df
    y = df['performance_gap']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Scale numerical features
    scaler = StandardScaler()
    X_train[numerical_features] = scaler.fit_transform(X_train[numerical_features])
    X_test[numerical_features] = scaler.transform(X_test[numerical_features])
    
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
    
    # Analyze basic numerical features
    print("\nBasic Feature Statistics for Cases with Performance Gap:")
    basic_features = ['patch_size', 'files_modified', 'problem_desc_length', 'problem_patch_similarity']
    gap_stats = df[df['performance_gap'] == 1][basic_features].describe()
    print(gap_stats)
    
    print("\nBasic Feature Statistics for Cases without Performance Gap:")
    no_gap_stats = df[df['performance_gap'] == 0][basic_features].describe()
    print(no_gap_stats)
    
    # Analyze code structure changes
    print("\nCode Structure Change Analysis:")
    structure_changes = analyze_code_structure_changes(df)
    print("\nTop 10 Most Predictive Code Changes:")
    print(structure_changes.head(10))

if __name__ == "__main__":
    main()