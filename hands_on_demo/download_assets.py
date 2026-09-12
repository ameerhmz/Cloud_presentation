#!/usr/bin/env python3
"""
===============================================================================
Automated Model Asset Pre-Downloader (100% Offline Preparation)
Course: Cloud Infrastructure and Services - MCA III
Topic: Leveraging NVIDIA H100 on Lightning AI for High-Performance Cloud Computing
Presenter: Ameer Hamza (Group 1 Lead)
===============================================================================
"""

import argparse
import os
import sys
import socket

# Force IPv4 to prevent hanging on macOS broken IPv6 routes
_orig_getaddrinfo = socket.getaddrinfo
def _ipv4_getaddrinfo(*args, **kwargs):
    responses = _orig_getaddrinfo(*args, **kwargs)
    ipv4_res = [r for r in responses if r[0] == socket.AF_INET]
    return ipv4_res if ipv4_res else responses
socket.getaddrinfo = _ipv4_getaddrinfo

try:
    from huggingface_hub import snapshot_download
except ImportError:
    print("[ERROR] huggingface_hub not found. Run: pip install huggingface_hub", flush=True)
    sys.exit(1)


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_REGISTRY = {
    "qwen3b-int4": {
        "repo": "Qwen/Qwen2.5-3B-Instruct-GPTQ-Int4",
        "dir": os.path.join(SCRIPT_DIR, "qwen_model"),
        "name": "Qwen-2.5 3B Instruct Pre-Quantized (GPTQ-Int4, 1.93 GB - Official Alibaba Cloud)"
    },
    "qwen1.5b-int4": {
        "repo": "Qwen/Qwen2.5-1.5B-Instruct-GPTQ-Int4",
        "dir": os.path.join(SCRIPT_DIR, "qwen_model_1.5b"),
        "name": "Qwen-2.5 1.5B Instruct Pre-Quantized (GPTQ-Int4, 1.07 GB)"
    },
    "qwen3b-fp16": {
        "repo": "Qwen/Qwen2.5-3B-Instruct",
        "dir": os.path.join(SCRIPT_DIR, "model_cache", "qwen2.5-3b"),
        "name": "Qwen-2.5 3B Instruct Full FP16 (5.75 GB)"
    }
}


def main():
    parser = argparse.ArgumentParser(description="Pre-download LLM assets for offline presentation")
    parser.add_argument(
        "--model",
        choices=["qwen3b-int4", "qwen1.5b-int4", "qwen3b-fp16"],
        default="qwen3b-int4",
        help="Select model to download (default: qwen3b-int4, 1.93 GB pre-quantized)"
    )
    args = parser.parse_args()
    selected = MODEL_REGISTRY[args.model]

    print("=" * 76, flush=True)
    print(f"  🚀 AUTOMATED PRE-DOWNLOAD: {selected['name'].upper()}", flush=True)
    print("=" * 76, flush=True)
    print(f"[*] Hugging Face Repo : {selected['repo']}", flush=True)
    print(f"[*] Target Directory  : {selected['dir']}", flush=True)
    print("[*] Purpose           : Pre-cache weights & tokenizer for 100% OFFLINE live demo!", flush=True)
    print("-" * 76, flush=True)

    os.makedirs(selected["dir"], exist_ok=True)

    print("[*] Starting multi-threaded download via huggingface_hub (IPv4 Accelerated)...", flush=True)
    print("[*] Downloading weights, tokenizer, config files with automatic resume support...\n", flush=True)

    try:
        download_path = snapshot_download(
            repo_id=selected["repo"],
            local_dir=selected["dir"],
            ignore_patterns=["*.msgpack", "*.h5", "*.ot", "*.bin"],  # Download safetensors only
            max_workers=4
        )
        print("\n" + "=" * 76, flush=True)
        print(f"  🎉 ALL ASSETS DOWNLOADED SUCCESSFULLY FOR {selected['repo']}!", flush=True)
        print(f"  Saved locally in: {download_path}", flush=True)
        print("  You can now run 'python3 exp2_real_llm_finetune.py' with zero internet!", flush=True)
        print("=" * 76 + "\n", flush=True)
    except Exception as e:
        print(f"\n[!] Download error: {e}", flush=True)
        print("[!] You can re-run this script anytime; it will resume from where it left off.", flush=True)


if __name__ == "__main__":
    main()

