# Which grounding data sources are best for downstream tasks?
## Date: 2025-08-20
## Author: Anas

Our current data pool is a mix of many different data sources. We want to figure out which data sources have the largest impact on downstream tasks. We trained Qwen 2.5 VL 7B on each of the data sources seperately (capping the number of samples at 4.9k to remove the confounder of data repetition). 

## Results

| Data Source | SS Pro Accuracy | SS V2 Accuracy | Showdown Clicks Accuracy | OS-World G Accuracy |
|-------------|----------------|----------------|--------------------------|--------------------|
| ShowUI-Web | **36.43%** | 86.77% | **63.73%** | **48.24%** |
| AutoGUI | **34.54%** | **87.68%** | **63.02%** | **47.06%** |
| PC-Agent-E | **34.28%** | **87.29%** | **63.73%** | **47.84%** |
| WaveUI | 33.40% | **87.16%** | **63.02%** | 44.71% |
| Omniact | 33.21% | **87.16%** | **62.12%** | 44.90% |
| ShowUI-Desktop | 32.01% | 85.21% | 60.68% | 42.16% |
| UGround | 31.82% | 85.99% | **63.73%** | 41.76% |
| Pixmo Points | 30.68% | 86.64% | 61.04% | 42.16% |
| SeeClick | 29.22% | 84.82% | 61.94% | 43.53% |

### Key Findings

**Top 3 performing data sources by benchmark (highlighted in table):**
- **ScreenSpot Pro (SS Pro)**: 
  1. ShowUI-Web (36.43%)
  2. AutoGUI (34.54%)
  3. PC-Agent-E (34.28%)
  
- **ScreenSpot V2 (SS V2)**: 
  1. AutoGUI (87.68%)
  2. PC-Agent-E (87.29%)
  3. Omniact & WaveUI (87.16% - tied)
  
- **Showdown Clicks**: 
  1. ShowUI-Web, PC-Agent-E, UGround (63.73% - three-way tie)
  2. WaveUI & AutoGUI (63.02% - tied)
  3. Omniact (62.12%)
  
- **OS-World G**: 
  1. ShowUI-Web (48.24%)
  2. PC-Agent-E (47.84%)
  3. AutoGUI (47.06%)

**Overall best performers:**
1. **ShowUI-Web** - Consistently strong across all benchmarks, particularly excelling in SS Pro and OS-World G
2. **PC-Agent-E** - Strong performance across all benchmarks with balanced results
3. **AutoGUI** - Highest SS V2 accuracy and good SS Pro performance

**Poorest performers:**
- **SeeClick** - Lowest SS Pro accuracy (29.22%)
- **Pixmo Points** - Second lowest SS Pro accuracy (30.68%)

