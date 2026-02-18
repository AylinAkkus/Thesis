# Remove the worst data sources
## Date: 2025-08-22
## Author: Anas

We removed the worst data sources from the training data based on the data source experiments in [which_data_sources_are_best_for_downstream_tasks_?.md](./which_data_sources_are_best_for_downstream_tasks_?.md). I did this by removing the bottom 3 data sources on SS Pro. These were:

- SeeClick
- Pixmo Points
- UGround

We then trained the model on the remaining data sources and sampled 10k samples with the best model filtering approach.

## Results

| Data Pool | SS Pro Accuracy | SS V2 Accuracy | Showdown Clicks Accuracy | OS-World G Accuracy |
|---|---|---|---|---|
| All Data Sources | 45.22% | 91.05% | 66.97% | N/A |
| Remove Bottom 3 on SS Pro (SeeClick, Pixmo Points, UGround) | 45.03% | 90.14% | 68.94% | N/A |
| Remove Worst one on SS Pro (Pixmo Points) | 44.78% | 90.79% | 67.68% | N/A |


# Add OS-Atlas and Jedi to the data pool
## Date: 2025-08-27
## Author: Anas

We added OS-Atlas and Jedi to the data pool and sampled 10k samples with the best model filtering approach. We had to use Qwen3B for the easy filtering for OS-Atlas due to time constraints. We also applied no filtering on Jedi data.

OS-Atlas is not a good data source.

## Results

| Data Pool | SS Pro Accuracy | SS V2 Accuracy | Showdown Clicks Accuracy | OS-World G Accuracy |
|---|---|---|---|---|
| 10k (with in-house professional app data) | 46.11% | 90.27% | 67.50% | N/A |
| + OS-Atlas | 35.35% | 88.19% | 64.63% | N/A |
| + Jedi | 46.62% | 90.79% | 67.14% | N/A |
