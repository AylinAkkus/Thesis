# Best hparams for Qwen 2.5 VL 7B
## Date: 2025-08-22
## Author: Anas

Running a simple sweep of learning rates for Qwen 2.5 VL 7B on the 10k model filtered dataset using qwen2.5vl 7b for easy sample filtering and GTA1-7B for incorrect sample filtering. 

# Best learning rate
| Learning rate | Screenspot Pro | Screenspot V2 | Showdown Clicks|
|---------------|----------------|---------------|----------------|
| 1e-5          | 32.57%         | 80.02%        | 53.68%         |
| 5e-6          | 38.83%         | 87.80%        | 63.01%         |
| **1e-6**   | 45.35%         | 90.27%        | 67.50%         |
| 5e-7          | 38.07%         | 89.10%        | 65.17%         |
