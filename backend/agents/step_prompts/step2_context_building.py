"""Step 2: Context Building - Understanding why the paper exists."""

STEP_2_PROMPT = """## Step 2: Context Building

### Goal
Contextualize the paper. Help the user understand WHY this paper exists and what problem it addresses.

### Focus Areas
- Introduction section: what motivated this work
- Conclusion section: what they achieved
- Related Work section (skim): how this fits in the broader landscape

### Key Narrative Structure
Explain in this order:
1. **Background**: What is the broader research area?
2. **Gap**: What specific problem or limitation did the authors identify?
3. **Their Solution**: How do they propose to address this gap? (high-level only)
4. **Impact**: What are the claimed benefits or contributions?

### What NOT to Do
- Do NOT repeat information from Step 1
- Do NOT dive into technical methodology yet
- Keep the solution explanation at a high level

### Tool Usage
- Use `extract_images` to show figures that illustrate:
  - The problem being solved
  - Comparison with prior work
  - High-level results or impact
- Use `display_images` to show the figures you extracted.
- Use `explain_images` to explain the figures you extracted.

### Ending
After explaining the context, ask the user if they have questions about the motivation and background. Check if they want to move on to understanding the methodology.
"""
