# Thesis Structure Overview

## 5-Chapter Organization

This thesis is organized into 5 main chapters, following a clear structure from introduction through methodology, results, and conclusions, with supplemental material in the appendix.

---

## **Chapter 1: Introduction**

### 1.1 Motivation
- Overview of GUI agents and computer-use tasks
- Evolution from language-only to visual agents
- Challenges in training multimodal models for GUI grounding

### 1.2 Contributions
- Click-100k Dataset
- Data Filtering Pipeline
- Training Recipe
- Comprehensive Evaluation

### 1.3 Related Work
#### 1.3.1 Vision-Language Models
- Qwen3-VL
- Qwen2.5-7B-VL

#### 1.3.2 Grounding Models and Computer-use Agents
- GTA1
- UI-TARS 1.5
- UI-Venus
- SE-GUI
- OmniParser

#### 1.3.3 GUI Grounding Datasets
- ShowUI
- AutoGUI
- SeeClick
- PixMo Points
- OS-Atlas
- UGround
- WaveUI
- PC-Agent-E
- UI-VISION

#### 1.3.4 Evaluation Benchmarks
- ScreenSpot-Pro
- OS-World-G

#### 1.3.5 Reinforcement Learning Methods
- GRPO
- DAPO

### 1.4 Thesis Organization

---

## **Chapter 2: Methodology**

### 2.1 Building the Click-100k Dataset

#### 2.1.1 Data Source Collection and Normalization
- Normalization Pipeline
- Special Processing Requirements

#### 2.1.2 Identifying Data Quality Issues

#### 2.1.3 Filtering Pipeline
- UI Element Detection Filter
- Difficulty Filtering
- Alignment Filtering
- Validation of Filtering Approach

#### 2.1.4 Supplementing with Professional Application Data
- Professional Application Sources
- Synthetic Annotation Process

#### 2.1.5 Final Refinements

#### 2.1.6 Dataset Statistics and Composition

### 2.2 Training Gelato with Reinforcement Learning

#### 2.2.1 Reinforcement Learning for Grounding

#### 2.2.2 Training Algorithm
- Base Algorithm: GRPO
- Modifications and Simplifications
- Reward Function

#### 2.2.3 Comparison with GTA1 Training Recipe
- Controlled Comparison
- Results

#### 2.2.4 Training Gelato-30B-A3B
- Base Model
- Training Configuration
- Training Progression
- Checkpoint Selection

#### 2.2.5 Eliciting Refusal Behavior
- Refusal Elicitation
- Performance Impact

#### 2.2.6 Training Efficiency and Scalability

---

## **Chapter 3: Results**

### 3.1 Grounding Benchmark Evaluation

#### 3.1.1 ScreenSpot-Pro

#### 3.1.2 OS-World-G

#### 3.1.3 Performance with Refusal

#### 3.1.4 Comparison with Prior Work

### 3.2 OS-World Agent Evaluation

#### 3.2.1 Agent Harness

#### 3.2.2 Implementation Details

#### 3.2.3 Automated Evaluation Results

#### 3.2.4 Variance Across Runs

#### 3.2.5 Trajectory Release

### 3.3 Human Evaluation

#### 3.3.1 Methodology

#### 3.3.2 Human Evaluation Results

#### 3.3.3 Detailed Results

### 3.4 Summary

---

## **Chapter 4: Conclusion and Future Work**

### 4.1 Reproducibility Challenges in Agent Evaluation

#### 4.1.1 Non-Deterministic Planning Models

#### 4.1.2 Evaluation Prompt Versioning

#### 4.1.3 Incomplete Evaluation Coverage

#### 4.1.4 Ambiguous Task Specifications

#### 4.1.5 Recommendations for Future Benchmarks

### 4.2 Limitations

#### 4.2.1 Dataset Limitations

#### 4.2.2 Model Limitations

#### 4.2.3 Evaluation Limitations

### 4.3 Future Directions

#### 4.3.1 Scaling and Efficiency

#### 4.3.2 Dataset Expansion

#### 4.3.3 Training Methodology

#### 4.3.4 Agent Architecture

#### 4.3.5 Evaluation and Analysis

### 4.4 Conclusion

---

## **Chapter 5: Appendix**

### A.1 Supplemental Data

---

## File Organization

```
chapters/
├── Introduction.tex                  # Chapter 1
│   └── RelatedWork/                  # Section 1.3 subsections
│       ├── VisionLanguageModels.tex
│       ├── GroundingModels.tex
│       ├── DataSets.tex
│       ├── EvaluationBenchmarks.tex
│       └── ReinforcementLearning.tex
│
├── Methodology.tex                   # Chapter 2
│   └── Methodology/                  # Section 2.1 & 2.2
│       ├── DataCuration.tex
│       └── Training.tex
│
├── Results.tex                       # Chapter 3
│
├── ConclusionAndFutureWork.tex      # Chapter 4
│
└── Appendix.tex                      # Chapter 5
```

---

## Key Features

✅ **5 Main Chapters** - Clear hierarchical structure  
✅ **Logical Flow** - From motivation through methods to results and conclusions  
✅ **Modular Organization** - Subsections in separate files for easy editing  
✅ **Comprehensive Coverage** - Related work integrated into Introduction  
✅ **Complete Methodology** - Data and training in one unified chapter  
✅ **Detailed Results** - Separate sections for benchmarks and agent evaluation  
✅ **Forward-Looking** - Limitations and future directions clearly outlined  
✅ **Supplemental Material** - Appendix for additional data

