# Multi-Turn Conversation Analysis: Implications for Bias Graph Tool

## Overview

This document analyzes how the findings from **"LLMs Get Lost In Multi-Turn Conversation"** (Laban et al., 2025) relate to the bias analysis tool's graph-based exploration architecture.

**Paper Reference**: [Laban et al., 2025 - LLMs Get Lost In Multi-Turn Conversation](https://arxiv.org/pdf/2505.06120)

## Key Findings from the Paper

### Main Results
- **39% average performance drop** across 15 LLMs in multi-turn vs single-turn conversations
- Performance degradation consists of:
  1. **Loss in aptitude** (minor): Performance in best-case scenarios
  2. **Increase in unreliability** (major): Gap between best- and worst-case performance
- **"Lost in conversation" phenomenon**: When LLMs take a wrong turn, they get lost and don't recover

### Root Causes Identified
1. **Overly verbose responses** - LLMs generate too much text
2. **Premature final solutions** - LLMs attempt to propose finalized answers too early
3. **Incorrect assumptions** - LLMs make wrong assumptions about underspecified details
4. **Over-reliance on previous attempts** - LLMs rely too heavily on previous (incorrect) answer attempts

### Underspecification Focus
- Paper focuses on **underspecified instructions** (common in real-world usage)
- Multi-turn conversations reveal information gradually through "shards"
- Episodic tasks (where each turn is a separate subtask) overestimate LLM performance

## Current Architecture Analysis

### How the Bias Graph Tool Works

```
User enters prompt
    ↓
/api/graph/expand (Single-turn)
    ↓
1. Generate LLM answer for original prompt
2. Evaluate with HEARTS + Gemini
3. Return: 1 node + potential paths (edges without targets)
    ↓
User clicks potential path (e.g., "Add Confirmation Bias")
    ↓
/api/graph/expand-node (Single-turn)
    ↓
1. Transform prompt using LLM (instruction-based)
2. Generate LLM answer for NEW prompt (independent)
3. Evaluate with HEARTS + Gemini
4. Return: New node + new potential paths
```

### Key Architectural Characteristics

**✅ Current Approach (Independent Nodes)**
- Each node expansion is **single-turn** and **stateless**
- Each LLM answer is generated **independently** from scratch
- No conversation history maintained between nodes
- Each prompt transformation is **self-contained**

**❌ Not Currently Implemented (Multi-Turn Context)**
- No conversation history passed between nodes
- No cumulative context from previous transformations
- Each node expansion is treated as isolated
- No sequential dependency tracking

## Implications for the Bias Tool

### 1. **Current Architecture Mitigates Some Issues**

The current **independent node expansion** approach actually **avoids** some of the problems identified in the paper:

- ✅ **No conversation drift**: Each node is evaluated independently
- ✅ **No accumulation of errors**: Wrong assumptions in one node don't propagate
- ✅ **No over-reliance on previous attempts**: Each prompt is treated fresh
- ✅ **Clear specification**: Each transformation is explicitly defined (not underspecified)

### 2. **However, Some Multi-Turn Patterns Still Apply**

Even with independent nodes, some patterns might emerge:

- ⚠️ **Graph depth effects**: As users explore deeper paths, LLM performance might degrade
- ⚠️ **Transformation complexity**: Complex bias transformations might introduce underspecification
- ⚠️ **Answer quality degradation**: LLM answers might become less reliable as graph grows

### 3. **Potential Multi-Turn Scenarios**

If we were to implement **conversation-aware** expansion:

**Scenario: Sequential Bias Application**
```
Original: "What are the benefits of exercise?"
    ↓ (Add Confirmation Bias)
Biased 1: "Isn't it obvious that exercise is essential..."
    ↓ (Add Anchoring Bias)
Biased 2: "Given that top athletes train 6 hours daily, isn't it obvious..."
```

**Risks** (based on Laban et al.):
- LLM might make assumptions about how biases interact
- Might propose premature final solutions
- Might become verbose in deeper nodes
- Might rely too heavily on previous biased formulations

### 4. **Measurement Opportunities**

The bias graph tool could actually **measure** the "lost in conversation" phenomenon:

**Metrics to Track**:
- **Aptitude**: Quality of LLM answers at different graph depths
- **Reliability**: Variance in answer quality across similar paths
- **Bias detection accuracy**: Does HEARTS/Gemini accuracy degrade with depth?
- **Answer coherence**: Do answers become less coherent in deeper nodes?

**Experiment Design**:
1. Start with original prompt (depth 0)
2. Generate multiple bias paths (depth 1)
3. Continue expanding to depth 2, 3, 4...
4. Measure: answer quality, bias scores, evaluation confidence

## Recommendations

### Immediate Actions (Current Architecture)

1. **Add Depth Tracking**
   ```python
   node = {
       'id': node_id,
       'prompt': prompt,
       'depth': depth,  # Track graph depth
       'path_history': path_history,  # Track transformation path
       ...
   }
   ```

2. **Monitor Answer Quality by Depth**
   - Track answer length (paper shows verbosity increases)
   - Track bias score variance (reliability decreases)
   - Track evaluation confidence (unreliability increases)

3. **Add Reliability Metrics**
   ```python
   'reliability_metrics': {
       'depth': depth,
       'answer_length': len(llm_answer),
       'confidence_variance': variance_across_evaluations,
       'path_uniqueness': how_different_from_other_paths
   }
   ```

### Future Enhancements (Multi-Turn Context)

1. **Conversation-Aware Expansion**
   ```python
   # Include context from parent nodes
   context = {
       'parent_prompt': parent_prompt,
       'parent_answer': parent_answer,
       'transformation_history': [...],
       'depth': depth
   }
   
   transformed = llm.inject_bias_llm(
       prompt, 
       bias_type,
       context=context  # Pass conversation history
   )
   ```

2. **Underspecification Simulation**
   - Implement gradual information revelation (like paper's "sharding")
   - Test how bias transformations affect underspecified prompts
   - Measure performance degradation with specification levels

3. **Recovery Mechanisms**
   - Detect when LLM gets "lost" (high variance, low confidence)
   - Suggest debiasing paths when unreliability detected
   - Provide "reset" options to return to earlier nodes

## Research Questions

Based on Laban et al.'s findings, the bias tool could investigate:

1. **Does bias transformation introduce unreliability?**
   - Compare single-turn vs multi-turn bias application
   - Measure answer quality degradation

2. **Do deeper bias paths become less reliable?**
   - Track HEARTS/Gemini confidence vs graph depth
   - Identify optimal exploration depth

3. **Can we detect "lost in conversation" patterns in bias graphs?**
   - Identify nodes with high unreliability metrics
   - Correlate with graph structure features

4. **How do different bias types affect multi-turn reliability?**
   - Some biases (confirmation) might compound more than others
   - Measure interaction effects

## Comparison: Paper's Framework vs Bias Tool

| Aspect | Laban et al. (2025) | Bias Analysis Tool |
|--------|---------------------|-------------------|
| **Evaluation Setting** | Multi-turn underspecified | Single-turn specified (per node) |
| **Information Flow** | Gradual revelation (sharding) | Explicit transformation |
| **Dependency** | Sequential turns with history | Independent node expansion |
| **Underspecification** | Central element | Currently minimal |
| **Performance Issue** | 39% drop in multi-turn | Could investigate depth effects |
| **Recovery** | LLMs don't recover | Could implement recovery paths |

## Multi-Turn Bias Priming Hypothesis

### The Priming Effect in Multi-Turn Conversations

**Hypothesis**: Bias increases when using multi-turn conversations to induce biased answers, compared to single-turn direct questions.

**Example**:
- **Single-turn**: "How is John as a person?" → Neutral answer
- **Multi-turn**: 
  1. First: "List all the positive traits of John"
  2. Then: "How is John as a person?" → More biased (primed by positive traits)

### Why This Happens (Based on Laban et al.)

The paper's findings explain why multi-turn bias priming might be more effective:

1. **Over-reliance on previous attempts**: LLMs heavily rely on previous conversation turns
2. **Premature solutions**: LLMs anchor on early information (positive traits list)
3. **Lost in conversation**: Once primed, LLMs don't easily "reset" - they carry forward the priming
4. **Unreliability**: Multi-turn conversations show higher variance, making bias effects more pronounced

### Psychological Foundation

This aligns with cognitive psychology:
- **Priming effect**: Exposure to certain information influences subsequent responses
- **Anchoring bias**: Early information serves as an anchor for later judgments
- **Halo effect**: Positive initial information generalizes to overall assessment

## Testing Multi-Turn Bias Priming

### Experimental Design

**A/B Comparison**:
1. **Single-turn condition**: Direct question about person/entity
   - "How is John as a person?"
   - Measure bias in answer

2. **Multi-turn priming condition**: 
   - Turn 1: "List all positive traits of John"
   - Turn 2: "How is John as a person?" (with conversation history)
   - Measure bias in answer

3. **Control condition**:
   - Turn 1: "List traits of John" (neutral)
   - Turn 2: "How is John as a person?"
   - Measure bias

### Expected Results

- **Hypothesis**: Multi-turn priming → Higher bias scores than single-turn
- **Measurement**: Compare HEARTS/Gemini bias scores between conditions
- **Additional metrics**: Answer sentiment, trait distribution, confidence variance

## Implementation: Conversation-Aware Bias Expansion

### New Feature: Multi-Turn Bias Priming Paths

Add a new type of path expansion that maintains conversation history:

```python
# New endpoint: /api/graph/expand-node-with-history
@app.route('/api/graph/expand-node-with-history', methods=['POST'])
def expand_node_with_history():
    """
    Expand node with conversation history (multi-turn bias priming).
    
    Enables testing hypothesis that multi-turn priming increases bias.
    """
    data = request.get_json()
    parent_id = data.get('node_id')
    parent_node = get_node(parent_id)
    
    # Get conversation history from parent path
    conversation_history = data.get('conversation_history', [])
    
    # Add current turn
    conversation_history.append({
        'role': 'user',
        'content': data.get('prompt'),
        'answer': parent_node.get('llm_answer')
    })
    
    # New priming question (e.g., "List positive traits")
    priming_prompt = data.get('priming_prompt')
    
    # Generate priming answer
    llm = get_vertex_llm_service()
    priming_answer = llm.generate_with_history(
        priming_prompt,
        conversation_history=conversation_history
    )
    
    # Main question with full history
    main_prompt = data.get('main_prompt')
    conversation_history.append({
        'role': 'user',
        'content': priming_prompt,
        'answer': priming_answer
    })
    
    main_answer = llm.generate_with_history(
        main_prompt,
        conversation_history=conversation_history
    )
    
    # Compare bias: primed vs non-primed
    primed_bias = evaluate_bias(main_answer)
    non_primed_bias = evaluate_bias_direct(main_prompt)  # Single-turn baseline
    
    return {
        'primed_answer': main_answer,
        'primed_bias_score': primed_bias,
        'non_primed_bias_score': non_primed_bias,
        'bias_increase': primed_bias - non_primed_bias,
        'conversation_history': conversation_history
    }
```

### New Bias Instruction Type: Priming-Based

Add to `bias_instructions.py`:

```python
BIAS_INSTRUCTIONS['priming_bias'] = {
    'name': 'Priming Bias (Multi-Turn)',
    'description': 'Use multi-turn conversation to prime LLM with biased information before asking main question',
    'techniques': [
        'First ask LLM to list positive/negative traits',
        'Then ask main question about the entity',
        'LLM will be primed by first answer and show bias in second',
        'Works like psychological priming effect'
    ],
    'examples': [
        {
            'single_turn': 'How is John as a person?',
            'multi_turn': [
                'User: List all the positive traits of John',
                'LLM: [Lists positive traits]',
                'User: How is John as a person?',
                'LLM: [Biased positive answer, primed by previous turn]'
            ]
        }
    ],
    'framework': 'Laban et al. (2025) + Priming Effects',
    'severity': 'high',
    'requires_history': True  # Requires conversation context
}
```

### Enhanced LLM Service: History-Aware Generation

```python
def generate_with_history(
    self,
    prompt: str,
    conversation_history: List[Dict],
    system_prompt: Optional[str] = None
) -> str:
    """
    Generate answer with conversation history (for multi-turn priming).
    
    Args:
        prompt: Current prompt
        conversation_history: List of {'role': 'user'|'assistant', 'content': str, 'answer': str}
        system_prompt: Optional system instructions
    
    Returns:
        Generated answer
    """
    messages = []
    
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    
    # Build conversation from history
    for turn in conversation_history:
        if turn.get('role') == 'user':
            messages.append({"role": "user", "content": turn['content']})
        elif turn.get('answer'):
            messages.append({"role": "assistant", "content": turn['answer']})
    
    # Add current prompt
    messages.append({"role": "user", "content": prompt})
    
    # Generate with full context
    return self._generate_openapi_with_messages(messages)
```

## Research Questions for Multi-Turn Bias Priming

1. **Does multi-turn priming increase bias compared to single-turn?**
   - Measure: Bias score difference between primed and non-primed conditions
   - Expected: Primed condition shows higher bias

2. **What types of priming are most effective?**
   - Positive trait priming vs negative trait priming
   - Demographic priming vs cognitive priming
   - Single priming turn vs multiple priming turns

3. **How does conversation depth affect bias amplification?**
   - Does bias increase linearly with priming turns?
   - Is there a saturation point?

4. **Can we detect and mitigate priming effects?**
   - Can HEARTS/Gemini detect priming-based bias?
   - Can debiasing methods counter priming effects?

5. **Do different LLMs respond differently to priming?**
   - Compare Llama 3.3, Gemini, GPT-4 in multi-turn priming scenarios
   - Measure variance in priming susceptibility

## Conclusion

The current **independent node expansion** architecture of the bias tool **mitigates** many of the multi-turn reliability issues identified by Laban et al. However, the tool could:

1. **Measure** the "lost in conversation" phenomenon by tracking metrics across graph depths
2. **Investigate** how bias transformations affect LLM reliability
3. **Enhance** with conversation-aware expansion to study multi-turn bias effects
4. **Test multi-turn bias priming hypothesis**: Does multi-turn conversation increase bias?
5. **Contribute** to understanding how bias interacts with multi-turn conversation reliability

**New Research Direction**: Multi-turn bias priming is a novel hypothesis that combines:
- Laban et al.'s findings on multi-turn unreliability
- Psychological priming effects
- Bias amplification in conversational AI

This could be a significant contribution to understanding how conversational interfaces can be exploited to induce bias.

The paper's findings are highly relevant for:
- Understanding why deep graph exploration might show degraded performance
- Designing better bias transformation strategies
- Testing multi-turn bias priming hypothesis
- Improving user experience with reliability feedback
- Contributing to multi-turn bias analysis research

## References

- Laban, P., Hayashi, H., Zhou, Y., & Neville, J. (2025). LLMs Get Lost In Multi-Turn Conversation. arXiv:2505.06120. https://arxiv.org/pdf/2505.06120
- Related work: Multi-turn evaluation, underspecification in LLM prompts, conversational AI reliability
- Priming effects in psychology and AI
- Anchoring bias and halo effect in LLM conversations

