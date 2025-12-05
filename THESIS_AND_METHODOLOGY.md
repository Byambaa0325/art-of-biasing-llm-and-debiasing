# Thesis and Methodology

## Research Thesis

**How do multi-turn cognitive biased conversations affect stereotype biases in Large Language Models (LLMs)?**

This project investigates how subtle cognitive biases introduced through conversational priming can influence LLM responses and amplify stereotypes. Unlike traditional bias studies that examine single-turn prompts, this research extends the HEARTS dataset framework by exploring how fragmented cognitive biased dialogue in multi-turn conversations affects model susceptibility to user cognitive biases.

### Core Research Question

The increasing deployment of LLMs in workplace and consumer products makes the study of implicit biases and stereotypes a critical guardrail. While stereotypes exist in the world, large-scale deployment of unknowingly biased models can amplify a singular set of biases throughout society. Most deployed LLM systems offer conversational interfaces and work in the context of users' subjective prompts within multi-turn conversations. It is widely understood that multi-turn conversations and irrelevant contexts affect the performance and fairness of LLMs.

**Key Hypothesis**: Subtle cognitive biases introduced through conversational "bait" (priming questions) before the main prompt can significantly influence LLM responses, making them more susceptible to stereotype reinforcement.

## Methodology

### 1. Multi-Turn Conversational Bias Injection

**Approach**: Instead of directly modifying prompts, we use a **"Conversational Bait"** methodology:

1. **Turn 1 - Priming Question**: Generate a subtle, contextually relevant question that applies a specific cognitive bias (e.g., Anchoring, Availability, Confirmation Bias) to prime a stereotype
2. **Turn 1 Response**: LLM responds to the priming question
3. **Turn 2 - Original Prompt**: The original user prompt is asked, with the full conversation history preserved
4. **Turn 2 Response**: LLM answers the original prompt, now influenced by the priming context

**Key Innovation**: The priming question is designed to be:
- Contextually relevant to the original prompt
- Subtle enough to avoid triggering AI safety filters
- Psychologically effective in steering thinking toward stereotypes
- Natural-sounding and plausible

### 2. Bias Detection Framework

The system employs multiple research-backed frameworks:

- **HEARTS Dataset** (Theo et al.): Extended with multi-turn conversational bias injection
- **BEATS Framework**: 29 comprehensive bias metrics across demographic, cognitive, and social dimensions
- **BiasBuster** (Echterhoff et al., 2024): Cognitive bias evaluation and self-help debiasing
- **Representational vs. Allocative Bias** (Neumann et al., FAccT 2025): Classification of how groups are portrayed vs. how resources are distributed
- **Cognitive Bias Taxonomy** (Sun & Kok, 2025): Systematic injection and measurement of cognitive biases

### 3. Interactive Graph-Based Analysis

**Visualization Method**: Interactive React Flow graph showing:
- **Root Node**: Original prompt with LLM answer and bias evaluations
- **Bias Pathways**: Red nodes showing biased variations (multi-turn and single-turn)
- **Debias Pathways**: Green nodes showing debiased versions
- **Expansion**: Users can recursively expand any node to further bias or debias

**Purpose**: Enables users to:
- Understand how biases compound through multiple injections
- Visualize the relationship between different bias types
- Compare original, biased, and debiased responses side-by-side
- Explore the full conversation history for multi-turn injections

### 4. Multi-Layer Bias Evaluation

**Evaluation Stack**:

1. **HEARTS ML Model**: Machine learning-based bias detection (when available)
2. **LLM Evaluators**: 
   - **Gemini 2.5 Flash** (Vertex AI): Zero-shot bias evaluation
   - **Claude Models** (Bedrock): Zero-shot bias evaluation with bias type identification
3. **Aggregated Scores**: Multiple evaluators provide comprehensive bias assessment

**Evaluation Metrics**:
- Bias severity scores
- Bias type identification
- Stereotype detection
- Fairness assessment

### 5. LLM-Based Bias Injection and Debiasing

**Bias Injection**:
- Uses LLMs (Claude, Llama, etc.) to generate subtle priming questions
- Applies specific cognitive bias types (Anchoring, Availability, Confirmation, Framing, etc.)
- Ensures contextual relevance to the original prompt

**Debiasing Methods**:
- **Self-Help Debiasing** (BiasBuster): LLM rewrites biased prompts neutrally
- **Self-Adaptive Cognitive Debiasing (SACD)**: Iterative bias detection and correction
- Multiple debiasing techniques available for comparison

### 6. Answer Generation with Constraints

**10-Word Limit**: All LLM answers are constrained to 10 words maximum to:
- Ensure concise, focused responses
- Reduce verbosity that might mask bias effects
- Enable clearer comparison between biased and debiased outputs

## Research Contributions

1. **Novel Methodology**: First systematic study of multi-turn conversational bias injection in LLMs
2. **Extended HEARTS Dataset**: Multi-turn extensions with cognitive bias priming
3. **Interactive Analysis Tool**: Graph-based visualization for understanding bias pathways
4. **Comprehensive Evaluation**: Multi-layer bias detection combining ML and LLM evaluators
5. **Explainability**: Full conversation history tracking to understand how biases compound

## Technical Implementation

- **Backend**: Flask API with LLM service integration (Vertex AI, AWS Bedrock)
- **Frontend**: React with ReactFlow for interactive graph visualization
- **LLM Services**: Support for multiple models (Claude, Llama, Gemini, Nova, Mistral, DeepSeek)
- **Deployment**: Dockerized for Google Cloud Run with optimized build processes

## Expected Outcomes

1. **Quantitative**: Measure LLM susceptibility to multi-turn cognitive bias injection
2. **Qualitative**: Understand how different bias types compound through conversation
3. **Practical**: Provide tools for detecting and mitigating conversational bias in LLM deployments
4. **Theoretical**: Contribute to understanding of prompt-induced bias mechanisms in conversational AI

## References

- HEARTS Dataset: https://arxiv.org/pdf/2409.11579
- BiasBuster Framework: https://arxiv.org/pdf/2403.00811
- Neumann et al. (FAccT 2025): System vs. user prompt bias effects
- Sun & Kok (2025): Cognitive bias taxonomy and injection
- Echterhoff et al. (2024): BiasBuster self-help debiasing
- Lyu et al. (2025): Self-Adaptive Cognitive Debiasing (SACD)

