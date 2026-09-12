#!/usr/bin/env python3
"""
===============================================================================
EXPERIMENT 1: The VRAM Capacity Wall & "CUDA Out of Memory" (OOM) Test
Course: Cloud Infrastructure and Services - MCA III
Topic: Leveraging NVIDIA H100 on Lightning AI for High-Performance Cloud Computing
Presenter: Ameer Hamza (Group 1 Lead)
===============================================================================
"""

import sys
import time

try:
    import torch
except ImportError:
    print("[ERROR] PyTorch is not installed. Please run: pip install torch")
    sys.exit(1)


def print_banner(title):
    print("\n" + "=" * 76)
    print(f"  🚀 {title.upper()}")
    print("=" * 76)


def main():
    print_banner("Experiment 1: VRAM Capacity Wall (Allocating 12.0 GB Tensor)")
    
    if not torch.cuda.is_available():
        print("[!] No CUDA GPU detected (running on CPU/macOS).")
        print("[*] To test on live GPU, run this inside a Lightning AI Studio with H100 or on an RTX 4060 laptop.")
        gpu_name = "CPU / Emulated Node"
        total_vram = 0.0
    else:
        gpu_name = torch.cuda.get_device_name(0)
        total_vram = round(torch.cuda.get_device_properties(0).total_memory / (1024 ** 3), 2)

    print(f"[*] Detected Compute Node : {gpu_name}")
    print(f"[*] Available Physical VRAM: {total_vram} GB")
    print(f"[*] Workload Test Goal    : Allocate a 12.0 GB Activation Matrix (Batch Size 64 for LLM)")
    print("-" * 76)
    
    time.sleep(1)

    if not torch.cuda.is_available():
        print("[INFO] Simulating allocation behavior for presentation:")
        print("  • On Laptop RTX 4060 (8 GB VRAM) : 💥 CRASH with 'CUDA out of memory' error.")
        print("  • On Cloud NVIDIA H100 (80 GB VRAM): ✔ SUCCESS! Uses 12 GB, leaving 68 GB free.")
        print("=" * 76 + "\n")
        return

    # 12 GB tensor in FP32 (4 bytes per element)
    # Total elements = 12 * 1024^3 / 4 = 3,221,225,472
    target_elements = int(12 * (1024 ** 3) / 4)
    rows = 16384
    cols = target_elements // rows

    print(f"[*] Attempting torch.empty(({rows}, {cols}), dtype=torch.float32, device='cuda')...\n")

    try:
        start_time = time.time()
        # Allocate and physically touch memory pages so the hardware graph reflects full 12 GB
        tensor = torch.zeros((rows, cols), dtype=torch.float32, device="cuda")
        torch.cuda.synchronize()
        alloc_time = time.time() - start_time
        allocated = torch.cuda.memory_allocated(0) / (1024 ** 3)
        free_vram = total_vram - allocated

        print(f"[✔] SUCCESS! Allocated {allocated:.2f} GB in {alloc_time*1000:.2f} ms on {gpu_name}!")
        print(f"[✔] Headroom Remaining: {free_vram:.2f} GB FREE for model weights, KV cache, and optimizer!")
        print(f"\n[*] 📊 Holding 12.0 GB in VRAM for 10 seconds to update Studio UI graph...")
        for remaining in range(10, 0, -1):
            print(f"    ⏳ Active in HBM3 VRAM... {remaining}s remaining (check the top-bar RAM/GPU graph!)", end="\r", flush=True)
            time.sleep(1)
        print("    ✔ 10s hold complete! Releasing memory back to system pool.                  ")

        print("\n" + "-" * 76)
        print("  +-------------------------------------------------------------------+")
        print("  |                  EXPERIMENT 1 RESULT: PASSED                     |")
        print("  +-----------------------------------+-------------------------------+ ")
        print("  | Laptop RTX 4060 (8 GB Ceiling)    | 💥 CRASH: CUDA Out Of Memory  |")
        print(f"  | Cloud NVIDIA H100 (80 GB Ceiling) | ✔ SUCCESS ({free_vram:.1f} GB Headroom) |")
        print("  +-----------------------------------+-------------------------------+ ")
        print("-" * 76)
        
        del tensor
        torch.cuda.empty_cache()

    except torch.cuda.OutOfMemoryError:
        print("[💥] BOOM! Caught Expected CUDA OutOfMemoryError:")
        print(f"     >>> RuntimeError: CUDA out of memory. Tried to allocate 12.00 GiB")
        print(f"     >>> GPU 0 has only {total_vram} GiB total physical capacity!")
        print("\n" + "-" * 76)
        print("  [AUDIENCE & FACULTY TAKEAWAY]:")
        print("  • A student's consumer GPU hits a hard hardware ceiling at 8 GB.")
        print("  • Modern LLMs (Llama-3, Mistral) require 12-24 GB minimum just for activations.")
        print("  • On a laptop, the project crashes immediately. On Cloud H100, it uses <15% VRAM.")
        print("=" * 76 + "\n")


if __name__ == "__main__":
    main()
