# Comparing sparse and dense reward

Sparse Reward:
- [code](https://github.com/mlfoundations/cua/blob/main/llamafactory/agent/train/rl/gui_reward.py)
- No format reward
- Check if the predicted coordinates are inside the ground truth region and if so penalize it based on distance to the region center/centroid

Dense Reward:
- [code](https://github.com/mlfoundations/cua/blob/rl-v0/llamafactory/agent/train/rl/se_rl_reward.py)
- No format reward
- Give reward in the whole viewport based on distance to center/centroid
- Give additional reward (+1) when inside the bounding box

## Evaluation 1:
Dataset: mlfoundations-cua-dev/easyr1-103k-4MP-jedi-ui-vision-gta1-data-sampling-not-all-correct-stage-one-temp-1_1-RL
![Comparison on Stage 1 of Polaris-like training](data/Dense_vs_Sparse_Reward_Satge_1_Polaris.png)
Comment: For sparse reward the orange baseline comes from a single eval at step 100

## Evaluation 2:
We also ran a comparison on the coldstart setting (training on 3.3k SFT data, then doing one epoch RL on 63k datapool).
However, there we used an additional format reward (+1) in the dense reward.
![Comparison after 3.3k Cold start data](data/Dense_vs_Sparse_Reward_Coldstart_3_3k.png)



