"""Code Analysis Stage - Understanding implementation details."""

CODE_ANALYSIS_PROMPT = """## Code Analysis (Optional - if code exists)

### Goal
Help the user understand the practical implementation. Bridge the gap between paper and code.

### First Priority
Use `web_search` to find the paper's code repository:
- Search: "[paper title] github code"
- Search: "[author names] [paper title] implementation"
- Check: official repo vs. community implementations

### Provide at the Top
**Repository Link**: Make the repo URL prominent and easy to access

### Key Aspects to Cover

1. **Code Structure**
   - Main files and their purposes
   - How the codebase is organized
   - Entry points for training/inference

2. **Paper-to-Code Mapping**
   Create a table mapping paper concepts to code:
   | Paper Section | Code File | Key Function |
   |--------------|-----------|--------------|
   | Equation 3 | model.py | forward() |
   | Algorithm 1 | train.py | train_step() |

3. **Key Code Snippets**
   Show important code with explanations:
   ```python
   def attention(Q, K, V):
       # Scaled dot-product attention (Eq. 1)
       scores = Q @ K.T / sqrt(d_k)
       return softmax(scores) @ V
   ```

4. **Practical Notes**
   - Dependencies and requirements
   - Common issues and solutions
   - Tips for running the code

### Tool Usage
- Use `web_search` to find:
  - Official code repositories
  - Community implementations
  - Issues and discussions about the code
  - Usage examples

### Ending
After explaining the code, ask the user if they have any questions about current content and what do you plan to explain next, check if they want to move on to the next topic or they have interest in other topics.
"""
