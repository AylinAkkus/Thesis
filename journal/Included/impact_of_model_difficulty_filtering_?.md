# What is the impact of model difficulty filtering on Qwen 2.5 VL 7B?
## Date: 2025-08-21
## Author: Anas

![Model Difficulty Filtering Impact](../journal/data/model_difficulty_filtering_impact.jpg)

If we filter out samples that are too easy or too hard, can we get better results? We run zero-shot evaluations of Qwen 2.5 VL 3B, Qwen 2.5 VL 7B, SE-GUI-3B, and GTA1 7B on the different data sources in the dataset. We use these results to filter out samples based on grounding model accuracy.

All experiments were run with the qwen tool calling + image resolution prompt on Qwen 2.5 VL 7B with 10k training samples.

**Key Finding**: By applying model difficulty filtering, we significantly improve ScreenSpot Pro performance from 36.12% to 45.22%, bringing us much closer to state-of-the-art open source models like SE-GUI-7B (47.3%) and GTA1-7B (50.1%) which use RL.

## Results

### Filter out samples that are too easy for the model

| Filtering | SS Pro Accuracy | SS V2 Accuracy | Showdown Clicks Accuracy | OS-World G Accuracy |
|-----------|----------------|----------------|--------------------------|--------------------|
| No Filtering | 36.12% | 88.59% | 66.43% | N/A |
| Qwen 2.5 VL 7B | 39.78% | 87.29% | 65.71% | N/A |

### Filter out samples that are too easy but not hard for the next best performing model

| Easy Samples Filtering | Hard Samples Filtering | SS Pro Accuracy | SS V2 Accuracy | Showdown Clicks Accuracy | OS-World G Accuracy |
|-------------------------|-------------------------|----------------|----------------|--------------------------|--------------------|
| No Filtering | No Filtering | 36.12% | 88.59% | 66.43% | N/A |
| Qwen 2.5 VL 7B | GTA1 7B | 45.22% | 91.05% | 66.97% | N/A |
| Qwen 2.5 VL 7B | GTA1 7B OR SE-GUI-3B | 42.06% | 88.45% | 67.32% | N/A |
| Qwen 2.5 VL 7B | GTA1 7B OR UI-Venus-7B | 44.46% | 89.75% | 67.68% | N/A |
| SE-GUI-3B | GTA1 7B | 41.62% | 90.27% | 67.50% | N/A |

### Comparison with State-of-the-Art Open Source Models on ScreenSpot Pro

| Model | ScreenSpot Pro Accuracy | Gap from Best Filtering |
|-------|------------------------|-------------------------|
| GTA1-7B (Best Open Source) | 50.1% | - |
| SE-GUI-7B | 47.3% | - |
| **Qwen 2.5 VL 7B + Easy/Hard Filtering** | **45.22%** | **4.88% from GTA1-7B** |
| Qwen 2.5 VL 7B + Easy Filtering | 39.78% | 10.32% from GTA1-7B |
| Qwen 2.5 VL 7B (No Filtering) | 36.12% | 13.98% from GTA1-7B |

The model difficulty filtering approach reduces the performance gap to state-of-the-art open source models by **65%** (from 13.98% to 4.88%).
