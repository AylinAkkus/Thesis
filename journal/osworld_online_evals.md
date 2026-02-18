# OS-World online evals
## Date: 2025-09-09
## Author: Dhruba

We want to test whether gains on offline grounding benchmarks transfer to online agent benchmarks when the grounding model is combined with a fixed planner model and framework.
For these results, we use Claude Sonnet 4 20250514 as the planner and test different models on OSWorld, setting max steps to 50.
Occasionally, a test example fails due to the planner output; we ignore these samples when calculating success rate.

## Results

| Data scale | SS Pro Accuracy | OS-World G Accuracy | OS-World Success | Avg. Steps on Success | Avg. Steps on Failure | Planner Errors | Grounder-only Score | Grounder Calls |
|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| [35k](https://huggingface.co/mlfoundations-cua-dev/qwen2_5vl_7b_easyr1_35k_hard_qwen7b_easy_gta1_4MP) (without replacement) | 47.2% | 56.2% | **29.2%** | 17.6 | 38.4 | 2 | **74.2%** | 1,069 |
| [80k](https://huggingface.co/mlfoundations-cua-dev/qwen2_5vl_7b_easyr1_38k_hard_qwen7b_easy_gta1_4MP_pro_apps_no_resolution_in_prompt) (with replacement) + improved prompt + pro apps in-house data | 49.6% | 57.6% | **27.5%** | 17.2 | 36.2 | 0 | **69.8%** | 1,007 |
| [114k](https://huggingface.co/mlfoundations-cua-dev/qwen2_5vl_7b_easyr1_114k_large_run) | 49.6% | 59.5% | **34.2%** | 15.6 | 32.4 | 1 | **78.0%** | 845 |
| [Soup (3x uniform)](https://huggingface.co/mlfoundations-cua-dev/qwen2_5vl_7b_model_soup_3x_uniform) | 51.1% | 60.4% | **24.1%** | 16.2 | 35.6 | 0 | **75.9%** | 1,079 |
| GTA1-7B | 50.1% | 67.7% | **30.6%** | 14.4 | 32.9 | 2 | **80.4%** | 873 |

\*Evaluated with "text-image" prompt to grounding model instead of corrected "image-text" prompt format.
