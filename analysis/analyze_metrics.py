"""
Analyze precision/recall metrics for top features.
"""
import json
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.metrics import precision_recall_curve, average_precision_score
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

def load_data():
    """Load the dataset and features."""
    df = pd.read_csv("data/features.csv")
    
    # Create performance gap target
    df['performance_gap'] = (df['top_model_success_rate'] > 0.6).astype(int)
    
    # Fill NaN values with 0
    df = df.fillna(0)
    
    return df

def analyze_feature(df, feature_name, thresholds=None):
    """Analyze precision/recall for a feature."""
    if thresholds is None:
        # Generate thresholds from data
        thresholds = np.percentile(
            df[feature_name], 
            q=[20, 40, 60, 80]
        )
    
    results = []
    for threshold in thresholds:
        # Predict failures based on threshold
        predictions = (df[feature_name] > threshold).astype(int)
        actual = df['performance_gap']
        
        # Calculate metrics
        true_pos = sum((predictions == 1) & (actual == 1))
        false_pos = sum((predictions == 1) & (actual == 0))
        false_neg = sum((predictions == 0) & (actual == 1))
        true_neg = sum((predictions == 0) & (actual == 0))
        
        precision = true_pos / (true_pos + false_pos) if (true_pos + false_pos) > 0 else 0
        recall = true_pos / (true_pos + false_neg) if (true_pos + false_neg) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        results.append({
            'threshold': threshold,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'true_positives': true_pos,
            'false_positives': false_pos,
            'true_negatives': true_neg,
            'false_negatives': false_neg
        })
    
    # Calculate AUC-PR
    precision, recall, _ = precision_recall_curve(
        df['performance_gap'],
        df[feature_name]
    )
    auc_pr = average_precision_score(
        df['performance_gap'],
        df[feature_name]
    )
    
    return pd.DataFrame(results), auc_pr

def analyze_top_features():
    """Analyze the top 5 features."""
    df = load_data()
    
    features = {
        'problem_desc_length': None,  # Use percentile thresholds
        'total_imports_after': [2, 4, 6, 8],  # Common import counts
        'problem_patch_similarity': [0.4, 0.5, 0.6, 0.7],  # Similarity thresholds
        'patch_size': [50, 100, 200, 500],  # Line count thresholds
        'total_lines_changed': [-100, 0, 100, 200]  # Net change thresholds
    }
    
    print("Feature Analysis Results")
    print("=" * 80)
    
    for feature_name, thresholds in features.items():
        print(f"\n{feature_name}")
        print("-" * 40)
        
        results, auc_pr = analyze_feature(df, feature_name, thresholds)
        
        print(f"AUC-PR Score: {auc_pr:.3f}")
        print("\nThreshold Analysis:")
        print(results.to_string(index=False, float_format=lambda x: '{:.3f}'.format(x)))
        
        # Print best threshold by F1 score
        best_threshold = results.loc[results['f1_score'].idxmax()]
        print(f"\nBest Threshold (by F1 score):")
        print(f"Threshold: {best_threshold['threshold']:.3f}")
        print(f"Precision: {best_threshold['precision']:.3f}")
        print(f"Recall: {best_threshold['recall']:.3f}")
        print(f"F1 Score: {best_threshold['f1_score']:.3f}")

if __name__ == "__main__":
    analyze_top_features()