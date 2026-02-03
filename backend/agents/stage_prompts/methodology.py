"""Methodology Stage - How they solve the problem."""

METHODOLOGY_PROMPT = """## Methodology Understanding

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
- Do NOT repeat information from previous stages
- Do NOT dive into heavy math derivations (save for Math Understanding)
- Use intuitive explanations instead of formal notation

### Image Handling
- Use `extract_images` for: architecture diagrams, method illustrations, result figures, comparison charts
- Use `display_images` for already-extracted figures
- **ALWAYS display images inline with your explanation** - when you mention a figure, show it immediately and explain it together
- Never list figures separately from their explanations

### Ending
After explaining the methodology, ask the user if they have any questions about current content and what do you plan to explain next, check if they want to move on to the next topic or they have interest in other topics.
"""
