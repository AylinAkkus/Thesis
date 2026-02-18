# Competitive 7B Model using SFT Soup
## Date: 2025-09-23
## Author: Anas

Documenting the process of achieving a very strong 7B model using SFT Soup -- no RL and how the performance of each model in the soup compares to the final model. The final model outperforms GTA1-7B (RL) and UI-Venus-7B (RL) on SS Pro.

## Results

We average 4 models in a soup:
- [SFT-7B (38k x 2 epochs)](https://huggingface.co/mlfoundations-cua-dev/qwen2_5vl_7b_easyr1_38k_hard_qwen7b_easy_gta1_4MP_pro_apps_no_resolution_in_prompt)
- [SFT-7B (114k)](https://huggingface.co/mlfoundations-cua-dev/qwen2_5vl_7b_easyr1_114k_large_run)
- [SFT-7B (63k)](https://huggingface.co/mlfoundations-cua-dev/qwen2_5vl_7b_easyr1_63k_with_ui_vision_and_manual_label_icons_yt_lr_1_0e-06)
- [SFT-7B (103k) - added GTA](https://huggingface.co/mlfoundations-cua-dev/qwen2_5vl_7b_easyr1_103k_4MP_jedi_ui_vision_gta1_data_lr_1_0e-06_z3_4nodes)
- [SFT-7B (110k) - added expanded youtube data](https://huggingface.co/mlfoundations-cua-dev/qwen2_5vl_7b_easyr1_110k_4MP_jedi_ui_vision_gta1_data_lr_1_0e-06_z3_4nodes)

The uniform average of all the models:
- [SFT Soup](https://huggingface.co/mlfoundations-cua-dev/qwen2_5vl_7b_model_soup_5x_uniform_add_110k_sft)

| Model | SS Pro Accuracy | OS-World G Accuracy |
|-------|----------------|----------------|
| SFT-7B (38k x 2 epochs) | 49.6% | 60.1% |
| SFT-7B (114k) | 49.6% | 60.1% |
| SFT-7B (103k) - added GTA | 48.4% | 61.7% |
| SFT-7B (63k) | 50.09% | 60.1% |
| SFT-7B (110k) | 49.15% | 61.1% |
| **SFT Soup** | **51.68%** | 60.6% |
| GTA1-7B (RL) | 50.1% | **67.7%** |
| UI-Venus-7B (RL) | 50.8% | 58.8% |
