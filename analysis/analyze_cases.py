"""
Analyze specific cases to understand true/false positives/negatives.
"""
import json
from pathlib import Path
import pandas as pd
import numpy as np

def load_data():
    """Load the dataset and features."""
    data_dir = Path("data")
    
    with open(data_dir / "instances.json") as f:
        instances = json.load(f)
    
    with open(data_dir / "systems.json") as f:
        systems = json.load(f)
        
    # Create instance lookup
    instance_lookup = {i['instance_id']: i for i in instances}
    
    return instances, systems, instance_lookup

def analyze_case(instance_id, instance, systems, feature_values):
    """Analyze a specific case."""
    # Get OpenHands performance
    openhands_data = systems.get('20241029_OpenHands-CodeAct-2.1-sonnet-20241022')
    if not openhands_data:
        return None
        
    openhands_pred = next(
        (p for p in openhands_data['predictions'] if p['instance_id'] == instance_id),
        None
    )
    if not openhands_pred:
        return None
    
    # Get top model performance
    top_success = 0
    for model, data in systems.items():
        if model == '20241029_OpenHands-CodeAct-2.1-sonnet-20241022':
            continue
        pred = next(
            (p for p in data['predictions'] if p['instance_id'] == instance_id),
            None
        )
        if pred and pred.get('resolved', False):
            top_success += 1
    
    # Determine if this is a performance gap case
    has_gap = not openhands_pred.get('resolved', False) and top_success >= 3
    
    return {
        'instance_id': instance_id,
        'problem': instance['problem_statement'],
        'repo': instance['repo'],
        'openhands_success': openhands_pred.get('resolved', False),
        'top_model_successes': top_success,
        'has_performance_gap': has_gap,
        'features': feature_values
    }

def find_examples(threshold_func, feature_name):
    """Find examples of true/false positives/negatives for a threshold."""
    instances, systems, instance_lookup = load_data()
    
    # Load features
    df = pd.read_csv("data/features.csv")
    
    results = {
        'true_positives': [],
        'true_negatives': [],
        'false_positives': [],
        'false_negatives': []
    }
    
    for idx, row in df.iterrows():
        instance_id = row['instance_id']
        instance = instance_lookup.get(instance_id)
        if not instance:
            continue
            
        # Get feature value and prediction
        feature_value = row[feature_name]
        predicted_positive = threshold_func(feature_value)
        
        # Analyze actual performance
        case = analyze_case(instance_id, instance, systems, {
            feature_name: feature_value
        })
        if not case:
            continue
        
        # Categorize case
        if predicted_positive and case['has_performance_gap']:
            results['true_positives'].append(case)
        elif not predicted_positive and not case['has_performance_gap']:
            results['true_negatives'].append(case)
        elif predicted_positive and not case['has_performance_gap']:
            results['false_positives'].append(case)
        else:  # not predicted_positive and case['has_performance_gap']
            results['false_negatives'].append(case)
    
    return results

def main():
    # Analyze problem description length threshold
    def desc_length_threshold(value):
        return value > 26
    
    results = find_examples(desc_length_threshold, 'problem_desc_length')
    
    print("Analysis of Problem Description Length > 26 words")
    print("=" * 80)
    
    for category in ['true_positives', 'true_negatives', 'false_positives', 'false_negatives']:
        print(f"\n{category.upper()}")
        print("-" * 40)
        
        # Print 2 examples from each category
        for case in results[category][:2]:
            print(f"\nRepository: {case['repo']}")
            print(f"Description Length: {case['features']['problem_desc_length']}")
            print(f"OpenHands Success: {case['openhands_success']}")
            print(f"Top Model Successes: {case['top_model_successes']}")
            print("\nProblem:")
            print(case['problem'][:200] + "..." if len(case['problem']) > 200 else case['problem'])
            print("\n" + "-" * 40)

if __name__ == "__main__":
    main()