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
git clone https://github.com/YOUR_GITHUB_USERNAME/Cloud_presentation.git
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
   * **What happens live**: It detects `RTX 4060 (8.0 GB VRAM)`. It attempts to allocate 12 GB and **CRASHES** with:
     `RuntimeError: CUDA out of memory. Tried to allocate 12.00 GiB on GPU with 8.00 GiB total capacity!`
   * **Your line to faculty**: *"See? Our 8 GB laptop crashes immediately. The project cannot even start locally."*

2. **Run Experiment 2 (The Qwen-2.5-3B 4-Bit QLoRA Bottleneck)**:
   ```bash
   python exp2_real_llm_finetune.py
   ```
   * **What happens live**: It starts the full 500-step training loop. Step 1, 2, and 3 run:  
     `Step [003/500] |█-----------------------| Step: 6840ms | Loss: 4.821 | ETA: 56.8 min remaining`
   * **Your line to faculty**: *"Look at the live ETA on our laptop: 56.8 minutes remaining! We obviously cannot make you wait an hour during a 45-minute presentation. I am pressing Ctrl+C to abort."*
   * **Action**: Press **`Ctrl+C`**. The script catches it cleanly without crashing and prints the graceful abort summary!
   * **Next move**: *"Now let's switch to our Cloud H100 to run the exact same 500 steps!"*

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
git clone https://github.com/YOUR_GITHUB_USERNAME/Cloud_presentation.git
cd Cloud_presentation/hands_on_demo
```
*(Lightning AI already has PyTorch, CUDA 12, and Hugging Face installed. ZERO manual installation needed!)*.

### Step 3: Run the Demos on H100

1. **Check the H100 GPU**:
   ```bash
   nvidia-smi
   ```
   *(Show the audience: `NVIDIA H100 80GB HBM3` with 81,559 MiB VRAM!)*

2. **Run Experiment 1 on H100**:
   ```bash
   python3 exp1_vram_oom.py
   ```
   * **What happens**: Allocates the 12 GB in **0.04 seconds**!  
     Prints: `[✔] Allocated 12.0 GB on NVIDIA H100 with 68 GB still free!`

3. **Run Experiment 2 on H100 (Qwen-2.5-3B Fine-Tuning)**:
   ```bash
   python3 exp2_real_llm_finetune.py
   ```
   * **What happens**: The steps fly by at **~148 ms** per step!  
     The entire 500 steps finish in **1 Minute 14 Seconds** (~46.2x faster!).  
     Outputs prompt adaptation before/after and the **Qwen-2.5 3B Live Comparison Card**.

4. **Show Cloud Cost Optimization**:
   * Switch the hardware selector to **Free CPU** or click **Pause Studio**.
   * Show that all files are preserved on `/teamspace/studios`, but GPU billing stops immediately.

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
