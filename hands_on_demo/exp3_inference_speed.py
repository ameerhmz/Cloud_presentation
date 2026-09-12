#!/usr/bin/env python3
"""
===============================================================================
EXPERIMENT 3: High-Throughput Cloud LLM Inference & Serving Benchmark
Course: Cloud Infrastructure and Services - MCA III
Topic: Serving AI at Scale: Why Cloud Supercomputers Dominate LLM Inference
Presenter: Ameer Hamza (Group 1 Lead)
===============================================================================
100% REAL AUTOREGRESSIVE GENERATION, STREAMING TTFT, AND BATCH CONCURRENCY
===============================================================================
"""

import os
import sys
import time
import socket
import argparse

# Force IPv4 to prevent DNS lookup hangs
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
    parser = argparse.ArgumentParser(description="Real LLM Inference Throughput Benchmark")
    parser.add_argument(
        "--model",
        type=str,
        default="Qwen/Qwen2.5-3B-Instruct",
        help="Model ID or local weights path (default: Qwen/Qwen2.5-3B-Instruct [3.09 Billion Parameters])"
    )
    parser.add_argument(
        "--max-new-tokens",
        type=int,
        default=60,
        help="Maximum tokens to generate per prompt (default: 60)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=4,
        help="Number of concurrent queries for batch throughput test (default: 4)"
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


def find_model_source(requested_model):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir) if os.path.basename(script_dir) == "hands_on_demo" else script_dir

    model_weights_dir = os.path.join(project_root, "model_weights")

    # Explicitly load only the downloaded base model from model_weights
    if os.path.exists(model_weights_dir) and (
        os.path.exists(os.path.join(model_weights_dir, "config.json")) or 
        any(f.endswith(".safetensors") for f in os.listdir(model_weights_dir) if not f.startswith("."))
    ):
        return model_weights_dir, f"Downloaded Base Model Weights ({model_weights_dir})"
    else:
        return requested_model, f"Hugging Face Hub ({requested_model})"



def main():
    args = parse_args()
    device, gpu_name, total_vram_gb, compute_dtype, is_cuda = get_hardware_info()

    print_banner("EXPERIMENT 3: HIGH-THROUGHPUT CLOUD LLM INFERENCE & SERVING")
    print(f"  Curriculum  : Cloud Infrastructure & Services (MCA III)", flush=True)
    print(f"  Core Focus  : Serving Latency, Time to First Token (TTFT), and Concurrent Batching", flush=True)
    print("=" * 76, flush=True)

    print(f"\n[*] Active Compute Node : {gpu_name}", flush=True)
    if is_cuda:
        print(f"[*] Available VRAM      : {total_vram_gb:.2f} GB", flush=True)
        print(f"[*] Compute Precision   : {compute_dtype}", flush=True)
    else:
        print("[*] Compute Precision   : Float32 (CPU Fallback)", flush=True)

    # 1. Load Model
    load_source, source_desc = find_model_source(args.model)
    print(f"\n[1/4] 📦 Loading Architecture & Parameters...", flush=True)
    print(f"      Source : {source_desc}", flush=True)
    print(f"      Path   : {load_source}", flush=True)

    t0_load = time.time()
    tokenizer = AutoTokenizer.from_pretrained(load_source, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        load_source,
        torch_dtype=compute_dtype if is_cuda else torch.float32,
        low_cpu_mem_usage=True,
        trust_remote_code=True
    )
    model.to(device)
    model.eval()
    t_load = time.time() - t0_load
    
    total_params = sum(p.numel() for p in model.parameters())
    print(f"      ✅ Model loaded ready for inference in {t_load:.2f}s ({total_params/1e9:.2f}B parameters)", flush=True)

    # 2. Test 1: Single-User Real-Time Streaming (Interactive Latency & TTFT)
    test_prompt = "Explain why large language model inference is memory-bandwidth bound rather than compute bound."
    formatted_prompt = f"<|im_start|>user\n{test_prompt}<|im_end|>\n<|im_start|>assistant\n"
    
    print_banner("TEST 1: SINGLE-USER REAL-TIME STREAMING (INTERACTIVE LATENCY)")
    print(f"[*] Prompt: \"{test_prompt}\"\n")
    print("-" * 76)
    print("🤖 MODEL RESPONSE STREAMING LIVE:")
    print("-" * 76)

    inputs = tokenizer(formatted_prompt, return_tensors="pt").to(device)
    streamer = TextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)

    if is_cuda:
        torch.cuda.synchronize()

    t_stream_start = time.time()
    with torch.no_grad():
        output_tokens = model.generate(
            **inputs,
            max_new_tokens=args.max_new_tokens,
            do_sample=False,
            streamer=streamer,
            pad_token_id=tokenizer.eos_token_id
        )

    if is_cuda:
        torch.cuda.synchronize()

    t_stream_end = time.time()
    total_stream_time = t_stream_end - t_stream_start
    gen_tokens_count = len(output_tokens[0]) - inputs["input_ids"].shape[1]
    stream_throughput = gen_tokens_count / total_stream_time if total_stream_time > 0 else 0

    print("-" * 76)
    print(f"[*] Tokens Generated    : {gen_tokens_count} tokens")
    print(f"[*] Total Stream Time   : {total_stream_time:.2f}s")
    print(f"[*] Stream Throughput   : ⚡ {stream_throughput:.1f} tokens/second")

    # 3. Test 2: Multi-User Concurrent Batch Inference (Throughput Scaling)
    batch_size = max(1, args.batch_size)
    print_banner(f"TEST 2: CONCURRENT BATCH INFERENCE ({batch_size} SIMULTANEOUS USERS)")
    print(f"[*] Simulating {batch_size} enterprise users requesting cloud answers concurrently:")

    batch_prompts = [
        "What are the benefits of NVIDIA HBM3 memory in cloud data centers?",
        "Why is NVLink 4.0 necessary for multi-GPU distributed deep learning?",
        "Compare cloud auto-scaling elasticity versus on-premises server infrastructure.",
        "How does FlashAttention-2 optimize memory IO during transformer inference?",
        "What is the role of the Hopper Transformer Engine in FP8 matrix calculation?",
        "How do cloud providers guarantee zero data loss during node migration?",
        "Explain the trade-off between model quantization and generation perplexity.",
        "What architectural advantages does H100 provide over consumer gaming GPUs?"
    ]
    selected_prompts = [batch_prompts[i % len(batch_prompts)] for i in range(batch_size)]
    for i, p in enumerate(selected_prompts, 1):
        print(f"    User #{i}: \"{p}\"")

    formatted_batch = [f"<|im_start|>user\n{p}<|im_end|>\n<|im_start|>assistant\n" for p in selected_prompts]
    tokenizer.padding_side = "left"
    batch_inputs = tokenizer(formatted_batch, padding=True, return_tensors="pt").to(device)

    if is_cuda:
        torch.cuda.synchronize()

    t_batch_start = time.time()
    with torch.no_grad():
        batch_outputs = model.generate(
            **batch_inputs,
            max_new_tokens=40,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id
        )

    if is_cuda:
        torch.cuda.synchronize()

    t_batch_end = time.time()
    total_batch_time = t_batch_end - t_batch_start
    total_batch_tokens = (batch_outputs.shape[1] - batch_inputs["input_ids"].shape[1]) * batch_size
    batch_throughput = total_batch_tokens / total_batch_time if total_batch_time > 0 else 0

    print(f"\n[*] Batch Execution Time: {total_batch_time:.2f}s")
    print(f"[*] Total Batch Tokens  : {total_batch_tokens} tokens")
    print(f"[*] Aggregate Throughput: ⚡ {batch_throughput:.1f} tokens/second")

    # 4. Final Inference Serving Summary
    print_banner("INFERENCE SERVING PERFORMANCE REPORT")
    print(f"📊 HARDWARE INFERENCE PROFILE ({gpu_name}):")
    print(f"   • Single-User Interactive Stream : {stream_throughput:.1f} tokens/sec")
    print(f"   • Multi-User Concurrent Batch    : {batch_throughput:.1f} tokens/sec ({batch_size} concurrent requests)")
    if is_cuda:
        vram_used = torch.cuda.max_memory_allocated() / (1024**3)
        print(f"   • Peak Inference VRAM            : {vram_used:.2f} GB")
    print(f"   -------------------------------------------------------------------------")
    print(f"   🎯 COMPUTER SCIENCE INSIGHT FOR FACULTY:")
    print(f"      • Autoregressive token generation must reload ALL model weights into cache")
    print(f"        for EVERY single generated token (Memory Wall).")
    print(f"      • On a laptop (272 GB/s GDDR6), throughput is throttled by memory bus width.")
    print(f"      • On Cloud H100 (3,350 GB/s HBM3), memory bandwidth is 12.3x higher, allowing")
    print(f"        data centers to serve hundreds of concurrent users with sub-second latency.")
    print("=" * 76 + "\n")


if __name__ == "__main__":
    main()
