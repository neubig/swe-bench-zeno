"""Generate visualization for SWE-bench Verified leaderboard."""

import os
import json
import pandas as pd
import zeno_client
from datasets import load_dataset

# Load the SWE-bench Verified dataset
ds = load_dataset('princeton-nlp/SWE-bench_Verified')

# Create a DataFrame with the problem statements
df_data = pd.DataFrame({
    'id': ds['test']['instance_id'],
    'problem_statement': ds['test']['problem_statement'],
    'data': ds['test']['problem_statement'],  # Use problem statement as data
})

# Create the Zeno project
API_KEY = os.environ.get("ZENO_API_KEY")
if not API_KEY:
    raise ValueError("No Zeno API key found in environment variables")

viz_client = zeno_client.ZenoClient(API_KEY)
viz_project = viz_client.create_project(
    name='SWE-bench Verified Leaderboard',
    view={
        'data': {'type': 'markdown'},
        'label': {'type': 'text'},
        'output': {'type': 'code'},
    },
    description='SWE-bench Verified leaderboard performance analysis',
    public=True,
    metrics=[
        zeno_client.ZenoMetric(name="resolved", type="mean", columns=["resolved"])
    ],
)

# Upload the dataset
viz_project.upload_dataset(
    df=df_data,
    id_column='id',
    data_column='data',
)

# Top 4 systems and their directories
systems = [
    ("Amazon Q Developer Agent (v20241202-dev)", "20241202_amazon-q-developer-agent-20241202-dev"),
    ("devlo", "20241108_devlo"),
    ("OpenHands + CodeAct v2.1", "20241029_OpenHands-CodeAct-2.1-sonnet-20241022"),
    ("Engine Labs (2024-11-25)", "20241125_enginelabs"),
]

# Load results for each system
for system_name, system_dir in systems:
    # Load predictions
    preds_file = f"/workspace/experiments/evaluation/verified/{system_dir}/all_preds.jsonl"
    preds = {}
    with open(preds_file, 'r') as f:
        for line in f:
            pred = json.loads(line)
            preds[pred['instance_id']] = pred.get('model_patch', 'No patch generated')
    
    # Load resolved status
    results_file = f"/workspace/experiments/evaluation/verified/{system_dir}/results/results.json"
    with open(results_file, 'r') as f:
        results = json.loads(f)
        resolved_ids = set(results.get('resolved', []))
    
    # Create a DataFrame with results
    df_system = pd.DataFrame({
        'id': df_data['id'],
        'resolved': [1 if id in resolved_ids else 0 for id in df_data['id']],
        'output': [preds.get(id, 'No patch generated') for id in df_data['id']],
    })
    
    # Upload the system results
    viz_project.upload_system(
        df=df_system,
        name=system_name,
        id_column='id',
        output_column='output',
    )

print("Visualization data generated successfully!")
print(f"Access your project at: https://hub.zenoml.com/project/{viz_project.id}/SWE-bench%20Verified%20Leaderboard")