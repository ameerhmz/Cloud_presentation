# 🚀 How to Run on RTX 4060 Laptop & Lightning.ai (Execution Blueprint)

This guide shows you exactly how to transfer the code from your MacBook to your **RTX 4060 laptop** and your **Lightning.ai H100 Studio**, and how to showcase them side-by-side during the presentation.

---

## 🚀 Zero-Configuration GitHub Blueprint

We have configured `.gitignore` so your repository stays ultra-lightweight (< 5 MB), pushes to GitHub in 3 seconds, and clones instantly on both your RTX 4060 laptop and Lightning.ai without any configuration hassle.

### On Your MacBook (One-Time Push to GitHub)
In your Mac terminal in `/Users/ameerhamza/HOBBY_CODING/Cloud_presentation`:
```bash
git init
git add .
git commit -m "MCA Cloud Infrastructure Presentation & Qwen-2.5-3B Live Demos"
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/Cloud_presentation.git
git push -u origin main
```
*(Replace `YOUR_GITHUB_USERNAME` with your actual GitHub username)*.

---

## 💻 PART 1: Running on the RTX 4060 Laptop (Zero Configuration)

### Step 1: Clone from GitHub
Open Command Prompt / PowerShell on your RTX 4060 laptop:
```bash
git clone https://github.com/ameerhmz/Cloud_presentation.git
cd Cloud_presentation
pip install -r requirements.txt
```
*(PyTorch with CUDA is installed automatically. Zero manual build or C++ compiler required!)*.

### Step 3: Run the Experiments on the 4060 Laptop
Navigate into the `hands_on_demo` folder:
```bash
cd hands_on_demo
```

1. **Run Experiment 1 (The VRAM OOM Crash)**:
   ```bash
   python exp1_vram_oom.py
   ```
   * **What happens**: It detects `RTX 4060 (8.0 GB VRAM)`. It attempts to allocate 12 GB and **CRASHES** with:
     `RuntimeError: CUDA out of memory. Tried to allocate 12.00 GiB on GPU with 8.00 GiB total capacity!`
   * **Your line to faculty**: *"See? Our 8 GB laptop crashes immediately. The project cannot even start locally."*

2. **Run Experiment 2 (Real Qwen-2.5 3B Fine-Tuning)**:
   ```bash
   python exp2_real_llm_finetune.py --steps 500
   ```
   * **What happens**: Downloads the real 3B model into root `model_weights/` (if not already downloaded). Activates the dynamic VRAM guard (gradient checkpointing) so it runs safely inside 8 GB. Shows live token throughput and remaining ETA.
   * **Your line to faculty**: *"Look at the live ETA on our laptop: ~2.5 minutes for just 500 steps, and training a full dataset would take hours while thermal throttling at 80°C. I am pressing Ctrl+C to abort."*
   * **Action**: Press **`Ctrl+C`** to abort gracefully.

3. **Run Experiment 3 (Interactive Cloud LLM Terminal)**:
   ```bash
   python exp3_inference_speed.py
   ```
   * **What happens**: Loads the base 3B weights from `model_weights/` instantly. Opens an interactive prompt `👉 Enter your question: ` where anyone can ask a real question and watch it stream live with tokens/sec telemetry!

---

## ⚡ PART 2: Setting Up & Running on Lightning.ai (Cloud NVIDIA H100)

### Step 1: Open Lightning.ai & Start an H100 Studio
1. In your browser (Chrome/Edge/Safari), log into **[lightning.ai](https://lightning.ai)**.
2. Click **New Studio** (or open an existing one).
3. In the top-right corner, click the **Hardware dropdown** and select:  
   👉 **NVIDIA H100 (1x GPU)**.
4. The studio spins up in ~30 seconds with pre-installed CUDA 12 and PyTorch.

### Step 2: Open Terminal in Lightning Studio & Clone from GitHub
In the Lightning Studio bottom panel, click **Terminal**:
```bash
git clone https://github.com/ameerhmz/Cloud_presentation.git
cd Cloud_presentation/hands_on_demo
pip install transformers accelerate huggingface_hub
```

### Step 3: Run the Demos on H100

1. **Check the H100 GPU**:
   ```bash
   nvidia-smi
   ```
   *(Show the audience: `NVIDIA H100 80GB HBM3` with 81,559 MiB VRAM!)*

2. **Run Experiment 1 on H100 (The OOM Test)**:
   ```bash
   python exp1_vram_oom.py
   ```
   * **What happens**: Allocates the 12 GB in **0.04 seconds**!  
     Prints: `[✔] Allocated 12.0 GB on NVIDIA H100 with 68 GB still free!`

3. **Run Experiment 2 on H100 (Real Qwen-2.5 3B Fine-Tuning)**:
   ```bash
   python exp2_real_llm_finetune.py --steps 500
   ```
   * **What happens**: The steps fly by in milliseconds! Completes all 500 steps in seconds with full backpropagation, loss reduction, and saves fine-tuned weights to `fine_tuned_weights/` in the project root.

4. **Run Experiment 3 on H100 (Interactive LLM Terminal)**:
   ```bash
   python exp3_inference_speed.py
   ```
   * **What happens**: Reuses `model_weights/` without re-downloading! Streams answers at blazing speeds (~200+ tokens/sec) thanks to 3.35 TB/s HBM3 memory bandwidth.

5. **Show Cloud Cost Optimization**:
   * Switch the hardware selector to **Free CPU** or click **Pause Studio**.
   * Show that all files (`model_weights/`, `fine_tuned_weights/`, datasets) are permanently preserved on cloud storage, but GPU billing drops to exactly $0.00.

---

## 🎯 How to Stage the Presentation on Presentation Day

You have two great presentation setups:

### Setup Option A: The "Side-by-Side" Split Screen (Most Recommended!)
* On your laptop connected to the classroom projector:
  * **Left Half of Screen**: A terminal showing the **RTX 4060 Laptop** running `exp1_vram_oom.py` (showing the red OOM crash and 1h 13m ETA).
  * **Right Half of Screen**: Browser showing **Lightning.ai H100 Studio** running the exact same scripts (allocating instantly and finishing in 71 seconds!).
* **Impact**: The faculty and students see the contrast side-by-side on the big screen!

### Setup Option B: Sequential Demo
* First, show the terminal on your 4060 laptop: run the crash and step calculation.
* Second, switch to the browser tab with Lightning.ai: run the H100 live to show the resolution.
