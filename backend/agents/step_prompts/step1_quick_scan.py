"""Step 1: Quick Scan - Initial paper overview."""

STEP_1_PROMPT = """## Step 1: Quick Scan

### Goal
Define WHAT the paper is and its primary high-level objective. Help the user get a first impression of the paper without diving into technical details.

### Focus Areas
- Paper title and what it tells us about the topic
- Abstract: main claims and contributions
- Key figures that illustrate the high-level idea

### What NOT to Do
- Do NOT explain the specific "Gap" the authors found yet
- Do NOT explain the specific technical mechanism (HOW) yet
- Do NOT dive into methodology details

### Tool Usage
- Use `extract_images` to extract figures that help explain the high-level idea (e.g., overview diagrams, teaser figures)
- After extracting, include images using markdown: `![Title](path)`

### Output Format
Your response MUST be valid JSON with exactly these fields:
```json
{
  "title": "The exact paper title",
  "summary": "Your summary with markdown images included"
}
```

### Ending
After providing the summary, ask the user if they have any questions about what the paper is about before moving deeper.
"""
