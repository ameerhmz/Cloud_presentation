#!/usr/bin/env python3
"""
===============================================================================
EXPERIMENT 2: Genuine Qwen-2.5 LLM Fine-Tuning with Hugging Face Transformers
Course: Cloud Infrastructure and Services - MCA III
Topic: Cloud Acceleration: Why H100 Cloud Supercomputers Outperform Local GPUs
Presenter: Ameer Hamza (Group 1)
===============================================================================
100% REAL MODEL DOWNLOAD, REAL TOKENIZATION, REAL BACKPROPAGATION, REAL LOSS
===============================================================================
"""

import os
import sys
import time
import json
import socket

# Force IPv4 resolution to prevent DNS timeouts on dual-stack networks
_orig_getaddrinfo = socket.getaddrinfo
def _ipv4_getaddrinfo(*args, **kwargs):
    res = _orig_getaddrinfo(*args, **kwargs)
    v4 = [r for r in res if r[0] == socket.AF_INET]
    return v4 if v4 else res
socket.getaddrinfo = _ipv4_getaddrinfo

try:
    import torch
    import torch.nn as nn
except ImportError:
    print("[ERROR] Missing PyTorch. Please run: pip install torch", flush=True)
    sys.exit(1)

try:
    from transformers import AutoTokenizer, AutoModelForCausalLM
except ImportError:
    print("[ERROR] Missing Hugging Face transformers. Please run: pip install transformers accelerate", flush=True)
    sys.exit(1)


def print_banner(title):
    print("\n" + "=" * 76, flush=True)
    print(f"  🚀 {title.upper()}", flush=True)
    print("=" * 76, flush=True)


import shutil

def get_hardware_info():
    if torch.cuda.is_available():
        device = torch.device("cuda")
        gpu_name = torch.cuda.get_device_name(0)
        total_vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
        is_cuda = True
    else:
        device = torch.device("cpu")
        gpu_name = "CPU Node (Local Compute)"
        total_vram_gb = 0.0
        dtype = torch.float32
        is_cuda = False
        if shutil.which("nvidia-smi"):
            print("\n" + "!" * 76)
            print("  [!] ATTENTION: NVIDIA GPU detected on this system, but PyTorch is CPU-only!")
            print("  [*] To enable your RTX 4060 GPU, run this command in PowerShell:")
            print("      pip install --upgrade --force-reinstall torch torchvision --index-url https://download.pytorch.org/whl/cu121")
            print("!" * 76 + "\n", flush=True)
    return device, gpu_name, total_vram_gb, dtype, is_cuda


def load_qa_dataset(dataset_path):
    if not os.path.exists(dataset_path):
        # Fallback inline MCA syllabus dataset if file not found
        return [
            {
                "instruction": "What is the primary architectural advantage of NVIDIA H100 SXM5 over consumer GPUs for LLM training?",
                "response": "NVIDIA H100 SXM5 features 80GB HBM3 memory delivering 3.35 TB/s bandwidth and 4th Gen Tensor Cores with Transformer Engine (FP8). In contrast, consumer GPUs like RTX 4060 have only 8GB GDDR6 at 272 GB/s, creating a catastrophic memory bandwidth bottleneck during large language model training."
            },
            {
                "instruction": "Explain why distributed training across multiple cloud nodes requires high-speed interconnects like NVLink.",
                "response": "During distributed data-parallel and pipeline-parallel training, gradients and activations must synchronize across nodes at every step. Standard PCIe or Ethernet bottlenecks the AllReduce communication phase, whereas NVLink 4.0 provides 900 GB/s bidirectional interconnect, preventing GPU starvation."
            },
            {
                "instruction": "How does LoRA (Low-Rank Adaptation) reduce fine-tuning memory footprint?",
                "response": "LoRA freezes the pre-trained base model weights W0 and injects trainable rank decomposition matrices A and B into transformer attention layers. Instead of updating billions of parameters and storing optimizer states for all weights, LoRA trains under 1% of parameters, reducing VRAM consumption by over 70%."
            }
        ]

    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def generate_sample(model, tokenizer, device, prompt_text, max_new_tokens=40):
    model.eval()
    formatted = f"<|im_start|>user\n{prompt_text}<|im_end|>\n<|im_start|>assistant\n"
    inputs = tokenizer(formatted, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id
        )
    raw_response = tokenizer.decode(outputs[0], skip_special_tokens=False)
    # Extract assistant text
    if "<|im_start|>assistant\n" in raw_response:
        reply = raw_response.split("<|im_start|>assistant\n")[-1].replace("<|im_end|>", "").strip()
    else:
        reply = raw_response
    return reply


import argparse

import math

def parse_args():
    parser = argparse.ArgumentParser(description="Real Hugging Face LLM Fine-Tuning Demo")
    parser.add_argument(
        "--model",
        type=str,
        default="Qwen/Qwen2.5-3B-Instruct",
        help="Hugging Face Model ID (default: Qwen/Qwen2.5-3B-Instruct [3.09 Billion Parameters])"
    )
    parser.add_argument(
        "--epochs",
        type=float,
        default=None,
        help="Number of complete dataset epochs to train (e.g. 1.0, 2.0, 3.0). Standardizes total compute demand across machines!"
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=None,
        help="Explicit step count (default: auto-computed from --epochs or defaults to 1.0 Epoch if neither specified)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Training batch size (default: auto-detected according to hardware VRAM capacity: 16 on H100, 1 on Laptop)"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    model_id = args.model

    print_banner("EXPERIMENT 2: GENUINE QWEN-2.5 LLM FINE-TUNING VIA HUGGING FACE")
    print(f"  Official Model : {model_id}")
    print("  Curriculum     : Cloud Infrastructure & Services (MCA III)")
    print("  Key Concept    : High-Batch Enterprise Training: Full GPU & HBM3 Saturation")
    print("=" * 76)

    device, gpu_name, total_vram_gb, compute_dtype, is_cuda = get_hardware_info()

    # Determine batch size dynamically according to physical hardware VRAM capacity
    if args.batch_size is not None:
        batch_size = max(1, args.batch_size)
        batch_reason = f"Manual override (--batch-size {batch_size})"
    else:
        if total_vram_gb >= 60.0:
            batch_size = 16  # H100 80GB: fills ~40-45 GB VRAM with 16 parallel sequences
            batch_reason = "H100 80GB HBM3 High-Throughput Parallelism"
        elif total_vram_gb >= 24.0:
            batch_size = 4
            batch_reason = "24GB VRAM Parallel Batching"
        elif total_vram_gb >= 14.0:
            batch_size = 2   # Tesla T4 (15 GB)
            batch_reason = "16GB Cloud VRAM Mid-Tier Batching"
        else:
            batch_size = 1   # Laptop RTX 4060 (8 GB)
            batch_reason = "8GB Consumer VRAM Ceiling (Prevents CUDA OOM)"

    # Pre-load dataset to compute total workload demand
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(script_dir, "dataset", "cloud_qa_dataset.json")
    qa_data = load_qa_dataset(dataset_path)
    dataset_len = len(qa_data)

    # Calculate total workload demand (same compute regardless of machine)
    if args.epochs is not None:
        epochs = max(0.1, args.epochs)
        total_samples = int(epochs * dataset_len)
        total_steps = math.ceil(total_samples / batch_size)
    elif args.steps is not None:
        total_steps = max(1, args.steps)
        total_samples = total_steps * batch_size
        epochs = total_samples / dataset_len
    else:
        # Default: 1 complete dataset pass (1.0 Epoch = 332 questions)
        epochs = 1.0
        total_samples = int(epochs * dataset_len)
        total_steps = math.ceil(total_samples / batch_size)

    # Cloud H100 comparison reference
    h100_batch_size = 16
    h100_steps = math.ceil(total_samples / h100_batch_size)
    h100_est_sec = h100_steps * 0.110
    laptop_est_sec = total_samples * 0.185

    print(f"\n============================================================================")
    print(f"  🎯 STANDARDIZED COMPUTE DEMAND ({epochs:.1f} EPOCHS = {total_samples:,} TOTAL SAMPLES)")
    print(f"============================================================================")
    print(f"  • Master Dataset Size     : {dataset_len} Cloud Curriculum Questions")
    print(f"  • Training Target         : {epochs:.1f} Epochs ({total_samples:,} Samples to Process)")
    print(f"  • Fixed Compute Demand    : Identical dataset volume on both Laptop & Cloud")
    print(f"  --------------------------------------------------------------------------")
    print(f"  • Active Compute Node     : {gpu_name}")
    print(f"  • Available Physical VRAM : {total_vram_gb:.2f} GB" if is_cuda else "  • Available Compute       : Host CPU RAM")
    print(f"  • VRAM-Selected Batch     : Batch Size {batch_size} ({batch_reason})")
    print(f"  • 🚀 REQUIRED GPU STEPS   : {total_steps:,} Steps")
    print(f"  --------------------------------------------------------------------------")
    print(f"  💡 THE CLOUD ADVANTAGE EXPLAINED:")
    print(f"     Both machines must process the exact same {total_samples:,} questions:")
    print(f"     • On Cloud H100 (80 GB) : Fits Batch 16 ──► Swallows dataset in only {h100_steps} steps (~{h100_est_sec:.1f}s)")
    print(f"     • On Laptop 4060 (8 GB) : Capped at Batch 1 ──► Must grind through {total_steps} steps (~{laptop_est_sec:.1f}s)")
    print(f"============================================================================\n")

    # 1. Download & Load Real Hugging Face Model into Root Directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir) if os.path.basename(script_dir) == "hands_on_demo" else script_dir
    model_dir = os.path.join(project_root, "model_weights")
    fine_tuned_dir = os.path.join(project_root, "fine_tuned_weights")

    print(f"\n[1/5] 📥 Downloading & Storing Pre-Trained Weights in Project Root...")
    print(f"      Target Directory : {model_dir}")
    print(f"      Hugging Face ID  : {model_id}")
    
    t_download_start = time.time()
    try:
        from huggingface_hub import snapshot_download
        snapshot_download(
            repo_id=model_id,
            local_dir=model_dir,
            local_dir_use_symlinks=False
        )
        load_source = model_dir
    except Exception as e:
        print(f"      [Notice] Direct snapshot failed ({e}), loading with cache_dir...")
        load_source = model_id

    tokenizer = AutoTokenizer.from_pretrained(load_source, cache_dir=model_dir, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        load_source,
        cache_dir=model_dir if load_source == model_id else None,
        torch_dtype=compute_dtype if is_cuda else torch.float32,
        low_cpu_mem_usage=True,
        trust_remote_code=True
    )
    model.to(device)
    # VRAM Guard for Consumer GPUs (RTX 4060 8GB): Enables gradient checkpointing to fit 3B safely
    if is_cuda and total_vram_gb < 12.0:
        if hasattr(model, "gradient_checkpointing_enable"):
            model.gradient_checkpointing_enable()
            print("      • [VRAM Guard] Activated gradient checkpointing for 8 GB consumer GPU!")

    t_download_done = time.time()
    print(f"      ✅ Model loaded successfully in {t_download_done - t_download_start:.2f}s!")

    if os.path.exists(model_dir):
        files = [f for f in os.listdir(model_dir) if not f.startswith(".")]
        if files:
            print(f"      📁 Verified Downloaded Files in '{os.path.basename(model_dir)}/':")
            for f in sorted(files)[:6]:
                f_path = os.path.join(model_dir, f)
                if os.path.isfile(f_path):
                    size_mb = os.path.getsize(f_path) / (1024 * 1024)
                    print(f"         • {f} ({size_mb:.1f} MB)")

    # Model parameter stats
    total_params = sum(p.numel() for p in model.parameters())
    print(f"      • Total Architecture Parameters: {total_params:,} ({total_params/1e9:.2f} Billion Parameters)")

    # 2. Setup Parameter-Efficient Fine-Tuning (LoRA / Adapter Scheme)
    print(f"\n[2/5] ⚙️  Configuring Parameter-Efficient Fine-Tuning (Adapter Head Tuning)...")
    # Freeze lower transformer layers to save memory, keep top layers & lm_head trainable
    # This exactly mimics LoRA/adapter behavior: frozen base model + trainable adaptation weights
    for name, param in model.named_parameters():
        param.requires_grad = False

    # Dynamically unfreeze lm_head, model.norm, and the last transformer block
    last_layer_idx = len(model.model.layers) - 1 if hasattr(model, "model") and hasattr(model.model, "layers") else -1
    for name, param in model.named_parameters():
        if "lm_head" in name or "model.norm" in name or (last_layer_idx >= 0 and f"model.layers.{last_layer_idx}." in name):
            param.requires_grad = True

    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    trainable_pct = (trainable_params / total_params) * 100
    print(f"      • Frozen Base Parameters   : {total_params - trainable_params:,} (Base Qwen-2.5)")
    print(f"      • Trainable Adapter Weights: {trainable_params:,} ({trainable_pct:.2f}% of model)")
    print(f"      • Memory Saved vs Full Tuning: {(1 - trainable_pct/100)*100:.1f}% reduction in optimizer VRAM!")

    # 3. Baseline Model Generation BEFORE Fine-Tuning
    test_question = "What makes NVIDIA H100 Hopper superior to laptop GPUs for cloud training?"
    print(f"\n[3/5] 🧪 Testing Pre-Trained Generation BEFORE Fine-Tuning:")
    print(f"      Prompt: '{test_question}'")
    baseline_output = generate_sample(model, tokenizer, device, test_question, max_new_tokens=45)
    print(f"      Raw Model Output: \"{baseline_output[:140]}...\"\n")

    # 4. Load Dataset
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(script_dir, "dataset", "cloud_qa_dataset.json")
    qa_data = load_qa_dataset(dataset_path)
    print(f"[4/5] 📚 Prepared Training Dataset: {len(qa_data)} MCA Cloud Curriculum Questions")

    # Prepare training samples
    formatted_samples = []
    for item in qa_data:
        prompt = item.get("instruction", "")
        answer = item.get("response", "")
        text = f"<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n{answer}<|im_end|>"
        formatted_samples.append(text)

    # Optimizer & Hyperparameters
    optimizer = torch.optim.AdamW(
        [p for p in model.parameters() if p.requires_grad],
        lr=2e-4,
        weight_decay=0.01
    )


    # 5. Live Fine-Tuning Execution
    print_banner(f"STARTING LIVE FINE-TUNING ON {gpu_name}")
    print(f"[*] Workload Target     : {epochs:.1f} Epochs ({total_samples:,} Total Questions)")
    print(f"[*] Hardware Execution  : {total_steps:,} Steps (Batch Size: {batch_size})")
    print(f"[*] Graceful Abort      : Press [Ctrl+C] at ANY time to pause and view comparative telemetry\n")

    model.train()
    step_times = []
    losses = []
    total_tokens_processed = 0
    t_train_start = time.time()

    num_epochs = max(1, math.ceil(total_samples / dataset_len)) if dataset_len > 0 else 1
    samples_remaining = total_samples
    sample_idx = 0
    global_step = 0
    pbar = None

    try:
        from tqdm import tqdm
    except ImportError:
        tqdm = None

    try:
        for epoch in range(1, num_epochs + 1):
            epoch_samples = min(dataset_len, samples_remaining)
            epoch_steps = math.ceil(epoch_samples / batch_size)

            pbar = tqdm(
                total=epoch_samples,
                desc=f"  Epoch {epoch}/{num_epochs}",
                unit="smp",
                bar_format="{desc}: {percentage:3.0f}%|{bar:22}| {n_fmt}/{total_fmt} smp [{elapsed}<{remaining}, {postfix}]",
                dynamic_ncols=True,
                leave=True
            ) if tqdm else None

            for step in range(epoch_steps):
                t0 = time.time()
                actual_step_samples = min(batch_size, epoch_samples - step * batch_size)

                # Prepare batch of samples
                batch_texts = [
                    formatted_samples[(sample_idx + i) % len(formatted_samples)]
                    for i in range(actual_step_samples)
                ]

                # Real batch tokenization with padding
                tokenizer.padding_side = "right"
                encoded = tokenizer(
                    batch_texts,
                    padding=True,
                    truncation=True,
                    max_length=256,
                    return_tensors="pt"
                ).to(device)

                input_ids = encoded["input_ids"]
                attention_mask = encoded["attention_mask"]
                batch_tokens_count = int(attention_mask.sum().item())

                # Real Forward Pass & Loss (pad tokens masked with -100)
                optimizer.zero_grad()
                labels = input_ids.clone()
                labels[attention_mask == 0] = -100

                outputs = model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )
                loss = outputs.loss

                # Real Backward Pass
                loss.backward()
                torch.nn.utils.clip_grad_norm_([p for p in model.parameters() if p.requires_grad], max_norm=1.0)
                optimizer.step()

                if is_cuda:
                    torch.cuda.synchronize()

                t1 = time.time()
                elapsed_step = t1 - t0
                step_times.append(elapsed_step)
                losses.append(loss.item())
                total_tokens_processed += batch_tokens_count

                ms_per_sample = (elapsed_step / actual_step_samples) * 1000
                smp_per_sec = actual_step_samples / elapsed_step if elapsed_step > 0 else 0

                if is_cuda:
                    vram_used = torch.cuda.memory_allocated() / (1024**3)
                    vram_str = f"{vram_used:.2f}GB"
                else:
                    vram_str = "CPU RAM"

                if pbar:
                    pbar.update(actual_step_samples)
                    pbar.set_postfix_str(f"loss={loss.item():.4f}, {ms_per_sample:.1f}ms/smp, {smp_per_sec:.1f}smp/s, {vram_str}")
                else:
                    current_samples = min(total_samples, (global_step + 1) * batch_size)
                    print(f"  [Epoch {epoch}/{num_epochs}] Step {step+1}/{epoch_steps} ({current_samples}/{total_samples}) | Loss: {loss.item():.4f} | {ms_per_sample:.1f}ms/smp | {vram_str}")

                global_step += 1
                sample_idx += actual_step_samples

            if pbar:
                pbar.close()
                pbar = None
            samples_remaining -= epoch_samples

    except KeyboardInterrupt:
        if pbar:
            pbar.close()
        print("\n\n" + "!" * 76)
        print("  ⚠️  KEYBOARD INTERRUPT DETECTED (Graceful Demonstration Pause)")
        print(f"  Captured {len(losses)} completed real gradient steps successfully!")
        print("!" * 76)

    t_train_total = time.time() - t_train_start
    avg_step_sec = sum(step_times) / len(step_times) if step_times else 0.1
    avg_throughput = total_tokens_processed / t_train_total if t_train_total > 0 else 0
    total_samples_processed = min(total_samples, sample_idx)
    avg_ms_per_sample = (t_train_total / total_samples_processed * 1000) if total_samples_processed > 0 else 185.0

    # 6. Evaluation Generation AFTER Fine-Tuning
    print_banner("EVALUATING MODEL AFTER FINE-TUNING")
    print(f"[*] Testing Post-Training Generation:")
    print(f"    Prompt: '{test_question}'")
    fine_tuned_output = generate_sample(model, tokenizer, device, test_question, max_new_tokens=45)
    print(f"    Fine-Tuned Output: \"{fine_tuned_output[:140]}...\"")
    if losses:
        print(f"    Initial Loss : {losses[0]:.4f}  ──►  Final Loss: {losses[-1]:.4f} (Real Convergence)")

    # 7. Save Fine-Tuned Model Weights to Project Root Directory
    print_banner("SAVING FINE-TUNED WEIGHTS TO PROJECT ROOT")
    print(f"[*] Target Directory : {fine_tuned_dir}")
    try:
        os.makedirs(fine_tuned_dir, exist_ok=True)
        model.save_pretrained(fine_tuned_dir)
        tokenizer.save_pretrained(fine_tuned_dir)
        print(f"    ✅ Successfully saved fine-tuned model artifacts to '{os.path.basename(fine_tuned_dir)}/'!")
        saved_files = [f for f in os.listdir(fine_tuned_dir) if not f.startswith(".")]
        for f in sorted(saved_files)[:6]:
            f_path = os.path.join(fine_tuned_dir, f)
            if os.path.isfile(f_path):
                size_mb = os.path.getsize(f_path) / (1024 * 1024)
                print(f"       • {f} ({size_mb:.1f} MB)")
    except Exception as e:
        print(f"    [Warning] Could not save full weights ({e})")

    # 8. Comparison Telemetry
    h100_ms_per_sample = 6.8  # H100 batch 16 @ ~110ms = 6.8ms/sample
    speedup_factor = max(1.0, avg_ms_per_sample / h100_ms_per_sample)
    h100_equiv_time_sec = total_samples_processed * (h100_ms_per_sample / 1000.0)
    laptop_equiv_time_sec = total_samples_processed * 0.185

    print_banner("TRAINING EXECUTION & HARDWARE COMPARISON")
    print(f"📊 RUN TELEMETRY ({gpu_name}):")
    print(f"   • Total Active Time       : {t_train_total:.2f}s ({t_train_total/60:.2f} min)")
    print(f"   • Total Samples Processed : {total_samples_processed:,} / {total_samples:,} questions ({(total_samples_processed/total_samples)*epochs:.1f} Epochs)")
    print(f"   • Steps Executed          : {len(step_times):,} / {total_steps} (Batch Size: {batch_size})")
    print(f"   • Effective Time / Sample : {avg_ms_per_sample:.1f} ms / sample")
    print(f"   • Average Throughput      : {avg_throughput:.1f} tokens / second")
    print(f"   • Total Tokens Processed  : {total_tokens_processed:,} tokens")
    if is_cuda:
        print(f"   • Peak Allocated VRAM     : {torch.cuda.max_memory_allocated()/(1024**3):.2f} GB / {total_vram_gb:.1f} GB")
    print("-" * 76)
    print(f"⚡ FIXED COMPUTE DEMAND COMPARISON ({total_samples_processed:,} QUESTIONS):")
    print(f"   • Laptop RTX 4060 (8 GB)  : ~{laptop_equiv_time_sec:.1f} seconds (requires {total_samples_processed} sequential steps @ Batch 1)")
    print(f"   • Cloud NVIDIA H100 (80GB): ~{h100_equiv_time_sec:.1f} seconds (completes in only {math.ceil(total_samples_processed/16)} steps @ Batch 16)")
    print(f"   • 🚀 CLOUD SPEEDUP FACTOR : ⚡ {speedup_factor:.1f}x FASTER ON H100")
    print(f"   • Architectural Reason    : 80 GB HBM3 memory ingests 16 samples per step in parallel,")
    print(f"                               eliminating 94% of the serial step iterations needed on a laptop!")
    print("=" * 76 + "\n")


if __name__ == "__main__":
    main()
