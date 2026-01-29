"""Step 4: Critical Analysis - Evaluating relevance and impact."""

STEP_4_PROMPT = """## Step 4: Critical Analysis

### Goal
Re-read the paper with a critical eye. Help the user understand the paper's current relevance and impact.

### Focus Areas
- Use web search to verify current relevance
- Identify what's still important vs. what's outdated
- Find community reactions and discussions

### For Older Papers (>2 years)
- Which parts are still standard practice today?
- What has been superseded by newer methods?
- What foundational concepts remain important?

### For Newer Papers
- What's the initial community reaction?
- Are there reproducibility concerns?
- What discussions exist about limitations?

### Key Aspects to Cover
1. **Relevance Check**: Is this still state-of-the-art or foundational?
2. **Limitations**: What are the known weaknesses?
3. **Community Response**: What do other researchers think?
4. **Key Takeaways**: What should the user remember?

### Tool Usage
- Use `web_search` to:
  - Check if methods are still relevant
  - Find newer related work
  - Look for community discussions (Twitter/X, Reddit, OpenReview)
  - Find follow-up papers or improvements
- Always cite sources from search results

### Ending
After the critical analysis, ask the user if they have any questions about current content and what do you plan to explain next, check if they want to move on to the next topic or they have interest in other topics.
"""
