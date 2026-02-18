# Add UI-Vision and Jedi to the data pool
## Date: 2025-09-14
## Author: Anas

We added UI-Vision and Jedi to the data pool. UI-Vision is a dataset of UI elements that we collected from Youtube and Jedi is a dataset of UI elements that we collected from Jedi.

## Results

Deepspeed ZeRO Stage 3 on 4 nodes with 4 40GB A100 GPUs at a batch size of 16:

| Model | Learning Rate | SS Pro Accuracy | OS-World-G Accuracy |
|-------|----------------|-----------------|---------------------|
| SFT-7B (38k) | 1e-6 | 49.3% | 57.4% |
| SFT-7B (38k) - 2 epochs (same as older SFT-7B (80k) but doubled BS) | 1e-6 | 50.16% | 56.0% |
| SFT-7B (44k) - add UI-Vision and manual label icons from YT | 1e-6 | 47.6% | 58.6% |
| SFT-7B (49k) - add UI-Vision and manual label icons from YT and 5k from Jedi | 1e-6 | 47.9% | 60.8% |
| SFT-7B (63k) - add UI-Vision and manual label icons from YT and all of Jedi | 1e-6 | 50.09% | 60.1% |
| SFT-7B (63k) - add UI-Vision and manual label icons from YT and all of Jedi (BS 8 w/ offload on 2 nodes) | 1e-6 | 48.26% | 60.4% |