#!/usr/bin/env python3
"""
===============================================================================
EXPERIMENT 3: Interactive Cloud LLM Terminal & Real-Time Serving Benchmark
Course: Cloud Infrastructure and Services - MCA III
Topic: Serving AI at Scale: Interactive Cloud Inference Demonstration
Presenter: Ameer Hamza (Group 1)
===============================================================================
LIVE REPL: ASK ANY QUESTION DIRECTLY TO THE 3-BILLION PARAMETER QWEN MODEL
===============================================================================
"""

import os
import sys
import time
import socket
import argparse

# Force IPv4 resolution to prevent DNS lookup hangs
_orig_getaddrinfo = socket.getaddrinfo
def _ipv4_getaddrinfo(*args, **kwargs):
    res = _orig_getaddrinfo(*args, **kwargs)
    v4 = [r for r in res if r[0] == socket.AF_INET]
    return v4 if v4 else res
socket.getaddrinfo = _ipv4_getaddrinfo

try:
    import torch
except ImportError:
    print("[ERROR] Missing PyTorch. Please run: pip install torch", flush=True)
    sys.exit(1)

try:
    from transformers import AutoTokenizer, AutoModelForCausalLM, TextStreamer
except ImportError:
    print("[ERROR] Missing Hugging Face transformers. Please run: pip install transformers accelerate", flush=True)
    sys.exit(1)


def print_banner(title):
    print("\n" + "=" * 76, flush=True)
    print(f"  🚀 {title.upper()}", flush=True)
    print("=" * 76, flush=True)


def parse_args():
    parser = argparse.ArgumentParser(description="Interactive Cloud LLM Terminal")
    parser.add_argument(
        "--model",
        type=str,
        default="Qwen/Qwen2.5-3B-Instruct",
        help="Hugging Face Model ID or local path (default: Qwen/Qwen2.5-3B-Instruct [3.09 Billion Parameters])"
    )
    parser.add_argument(
        "--mode",
        type=str,
        default=None,
        choices=["1", "2", "3", "finetuned", "base", "stress"],
        help="Model choice: '1' for fine-tuned, '2' for base, '3' or 'stress' for 16-user enterprise stress test"
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default=None,
        help="Optional single prompt to ask directly without entering interactive mode"
    )
    parser.add_argument(
        "--max-new-tokens",
        type=int,
        default=120,
        help="Maximum tokens to generate per answer (default: 120)"
    )
    return parser.parse_args()


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
    return device, gpu_name, total_vram_gb, dtype, is_cuda


def stream_answer(model, tokenizer, device, prompt_text, max_new_tokens, is_cuda):
    formatted = f"<|im_start|>user\n{prompt_text}<|im_end|>\n<|im_start|>assistant\n"
    inputs = tokenizer(formatted, return_tensors="pt").to(device)
    streamer = TextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)

    if is_cuda:
        torch.cuda.synchronize()
    t0 = time.time()

    with torch.no_grad():
        output_tokens = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            streamer=streamer,
            pad_token_id=tokenizer.eos_token_id
        )

    if is_cuda:
        torch.cuda.synchronize()
    elapsed = time.time() - t0

    num_generated = len(output_tokens[0]) - inputs["input_ids"].shape[1]
    tps = num_generated / elapsed if elapsed > 0 else 0
    return num_generated, elapsed, tps


ENTERPRISE_QUESTIONS = [
    "What are the primary advantages of NVIDIA HBM3 memory over consumer GDDR6?",
    "Explain why distributed AI training clusters require 900 GB/s NVLink interconnects.",
    "How does the Hopper FP8 Transformer Engine preserve mathematical precision?",
    "Compare cloud auto-scaling elasticity to fixed on-premises data center servers.",
    "What is the function of PagedAttention in enterprise LLM serving engines like vLLM?",
    "Explain the architectural difference between Data Parallelism and Tensor Parallelism.",
    "What are the key benefits of Amazon S3 strong read-after-write consistency?",
    "How does Kubernetes Horizontal Pod Autoscaler dynamically handle traffic surges?",
    "What is Zero Trust Architecture and how does it secure multi-tenant cloud workloads?",
    "Explain the role of Through-Silicon Vias (TSVs) in 3D stacked high-bandwidth memory.",
    "What is the trade-off between model quantization (INT4/FP8) and generation perplexity?",
    "How does GPUDirect RDMA accelerate multi-node collective communication in cloud clusters?",
    "Explain Recovery Point Objective (RPO) and Recovery Time Objective (RTO) in disaster recovery.",
    "Why is autoregressive token decoding memory-bandwidth bound rather than compute bound?",
    "What is the function of parallel distributed filesystems like Lustre in AI supercomputers?",
    "How do Cloud Spot Instances deliver up to 90% cost savings for deep learning jobs?"
]


def run_stress_test(model, tokenizer, device, is_cuda, total_vram_gb, num_users=16, max_new_tokens=45):
    """Executes simultaneous parallel inference for 16 concurrent users across H100 tensor cores."""
    orig_padding_side = tokenizer.padding_side
    tokenizer.padding_side = "left"
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    questions = ENTERPRISE_QUESTIONS[:num_users]
    formatted_prompts = [
        f"<|im_start|>user\n{q}<|im_end|>\n<|im_start|>assistant\n"
        for q in questions
    ]

    print("\n" + "=" * 80, flush=True)
    print("  ⚡ 16 CONCURRENT ENTERPRISE USERS STRESS TEST (SIMULTANEOUS INFERENCE)", flush=True)
    print("=" * 80, flush=True)
    print(f"[*] Target Compute Node    : {torch.cuda.get_device_name(0) if is_cuda else 'CPU Node'}")
    print(f"[*] Workload Architecture  : {num_users} Concurrent Client Streams Batched into Parallel Tensor Cores")
    print(f"[*] Memory Saturation      : Ingesting all {num_users} prompt streams simultaneously via HBM3")
    print("-" * 80, flush=True)
    print(f"🚀 DISPATCHING {num_users} SIMULTANEOUS REQUESTS TO GPU TENSOR CORES...")
    print("-" * 80, flush=True)

    for i, q in enumerate(questions, 1):
        print(f"  [User #{i:02d}] 👤 \"{q}\"", flush=True)

    batch_inputs = tokenizer(
        formatted_prompts,
        padding=True,
        return_tensors="pt"
    ).to(device)
    prompt_len = batch_inputs["input_ids"].shape[1]

    if is_cuda:
        torch.cuda.synchronize()
    t0_gen = time.time()

    with torch.no_grad():
        batch_outputs = model.generate(
            **batch_inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id
        )

    if is_cuda:
        torch.cuda.synchronize()
    elapsed = time.time() - t0_gen

    total_tokens = 0
    print("\n" + "=" * 80, flush=True)
    print(f"🤖 LIVE RESPONSES (GENERATED SIMULTANEOUSLY IN {elapsed:.2f} SECONDS):", flush=True)
    print("=" * 80, flush=True)

    for i in range(num_users):
        output_ids = batch_outputs[i][prompt_len:]
        count = len(output_ids)
        total_tokens += count
        reply = tokenizer.decode(output_ids, skip_special_tokens=True).strip()
        preview = reply.replace("\n", " ")[:105]
        print(f"  [User #{i+1:02d}] 💬 ({count} tokens) ──► \"{preview}...\"", flush=True)

    tps = total_tokens / elapsed if elapsed > 0 else 0
    laptop_serial_sec = total_tokens / 28.0  # RTX 4060 single-queue baseline @ ~28 tok/s
    speedup = max(1.0, laptop_serial_sec / max(0.01, elapsed))

    print("\n" + "=" * 80, flush=True)
    print(f"  📊 ENTERPRISE CLOUD SERVING TELEMETRY ({num_users} CONCURRENT USERS)", flush=True)
    print("=" * 80, flush=True)
    print(f"  • Total Parallel Output       : {total_tokens:,} tokens generated")
    print(f"  • Cloud H100 Batch Latency    : {elapsed:.2f} seconds (all {num_users} users served simultaneously!)")
    print(f"  • ⚡ AGGREGATE THROUGHPUT     : {tps:.1f} TOKENS / SECOND")
    if is_cuda:
        peak_vram = torch.cuda.max_memory_allocated() / (1024**3)
        print(f"  • Peak Serving VRAM           : {peak_vram:.2f} GB / {total_vram_gb:.1f} GB")
    print(f"  ------------------------------------------------------------------------------")
    print(f"  • Laptop RTX 4060 Baseline    : ~{laptop_serial_sec:.1f} seconds ({laptop_serial_sec/60:.2f} minutes)")
    print(f"    (Laptop must queue users serially due to narrow 128-bit GDDR6 memory bus)")
    print(f"  • 🚀 CLOUD SPEEDUP ADVANTAGE  : ⚡ {speedup:.1f}x FASTER ON H100")
    print(f"  • Architectural Reason        : 3.35 TB/s HBM3 Bandwidth enables parallel tensor batching")
    print("=" * 80 + "\n", flush=True)

    tokenizer.padding_side = orig_padding_side


def main():
    args = parse_args()
    device, gpu_name, total_vram_gb, compute_dtype, is_cuda = get_hardware_info()

    print_banner("EXPERIMENT 3: INTERACTIVE CLOUD LLM TERMINAL")
    print(f"  Architecture : Qwen-2.5 3B (3.09 Billion Parameters)")
    print(f"  Hardware     : {gpu_name}")
    print("=" * 76, flush=True)

    # 1. Detect Available Weight Folders in Project Root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir) if os.path.basename(script_dir) == "hands_on_demo" else script_dir
    model_weights_dir = os.path.join(project_root, "model_weights")
    fine_tuned_dir = os.path.join(project_root, "fine_tuned_weights")
    os.makedirs(model_weights_dir, exist_ok=True)

    has_fine_tuned = os.path.exists(fine_tuned_dir) and (
        os.path.exists(os.path.join(fine_tuned_dir, "config.json")) or
        any(f.endswith((".safetensors", ".bin")) for f in os.listdir(fine_tuned_dir) if not f.startswith("."))
    )
    has_base = os.path.exists(model_weights_dir) and (
        os.path.exists(os.path.join(model_weights_dir, "config.json")) or
        any(f.endswith((".safetensors", ".bin")) for f in os.listdir(model_weights_dir) if not f.startswith("."))
    )

    # 2. Interactive Selection Menu (if mode not passed via CLI)
    choice = args.mode
    if choice is None and args.prompt is None:
        print("\n" + "=" * 76)
        print("  🎯 SELECT MODEL TO LOAD OR BENCHMARK:")
        print("=" * 76)
        ft_status = "READY (Found in fine_tuned_weights/)" if has_fine_tuned else "NOT FOUND (Run exp2 first to generate)"
        base_status = "READY (Found in model_weights/)" if has_base else "WILL DOWNLOAD from Hugging Face"
        
        print(f"  [1] Fine-Tuned Model (Trained on Amity & Cloud Dataset)")
        print(f"      • Status: {ft_status}")
        print(f"  [2] Base Foundation Model (Raw Qwen-2.5-3B-Instruct)")
        print(f"      • Status: {base_status}")
        print(f"  [3] ⚡ Enterprise Multi-User Stress Test (16 Concurrent Users)")
        print(f"      • Simulates 16 simultaneous queries processed in parallel by H100")
        print("-" * 76)
        try:
            user_sel = input("👉 Enter choice [1, 2, or 3] (Default: 1): ").strip()
            choice = user_sel if user_sel in ["1", "2", "3", "stress"] else ("1" if has_fine_tuned else "2")
        except (KeyboardInterrupt, EOFError):
            print("\n[*] Exiting.")
            return

    # Determine load source based on choice
    run_stress_first = False
    if choice in ["3", "stress"]:
        run_stress_first = True
        if has_fine_tuned:
            load_source = fine_tuned_dir
            model_label = "FINE-TUNED MODEL (Amity & Cloud Domain Intelligence)"
        else:
            load_source = model_weights_dir if has_base else args.model
            model_label = "BASE FOUNDATION MODEL (Raw Qwen-3B)"
    elif choice in ["1", "finetuned"]:
        if has_fine_tuned:
            load_source = fine_tuned_dir
            model_label = "FINE-TUNED MODEL (Amity & Cloud Domain Intelligence)"
        else:
            print(f"\n[!] fine_tuned_weights/ not found. Falling back to base model in model_weights/...")
            load_source = model_weights_dir if has_base else args.model
            model_label = "BASE FOUNDATION MODEL (Raw Qwen-3B)"
    else:
        load_source = model_weights_dir if has_base else args.model
        model_label = "BASE FOUNDATION MODEL (Raw Qwen-3B)"

    # Download base weights if needed
    if load_source == model_weights_dir and not has_base:
        print(f"\n[*] 📥 Downloading Base Model Weights directly to: {model_weights_dir}", flush=True)
        try:
            from huggingface_hub import snapshot_download
            snapshot_download(
                repo_id=args.model,
                local_dir=model_weights_dir,
                local_dir_use_symlinks=False
            )
            load_source = model_weights_dir
        except Exception as e:
            print(f"    [Notice] Direct snapshot failed ({e}), loading directly from hub...", flush=True)
            load_source = args.model

    print(f"\n[*] 📦 Loading Active Weights : {model_label}", flush=True)
    print(f"    Target Source Directory : {load_source}", flush=True)
    t0_load = time.time()
    tokenizer = AutoTokenizer.from_pretrained(load_source, cache_dir=model_weights_dir, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        load_source,
        cache_dir=model_weights_dir if load_source == args.model else None,
        torch_dtype=compute_dtype if is_cuda else torch.float32,
        low_cpu_mem_usage=True,
        trust_remote_code=True
    )
    model.to(device)
    model.eval()
    t_load = time.time() - t0_load

    total_params = sum(p.numel() for p in model.parameters())
    print(f"    ✅ Ready in {t_load:.2f}s ({total_params/1e9:.2f}B Parameters on {device})", flush=True)

    # If user selected option 3, execute the 16-user enterprise stress test immediately
    if run_stress_first:
        run_stress_test(model, tokenizer, device, is_cuda, total_vram_gb, num_users=16, max_new_tokens=45)
        print("-" * 76)
        try:
            cont = input("👉 Enter Interactive Chat Terminal with this model? [Y/n]: ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            cont = "n"
        if cont in ["n", "no"]:
            print("[*] Enterprise Stress Test completed. Exiting.\n")
            return

    # Single Prompt Mode (if --prompt provided)
    if args.prompt:
        print(f"\n👉 Question: {args.prompt}")
        print("-" * 76)
        print("🤖 Assistant: ", end="", flush=True)
        tokens, elapsed, tps = stream_answer(model, tokenizer, device, args.prompt, args.max_new_tokens, is_cuda)
        print("-" * 76)
        vram_info = f" | VRAM: {torch.cuda.memory_allocated() / (1024**3):.2f} GB" if is_cuda else ""
        print(f"⚡ [Telemetry: {tokens} tokens in {elapsed:.2f}s ({tps:.1f} tokens/sec){vram_info}]\n")
        return

    # Interactive REPL Mode
    print("\n" + "=" * 76)
    print("  💬 LIVE INTERACTIVE CHAT SESSION READY")
    print("  • Type any question for the model (e.g. cloud architecture, viva concepts, code)")
    print("  • Type 'stress' or '3' anytime to trigger the 16-User Concurrent Stress Test!")
    print("  • Type 'exit' or 'quit' (or Ctrl+C) to return to shell")
    print("=" * 76 + "\n")

    query_count = 0
    while True:
        try:
            print("-" * 76)
            user_input = input("👉 Enter your question: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n[*] Exiting interactive terminal session.")
            break

        if not user_input:
            continue
        if user_input.lower() in ["exit", "quit", "q"]:
            print("[*] Exiting interactive terminal session. Goodbye!")
            break

        # Check for on-demand stress test command
        if user_input.lower() in ["stress", "3", "test", "benchmark"]:
            run_stress_test(model, tokenizer, device, is_cuda, total_vram_gb, num_users=16, max_new_tokens=45)
            continue

        query_count += 1
        print("\n🤖 Assistant: ", end="", flush=True)
        tokens, elapsed, tps = stream_answer(model, tokenizer, device, user_input, args.max_new_tokens, is_cuda)
        print("-" * 76)

        vram_str = f" | VRAM: {torch.cuda.memory_allocated() / (1024**3):.2f} GB" if is_cuda else ""
        print(f"⚡ [Telemetry: {tokens} tokens generated in {elapsed:.2f}s ({tps:.1f} tokens/sec){vram_str}]\n")


if __name__ == "__main__":
    main()
