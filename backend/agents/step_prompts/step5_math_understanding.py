"""Step 5: Mathematical Understanding - Deep dive into equations and derivations."""

STEP_5_PROMPT = """## Step 5: Mathematical Understanding (Optional)

### Goal
Provide deep understanding of the mathematical foundations. This step is for users who want to understand the formal details.

### NO IMAGES for this step - focus on pure mathematical derivation.

### Key Aspects to Cover
For each key equation:

1. **Intuition First**
   - Plain English explanation
   - Analogy to familiar concepts
   - Why this formulation makes sense

2. **Step-by-Step Derivation**
   - Show each step clearly
   - Explain what happens at each step
   - Highlight key transformations

3. **Variable Breakdown**
   - What each symbol represents
   - Dimensions/shapes of tensors
   - Typical value ranges

4. **Numerical Example**
   - Concrete numbers to verify understanding
   - Walk through a simple case

### LaTeX Formatting
Use LaTeX syntax for all equations:
- Inline: `\\[equation\\]`
- Block equations:
```
\\[
\\text{Attention}(Q, K, V) = \\text{softmax}\\left(\\frac{QK^T}{\\sqrt{d_k}}\\right)V
\\]
```
- Number derivation steps clearly

### Self-Check Exercises
Offer exercises for the user:
- "Can you derive equation X starting from Y?"
- "What happens to this equation when parameter Z approaches 0?"
- "Try computing this for a 2x2 example"

### Ending
Ask: "Would you like to try deriving any equation yourself? I can check your work or provide hints."

Offer to move to code analysis if available.
"""
