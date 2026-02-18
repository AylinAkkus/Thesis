# Can we improve SS-pro performance by composing high resolution frames? (Mock dual-screen and large desktop montages)
## Date: 2025-08-24
## Author: Anas

To improve SS-pro performance on the high-resolution frames, we can mock dual-screen and large desktop montages. For this experiment we do the naive of just creating some dual-screen samples (20% of the dataset) from random frames across data sources and compose large desktops by overlaying random frames on a large desktop background. We don't do any checks to make sure the instructions don't collide with each other. This naive approach doesn't work well at all.

## Results

| Model | SS-Pro Accuracy |
|-------|---------|
| Baseline | 45.22% |
| Composed High-Resolution Frames | 36.94% |