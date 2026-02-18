# How does scaling data impact SFT?
## Date: 2025-08-21
## Author: Anas

We want to understand how scaling the data impacts the SFT process. We trained the model on 10k, 20k and 35k samples with the hard samples filtered using GTA1 7B and easy samples filtered using Qwen 2.5 VL 7B. We sample the data from each of the data sources and choose to either sample with replacement or without replacement. We find slightly better performance when scaling to 20k and then 35k samples on SS Pro.

## Results

| Data scale | SS Pro Accuracy | SS V2 Accuracy | Showdown Clicks Accuracy | OS-World G Accuracy |
|--------|----------------|----------------|--------------------------|--------------------|
| 10k (without replacement) | 45.22% | 91.05% | 66.97% | N/A |
| 10k (without replacement) stacked with best training prompt (no resolution) | 46.23% | Missing? | 67.50% | N/A |
| 20k (with replacement) | 45.41% | 90.66% | 66.61% | N/A |
| 20k (without replacement) | 46.55% | 90.27% | 67.14% | N/A |
| 35k (without replacement) | 47.18% | 90.66% | 69.12% | N/A |
| 80k (with replacement) + improved prompt + pro apps in-house data | 49.65% | 90.79% | 68.40% | N/A |