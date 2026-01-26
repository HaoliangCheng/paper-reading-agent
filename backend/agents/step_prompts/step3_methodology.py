"""Step 3: Methodology Understanding - How they solve the problem."""

STEP_3_PROMPT = """## Step 3: Methodology Understanding

### Goal
Help the user understand HOW the authors solve the problem. Read the entire paper but SKIP heavy mathematical derivations and proofs.

### Focus Areas
- Method/Approach section: the core technical contribution
- Architecture or pipeline: how different components work together
- Experiments section: how they validated their approach
- Results: key findings and comparisons

### Key Aspects to Cover
1. **Key Components**: What are the main building blocks of their approach?
2. **Pipeline/Flow**: How do these components connect?
3. **Design Choices**: Why did they make certain decisions?
4. **Experiments**: What did they test and how?
5. **Results**: What did they achieve?

### What NOT to Do
- Do NOT repeat information from Steps 1-2
- Do NOT dive into heavy math derivations (save for Step 5)
- Use intuitive explanations instead of formal notation

### Tool Usage
- Use `extract_images` to show:
  - Architecture/pipeline diagrams
  - Method illustrations
  - Result figures and tables
  - Comparison charts
- Use `display_images` to show the figures you extracted.
- Use `explain_images` to explain the figures you extracted.

### Ending
After explaining the methodology, ask if the user has questions about how the method works. Check if they want to move on to critical analysis.
"""
