# How does instruction rewriting impact SFT?
## Date: 2025-08-21
## Author: Anas

We want to understand how scaling the data impacts the SFT process. We trained Qwen 2.5 VL 7B on 10k samples with the hard samples filtered using GTA1 7B and easy samples filtered using Qwen 2.5 VL 7B. We also tried to improve the data by rewriting the prompts using LLM (Qwen3 4B) to remove noisy artifacts and by using image aware synthetic prompts (Qwen 2.5 VL 7B) to rewrite the prompts to include action intent.

## Results

| Rewriting strategy | SS Pro Accuracy | SS V2 Accuracy | Showdown Clicks Accuracy | OS-World G Accuracy |
|--------|----------------|----------------|--------------------------|--------------------|
| No Rewriting | 45.22% | 91.05% | 66.97% | N/A |
| Rewritten Prompts using LLM (Qwen3 4B) | 42.25% | 88.84% | 66.24% | N/A |
| Image aware Synthetic Prompts (Qwen 2.5 VL 7B)| 39.27% | 85.86% | 67.14% | N/A |
