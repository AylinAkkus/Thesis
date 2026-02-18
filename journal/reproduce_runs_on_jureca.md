# Reproduce SFT runs on Jureca
## Date: 2025-09-10
## Author: Anas

Reproduced SFT runs on Jureca to sanity check the new cluster. Previously all of our SFT runs were on a single node of 80GB H100/A100 GPUs.

## Results

This new model was trained on 4 nodes with 4 40GB A100 GPUs. We had to use deepspeed with ZeRO stage 3 to fit the model on the GPUs. The previous model was trained on a single H100 node with fsdp.

| Model | SS Pro Accuracy | OS-World-G Accuracy |
|-------|----------------|----------------|
| SFT-7B (114k) | 49.6% | 59.5% |
| Reproduced SFT-7B (114k) - ZeRO Stage 3 (x2 BS & half training steps) | 47.8% | 59.3% | 
| Reproduced SFT-7B (114k) - ZeRO Stage 2 (x4 BS & quarter training steps) | 49.6% | 59.2% | 

To show that we can reproduce an exact model on the new cluster, we re-trained the 10k baseline on 2 nodes with 4 40GB A100 GPUs and used ZeRO stage 3 with offload to be able to replicate the 8 batch size of the previous model.

| Model | SS Pro Accuracy | OS-World-G Accuracy |
|-------|----------------|----------------|
| SFT-7B (10k) | 45.22% | - |
| Reproduced SFT-7B (10k) - ZeRO Stage 3 with offload (8 BS // 1.25k steps) | 45.86% | 57.6% | 
| Reproduced SFT-7B (10k) - ZeRO Stage 2 (double BS at 16 // 625 steps) | 44.91% | 57.4% | 