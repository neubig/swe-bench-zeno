"""
Extract features from SWE-bench data.
"""
import json
from pathlib import Path
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans

def extract_patch_features(patch):
    if not patch:
        return {
            'patch_size': 0,
            'files_modified': 0,
            'has_patch': False
        }
    
    # Count lines changed
    lines = patch.split('\n')
    patch_size = sum(1 for line in lines if line.startswith('+') or line.startswith('-'))
    
    # Count files modified (look for diff headers)
    files_modified = sum(1 for line in lines if line.startswith('diff --git'))
    
    return {
        'patch_size': patch_size,
        'files_modified': files_modified,
        'has_patch': True
    }

def extract_problem_features(problem_statement, repo):
    return {
        'problem_desc_length': len(problem_statement.split()),
        'repo_name': repo.split('/')[-1],
        'org_name': repo.split('/')[-2]
    }

def get_embeddings(texts, model):
    """Get embeddings for a list of texts."""
    return model.encode(texts, show_progress_bar=True)

def cluster_embeddings(embeddings, n_clusters=5):
    """Cluster embeddings using K-means."""
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    return kmeans.fit_predict(embeddings)

def main():
    data_dir = Path("data")
    
    # Load data
    with open(data_dir / "instances.json") as f:
        instances = json.load(f)
    
    with open(data_dir / "systems.json") as f:
        systems = json.load(f)
    
    # Create instance lookup
    instance_lookup = {i['instance_id']: i for i in instances}
    
    # Find top models by resolve rate
    model_scores = {}
    for model, data in systems.items():
        predictions = data['predictions']
        if predictions:
            resolve_rate = sum(p['resolved'] for p in predictions) / len(predictions)
            model_scores[model] = resolve_rate
    
    # Get top 5 models and OpenHands
    top_models = sorted(model_scores.items(), key=lambda x: x[1], reverse=True)[:5]
    top_model_names = [m[0] for m in top_models]
    
    # Create feature dataset focusing on OpenHands vs top models
    rows = []
    openhands_data = systems.get('20241029_OpenHands-CodeAct-2.1-sonnet-20241022')
    
    if not openhands_data:
        print("OpenHands data not found!")
        return
    
    # Create mapping of instance_id to OpenHands performance
    openhands_results = {p['instance_id']: p['resolved'] 
                        for p in openhands_data['predictions']}
    
    # Load sentence transformer model
    print("Loading sentence transformer model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Collect all problem statements and patches for embedding
    problem_statements = []
    patches = []
    instance_ids = []
    
    for pred in openhands_data['predictions']:
        instance_id = pred['instance_id']
        instance = instance_lookup[instance_id]
        
        # Check how top models did on this instance
        top_model_success = 0
        for model_name in top_model_names:
            if model_name == 'openhands/openhands-agent':
                continue
            model_data = systems[model_name]
            instance_results = [p for p in model_data['predictions'] 
                              if p['instance_id'] == instance_id]
            if instance_results and instance_results[0]['resolved']:
                top_model_success += 1
        
        # Only include instances where there's a performance gap
        if not pred['resolved'] and top_model_success >= 3:  # At least 3 top models succeeded
            # Extract features
            patch_features = extract_patch_features(pred['patch'])
            problem_features = extract_problem_features(
                instance['problem_statement'], 
                instance['repo']
            )
            
            # Add to lists for embedding
            problem_statements.append(instance['problem_statement'])
            patches.append(pred['patch'] if pred['patch'] else "")
            instance_ids.append(instance_id)
            
            rows.append({
                'instance_id': instance_id,
                **patch_features,
                **problem_features,
                'top_model_success_rate': top_model_success / len(top_model_names)
            })
    
    # Create embeddings and clusters
    print("Creating embeddings for problem statements...")
    problem_embeddings = get_embeddings(problem_statements, model)
    print("Creating embeddings for patches...")
    patch_embeddings = get_embeddings(patches, model)
    
    # Cluster embeddings
    print("Clustering embeddings...")
    problem_clusters = cluster_embeddings(problem_embeddings)
    patch_clusters = cluster_embeddings(patch_embeddings)
    
    # Add cluster information to features
    features_df = pd.DataFrame(rows)
    features_df['problem_cluster'] = problem_clusters
    features_df['patch_cluster'] = patch_clusters
    
    # Add embedding similarity between problem and patch
    similarities = np.array([
        np.dot(p, q) / (np.linalg.norm(p) * np.linalg.norm(q))
        for p, q in zip(problem_embeddings, patch_embeddings)
    ])
    features_df['problem_patch_similarity'] = similarities
    
    # Save features DataFrame
    features_df.to_csv(data_dir / "features.csv", index=False)

if __name__ == "__main__":
    main()