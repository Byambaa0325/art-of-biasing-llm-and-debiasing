# Comprehensive Benchmark for Cognitive Biases in LLMs

## Overview

This document consolidates the major benchmarks and evaluation frameworks for cognitive biases in Large Language Models (LLMs). It provides a comprehensive overview of existing datasets, methodologies, and findings from key research papers.

## 1. Malberg et al. (2025): Large-Scale Cognitive Bias Evaluation

**Reference**: Malberg, S., Poletukhin, R., Schuster, C. M., & Groh, G. (2025). A Comprehensive Evaluation of Cognitive Biases in LLMs. *NLP4DH 2025*. [https://aclanthology.org/2025.nlp4dh-1.50.pdf](https://aclanthology.org/2025.nlp4dh-1.50.pdf)

### Key Contributions

1. **Novel General-Purpose Test Framework**: Systematic framework for defining, diversifying, and conducting tests for cognitive biases in LLMs
2. **Large-Scale Benchmark Dataset**: **30,000 tests** for detecting cognitive biases in LLMs
3. **Comprehensive Model Evaluation**: Assessment of **30 cognitive biases** in **20 state-of-the-art LLMs**

### Scope and Scale

- **Biases Tested**: 30 cognitive biases (comprehensive coverage)
- **Models Evaluated**: 20 LLMs from 8 developers
  - OpenAI: GPT-4o, GPT-4o mini, GPT-3.5 Turbo
  - Meta: Llama 3.1 (405B, 70B, 8B), Llama 3.2 (3B, 1B)
  - Anthropic: Claude 3 Haiku
  - Google: Gemini 1.5 Pro, Gemini 1.5 Flash, Gemma 2 (27B, 9B)
  - Mistral AI: Mistral Large, Mistral Small
  - Microsoft: WizardLM-2 (8x22B, 7B), Phi-3.5
  - Alibaba Cloud: Qwen2.5 72B
  - 01.AI: Yi-Large
- **Test Scenarios**: 200 different managerial decision-making scenarios
- **Test Generation**: LLM-based generation with verification using IFEVAL (Instruction Following Evaluation)

### Cognitive Biases Evaluated (30 Total)

The study evaluated 30 cognitive biases, ranked by frequency in management literature:

| Rank | Cognitive Bias | Status | Notes |
|------|----------------|--------|-------|
| #2 | Conservatism | Included | |
| #3 | Anchoring | Included | 98.4% verification accuracy |
| #4 | Stereotyping | Included | |
| #5 | Social Desirability Bias | Included | |
| #6 | Loss Aversion | Included | |
| #7 | Halo Effect | Included | |
| #8 | Reactance | Included | |
| #10 | Confirmation Bias | Included | |
| #11 | Not Invented Here | Included | 100% verification accuracy |
| #13 | Illusion of Control | Included | |
| #14 | Survivorship Bias | Included | |
| #15 | Escalation of Commitment | Included | |
| #16 | Information Bias | Included | |
| #17 | Mental Accounting | Included | |
| #18 | Optimism Bias | Included | |
| #20 | Status-Quo Bias | Included | |
| #21 | Hindsight Bias | Included | 100% verification accuracy |
| #22 | Self-Serving Bias | Included | |
| #23 | Availability Heuristic | Included | |
| #24 | Risk Compensation | Included | |
| #25 | Bandwagon Effect | Included | 99.6% verification accuracy |
| #26 | Endowment Effect | Included | |
| #27 | Framing Effect | Included | |
| #28 | Anthropomorphism | Included | 100% verification accuracy |
| #29 | Fundamental Attribution Error | Included | 100% verification accuracy |
| #30 | Planning Fallacy | Included | 96.7% verification accuracy |
| #31 | Hyperbolic Discounting | Included | |
| #32 | Negativity Bias | Included | |
| #34 | In-Group Bias | Included | |
| #35 | Disposition Effect | Included | |

**Excluded Biases**:
- Prejudice (#1): Unclear LLM testing procedure
- Placebo Effect (#9): Unclear LLM testing procedure
- Selective Perception (#12): Too similar to Confirmation Bias
- Essentialism (#19): Unclear LLM testing procedure

### Key Findings

1. **Universal Bias Presence**: Evidence of all 30 tested biases in at least some of the 20 LLMs
2. **Model Susceptibility**: Different models show varying susceptibility to different bias types
3. **Systematic Testing**: Framework allows for reliable, large-scale test generation
4. **Managerial Context**: Tests focus on managerial decision-making scenarios (high-stakes contexts)

### Methodology

#### Test Generation Framework

The framework uses a template-based approach with LLM-generated content:

1. **Template Definition**: Control and treatment templates for each bias
2. **LLM-Based Diversification**: Use LLMs to fill template gaps with diverse content
3. **Verification**: IFEVAL (Instruction Following Evaluation) to verify generated tests
4. **Validation**: High verification accuracy (96.7% - 100% for tested biases)

#### Example Test Structure

```
Control Template: [LLM fills] → Control Test
Treatment Template: [LLM fills] → Treatment Test

Comparison: LLM responses to control vs treatment
Bias Score: Difference in responses indicates bias presence
```

### Verification Accuracy by Bias Type

| Bias Type | Verification Instruction | Accuracy |
|-----------|-------------------------|----------|
| Anchoring | "Do not include any numbers." | 98.4% |
| Hindsight Bias | "Do not include any numbers." | 100% |
| Planning Fallacy | "Explicitly include a given number." | 96.7% |
| Fundamental Attribution Error | "Use second-/third-person pronouns." | 100% |
| Not Invented Here | "Use second-person pronouns." | 100% |
| Bandwagon Effect | "Do not include any notion of order between opinions." | 99.6% |
| Anthropomorphism | "Give a direct quote without quotation marks." | 100% |

### Dataset Characteristics

- **Size**: 30,000 tests total
- **Diversity**: Tests grouped by bias type show clear separation in embedding space (t-SNE visualization)
- **Bias Distribution**: Tests distributed across different bias severity levels
- **Embedding Model**: text-embedding-3-large by OpenAI for test representation

### Comparison with Other Benchmarks

| Aspect | Malberg et al. (2025) | BiasBuster (2024) | Our Tool |
|--------|----------------------|-------------------|----------|
| **Biases Covered** | 30 | 5 | 8+ (expandable) |
| **Test Size** | 30,000 | 13,465 | Dynamic (user-generated) |
| **Scenario Focus** | Managerial decisions | Student admissions | General prompts |
| **Models Evaluated** | 20 LLMs | Not specified | Vertex AI models |
| **Test Generation** | LLM-based with verification | Rule-based + LLM | Instruction-based LLM |
| **Bias Detection** | Control vs treatment comparison | Decision pattern analysis | HEARTS + Gemini + Rule-based |
| **Framework Type** | Benchmark dataset | Evaluation + mitigation | Interactive exploration |

### Relevance to Our Tool

1. **Bias Coverage Expansion**: Can integrate additional biases from the 30-bias taxonomy
2. **Test Methodology**: Can adapt their control/treatment template approach
3. **Verification**: Can implement IFEVAL-style verification for generated tests
4. **Model Comparison**: Can compare bias susceptibility across different models
5. **Scenario Diversity**: Can leverage their 200 managerial scenarios

## 2. BiasBuster Framework (Echterhoff et al., 2024)

**Reference**: Echterhoff, J., et al. (2024). Cognitive Bias in Decision-Making with LLMs. [arXiv:2403.00811](https://arxiv.org/pdf/2403.00811)

### Key Metrics

- **Test Size**: 13,465 prompts
- **Biases Covered**: 5 cognitive biases
- **Focus**: High-stakes decision-making (student admissions)
- **Innovation**: Self-help debiasing method

### Bias Types in BiasBuster

1. Prompt-Induced Bias
2. Sequential Bias (Anchoring, Status Quo/Primacy)
3. Inherent Bias
4. Framing Bias
5. Gender Association (GA) Bias

## 3. BEATS Framework (29 Metrics)

### Coverage

- **Demographic Biases**: 8 categories
- **Cognitive Biases**: 6+ types
- **Social Biases**: Multiple
- **Ethical Reasoning**: Fairness, justice, harm
- **Factuality**: Accuracy, hallucination detection

## 4. Our Tool's Bias Coverage

### Currently Implemented

1. **Demographic Biases** (Representational & Allocative)
   - Race/Ethnicity, Gender, Age, Religion, Nationality, Socioeconomic Status

2. **Cognitive Biases**
   - Confirmation Bias
   - Availability Bias
   - Anchoring Bias
   - Framing Bias
   - Leading Question Bias
   - Stereotypical Assumption Bias
   - Halo Effect
   - Negativity Bias

3. **Structural Biases**
   - Template Bias
   - Positional Bias
   - Context Bias

### Gaps Identified (Can Add from Malberg et al.)

**High Priority** (Well-tested, common):
- Conservatism (#2)
- Social Desirability Bias (#5)
- Loss Aversion (#6)
- Reactance (#8)
- Illusion of Control (#13)
- Survivorship Bias (#14)
- Escalation of Commitment (#15)
- Information Bias (#16)
- Mental Accounting (#17)
- Optimism Bias (#18)
- Status-Quo Bias (#20)
- Hindsight Bias (#21)
- Self-Serving Bias (#22)
- Risk Compensation (#24)
- Bandwagon Effect (#25)
- Endowment Effect (#26)
- Planning Fallacy (#30)
- Hyperbolic Discounting (#31)
- In-Group Bias (#34)
- Disposition Effect (#35)

**Medium Priority** (Complex to implement):
- Not Invented Here (#11)
- Fundamental Attribution Error (#29)
- Anthropomorphism (#28)

## 5. Benchmark Comparison Matrix

| Framework | Scope | Test Size | Biases | Models | Strengths | Weaknesses |
|-----------|-------|-----------|--------|--------|-----------|------------|
| **Malberg et al. (2025)** | Large-scale | 30,000 | 30 | 20 | Most comprehensive, systematic framework, verified tests | Managerial focus only |
| **BiasBuster (2024)** | High-stakes | 13,465 | 5 | Not specified | Mitigation methods, self-help debiasing | Limited bias types |
| **BEATS** | Broad | Not specified | 29 | Not specified | Covers demographics + cognitive | Less systematic |
| **Our Tool** | Interactive | Dynamic | 8+ | Vertex AI | Interactive exploration, multi-layer detection | Smaller bias coverage |

## 6. Integration Opportunities

### How Our Tool Can Leverage Malberg et al. Benchmark

1. **Bias Instruction Expansion**
   - Add instructions for 20+ additional biases from their taxonomy
   - Use their bias definitions and examples

2. **Test Template Adaptation**
   - Implement control/treatment template generation
   - Use their verification methods (IFEVAL)

3. **Scenario Integration**
   - Incorporate their 200 managerial decision-making scenarios
   - Adapt scenarios for interactive graph exploration

4. **Model Comparison**
   - Test same biases across different Vertex AI models
   - Compare with their findings on 20 LLMs

5. **Systematic Evaluation**
   - Generate systematic test sets using their framework
   - Measure bias presence across different model configurations

### Implementation Roadmap

**Phase 1: Expand Bias Instructions**
- Add 10 most common biases from Malberg et al. taxonomy
- Create instruction guides for each (following existing pattern)

**Phase 2: Template-Based Generation**
- Implement control/treatment template system
- Generate test variations using LLM

**Phase 3: Verification System**
- Integrate IFEVAL-style verification
- Validate generated biased prompts

**Phase 4: Scenario Library**
- Add managerial decision-making scenarios
- Create scenario-specific bias tests

## 7. Research Contributions

### What Our Tool Adds to Existing Benchmarks

1. **Interactive Exploration**: Unlike static datasets, users can explore bias dynamically
2. **Multi-Turn Analysis**: Test multi-turn bias priming hypothesis (novel contribution)
3. **Multi-Layer Detection**: HEARTS ML + Gemini + Rule-based ensemble
4. **Explainability**: SHAP token importance shows which words contribute to bias
5. **Graph Visualization**: Visual representation of bias pathways and transformations
6. **Real-Time Evaluation**: Immediate feedback on bias presence and severity

### Novel Research Questions Our Tool Can Answer

1. **Multi-Turn Bias Priming**: Does multi-turn conversation increase bias? (Based on Laban et al., 2025)
2. **Bias Interaction**: How do multiple biases interact when combined?
3. **Transformation Effects**: How do different transformation methods affect bias?
4. **Model Comparison**: Compare bias susceptibility across Vertex AI models
5. **Depth Effects**: Does bias increase/decrease with graph exploration depth?

## 8. Future Directions

### Short-Term Enhancements

1. **Expand Bias Coverage**: Add 10-15 biases from Malberg et al. taxonomy
2. **Template System**: Implement control/treatment template generation
3. **Verification**: Add IFEVAL-style verification for generated tests
4. **Scenario Library**: Create library of decision-making scenarios

### Long-Term Research

1. **Benchmark Contribution**: Generate systematic test set comparable to Malberg et al.
2. **Model Evaluation**: Comprehensive evaluation across multiple Vertex AI models
3. **Bias Taxonomy**: Contribute to unified cognitive bias taxonomy for LLMs
4. **Mitigation Methods**: Test effectiveness of different debiasing methods
5. **Multi-Turn Studies**: Research on multi-turn bias priming and conversation effects

## 9. References

### Primary Benchmarks

1. **Malberg, S., Poletukhin, R., Schuster, C. M., & Groh, G. (2025)**. A Comprehensive Evaluation of Cognitive Biases in LLMs. *NLP4DH 2025*. [https://aclanthology.org/2025.nlp4dh-1.50.pdf](https://aclanthology.org/2025.nlp4dh-1.50.pdf)
   - 30 biases, 20 LLMs, 30,000 tests, systematic framework

2. **Echterhoff, J., et al. (2024)**. Cognitive Bias in Decision-Making with LLMs. [arXiv:2403.00811](https://arxiv.org/pdf/2403.00811)
   - BiasBuster framework, 13,465 prompts, 5 biases, self-help debiasing

3. **Laban, P., Hayashi, H., Zhou, Y., & Neville, J. (2025)**. LLMs Get Lost In Multi-Turn Conversation. arXiv:2505.06120. [https://arxiv.org/pdf/2505.06120](https://arxiv.org/pdf/2505.06120)
   - Multi-turn conversation reliability, 39% performance drop

### Supporting Frameworks

- **BEATS Framework**: 29-metric evaluation
- **FairMonitor**: Four-stage detection
- **SAGED**: Five-stage benchmarking pipeline
- **Neumann et al. (FAccT 2025)**: Representational vs. allocative bias
- **Sun & Kok (2025)**: Cognitive bias taxonomy
- **Xu et al. (LREC 2024)**: Structural/template prompt bias

## 10. Summary

The **Malberg et al. (2025)** benchmark represents the most comprehensive evaluation of cognitive biases in LLMs to date, with:

- ✅ **30 cognitive biases** systematically tested
- ✅ **20 state-of-the-art LLMs** evaluated
- ✅ **30,000 tests** across 200 managerial scenarios
- ✅ **Verified test generation** framework
- ✅ **Systematic methodology** for large-scale evaluation

Our tool complements this benchmark by providing:
- 🔬 **Interactive exploration** of bias pathways
- 🔬 **Multi-turn analysis** for priming effects
- 🔬 **Multi-layer detection** with explainability
- 🔬 **Real-time evaluation** with visual feedback
- 🔬 **Dynamic test generation** based on user prompts

Together, these approaches provide a comprehensive framework for understanding, detecting, and mitigating cognitive biases in LLMs.

