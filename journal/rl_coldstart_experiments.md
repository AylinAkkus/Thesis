# RL Coldstart Experiments
## Date: 2025-09-16
## Author: Anas

We are running RL coldstart experiments to see how much the gains from RL training are affected by the amount of data used for SFT.
We ran RL on Qwen2.5-VL-7B-Instruct models trained on 1k, 3.3k, 10k, and 63k samples (single epoch of SFT).

## Results

![Coldstart performance](./data/rl_coldstart_scaling_overlay.png)

| SFT Budget | OSWorld-G | ScreenSpot-Pro |
|---|---:|---:|
| 1k | 0.6176 | 0.4282 |
| 3.3k | 0.6373 | 0.4269 |
| 10k | 0.6392 | 0.4611 |
| 63k | 0.6804 | 0.5079 |

> Table shows best accuracy across all evaluated steps for each model on each benchmark. The OSWorld-G accuracy is not including the refusal subset so the numbers are higher than the ones in the main plots.

### Per-step scaling plots

- 1k: ![1k scaling](./data/scaling/scaling_grpo-coldstart-1k-on-63k-nores-jedi-fix-synced-ui-vision-manually-labeled-icon-data-from-yt-4MP-max-prompt-5200-dynamic-batching-bs_128_8nodes.png)
- 3.3k: ![3.3k scaling](./data/scaling/scaling_grpo-coldstart-3_3k-on-63k-nores-jedi-fix-synced-ui-vision-manually-labeled-icon-data-from-yt-4MP-max-prompt-5200-dynamic-batching-bs_128_8nodes.png)
- 10k: ![10k scaling](./data/scaling/scaling_grpo-coldstart-10k-on-63k-nores-jedi-fix-synced-ui-vision-manually-labeled-icon-data-from-yt-4MP-max-prompt-5200-dynamic-batching-bs_128_8nodes.png)
- 63k: ![63k scaling](./data/scaling/scaling_grpo-coldstart-63k-on-63k-nores-jedi-fix-synced-ui-vision-manually-labeled-icon-data-from-yt-4MP-max-prompt-5200-dynamic-batching-bs_128_8nodes.png)



