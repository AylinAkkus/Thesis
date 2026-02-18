# Randomly size up training images
## Date: 2025-08-24
## Author: Anas

Trying out randomly resizing up the training images as the [Phi-Grounding](https://arxiv.org/abs/2507.23779) paper showed that this had a +8 pt boost in accuracy on SS Pro.

## Results

| Model | SS Pro Accuracy | SS V2 Accuracy | Showdown Clicks Accuracy | OS-World G Accuracy |
|-------|-----------------|-----------------|--------------------------|--------------------|
| Baseline| 45.22% | 91.05% | 66.97% | N/A |
| Random resize up to 4MP | 44.14% | 88.45% | 67.14% | N/A |
