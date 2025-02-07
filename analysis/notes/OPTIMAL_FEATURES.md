# Optimal Features for Predicting OpenHands Performance

## Individual Features (Ranked by F1 Score)

1. **Total Imports** (F1: 0.800)
   - Threshold: 0 imports
   - Precision: 0.744
   - Recall: 0.865
   - Rule: Flag any change that adds imports

2. **Total Lines Changed** (F1: 0.800)
   - Threshold: 0 lines
   - Precision: 0.744
   - Recall: 0.865
   - Rule: Flag any non-zero net change

3. **Problem Description Length** (F1: 0.787)
   - Threshold: 26 words
   - Precision: 0.649
   - Recall: 1.000
   - Rule: Flag any description longer than 26 words

4. **Problem-Patch Similarity** (F1: 0.785)
   - Threshold: 0.521
   - Precision: 0.738
   - Recall: 0.838
   - Rule: Flag when similarity exceeds 0.521

5. **Patch Size** (F1: 0.753)
   - Threshold: 0 lines
   - Precision: 0.625
   - Recall: 0.946
   - Rule: Flag any non-empty patch

## Optimal Feature Combinations

1. **Imports + Patch Size** (F1: 0.845 ±0.050)
   - Rule 1: Flag if (imports ≤ 0.5 AND patch_size ≤ 2)
   - Rule 2: Flag if (0.5 < imports ≤ 17.5)

2. **Patch Size + Lines Changed** (F1: 0.835 ±0.057)
   - Rule 1: Flag if (lines_changed ≤ 1 AND patch_size ≤ 2)
   - Rule 2: Flag if (1 < lines_changed ≤ 24.5)
   - Rule 3: Flag if (lines_changed > 24.5)

3. **Imports + Patch + Lines** (F1: 0.813 ±0.088)
   - Rule 1: Flag if (lines_changed ≤ 1 AND patch_size ≤ 2)
   - Rule 2: Flag if (lines_changed > 1 AND imports ≤ 17.5 AND lines_changed ≤ 24.5)
   - Rule 3: Flag if (lines_changed > 1 AND imports ≤ 17.5 AND lines_changed > 24.5)

## Implementation Recommendations

1. **Quick Screening** (Single Feature)
   - Use problem description length > 26 words
   - 100% recall but lower precision
   - Best for initial filtering

2. **Balanced Assessment** (Two Features)
   - Use imports + patch size rules
   - Best overall F1 score (0.845)
   - Good balance of precision and recall

3. **High Confidence** (Three Features)
   - Use imports + patch + lines rules
   - More complex but more interpretable
   - Better for detailed analysis

4. **Threshold Guidelines**
   - Critical thresholds:
     * 0 net line changes
     * 26 words in description
     * 0.521 semantic similarity
   - Warning thresholds:
     * 17.5 imports
     * 24.5 line changes
     * 2 lines patch size

## Usage in Practice

1. **Initial Screening**
   ```python
   def quick_screen(description_length):
       return description_length > 26
   ```

2. **Detailed Assessment**
   ```python
   def detailed_check(imports, patch_size):
       if imports <= 0.5 and patch_size <= 2:
           return "High Risk"
       if 0.5 < imports <= 17.5:
           return "High Risk"
       return "Low Risk"
   ```

3. **Full Analysis**
   ```python
   def full_analysis(imports, patch_size, lines_changed):
       if lines_changed <= 1 and patch_size <= 2:
           return "High Risk"
       if lines_changed > 1 and imports <= 17.5:
           if lines_changed <= 24.5:
               return "Medium Risk"
           return "High Risk"
       return "Low Risk"
   ```