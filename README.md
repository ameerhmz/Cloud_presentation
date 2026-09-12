# 🚀 MCA III Cloud Infrastructure & Services Presentation Package

**Topic**: Leveraging NVIDIA H100 on Lightning AI for High-Performance Cloud Computing  
**Date of Presentation**: 14/09/2026  
**Total Duration**: 45 Minutes (Theory + Live Hands-on Demonstration + Faculty Q&A)  
**Group 1 Members**:
1. **Ameer Hamza** (A073145025016) — Host, Live Hands-On Demo, In-Between Transitions, Q&A Coordination
2. **Suhail Alam** (A073145025036) — Part 1: Foundations of AI Compute & The Cloud Shift (3 Mins)
3. **Harsh Mishra** (A073145025008) — Part 2: NVIDIA H100 Hopper Deep-Dive (8.5 Mins)
4. **Mirza Saad Beg** (A073145025035) — Part 3: Lightning AI Cloud Infrastructure & Distributed Scaling (7.5 Mins)
5. **Harshit Tandon** (A073145025042) — Part 5: Cloud Economics, Hyperscaler Comparison & ROI (5 Mins)

---

## 📁 Project Directory Structure

```
.
├── README.md                              <- Master overview and quick start
├── SPEAKER_SCRIPTS.md                     <- Complete word-by-word scripts, timing cues & top 10 viva defense Q&A
├── presentation/
│   └── index.html                         <- Full-screen interactive Web slide deck (press F for fullscreen)
└── hands_on_demo/
    ├── exp1_vram_oom.py                   <- Experiment 1: The VRAM Capacity Wall & CUDA OOM test
    ├── exp2_real_llm_finetune.py          <- Experiment 2: Qwen-2.5-3B Quantized LLM Fine-Tuning (57m vs 74s)
    ├── download_assets.py                 <- Automated pre-downloader for Qwen-2.5-3B model cache
    ├── dataset/
    │   └── cloud_qa_dataset.json          <- Real MCA Cloud Infrastructure Q&A dataset
    └── lightning_studio_quickstart.md     <- Ameer's step-by-step live demo cheatsheet on Lightning.ai
```

---

## ⏱️ Master 45-Minute Schedule

| Time | Duration | Segment & Topic | Speaker | Core Deliverable |
| :--- | :--- | :--- | :--- | :--- |
| **00:00 - 04:00** | 4.0 min | **Welcome & The AI Compute Crisis** | **Ameer Hamza** | Sets context, Moore's Law wall, roadmap |
| **04:00 - 07:00** | **3.0 min** | **Part 1: The Cloud AI Foundation** | **Suhail Alam** | CPU vs GPU parallelism, why on-prem H100 ($300k) is unviable |
| **07:00 - 15:30** | **8.5 min** | **Part 2: NVIDIA H100 Hopper Deep-Dive** | **Harsh Mishra** | TSMC 4N, 4th Gen Tensor Cores, FP8 Transformer Engine, HBM3 3.35 TB/s |
| **15:30 - 23:00** | **7.5 min** | **Part 3: Lightning AI Cloud Infrastructure** | **Mirza Saad Beg** | Cloud virtualization, instant hardware switching (CPU $\leftrightarrow$ H100), DDP & FSDP |
| **23:00 - 36:00** | **13.0 min**| **Part 4: LIVE Hands-On Masterclass** | **Ameer Hamza** | Live Lightning Studio, VRAM OOM test, 3B Quantized LLM fine-tuning, auto-sleep trick |
| **36:00 - 41:00** | **5.0 min** | **Part 5: Cloud Economics & Comparison**| **Harshit Tandon** | Hyperscaler quota bottlenecks (AWS/GCP), pricing matrix, cost optimization |
| **41:00 - 45:00** | 4.0 min | **Conclusion, Faculty Viva & Q&A** | **Ameer & All Members** | Key takeaways, answering professors' questions |

---

## 🖥️ How to Run the Presentation Slide Deck

1. Open `presentation/index.html` in Google Chrome, Edge, or Safari.
2. Press <kbd>F</kbd> (or click **Fullscreen** button) for projector view.
3. Use the arrow keys (<kbd>◀</kbd> / <kbd>▶</kbd>) or <kbd>Space</kbd> to move through slides.
4. Notice the **live elapsed timer** in the top bar to keep everyone on pace!

---

## 🔬 How to Run the Live Hands-on Demo

1. Open **[lightning.ai](https://lightning.ai)** and create/open a Studio.
2. Switch hardware to **NVIDIA H100**.
3. Upload `hands_on_demo/exp1_vram_oom.py`, `hands_on_demo/exp2_real_llm_finetune.py`, and `hands_on_demo/dataset/`.
4. In the studio terminal, run Experiment 1:
   ```bash
   python3 exp1_vram_oom.py
   ```
5. Run Experiment 2 (3 Billion Parameter Quantized Fine-Tuning):
   ```bash
   python3 exp2_real_llm_finetune.py
   ```
6. Follow the step-by-step checklist in [`hands_on_demo/lightning_studio_quickstart.md`](hands_on_demo/lightning_studio_quickstart.md).
