# How does the training prompt impact Qwen 2.5 VL training?
## Date: 2025-08-21
## Author: Anas

![Prompt Impact](../journal/data/qwen_prompt_ablation.jpg)

We trained Qwen 2.5 VL 7B on 10k samples with different training prompts. We want to figure out two things:

1. Is the "base" Qwen model's verbose tool calling computer-use prompt necessary for the model to perform well?
2. How important is passing in the image resolution in the prompt?

We find that the default prompt is sufficient for the model to perform well, achieving competitive results across benchmarks. The impact of including image resolution in the prompt is mixed - while it slightly improves performance on ScreenSpot V2 and Showdown Clicks, it actually decreases performance on ScreenSpot Pro.

## Results

| Prompt | SS Pro Accuracy | SS V2 Accuracy | Showdown Clicks Accuracy | OS-World G Accuracy |
|--------|----------------|----------------|--------------------------|--------------------|
| Qwen Tool Calling Prompt + Image Resolution | 37.76% | 88.59% | 61.94% | N/A |
| Default Prompt + Image Resolution | 36.12% | 88.59% | 66.43% | N/A |
| Default Prompt | 39.03% | 87.68% | 64.09% | N/A |
