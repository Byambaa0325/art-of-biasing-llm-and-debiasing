"""
Test script for persona-based bias injection

This demonstrates the difference between persona-based and psycholinguistic approaches.
"""

from backend.bias_instructions import get_sentence_generation_guide, get_bias_instruction

def test_persona_templates():
    """Test that persona templates are loaded correctly"""
    print("=" * 80)
    print("TESTING PERSONA-BASED BIAS INJECTION TEMPLATES")
    print("=" * 80)

    bias_types = [
        'confirmation_bias',
        'availability_bias',
        'anchoring_bias',
        'framing_bias',
        'leading_question',
        'demographic_bias',
        'negativity_bias',
        'stereotypical_assumption'
    ]

    test_sentence = "The software developer is ===nerdy==="
    test_trait = "nerdy"

    for bias_type in bias_types:
        print(f"\n{'-' * 80}")
        print(f"Bias Type: {bias_type}")
        print(f"{'-' * 80}")

        # Get persona template
        template = get_sentence_generation_guide(bias_type)

        if template:
            # Format the template
            formatted = template.format(sentence=test_sentence, trait=test_trait)

            # Extract persona name
            import re
            persona_match = re.search(r'USER PERSONA \(([^)]+)\):', template)
            persona_name = persona_match.group(1) if persona_match else "Unknown"

            print(f"[OK] Persona Template Found: {persona_name}")
            print(f"\nTemplate Preview (first 300 chars):")
            print(formatted[:300] + "...")
        else:
            print(f"[X] No persona template found for {bias_type}")

    print("\n" + "=" * 80)
    print("COMPARISON: Persona vs Psycholinguistic Approach")
    print("=" * 80)

    # Show the difference between approaches
    confirmation_bias = get_bias_instruction('confirmation_bias')
    confirmation_persona = get_sentence_generation_guide('confirmation_bias')

    print("\n1. PSYCHOLINGUISTIC APPROACH (Original):")
    print("-" * 80)
    print(f"Bias Name: {confirmation_bias['name']}")
    print(f"Description: {confirmation_bias['description']}")
    print(f"Techniques: {', '.join(confirmation_bias['techniques'][:2])}...")
    print(f"Framework: {confirmation_bias['framework']}")

    print("\n2. PERSONA-BASED APPROACH (New):")
    print("-" * 80)
    persona_match = re.search(r'USER PERSONA \(([^)]+)\):[^\n]*\n\s*(.+?)(?=\n\s*\n|\n\s*INSTRUCTION)', confirmation_persona, re.DOTALL)
    if persona_match:
        persona_name = persona_match.group(1)
        persona_desc = persona_match.group(2).strip()
        print(f"Persona: {persona_name}")
        print(f"Description: {persona_desc}")

    print("\n" + "=" * 80)
    print("KEY DIFFERENCES:")
    print("=" * 80)
    print("- Psycholinguistic: Explicit instructions on plausible deniability, tone guidelines")
    print("- Persona-based: Masked instructions with realistic user personas")
    print("- Psycholinguistic: Focus on 'how to construct' the bias")
    print("- Persona-based: Focus on 'who is asking' the question")
    print("\nBoth approaches aim to generate subtle priming questions that avoid safety filters.")
    print("=" * 80)


if __name__ == "__main__":
    test_persona_templates()
