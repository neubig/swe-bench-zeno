"""
Analyze features that predict OpenHands performance gaps.
"""
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import numpy as np

def analyze_clusters(df, cluster_col, gap_col):
    """Analyze the relationship between clusters and performance gaps."""
    cluster_stats = pd.DataFrame()
    
    for cluster in df[cluster_col].unique():
        cluster_data = df[df[cluster_col] == cluster]
        gap_rate = cluster_data[gap_col].mean()
        size = len(cluster_data)
        cluster_stats.loc[cluster, 'size'] = size
        cluster_stats.loc[cluster, 'gap_rate'] = gap_rate
    
    return cluster_stats.sort_values('gap_rate', ascending=False)

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

def analyze_complexity_patterns(df: pd.DataFrame) -> dict:
    """Analyze patterns in code complexity metrics."""
    # Calculate complexity scores
    df['complexity_before'] = (
        df['max_nested_depth_before'] * 
        df['total_control_statements_before'] * 
        df['total_variables_before']
    ) / (df['total_functions_before'] + 1)
    
    df['complexity_after'] = (
        df['max_nested_depth_after'] * 
        df['total_control_statements_after'] * 
        df['total_variables_after']
    ) / (df['total_functions_after'] + 1)
    
    df['complexity_change'] = df['complexity_after'] - df['complexity_before']
    
    return {
        'complexity_correlation': df['complexity_change'].corr(df['performance_gap']),
        'avg_complexity_success': df[df['performance_gap'] == 0]['complexity_change'].mean(),
        'avg_complexity_fail': df[df['performance_gap'] == 1]['complexity_change'].mean(),
        'max_complexity_success': df[df['performance_gap'] == 0]['complexity_after'].max(),
        'max_complexity_fail': df[df['performance_gap'] == 1]['complexity_after'].max()
    }

def main():
    # Load features
    df = pd.DataFrame(pd.read_csv("data/features.csv"))
    
    # Create binary target: 1 if top models significantly outperform OpenHands
    df['performance_gap'] = (df['top_model_success_rate'] > 0.6).astype(int)
    
    # Prepare features
    categorical_features = ['repo_name', 'org_name', 'problem_cluster', 'patch_cluster']
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
    X = pd.get_dummies(df[categorical_features + numerical_features], 
                      columns=categorical_features)
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
    
    # Analyze complexity patterns
    print("\nCode Complexity Analysis:")
    complexity_stats = analyze_complexity_patterns(df)
    print(f"Complexity change correlation with failures: {complexity_stats['complexity_correlation']:.3f}")
    print(f"Average complexity change (success): {complexity_stats['avg_complexity_success']:.2f}")
    print(f"Average complexity change (failure): {complexity_stats['avg_complexity_fail']:.2f}")
    print(f"Maximum complexity (success): {complexity_stats['max_complexity_success']:.2f}")
    print(f"Maximum complexity (failure): {complexity_stats['max_complexity_fail']:.2f}")
    
    # Analyze clusters
    print("\nProblem Statement Cluster Analysis:")
    problem_cluster_stats = analyze_clusters(df, 'problem_cluster', 'performance_gap')
    print(problem_cluster_stats)
    
    print("\nPatch Cluster Analysis:")
    patch_cluster_stats = analyze_clusters(df, 'patch_cluster', 'performance_gap')
    print(patch_cluster_stats)
    
    # Analyze problem-patch similarity
    print("\nProblem-Patch Similarity Analysis:")
    similarity_corr = df['problem_patch_similarity'].corr(df['performance_gap'])
    print(f"Correlation with performance gap: {similarity_corr:.3f}")
    
    print("\nSimilarity Statistics for Cases with Performance Gap:")
    print(df[df['performance_gap'] == 1]['problem_patch_similarity'].describe())
    
    print("\nSimilarity Statistics for Cases without Performance Gap:")
    print(df[df['performance_gap'] == 0]['problem_patch_similarity'].describe())

if __name__ == "__main__":
    main()