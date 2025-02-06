# SWE-bench Performance Analysis

This analysis examines the performance gaps between OpenHands and other top-performing models on the SWE-bench benchmark. The goal is to identify patterns in problems where OpenHands struggles but other models succeed.

## Scripts

1. `download_data.py` - Downloads and stores SWE-bench data locally
2. `feature_engineering.py` - Extracts relevant features from the data
3. `analyze_performance.py` - Builds and evaluates a classifier to identify important features

## Key Findings

### Most Important Features
1. Problem description length (33.5% importance)
2. Patch size (28.0% importance)
3. Number of files modified (17.5% importance)
4. Repository-specific factors (remaining ~21%)

### Performance Gap Characteristics
Problems where OpenHands struggles tend to have:
- Longer problem descriptions (mean: 242 words vs 173 words)
- Larger patches (mean: 136 lines vs 69 lines)
- More files modified (mean: 3.6 files vs 2.8 files)

### Repository Impact
Some repositories appear more challenging for OpenHands:
- sympy
- django
- xarray
- astropy
- scikit-learn

## Recommendations

1. Enhance the model's ability to process and understand longer problem descriptions
2. Improve coordination capabilities for multi-file changes
3. Focus on better handling of larger code changes
4. Consider specialized training or prompting for scientific computing and web framework codebases

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