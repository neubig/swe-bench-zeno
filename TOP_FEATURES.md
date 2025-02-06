# Top 5 Most Predictive Features for OpenHands Performance

## 1. Problem Description Length
- **Importance Score**: 11.7%
- **Correlation**: Strong positive (longer descriptions → more failures)
- **Metrics**:
  - Failed cases avg: 242.14 words
  - Successful cases avg: 173.33 words
  - Difference: +39.7% longer in failures
- **Example Success**: NDDataRef mask propagation
  ```
  Problem: Mask propagation fails when operand lacks mask
  Length: 35 words
  Result: Clean, focused fix
  ```
- **Example Failure**: FITS Card string representation
  ```
  Problem: Complex description of float formatting issues with multiple scenarios
  Length: 183 words
  Result: Overly complex solution
  ```

## 2. Import Dependencies
- **Importance Score**: 9.1%
- **Correlation**: 0.0649 (more imports → slightly more failures)
- **Metrics**:
  - Failed cases avg: 5.03 new imports
  - Successful cases avg: 4.29 new imports
  - Change difference: +0.74 imports in failures
- **Example Success**: Simple numpy import for mask handling
  ```python
  import numpy as np
  # Single, focused import
  ```
- **Example Failure**: Multiple format handling imports
  ```python
  import numpy as np
  import warnings
  from astropy.io.fits import conf
  from astropy.utils.exceptions import AstropyWarning
  ```

## 3. Problem-Patch Semantic Similarity
- **Importance Score**: 8.6%
- **Correlation**: 0.119 (higher similarity → more failures)
- **Metrics**:
  - Failed cases similarity: 0.590
  - Successful cases similarity: 0.551
  - Variance: 0.181 vs 0.103 (higher in failures)
- **Example Success**: Direct problem-solution mapping
  ```
  Problem: "Handle None mask"
  Solution: "if mask is None: return None"
  ```
- **Example Failure**: Over-aligned but incorrect
  ```
  Problem: "Fix float formatting"
  Solution: Complex string formatting that matches keywords but misses core issue
  ```

## 4. Patch Size
- **Importance Score**: 7.1%
- **Correlation**: Strong positive (larger patches → more failures)
- **Metrics**:
  - Failed cases avg: 136.27 lines
  - Successful cases avg: 69.05 lines
  - Difference: +97.3% larger in failures
- **Example Success**: Focused 5-line fix
  ```python
  if mask is None:
      return None
  return deepcopy(mask)
  ```
- **Example Failure**: Large multi-file change
  ```python
  # 50+ lines of changes across multiple files
  # Complex formatting logic
  # Test cases
  # Edge case handling
  ```

## 5. Total Lines Changed
- **Importance Score**: 7.0%
- **Correlation**: -0.102 for control flow changes
- **Metrics**:
  - Failed cases net change: -106.32 lines
  - Successful cases net change: +26.26 lines
  - Key difference: Failures tend to remove code
- **Example Success**: Incremental addition
  ```python
  # Adds 2-3 validation checks
  # Preserves existing logic
  ```
- **Example Failure**: Major restructuring
  ```python
  # Removes multiple functions
  # Replaces with new implementation
  # Changes core logic flow
  ```

## Key Patterns

1. **Complexity Indicators**:
   - Problem length strongly predicts difficulty
   - Import count signals solution complexity
   - Semantic similarity can be misleading

2. **Change Patterns**:
   - Successful changes are smaller
   - Failures often involve removal
   - Focused changes perform better

3. **Success Factors**:
   - Clear, concise problem statements
   - Minimal dependencies
   - Focused, additive changes
   - Preserved existing structure

4. **Risk Factors**:
   - Long, detailed problem descriptions
   - Multiple dependencies
   - Large code removals
   - Complex restructuring