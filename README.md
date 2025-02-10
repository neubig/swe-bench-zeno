# swe-bench-zeno

Scripts for analyzing the SWE-bench dataset with [Zeno](https://zenoml.com) and understanding model performance patterns.

## Core Analysis Scripts

### Visualization
- `acquire_data.py`: Downloads data from both swe-bench official and OpenHands repositories
- `download_issues.py`: Downloads all GitHub issues from a repository
- `visualize_results.py`: Visualization code with Zeno

### Performance Analysis
- `download_data.py`: Downloads and stores SWE-bench data locally
- `feature_engineering.py`: Extracts features including semantic embeddings
- `analyze_performance.py`: Builds and evaluates predictive models

## Usage

### Visualization
1. Clone the repo with `acquire_data.py`
2. Add your evaluation results (must include `output.jsonl` and `report.json` files for swe-bench or `output.jsonl` for aider bench) to the `od_eval` folder
3. Add your Zeno API Key
4. Run `visualize_results.py` to generate visualizations

## Requirements
- Python 3.8+
- pandas
- scikit-learn
- sentence-transformers
- swe-bench (local installation)
- Zeno API key (for visualization)
