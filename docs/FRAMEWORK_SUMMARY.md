# Bias Framework Summary

## Quick Reference: Research-Backed Bias Framework

This project implements a comprehensive bias detection and analysis framework based on established research and industry standards.

## Primary Bias Classifications

### 1. Representational vs. Allocative (Neumann et al., FAccT 2025)

**Representational Bias**: How groups are portrayed
- Stereotypical associations
- Underrepresentation
- Negative portrayals

**Allocative Bias**: How resources/outcomes are distributed
- Unequal recommendations
- Disparate treatment
- Systematic disadvantage

### 2. Demographic Biases (BEATS Framework)

- Race/Ethnicity
- Gender
- Age
- Religion
- Nationality
- Socioeconomic Status
- Sexual Orientation
- Disability

### 3. Cognitive Biases (Sun & Kok, 2025; BEATS; BiasBuster)

- Confirmation Bias
- Availability Bias
- Anchoring Bias (BiasBuster: sequential bias)
- Framing Bias
- Leading Question Bias
- Stereotypical Assumption
- Halo Effect
- Negativity Bias
- Status Quo/Primacy Bias (BiasBuster: sequential bias)
- Gender Association Bias (BiasBuster)

### 4. Structural Biases (Xu et al., LREC 2024)

- Template Bias
- Positional Bias

## Framework Alignments

Our implementation aligns with:

1. **BiasBuster** (Echterhoff et al., 2024): Cognitive bias evaluation and self-help debiasing
2. **SAGED**: Five-stage benchmarking pipeline
3. **BEATS**: 29-metric evaluation
4. **FairMonitor**: Four-stage detection

## Implementation

The bias detection module automatically:
- Classifies biases as representational or allocative
- Identifies demographic, cognitive, and structural biases
- Detects sequential biases (anchoring, primacy) as identified in BiasBuster
- Provides research-backed explanations
- Links detections to specific frameworks

## Debiasing Methods

Our debiasing module implements:
- **BiasBuster Self-Help**: LLM automatically paraphrases biased prompts neutrally
- **Counterfactual & Contrastive**: Examples of biased vs. unbiased behavior
- **SACD**: Iterative bias detection and correction
- **Instruction-based**: Simple fairness instructions

See `BIAS_FRAMEWORK.md` for complete documentation.

