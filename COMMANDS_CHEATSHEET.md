# 📋 MASTER COPY-PASTE COMMAND CHEAT SHEET
### Course: Cloud Infrastructure and Services (MCA III)
### Topic: Leveraging NVIDIA H100 on Lightning AI for High-Performance Cloud Computing
### Presenter: Ameer Hamza (Group 1)

---

## 💻 PART 1: RTX 4060 LAPTOP (Windows PowerShell / Command Prompt)

### 1. One-Time Setup & Clone
```bash
# Clone the repository
git clone https://github.com/ameerhmz/Cloud_presentation.git

# Enter the demo directory
cd Cloud_presentation/hands_on_demo

# Install required packages
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt
```

### 2. If Already Cloned (Pull Latest Code)
```bash
cd Cloud_presentation/hands_on_demo
git pull
```

---

### 🚀 Laptop Live Presentation Commands (Run in Order)

#### [Laptop Test 1] Experiment 1: The VRAM Capacity Wall (Allocating 12 GB)
```bash
python exp1_vram_oom.py
```
> **What Happens**: Attempts to allocate 12 GB FP32 tensor. Crashes with red `CUDA out of memory` on the 8 GB laptop!  
> **Speaker Cue**: *"See? Our 8 GB laptop crashes immediately. We hit the physical memory wall before our project can even start."*

#### [Laptop Test 2] Experiment 2: LLM Fine-Tuning (Thermal & Slow Speed Demo)
```bash
python exp2_real_llm_finetune.py --steps 50 --batch-size 1
```
> **What Happens**: Activates Gradient Checkpointing to fit inside 8 GB VRAM. Step time is ~350–500 ms/step.  
> **Action**: Let it run for 10–15 steps so faculty see the slow step time and high ETA, then press **`Ctrl+C`** to gracefully abort!  
> **Speaker Cue**: *"Even for a tiny batch size of 1, training crawls and causes thermal throttling. Scaling this on a laptop is impossible."*

#### [Laptop Test 3] Experiment 3: Interactive LLM Terminal
```bash
python exp3_inference_speed.py
```
> **What Happens**: Select Option `[2]` for Base Model. Demonstrates single-user generation on laptop (~28 tokens/sec).

#### [Laptop Test 4] Experiment 4: Multi-User Stress Test (Laptop Serial Bottleneck)
```bash
python exp4_enterprise_stress_test.py
```
> **What Happens**: Queues users serially. Takes ~25–40 seconds due to narrow 128-bit GDDR6 memory bus.

---
---

## ⚡ PART 2: LIGHTNING.AI STUDIO (Cloud NVIDIA H100 80GB HBM3)

### 1. One-Time Setup & Clone (in Lightning Studio Terminal)
```bash
# Clone into the studio workspace
cd /teamspace/studios/this_studio
git clone https://github.com/ameerhmz/Cloud_presentation.git

# Enter demo directory
cd Cloud_presentation/hands_on_demo

# Install dependencies (fast cloud network, takes ~15 seconds)
pip install transformers accelerate huggingface_hub
```

### 2. If Already Cloned (Pull Latest Updates)
```bash
cd /teamspace/studios/this_studio/Cloud_presentation/hands_on_demo
git pull
```

---

### 🚀 H100 Live Presentation Commands (Run in Order)

#### [H100 Step 0] Verify the Monster Hardware
```bash
nvidia-smi
```
> **What to Point Out**: Point to `NVIDIA H100 80GB HBM3` and `81559MiB` physical VRAM on screen.

#### [H100 Step 1] Experiment 1: The VRAM Wall Conquered (12 GB Allocation)
```bash
python exp1_vram_oom.py
```
> **What Happens**: Allocates 12.0 GB in **144 milliseconds** with **67+ GB headroom remaining**!  
> **Note**: Holds the allocation for 10 seconds so the Lightning AI web dashboard graph shows the 12 GB spike live.  
> **Speaker Cue**: *"Where our laptop crashed instantly, the Cloud H100 allocates 12 GB in 144 milliseconds and still has 67 GB of headroom free."*

#### [H100 Step 2] Experiment 2: Billion-Scale LLM Fine-Tuning (Batch 16)
```bash
# Standard high-speed run (50 steps with batch 16 to saturate ~45 GB VRAM)
python exp2_real_llm_finetune.py --steps 50 --batch-size 16
```
> **What Happens**: Ingests 16 samples per step. Steps complete in ~110 ms. Total training finishes in ~15 seconds, saving trained weights to `fine_tuned_weights/`!  
> **Speaker Cue**: *"Watch the throughput: we are processing over 12,000 tokens per second with full gradient backpropagation on real Qwen 3B parameters."*

#### [H100 Step 3] Experiment 3: Interactive Chat REPL (Fine-Tuned vs Base)
```bash
python exp3_inference_speed.py
```
> **Menu Choices**:
> - Type `1` to load your **Fine-Tuned Model** (trained on Amity & Cloud questions).
> - Type `2` to load the raw **Base Foundation Model**.
> - Type `3` to fire the **16-User Enterprise Stress Test**.
> 
> **Interactive Test Questions to Ask**:
> - *"What is the minimum attendance requirement at Amity University?"*
> - *"Explain why HBM3 memory bandwidth outperforms GDDR6 in cloud data centers."*
> - *(Type `stress` at any point to trigger the 16-user parallel benchmark!)*

#### [H100 Step 4] Experiment 4: 16-User Concurrent Enterprise Stress Test
```bash
python exp4_enterprise_stress_test.py
```
> **What Happens**:
> - Fires 16 distinct technical questions simultaneously.
> - Answers all 16 users in parallel in **~1.3–1.5 seconds**.
> - Live telemetry reports: **`⚡ 1,450+ TOKENS / SECOND`** (over **20x faster** than laptop).  
> **Speaker Cue**: *"In production, ChatGPT or enterprise search servers receive thousands of requests at the same second. The H100's 3.35 TB/s HBM3 memory answers all 16 distinct users simultaneously in 1.4 seconds flat."*

---

### 💰 PART 3: THE CLOUD ELASTICITY & COST-SAVING FINALE (2 Minutes)

*When done presenting live on Lightning AI:*

1. In the top-right hardware selector of Lightning Studio:
   - Click the dropdown and switch from **NVIDIA H100** to **Free CPU** (or click **Pause Studio**).
2. Run in terminal:
```bash
ls -lh /teamspace/studios/this_studio/Cloud_presentation/fine_tuned_weights
```
3. **Audience Punchline**:  
   *"Notice our trained model weights, datasets, and scripts remain 100% saved on persistent cloud storage. But our GPU billing just dropped from $3.00/hour to exactly $0.00. That is the power of Cloud Elasticity: pay only for the exact seconds of compute you consume."*

---

## ⚡ QUICK COPY-PASTE CHEAT CARDS

### 💻 Laptop Fast Block
```bash
cd Cloud_presentation/hands_on_demo
git pull
python exp1_vram_oom.py
python exp2_real_llm_finetune.py --steps 50 --batch-size 1
python exp3_inference_speed.py
python exp4_enterprise_stress_test.py
```

### 🌩️ Lightning AI Fast Block
```bash
cd /teamspace/studios/this_studio/Cloud_presentation/hands_on_demo
git pull
nvidia-smi
python exp1_vram_oom.py
python exp2_real_llm_finetune.py --steps 50 --batch-size 16
python exp3_inference_speed.py
python exp4_enterprise_stress_test.py
```
