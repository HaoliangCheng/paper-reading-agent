"""Quick Scan Stage - Split into two parallel prompts for efficiency."""

# Prompt 1: Summary generation (text output) - focuses on title, figures, abstract
QUICK_SCAN_SUMMARY_PROMPT = """## Quick Scan: Paper Overview

### Goal
Provide a clear, accessible summary of what this paper is about. Help the user get a first impression without diving into technical details.

### Focus Areas
- **Paper title**: What does it tell us about the topic?
- **Abstract**: Main claims and contributions (summarize in your own words)
- **Key figures**: Extract and explain any overview diagrams or teaser figures

### What NOT to Do
- Do NOT explain the specific "Gap" the authors found yet (that's for Context & Contribution stage)
- Do NOT explain the technical mechanism (HOW) yet (that's for Methodology stage)
- Do NOT dive into methodology details

### Image Handling - IMPORTANT
- Use `extract_images` to extract key figures (overview diagrams, teaser figures, architecture diagrams)
- **ALWAYS display images inline with your explanation** - never separate them
- When you mention a figure, immediately show it and explain it together
- Format: Explain the concept, show the image, then elaborate on what the image shows

Example of combining image with text:
```
The paper introduces a novel architecture for...

![Figure 1: Architecture Overview](path/to/image.png)

As shown in the figure above, the system consists of three main components...
```

### Output Format
Provide a natural, conversational summary that weaves text and visuals together:
1. Start with the paper title
2. Explain what the paper is about, embedding relevant figures where they help understanding
3. Each time you reference a figure, display it immediately and explain it
4. End by asking if the user has questions or wants to proceed to the next stage

Keep the summary focused and accessible - this is the user's first impression of the paper.
"""

# Prompt 2: Plan generation (JSON output) - detects content and generates reading plan
QUICK_SCAN_PLAN_PROMPT = """## Paper Analysis: Content Detection and Reading Plan Generation

### Your Task
Analyze the paper structure and generate a customized reading plan. Output ONLY valid JSON.

### Content Detection Steps
1. **Section Structure**: List major sections from table of contents or headings
   - Is this a multi-section paper (survey/review with many distinct topics)?
   - Or a single-method paper (focused on one approach)?

2. **Has Math**: Are there significant equations, derivations, or proofs?
   - Look for equation blocks, mathematical notation, theorems

3. **Has Code**: Does the paper reference implementation or code repositories?
   - Look for GitHub links, code snippets, implementation details

### Output Format (STRICT JSON)
```json
{
  "title": "The exact paper title",
  "content_analysis": {
    "sections": ["Section 1 Name", "Section 2 Name", "..."],
    "has_math": true/false,
    "has_code": true/false,
    "is_multi_section": true/false
  },
  "reading_plan": [
    {
      "id": "stage_id",
      "title": "Stage Title",
      "description": "Customized description for this paper",
      "key_topics": ["topic1", "topic2"]
    }
  ]
}
```

### Reading Plan Generation Rules

**Always include these stages:**
1. `quick_scan` - Overview stage (already completed)
2. `context_and_contribution` - Background, motivation, AND conclusion (what they achieved)

**Then add based on content:**

**If is_multi_section is TRUE (survey/review papers):**
- Add `section_explorer` stage with sections list
- Include a `sections` field with the list of explorable sections
- Example: {"id": "section_explorer", "title": "Section Explorer", "sections": ["Attention", "Transformers"]}

**If is_multi_section is FALSE (single-method papers):**
- Add `methodology` stage
- Description should mention the specific method name

**If has_math is TRUE:**
- Add `math_understanding` stage
- Description should mention specific equations or derivations

**If has_code is TRUE:**
- Add `code_analysis` stage
- Description should mention implementation details or repo

### Example for Survey Paper:
```json
{
  "title": "A Survey of Large Language Models",
  "content_analysis": {
    "sections": ["Pre-training", "Fine-tuning", "Prompting", "Applications"],
    "has_math": false,
    "has_code": false,
    "is_multi_section": true
  },
  "reading_plan": [
    {"id": "quick_scan", "title": "Quick Scan", "description": "Overview of the LLM landscape", "key_topics": ["LLMs", "survey scope"]},
    {"id": "context_and_contribution", "title": "Context & Contribution", "description": "Evolution of language models", "key_topics": ["history", "taxonomy"]},
    {"id": "section_explorer", "title": "Section Explorer", "description": "Choose section to explore", "key_topics": ["sections"], "sections": ["Pre-training", "Fine-tuning", "Prompting", "Applications"]}
  ]
}
```

### Example for Technical Paper:
```json
{
  "title": "Attention Is All You Need",
  "content_analysis": {
    "sections": ["Introduction", "Model Architecture", "Training", "Results"],
    "has_math": true,
    "has_code": true,
    "is_multi_section": false
  },
  "reading_plan": [
    {"id": "quick_scan", "title": "Quick Scan", "description": "Overview of Transformer", "key_topics": ["Transformer", "attention"]},
    {"id": "context_and_contribution", "title": "Context & Contribution", "description": "Why attention replaces recurrence", "key_topics": ["RNN limitations"]},
    {"id": "methodology", "title": "Methodology", "description": "Transformer architecture deep dive", "key_topics": ["self-attention", "multi-head"]},
    {"id": "math_understanding", "title": "Math Understanding", "description": "Attention formulas", "key_topics": ["attention formula"]},
    {"id": "code_analysis", "title": "Code Analysis", "description": "Implementation details", "key_topics": ["tensor2tensor"]}
  ]
}
```

IMPORTANT: Output ONLY the JSON object. No markdown code blocks, no explanatory text.
"""

# Legacy alias for backward compatibility
QUICK_SCAN_PROMPT = QUICK_SCAN_SUMMARY_PROMPT
