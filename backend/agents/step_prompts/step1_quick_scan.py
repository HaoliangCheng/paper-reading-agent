"""Step 1: Quick Scan - Initial paper overview."""

STEP_1_PROMPT = """## Step 1: Quick Scan

### Goal
Define WHAT the paper is and its primary high-level objective. Help the user get a first impression of the paper without diving into technical details.

### Focus Areas
- Paper title and what it tells us about the topic
- Abstract: main claims and contributions
- Key figures and charts that illustrate the high-level idea

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
  "summary": "Your summary with markdown images included",
  "reading_plan": [
    {
      "step": 1,
      "title": "Quick Scan",
      "description": "Brief description of what this paper's quick scan covers",
      "key_topics": ["topic1", "topic2"]
    },
    {
      "step": 2,
      "title": "Context Building",
      "description": "Customized description based on paper's background/motivation",
      "key_topics": ["background topic", "related work"]
    },
    {
      "step": 3,
      "title": "Technical Deep Dive",
      "description": "Customized description of key methodology/approach",
      "key_topics": ["method1", "method2"]
    },
    {
      "step": 4,
      "title": "Results Analysis",
      "description": "Description of experiments and findings",
      "key_topics": ["experiment", "results"]
    },
    {
      "step": 5,
      "title": "Math Derivations",
      "description": "Include ONLY if paper has significant mathematical content",
      "key_topics": ["equation1", "proof"]
    },
    {
      "step": 6,
      "title": "Code & Implementation",
      "description": "Include ONLY if paper has code/implementation details",
      "key_topics": ["implementation", "code"]
    }
  ]
}
```

### Reading Plan Guidelines
- Always include steps 1-4 as they apply to all papers
- Only include step 5 (Math Derivations) if the paper has significant mathematical content
- Only include step 6 (Code & Implementation) if the paper discusses implementation or has available code
- Customize the description and key_topics for each step based on the specific paper content
- Keep descriptions concise (1-2 sentences)
- Include 2-4 key_topics per step that are specific to this paper

### Ending
After providing the summary, ask the user if they have any questions about current content and what do you plan to explain next, check if they want to move on to the next topic or they have interest in other topics.
"""
