# Bias Framework for LLM Prompt Analysis

This document outlines the comprehensive bias framework used in this project, based on established research and recent academic work.

## 1. Representational vs. Allocative Bias (Neumann et al., FAccT 2025)

### Representational Bias
- **Definition**: How groups are portrayed or represented in model outputs
- **Examples**: 
  - Stereotypical associations (e.g., associating certain groups with specific traits)
  - Underrepresentation or misrepresentation of groups
  - Harmful or negative portrayals
- **Impact**: Affects how groups are perceived and understood

### Allocative Bias
- **Definition**: How resources, opportunities, or outcomes are distributed across groups
- **Examples**:
  - Unequal recommendations for jobs, loans, or opportunities
  - Disparate treatment in decision-making
  - Systematic disadvantage in resource allocation
- **Impact**: Affects real-world outcomes and opportunities

**Key Finding**: The placement of demographic information (system prompt vs. user prompt) significantly affects both representational and allocative biases.

## 2. SAGED Framework

A five-stage bias benchmarking pipeline:

1. **Scraping Materials**: Collecting diverse datasets
2. **Assembling Benchmarks**: Creating standardized assessments
3. **Generating Responses**: Producing model outputs
4. **Extracting Numeric Features**: Quantifying response aspects
5. **Diagnosing with Disparity Metrics**: Using metrics like impact ratio and bias concentration

This framework addresses metric tool bias and contextual bias in prompts through counterfactual branching and baseline calibration.

## 3. BEATS Framework (29 Metrics)

Comprehensive evaluation across multiple dimensions:

### Demographic Biases
- Gender bias
- Race/ethnicity bias
- Age bias
- Religion bias
- Nationality bias
- Socioeconomic status bias
- Sexual orientation bias
- Disability bias

### Cognitive Biases
- **Confirmation Bias**: Seeking information that confirms pre-existing beliefs
- **Availability Bias**: Over-relying on easily recalled information
- **Anchoring Bias**: Over-relying on initial information
- **Framing Bias**: Being influenced by how information is presented
- **Halo Effect**: Generalizing from one trait to overall impression
- **Negativity Bias**: Giving more weight to negative information

### Social Biases
- Stereotyping
- In-group/out-group bias
- Status quo bias
- Authority bias

### Ethical Reasoning
- Fairness considerations
- Justice principles
- Harm assessment

### Factuality
- Accuracy of information
- Hallucination detection

## 4. FairMonitor Framework

Four-stage detection approach:

1. **Direct Inquiry Testing**: Direct questions about sensitive topics
2. **Serial/Adapted Story Testing**: Biases in narrative contexts
3. **Implicit Association Testing**: Measuring implicit biases
4. **Unknown Situation Testing**: Novel scenarios to uncover hidden biases

## 5. BiasBuster Framework (Echterhoff et al., 2024)

**BiasBuster** is a systematic framework for uncovering, evaluating, and mitigating cognitive bias in LLMs, particularly in high-stakes decision-making tasks ([Echterhoff et al., 2024](https://arxiv.org/pdf/2403.00811)).

### Key Contributions

1. **Comprehensive Evaluation Dataset**: 13,465 prompts to evaluate LLM decisions on different cognitive biases
2. **High-Stakes Decision-Making Focus**: Student admissions scenario to avoid cross-contamination with training data
3. **Multiple Bias Types**: Evaluates prompt-induced, sequential, and inherent cognitive biases
4. **Novel Self-Help Debiasing**: LLMs debias their own prompts automatically

### Cognitive Bias Categories in BiasBuster

1. **Prompt-Induced Bias**: Biases introduced through the wording of the prompt itself
2. **Sequential Bias**: Biases that emerge from the order or sequence of information
   - **Anchoring Bias**: Initial information unduly influences subsequent decisions
   - **Status Quo/Primacy Bias**: Tendency to favor first-encountered options
3. **Inherent Bias**: Biases that exist in the model's training or reasoning patterns
4. **Framing Bias**: Decisions influenced by how information is presented (positive vs. negative)
5. **Gender Association (GA) Bias**: Gender-based associations affecting decisions

### Evaluation Metrics

BiasBuster assesses:
- **Self-Consistency**: Whether the model makes consistent decisions across similar scenarios
- **Decision Confidence**: How confident the model is in its decisions
- **Bias Patterns**: Quantitative assessment of how models respond to "biased" vs. "neutral" prompts

### Debiasing Methods

#### 1. Self-Help Debiasing (Novel Method)
- **Approach**: LLM is instructed to paraphrase biased questions neutrally
- **Process**: Model identifies and removes bias-inducing language from its own prompts
- **Advantage**: No manual crafting of examples needed for each bias type
- **Example**: Removes leading phrases, rephrases questions to be neutral

#### 2. Counterfactual Debiasing
- **Approach**: Provides examples of incorrect (biased) behavior and correct (unbiased) behavior
- **Method**: Shows model what NOT to do and what TO do
- **Use Case**: Effective for sequential biases like anchoring and status quo

#### 3. Contrastive Debiasing
- **Approach**: Shows only incorrect (biased) behavior examples
- **Method**: Model learns to avoid specific bias patterns
- **Use Case**: Useful when you want to highlight what to avoid

#### 4. Zero-Shot and Few-Shot Prompting
- Tests various debiasing strategies with and without examples
- Evaluates effectiveness across different prompting paradigms

### Key Findings

- LLMs exhibit patterns functionally resembling human cognitive bias
- Cognitive bias can impede fair and explainable decisions in high-stakes scenarios
- Self-help debiasing effectively mitigates model answers displaying cognitive bias patterns
- Different models show varying susceptibility to different types of cognitive bias
- Sequential biases (anchoring, primacy) are particularly challenging to mitigate

### Relationship to Other Frameworks

- **Connects to Sun & Kok (2025)**: Both address cognitive bias in prompts, but BiasBuster focuses on decision-making tasks
- **Connects to Self-Help Prompting**: BiasBuster introduces and evaluates the self-help method
- **Connects to SACD (Lyu et al., 2025)**: Both use iterative debiasing, but BiasBuster's self-help is single-pass
- **High-Stakes Focus**: Unlike general prompt analysis, BiasBuster specifically targets decision-making scenarios

## 6. Cognitive Bias Taxonomy (Sun & Kok, 2025)

### Prompt-Induced Cognitive Biases

1. **Confirmation Bias**
   - Patterns: "isn't it true that", "clearly shows", "obviously"
   - Effect: LLM seeks confirming evidence rather than evaluating critically

2. **Availability Bias**
   - Patterns: "recent examples", "you've probably heard", "common knowledge"
   - Effect: Over-reliance on easily accessible information

3. **Anchoring Bias**
   - Patterns: "compared to", "relative to", "more than X"
   - Effect: Initial reference point unduly influences judgment

4. **Framing Bias**
   - Patterns: Positive vs. negative framing, loss vs. gain framing
   - Effect: Same information presented differently leads to different conclusions

5. **Leading Question Bias**
   - Patterns: "Why is X so bad?", "Don't you think...", "Wouldn't you agree..."
   - Effect: Suggests a particular answer

6. **Stereotypical Assumption Bias**
   - Patterns: "typically", "usually", "always", "never", "all"
   - Effect: Makes broad generalizations that may not apply to individuals

## 7. Prompt Bias Classification (Xu et al., LREC 2024)

### Types of Prompt Bias

1. **Template Bias**: Systematic skewing toward particular labels due to prompt structure
2. **Learned Prompt Bias**: Overfitting to skewed training data (AutoPrompt/OptiPrompt)
3. **Semantic Bias**: Bias introduced through word choice and phrasing
4. **Positional Bias**: Bias based on where information appears in the prompt

## 8. Implementation Framework

Our tool categorizes biases as:

### Primary Categories

1. **Demographic Biases** (Representational & Allocative)
   - Race/Ethnicity
   - Gender
   - Age
   - Religion
   - Nationality
   - Socioeconomic Status

2. **Cognitive Biases**
   - Confirmation Bias
   - Availability Bias
   - Anchoring Bias
   - Framing Bias
   - Leading Question Bias
   - Stereotypical Assumption Bias

3. **Language-Level Biases**
   - Stereotypical Language
   - Assumption-Laden Phrasing
   - Leading Questions
   - Absolute Statements

4. **Structural Biases**
   - Template Bias
   - Positional Bias
   - Context Bias

## 9. Bias Severity Levels

- **Low (0-30%)**: Minimal bias, mostly neutral language
- **Moderate (31-60%)**: Some biased patterns detected
- **High (61-100%)**: Multiple strong bias indicators present

## 10. Debiasing Methods Alignment

Our debiasing methods align with:

- **BiasBuster Self-Help** (Echterhoff et al., 2024): LLM paraphrases biased questions neutrally, automatically removing bias-inducing language
- **Counterfactual & Contrastive Debiasing** (Echterhoff et al., 2024): Showing examples of biased vs. unbiased behavior
- **SACD** (Lyu et al., 2025): Iterative bias detection and correction
- **Representation-based Debiasing** (Xu et al., LREC 2024): Removing bias vectors from latent states
- **Instruction-based Normalization** (BiasFreeBench, 2024): Adding fairness instructions

## References

- Neumann, M., et al. (FAccT 2025). System vs. user prompt bias
- Echterhoff, J., et al. (2024). Cognitive Bias in Decision-Making with LLMs. [arXiv:2403.00811](https://arxiv.org/pdf/2403.00811) - BiasBuster framework
- Sun, X., & Kok, S. (2025). Cognitive bias injection in prompts
- Xu, H., et al. (LREC 2024). Prompt bias in knowledge retrieval
- Lyu, et al. (2025). Self-Adaptive Cognitive Debiasing (SACD)
- BEATS: Bias Evaluation and Assessment Test Suite
- FairMonitor: Four-stage bias detection framework

