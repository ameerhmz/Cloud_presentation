#!/usr/bin/env python3
"""
===============================================================================
EXPERIMENT 3: Interactive Cloud LLM Terminal & Real-Time Serving Benchmark
Course: Cloud Infrastructure and Services - MCA III
Topic: Serving AI at Scale: Interactive Cloud Inference Demonstration
Presenter: Ameer Hamza (Group 1 Lead)
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


def find_model_source(requested_model):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir) if os.path.basename(script_dir) == "hands_on_demo" else script_dir

    model_weights_dir = os.path.join(project_root, "model_weights")

    # Load from downloaded model_weights directory in root
    if os.path.exists(model_weights_dir) and (
        os.path.exists(os.path.join(model_weights_dir, "config.json")) or 
        any(f.endswith(".safetensors") for f in os.listdir(model_weights_dir) if not f.startswith("."))
    ):
        return model_weights_dir, f"Downloaded Base Weights ({os.path.basename(model_weights_dir)}/)"
    else:
        return requested_model, f"Hugging Face Hub ({requested_model})"


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


def main():
    args = parse_args()
    device, gpu_name, total_vram_gb, compute_dtype, is_cuda = get_hardware_info()

    print_banner("EXPERIMENT 3: INTERACTIVE CLOUD LLM TERMINAL (QWEN-2.5 3B)")
    print(f"  Model Scale : 3.09 Billion Parameters")
    print(f"  Hardware    : {gpu_name}")
    print("=" * 76, flush=True)

    # 1. Load Model
    load_source, source_desc = find_model_source(args.model)
    print(f"\n[*] 📦 Loading Model from: {source_desc}", flush=True)
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
    print(f"    ✅ Ready in {t_load:.2f}s ({total_params/1e9:.2f}B Parameters on {device})", flush=True)

    # 2. Single Prompt Mode (if --prompt provided)
    if args.prompt:
        print(f"\n👉 Question: {args.prompt}")
        print("-" * 76)
        print("🤖 Assistant: ", end="", flush=True)
        tokens, elapsed, tps = stream_answer(model, tokenizer, device, args.prompt, args.max_new_tokens, is_cuda)
        print("-" * 76)
        vram_info = f" | VRAM: {torch.cuda.memory_allocated() / (1024**3):.2f} GB" if is_cuda else ""
        print(f"⚡ [Telemetry: {tokens} tokens in {elapsed:.2f}s ({tps:.1f} tokens/sec){vram_info}]\n")
        return

    # 3. Interactive REPL Mode
    print("\n" + "=" * 76)
    print("  💬 LIVE INTERACTIVE CHAT SESSION READY")
    print("  • Type any question for the model (e.g. cloud architecture, viva concepts, code)")
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

        query_count += 1
        print("\n🤖 Assistant: ", end="", flush=True)
        tokens, elapsed, tps = stream_answer(model, tokenizer, device, user_input, args.max_new_tokens, is_cuda)
        print("-" * 76)

        vram_str = f" | VRAM: {torch.cuda.memory_allocated() / (1024**3):.2f} GB" if is_cuda else ""
        print(f"⚡ [Telemetry: {tokens} tokens generated in {elapsed:.2f}s ({tps:.1f} tokens/sec){vram_str}]\n")


if __name__ == "__main__":
    main()
