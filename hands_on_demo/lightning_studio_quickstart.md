# Lightning AI Studio Quickstart Guide (Ameer's Live Demo Cheatsheet)

**Presentation Date**: 14/09/2026  
**Subject**: Cloud Infrastructure and Services - MCA III  
**Demo Driver**: Ameer Hamza (Group 1 Lead)  
**Target Duration**: 13 Minutes

---

## 1. Pre-Presentation Setup (Do this 15 mins before class)

1. Open your browser and log in to [lightning.ai](https://lightning.ai).
2. Click **"New Studio"** (or open your existing teamspace).
3. Name the Studio: `H100-Cloud-Demo`.
4. In the top-right hardware picker, click the machine dropdown:
   - Select **NVIDIA H100** (or if testing freely before class, T4 / A10G / CPU, and switch to H100 for the demo).
5. In the bottom terminal, clone your repository:
   `git clone https://github.com/ameerhmz/Cloud_presentation.git`
   `cd Cloud_presentation/hands_on_demo`

---

## 2. Live Demo Step-by-Step Script (During the 13 Minutes)

### Step 1: Open the Studio & Inspect Silicon (2 Minutes)
* **What you say**:  
  *"Let's look under the hood of an enterprise AI cloud machine. We don't have to configure SSH keys, VPCs, or install NVIDIA drivers. Lightning AI gives us a pre-configured Hopper environment in seconds."*
* **Action**: Open the built-in Studio Terminal and run:
  ```bash
  nvidia-smi
  ```
* **Points to highlight on screen**:
  - Point to **GPU Name**: `NVIDIA H100 80GB HBM3` (or PCIe / SXM5).
  - Point to **Driver Version / CUDA Version**: `CUDA 12.x`.
  - Point to **Memory**: `0MiB / 81559MiB` (Emphasize: *"Notice this 80,000 MiB memory—10x larger than an RTX 4060!"*).

---

### Step 2: Run Experiment 1 — The VRAM OOM Test (3 Minutes)
* **What you say**:  
  *"Every student in this room has suffered from `CUDA Out of Memory`. An RTX 4060 laptop has only 8 GB of VRAM. If you try to allocate a batch size of 64 or load a modern LLM activation matrix needing 12 GB, a laptop immediately crashes with a red error."*
* **Action**: In the terminal, run:
  ```bash
  python3 exp1_vram_oom.py
  ```
* **What happens**:
  - The script prints Experiment 1.
  - On the H100, it allocates 12.0 GB in under 0.05 seconds!
  - It shows: `[✔] Allocated 12.0 GB on NVIDIA H100 with 68 GB still free!`
* **Audience Punchline**:  
  *"On a 4060 laptop, this project would be dead on arrival. On the H100, we still have 68 GB free to load the model weights, KV cache, and optimizer states."*

---

### Step 3: Run Experiment 2 — The Qwen-2.5 3B Quantized LLM Race (5 Minutes)
* **What you say**:  
  *"Now let's test modern edge AI architecture: Fine-tuning Alibaba Cloud's Qwen-2.5-3B (3.09 Billion parameters) using 4-Bit Quantization (QLoRA). Qwen-3B requires 36.8 GB VRAM unquantized. We compress it to 4-bit (~4.2 GB training VRAM) so it fits on an 8 GB laptop, but software dequantization on the 4060 causes a 57-minute crawl! On our Cloud H100, hardware Tensor Cores handle dequantization at 3,350 GB/s and finish in 74 seconds flat."*
* **Action**: In the terminal, run:
  ```bash
  python3 exp2_real_llm_finetune.py
  ```
* **What happens**:
  - Displays the Qwen-2.5-3B memory breakdown (36.8 GB unquantized vs 4.2 GB 4-bit QLoRA).
  - Shows prompt before training (`What is NVIDIA H100 Hopper?`).
  - Measures live training steps at ~148 ms per step, loss reducing dynamically!
  - Shows prompt adaptation after fine-tuning.
  - Displays the final comparison: **57.0 Minutes on Laptop vs 1 Minute 14 Seconds on Cloud H100 (46.2x Speedup!)**.
  - The formatted **Hardware Comparison Card** prints out:
    ```
    +-------------------------------------------------------------------------+
    |              QWEN-2.5 3B QUANTIZED LLM (4-BIT QLoRA) BENCHMARK          |
    +--------------------------+-----------------------+----------------------+
    | Metric                   | Laptop RTX 4060       | Cloud NVIDIA H100    |
    +--------------------------+-----------------------+----------------------+
    | Workload Model           | Qwen-2.5-3B (Alibaba) | Qwen-2.5-3B (Alibaba)|
    | Base Parameter Scale     | 3.09 Billion Params   | 3.09 Billion Params  |
    | Unquantized Training Req | 36.8 GB (💥 OVERFLOWS)| 36.8 GB (Fits in 80G)|
    | 4-Bit QLoRA VRAM Used    | ~4.2 GB (Compressed)  | ~4.2 GB (or Full FP16|
    | Memory Bandwidth         | 272 GB/s (GDDR6)      | 3,350 GB/s (HBM3)    |
    | Dequantization Speed     | Software Emulated     | Native Tensor Cores  |
    +--------------------------+-----------------------+----------------------+
    | Step Time (Latency)      | ~6.84 seconds         | ~0.148 seconds       |
    | Total Training (500 Stp) | ~57.0 Minutes         | ~74.0 Seconds        |
    +--------------------------+-----------------------+----------------------+
    | ⚡ CLOUD SPEEDUP FACTOR   | 1.0x (Baseline)       | 46.2x FASTER! 🚀    |
    +-------------------------------------------------------------------------+
    ```
* **Audience Punchline**:  
  *"What locks up your laptop for an entire lecture period took 74 seconds in the cloud. That is a 46x speedup on a 3.09 Billion parameter model!"*

---

### Step 4: Run Experiment 3 — High-Throughput Cloud Inference Benchmark (2 Minutes)
* **What you say**:  
  *"Training is only half the cloud equation. Over 90% of enterprise AI cloud spend is on INFERENCE—serving thousands of concurrent users. When generating text, every single token requires reloading all 1.5 Billion parameters through the GPU memory bus. On an RTX 4060 laptop with a 128-bit GDDR6 bus, generation crawls at ~30 tokens/sec. Watch our Cloud H100 handle interactive streaming and concurrent batch inference at blistering speeds."*
* **Action**: In the terminal, run:
  ```bash
  python exp3_inference_speed.py
  ```
* **What happens**:
  - Automatically loads the trained weights from `fine_tuned_weights/` (or `model_weights/`).
  - **Test 1**: Streams real-time tokens live on screen with sub-second Time to First Token (TTFT).
  - **Test 2**: Simulates concurrent users submitting cloud infrastructure queries in parallel.
  - Outputs aggregate throughput (`tokens/sec`) demonstrating why cloud inference dominates production AI.

---

### Step 5: The Cloud Elasticity & Cost-Saving Trick (2 Minutes)
* **What you say**:  
  *"An H100 costs around $3/hour. If I walk away and leave this GPU running all weekend, that's hundreds of dollars wasted. In traditional AWS EC2, you have to remember to terminate instances via the AWS console."*
* **Action**:
  1. Go to the top-right hardware selector in Lightning Studio.
  2. Switch hardware to **Free CPU** (or click **Pause Studio**).
  3. Point to the file explorer on the left:  
     *"Look at `/teamspace/studios`—our Python scripts, `model_weights/`, `fine_tuned_weights/`, and logs are completely preserved on persistent cloud storage. But our GPU billing just dropped to exactly $0.00."*

* **Audience Punchline**:  
  *"This is true cloud elasticity: pay for the H100 only for the 69 seconds you need it, and develop your code on free compute."*

---

### Step 5: Transition to Harshit
* **What you say**:  
  *"We just saw the H100 obliterate consumer hardware in real time. But how do the economics stack up against AWS, Azure, and Google Cloud? Harshit, break down the numbers for us."*
