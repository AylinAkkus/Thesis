# Does the in-house professional app data we collected from Youtube improve SS Pro performance?
## Date: 2025-08-21
## Author: Anas

We added the in-house professional app data we collected from Youtube to the training data, added it to the model difficulty filtered data and sampled 10k samples total. We find that the performance slightly improves from 45.22% to 46.11% on SS Pro.

## Results

| Data scale | SS Pro Accuracy | SS V2 Accuracy | Showdown Clicks Accuracy | OS-World G Accuracy |
|--------|----------------|----------------|--------------------------|--------------------|
| 10k | 45.22% | 91.05% | 66.97% | N/A |
| 10k (with in-house professional app data) | 46.11% | 90.27% | 67.50% | N/A |