import argparse
import os
import re
import pandas as pd
import zeno_client
from data_utils import load_data
import sys

def ensure_conversation_format(conversation):
    if isinstance(conversation, str):
        return [{'role': 'assistant', 'content': conversation}]
    elif isinstance(conversation, list):
        return [
            msg if isinstance(msg, dict) else {'role': 'unknown', 'content': str(msg)}
            for msg in conversation
        ]
    else:
        return []
def visualise_swe_bench(input_files: list[str]):
    """Visualize data from multiple input files."""
    data = [load_data(input_file) for input_file in input_files]
    ids = [x[0] for x in data[0]]
    id_map = {x: i for (i, x) in enumerate(ids)}

    seen = set()
    duplicates = set()
    for x in ids:
        if x in seen:
            duplicates.add(x)
        seen.add(x)

    API_KEY = os.environ["Zeno_Key"]
    vis_client = zeno_client.ZenoClient(API_KEY)

    # Create DataFrame with properly formatted conversations
    df_data = pd.DataFrame(
        {
            'id': ids,
            'problem_statement': [x[1] for x in data[0]],
            # 'resolved': [x[2] for x in data[0]],  # Add resolved status here
            'data': [x[1] for x in data[0]],  # Use problem statement as data
        },
        index=ids,
    )
    df_data['statement_length'] = df_data['problem_statement'].apply(len)
    df_data['repo'] = df_data['id'].str.rsplit('-', n=1).str[0]

    # Create project with proper view specification
    vis_project = vis_client.create_project(
        name='SWE-bench Conversation Analysis',
        view={
            'data': {'type': 'markdown'},
            'label': {'type': 'text'},
            'output': {
                'type': 'list',
                'elements': {
                    'type': 'message',
                    'content': {'type': 'markdown'}
                }
            }
        },
        description='Analysis of SWE-bench conversations with enhanced visualization',
        public=False,
        metrics=[
            zeno_client.ZenoMetric(name='resolved', type='mean', columns=['resolved']),
        ],
    )

    # Upload dataset
    vis_project.upload_dataset(
        df_data,
        id_column='id',
        data_column='data',
    )

    # Process each system
    for input_file, data_entry in zip(input_files, data):
        try:
            conversations = [''] * len(data[0])
            resolved = [0] * len(data[0])
            
            for entry in data_entry:
                idx = id_map[entry[0]]
                resolved[idx] = entry[2]
                messages = entry[3]  # Assuming entry[3] contains the conversation
                
                # Convert any non-list messages to a list format
                if not isinstance(messages, list):
                    if isinstance(messages, str):
                        messages = [{'role': 'assistant', 'content': messages}]
                    else:
                        messages = []
                
                # Ensure each message in the list is a dictionary
                if isinstance(messages, list):
                    messages = [
                        msg if isinstance(msg, dict) else {'role': 'assistant', 'content': str(msg)}
                        for msg in messages
                    ]
                
                conversations[idx] = messages
            
            df_system = pd.DataFrame(
                {
                    'id': ids,
                    'resolved': resolved,
                    'output': conversations,
                },
                index=ids,
            )
            
            model_name = re.sub(r'data/.*lite/', '', input_file)
            model_name = re.sub(r'(od_output|output).jsonl', '', model_name)
            model_name = model_name.replace('/', '_')
            
            if not model_name:
                print(f"Warning: Empty model name for file {input_file}. Using default name.")
                model_name = f"System_{input_files.index(input_file)}"
            
            vis_project.upload_system(
                df_system, 
                name=model_name, 
                id_column='id', 
                output_column='output',
            )
            
            print(f"Successfully processed file: {input_file}")
            
        except Exception as e:
            print(f"Error processing file: {input_file}", file=sys.stderr)
            print(f"Error message: {str(e)}", file=sys.stderr)
            
      

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Visualize results from SWE-bench experiments.'
    )
    parser.add_argument('input_files', help='Path to multiple input files', nargs='+')
    parser.add_argument(
        'benchmark',
        help='Benchmark to visualize',
        type=str,
        choices=['swe-bench', 'aider-bench'],
        default='swe-bench',
    )
    args = parser.parse_args()
    if args.benchmark == 'swe-bench':
        visualise_swe_bench(args.input_files)
    else:
        visualize_aider_bench(args.input_files)