# swe-bench-zeno

Scripts for analyzing the SWE-bench dataset with [Zeno](https://zenoml.com).

Included scripts:

- `acquire_data.py`: Downloads data from both swe-bench official and OpenHands repositories.
- `download_issues.py`: A function to download all the github issues from a repository.
- `visualize_results.py`: Visualization code with Zeno

## Usage
1. Clone the repo with `acquire_data.py`
2. Add your evaluation results (must include `output.jsonl` and `report.json` files for swe-bench or `output.jsonl` for aider bench) to the `od_eval` folder
3. Add your Zeno API Key
4. Run `visualize_results.py` to generate visualizations
