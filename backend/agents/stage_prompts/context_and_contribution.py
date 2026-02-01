"""Context & Contribution Stage - Understanding why the paper exists and what it achieved."""

CONTEXT_AND_CONTRIBUTION_PROMPT = """## Stage: Context & Contribution

### Goal
Help the user understand:
1. WHY this paper exists (the problem and motivation)
2. WHAT they achieved (the contributions and results from the conclusion)

This stage covers both the BEGINNING (Introduction) and END (Conclusion) of the paper to give users the full picture of purpose and achievement.

### Focus Areas
- Introduction section: what motivated this work
- Conclusion section: what they achieved, key results
- Related Work section (skim): how this fits in the broader landscape

### Key Narrative Structure
Explain in this order:
1. **Background**: What is the broader research area?
2. **Gap/Problem**: What specific problem or limitation did the authors identify?
3. **Their Solution** (high-level): How do they propose to address this gap?
4. **What They Achieved**: Key results and contributions from the conclusion
5. **Impact**: Why does this matter? What are the implications?

### What NOT to Do
- Do NOT repeat the overview from Quick Scan
- Do NOT dive into technical methodology details yet
- Do NOT explain HOW the method works in detail
- Keep the solution explanation at a high level

### Image Handling
- Use `extract_images` for figures illustrating: the problem, comparisons, results
- Use `display_images` for already-extracted figures
- **ALWAYS display images inline with your explanation** - when you mention a figure, show it immediately and explain it together
- Never list figures separately from their explanations

### Ending
After explaining the context and contribution, ask the user:
- Do they have questions about the motivation or results?
- Are they ready to dive deeper into the methodology/sections?
"""
