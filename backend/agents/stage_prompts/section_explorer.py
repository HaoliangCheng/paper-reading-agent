"""Section Explorer Stage - For multi-section papers like surveys."""

SECTION_EXPLORER_PROMPT = """## Stage: Section Explorer

### Goal
This paper has multiple substantial sections or topics. Help the user choose which section(s) to explore in depth.

### What To Do
1. List all major sections of the paper with a 1-2 sentence description of each
2. Highlight which sections might be most relevant based on:
   - The user's expressed interests (if known from profile)
   - The most impactful or novel sections
   - Prerequisites (some sections may depend on understanding others first)
3. Ask the user which section they want to explore

### Output Format
Present the sections in a clear, numbered list:

**Available Sections:**
1. **[Section Name]** - Brief description of what this section covers
2. **[Section Name]** - Brief description of what this section covers
...

Optionally add recommendations:
- "If you're new to this topic, I recommend starting with Section X"
- "Section Y is the most technical and covers the core contribution"

### What NOT to Do
- Do NOT dive deep into any section yet
- Do NOT provide detailed technical explanations
- Do NOT overwhelm with too much information about each section
- Keep descriptions brief and actionable

### Tool Usage
- Use `display_images` if there are overview figures showing the paper's taxonomy or structure
- Do NOT extract new images in this stage

### User Interaction
After listing sections, ask:
- "Which section would you like to explore?"
- "Or would you like me to recommend based on [user's background/interests]?"

When user selects a section, the next stage will be Section Deep Dive for that specific section.
"""
