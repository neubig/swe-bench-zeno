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

## Performance Analysis Findings

Our analysis of OpenHands' performance on SWE-bench reveals several key patterns:

### Most Important Features
1. Problem description length (20.9%)
2. Patch size (18.4%)
3. Problem-patch semantic similarity (17.9%)
4. Number of files modified (10.7%)
5. Cluster-based features (32.1%)

### Key Insights
1. **Semantic Understanding**:
   - High semantic similarity doesn't guarantee success
   - Some problem clusters have up to 72.7% failure rate
   - Patch clusters show even stronger patterns (up to 85.7% failure)

2. **Technical Challenges**:
   - Struggles with longer problem descriptions (242 vs 173 words)
   - Difficulty with larger patches (136 vs 69 lines)
   - Multi-file changes are problematic (3.6 vs 2.8 files)

3. **Quality Signals**:
   - High variance in semantic similarity for problematic cases
   - Some failed cases show negative problem-patch similarity
   - Clear cluster-based patterns that could predict failures

For detailed analysis and recommendations, see [PERFORMANCE_ANALYSIS.md](PERFORMANCE_ANALYSIS.md).

## Usage

### Visualization
1. Clone the repo with `acquire_data.py`
2. Add your evaluation results (must include `output.jsonl` and `report.json` files for swe-bench or `output.jsonl` for aider bench) to the `od_eval` folder
3. Add your Zeno API Key
4. Run `visualize_results.py` to generate visualizations

### Performance Analysis
1. Install dependencies:
   ```bash
   pip install pandas scikit-learn sentence-transformers
   ```

2. Run the analysis pipeline:
   ```bash
   python download_data.py
   python feature_engineering.py
   python analyze_performance.py
   ```

## Requirements
- Python 3.8+
- pandas
- scikit-learn
- sentence-transformers
- swe-bench (local installation)
- Zeno API key (for visualization)
