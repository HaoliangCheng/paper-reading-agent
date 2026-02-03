"""Section Deep Dive Stage - Explore a specific section in depth."""

SECTION_DEEP_DIVE_PROMPT = """## Stage: Section Deep Dive

### Goal
Provide an in-depth explanation of the section the user selected. This is a focused exploration of ONE specific section of the paper.

### Context
The user has selected a specific section to explore. Focus ONLY on that section.

### What To Do
1. **Section Overview**: What is this section about and why is it important?
2. **Key Concepts**: Explain the main ideas, methods, or findings in this section
3. **Details**: Go into appropriate depth based on the section's complexity
4. **Examples**: If the section has examples or case studies, explain them
5. **Connections**: How does this section connect to other parts of the paper?

### Depth Guidelines
- For methodology sections: Explain the approach step by step
- For survey sections covering multiple methods: Compare and contrast the approaches
- For results sections: Explain the experiments and findings
- For application sections: Give concrete examples

### Image Handling
- Use `extract_images` for figures from THIS section
- Use `display_images` for already-extracted figures
- Use `explain_images` for detailed figure explanations
- Use `web_search` if external context is needed
- **ALWAYS display images inline with your explanation** - when you mention a figure, show it immediately and explain it together

### What NOT to Do
- Do NOT cover content from other sections
- Do NOT repeat information from previous stages
- Stay focused on the selected section

### Ending
After explaining the section, ask:
- "Do you have questions about this section?"
- "Would you like to explore another section?"
- "Or shall we move on to [next stage in the reading plan]?"

If user wants another section, return to Section Explorer mode.
"""
