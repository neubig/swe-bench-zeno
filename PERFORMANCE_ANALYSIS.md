# SWE-bench Performance Analysis

This analysis examines the performance gaps between OpenHands and other top-performing models on the SWE-bench benchmark. The goal is to identify patterns in problems where OpenHands struggles but other models succeed.

## Scripts

1. `download_data.py` - Downloads and stores SWE-bench data locally
2. `feature_engineering.py` - Extracts relevant features from the data
3. `analyze_performance.py` - Builds and evaluates a classifier to identify important features

## Key Findings

### Most Important Features
1. Problem description length (20.9% importance)
2. Patch size (18.4% importance)
3. Problem-patch semantic similarity (17.9% importance)
4. Number of files modified (10.7% importance)
5. Cluster-based features (32.1% combined importance)

### Performance Gap Characteristics
Problems where OpenHands struggles tend to have:
- Longer problem descriptions (mean: 242 words vs 173 words)
- Larger patches (mean: 136 lines vs 69 lines)
- More files modified (mean: 3.6 files vs 2.8 files)

### Semantic Patterns
1. Problem Statement Clusters:
   - Cluster 3 (11 cases): 72.7% performance gap rate
   - Cluster 1 (14 cases): 71.4% performance gap rate
   - Other clusters show lower gap rates (53-62%)

2. Patch Clusters:
   - Cluster 1 (14 cases): 85.7% performance gap rate
   - Cluster 3 (5 cases): 80.0% performance gap rate
   - Other clusters show lower gap rates (50-75%)

3. Problem-Patch Similarity:
   - Cases with performance gaps show slightly higher semantic similarity (mean: 0.590 vs 0.551)
   - Higher variance in similarity for problematic cases (std: 0.181 vs 0.103)
   - Some problematic cases show negative similarity, indicating potential misalignment

### Repository Impact
Some repositories appear more challenging for OpenHands:
- sympy (2.0% importance)
- django
- xarray
- astropy
- scikit-learn

## Recommendations

1. Semantic Understanding:
   - Enhance the model's ability to process and understand longer problem descriptions
   - Focus on cases where problem-patch semantic similarity is high but the solution fails
   - Investigate patterns in problematic clusters to identify common failure modes

2. Technical Capabilities:
   - Improve coordination capabilities for multi-file changes
   - Focus on better handling of larger code changes
   - Consider specialized training or prompting for scientific computing and web framework codebases

3. Quality Assurance:
   - Implement semantic similarity checks between problems and generated patches
   - Use cluster analysis to identify high-risk cases that may need additional verification
   - Consider different prompting strategies for different problem clusters

## Setup

This analysis requires Python with poetry for dependency management. Required packages:
- pandas
- scikit-learn
- swe-bench

To run the analysis:
```bash
poetry install
python download_data.py
python feature_engineering.py
python analyze_performance.py
```