Mechanisms of Prompt-Induced Bias in LLMs

Recent studies show that even innocuous prompt wording can amplify or reveal social biases in LLM outputs. Neumann et al. (FAccT 2025) demonstrate that where demographic information appears – as a system prompt vs. a user prompt – dramatically changes model behavior
arxiv.org
arxiv.org
. Across six popular LLMs and 50 demographic groups, they found that placing identity cues in the (hidden) system prompt caused large representational and allocative biases that differed from putting the same cues in the user prompt
arxiv.org
arxiv.org
. Because system prompts are opaque to end-users, such effects can produce unfair or harmful outcomes without being detected. Similarly, Sun and Kok (2025) specifically injected cognitive biases (e.g. confirmation or availability bias) into user prompts and measured LLM responses. They report that even subtle biases in a prompt significantly altered LLM answers, and that biased prompts not only changed outputs but shifted internal attention patterns in the model
arxiv.org
arxiv.org
. In other words, prompts carrying hidden assumptions can skew an LLM’s reasoning and lead to misleading or unjust results.

Xu et al. (LREC 2024) study a related phenomenon in factual-knowledge tasks: certain prompt templates systematically skew answers toward particular labels. They show that all prompt styles they tested exhibited “prompt bias,” with learned prompts (AutoPrompt/OptiPrompt) having especially high bias, causing inflated accuracy by overfitting skewed test data
aclanthology.org
. For example, a model asked “The religion of Albanians is [MASK]” might incorrectly predict “Christian” due to prompt phrasing. These authors propose assessing this by a “prompt-only” query (with a dummy subject) to estimate a biased representation, then removing that bias vector from the model’s hidden state to produce a corrected (“debiased”) output
aclanthology.org
. In sum, this and other work show that both system-level instructions and user queries can activate latent stereotypes or preferences in LLMs, altering outputs in socially meaningful ways.

Predicting Prompt Effects on Bias

Given the complexity of LLMs, predicting how a new prompt will affect bias remains challenging. One line of work tries to quantify an LLM’s sensitivity to prompt wording. Yan and Kok (EMNLP 2024 Findings) introduce a metric called PromptSensiScore (PSS) to measure output variance across semantically equivalent prompts
aclanthology.org
. They found large differences between models: some are extremely prompt-sensitive, others more stable. Importantly, LLM outputs with higher confidence tend to be more robust to rephrasing. In their words, “greater confidence in its outputs corresponds to enhanced resilience against changes in prompt semantics”
aclanthology.org
. This suggests one can partially anticipate instability: if an LLM’s answer is low-confidence, it may change wildly under reworded prompts.

Beyond sensitivity metrics, recent work proposes formal tools to certify bias over distributions of prompts. Sushil et al. (ICLR 2025) develop LLMCert-B, a black-box framework that estimates the probability of an LLM producing unbiased answers across random prompt variants
proceedings.iclr.cc
proceedings.iclr.cc
. In this setup, they sample many “counterfactual” prompt sets (e.g. same query with different demographic indicators) and check the model’s outputs for bias. By applying statistical confidence intervals, LLMCert-B can say, for a given range of prefixes or sensitive attributes, “with high confidence, the model will be unbiased at least P% of the time”
proceedings.iclr.cc
proceedings.iclr.cc
. Rather than predicting a single output, this quantifies the risk of biased behavior under prompt variation. Such probabilistic guarantees are a first step toward anticipating how robust an LLM is to prompt-induced biases, even if exact outcomes remain hard to foresee.

Prompt Debiasing and Normalization Methods

A growing body of work has begun to "normalize" or debias prompts before or during model use. One approach is to rewrite user queries into neutral form. For example, Echterhoff et al. (2024) introduce BiasBuster, a framework that includes a Self-Help prompting strategy where the LLM is instructed to paraphrase a biased question neutrally. BiasBuster provides 13,465 prompts to evaluate cognitive bias in high-stakes decision-making tasks and demonstrates that self-help debiasing effectively mitigates model answers displaying patterns akin to human cognitive bias. Extending this idea, Lyu et al. (2025) introduce Self-Adaptive Cognitive Debiasing (SACD) for decision-making prompts. SACD first identifies one or more cognitive biases present in a user prompt, then iteratively asks the LLM to correct them. In practice, SACD involves: (1) Bias detection on the original prompt, (2) analysis, and (3) rewriting. After each rewrite, the prompt is checked again and refined until no obvious biases remain. On financial, healthcare, and legal QA tasks, SACD substantially improved the factual accuracy of LLM answers compared to raw prompts or single-shot corrections
arxiv.org
arxiv.org
. In effect, SACD “normalizes” user instructions by harnessing the model itself to remove unintended slants.

Another technique operates on the model’s internals. Xu et al. (LREC 2024) propose a representation-based debiasing during inference. Rather than changing the prompt text, they subtract a bias vector from the model’s latent state. Concretely, they issue a “prompt-only” query (masking the factual slot) to estimate how the prompt biases the internal representation
aclanthology.org
, then remove that component before generating the final answer. This filter effectively neutralizes the prompt’s skew in the model’s hidden layer, improving fairness. Experiments showed this method both removed overfitting of benchmarks and gave up to 10% absolute gains in retrieval accuracy on factual probes
aclanthology.org
.

Finally, broad benchmarking suggests simple prompting can help. A comprehensive study (BiasFreeBench, 2024) found that adding a brief instruction like “Be fair and unbiased” or otherwise “making the LLM aware of potential bias” often reduced harmful output more than expensive fine-tuning
openreview.net
. In other words, even small prompt hints or normalization (e.g. specifying neutrality) can act as a guardrail. Taken together, these works point to a toolkit for prompt normalization: iterative rewrites (using the LLM or algorithms) and representations-based filters can remove bias cues in user prompts
arxiv.org
aclanthology.org
. They demonstrate that it is possible – at least in part – to preprocess or adjust prompts to achieve more fair LLM behavior.

References: Key studies include Neumann et al.’s ACM FAccT 2025 paper on system vs. user prompts
arxiv.org
arxiv.org
, Sun & Kok’s 2025 arXiv on cognitive prompt biases
arxiv.org
arxiv.org
, Xu et al.’s LREC 2024 work on prompt bias in knowledge retrieval
aclanthology.org
aclanthology.org
, Yan & Kok’s Findings of EMNLP 2024 on prompt sensitivity
aclanthology.org
aclanthology.org
, Sushil et al.’s ICLR 2025 LLMCert-B framework
proceedings.iclr.cc
proceedings.iclr.cc
, and Lyu et al.’s 2025 arXiv on Self-Adaptive Cognitive Debiasing
arxiv.org
arxiv.org
. Each provides methods and results on how prompts shape or can be shaped to mitigate LLM bias.