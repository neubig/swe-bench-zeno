"""
Optimize feature thresholds for F1 score.
"""
import json
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.metrics import f1_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import cross_val_score
from itertools import combinations

def load_data():
    """Load the dataset and features."""
    df = pd.read_csv("data/features.csv")
    df['performance_gap'] = (df['top_model_success_rate'] > 0.6).astype(int)
    return df.fillna(0)

def find_optimal_threshold(df, feature, n_thresholds=100):
    """Find the threshold that maximizes F1 score for a single feature."""
    values = df[feature].values
    min_val, max_val = np.min(values), np.max(values)
    thresholds = np.linspace(min_val, max_val, n_thresholds)
    
    best_f1 = 0
    best_threshold = None
    best_precision = None
    best_recall = None
    
    for threshold in thresholds:
        predictions = (values > threshold).astype(int)
        true_pos = sum((predictions == 1) & (df['performance_gap'] == 1))
        false_pos = sum((predictions == 1) & (df['performance_gap'] == 0))
        false_neg = sum((predictions == 0) & (df['performance_gap'] == 1))
        
        precision = true_pos / (true_pos + false_pos) if (true_pos + false_pos) > 0 else 0
        recall = true_pos / (true_pos + false_neg) if (true_pos + false_neg) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        if f1 > best_f1:
            best_f1 = f1
            best_threshold = threshold
            best_precision = precision
            best_recall = recall
    
    return {
        'feature': feature,
        'threshold': best_threshold,
        'f1_score': best_f1,
        'precision': best_precision,
        'recall': best_recall
    }

def find_optimal_feature_combinations(df, features, max_features=3):
    """Find the best combinations of features for predicting performance gaps."""
    results = []
    
    # Try different feature combinations
    for n in range(1, max_features + 1):
        for feature_combo in combinations(features, n):
            # Create decision tree with just these features
            X = df[list(feature_combo)]
            y = df['performance_gap']
            
            # Use cross-validation to evaluate
            clf = DecisionTreeClassifier(max_depth=n)
            scores = cross_val_score(clf, X, y, cv=5, scoring='f1')
            
            results.append({
                'features': feature_combo,
                'f1_score': np.mean(scores),
                'f1_std': np.std(scores)
            })
    
    return sorted(results, key=lambda x: x['f1_score'], reverse=True)

def analyze_decision_boundaries(df, feature_combo):
    """Analyze the decision boundaries for a feature combination."""
    X = df[list(feature_combo)]
    y = df['performance_gap']
    
    clf = DecisionTreeClassifier(max_depth=len(feature_combo))
    clf.fit(X, y)
    
    # Get decision paths
    n_nodes = clf.tree_.node_count
    children_left = clf.tree_.children_left
    children_right = clf.tree_.children_right
    feature = clf.tree_.feature
    threshold = clf.tree_.threshold
    
    # Extract rules
    rules = []
    
    def recurse(node, path):
        if children_left[node] == children_right[node]:  # Leaf
            if clf.tree_.value[node][0][1] > clf.tree_.value[node][0][0]:  # Majority class is 1
                rules.append(path)
        else:
            feature_name = list(feature_combo)[feature[node]]
            threshold_value = threshold[node]
            
            # Left path (<=)
            recurse(children_left[node], 
                   path + [(feature_name, '<=', threshold_value)])
            
            # Right path (>)
            recurse(children_right[node],
                   path + [(feature_name, '>', threshold_value)])
    
    recurse(0, [])
    return rules

def main():
    df = load_data()
    
    # Key features to analyze
    features = [
        'problem_desc_length',
        'total_imports_after',
        'problem_patch_similarity',
        'patch_size',
        'total_lines_changed'
    ]
    
    print("Individual Feature Analysis")
    print("=" * 80)
    
    # Find optimal thresholds for individual features
    individual_results = []
    for feature in features:
        result = find_optimal_threshold(df, feature)
        individual_results.append(result)
    
    # Sort by F1 score
    individual_results.sort(key=lambda x: x['f1_score'], reverse=True)
    
    # Print individual feature results
    for result in individual_results:
        print(f"\nFeature: {result['feature']}")
        print(f"Threshold: {result['threshold']:.3f}")
        print(f"F1 Score: {result['f1_score']:.3f}")
        print(f"Precision: {result['precision']:.3f}")
        print(f"Recall: {result['recall']:.3f}")
    
    print("\nFeature Combination Analysis")
    print("=" * 80)
    
    # Find best feature combinations
    combo_results = find_optimal_feature_combinations(df, features)
    
    # Print top combinations
    for i, result in enumerate(combo_results[:5]):
        print(f"\nTop Combination {i+1}:")
        print(f"Features: {', '.join(result['features'])}")
        print(f"F1 Score: {result['f1_score']:.3f} (±{result['f1_std']:.3f})")
        
        # Analyze decision boundaries for this combination
        rules = analyze_decision_boundaries(df, result['features'])
        print("\nDecision Rules:")
        for j, rule in enumerate(rules):
            print(f"Rule {j+1}:")
            for feature, op, threshold in rule:
                print(f"  {feature} {op} {threshold:.3f}")

if __name__ == "__main__":
    main()