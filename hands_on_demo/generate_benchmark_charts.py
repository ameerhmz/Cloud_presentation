#!/usr/bin/env python3
"""
===============================================================================
HARDWARE BENCHMARK VISUALIZATION GENERATOR
Course: CSIT805: Cloud Infrastructure and Services
Topic: RTX 3050 Mobile vs. RTX 4060 Mobile vs. Cloud NVIDIA H100 SXM5
Presenter: Ameer Hamza (Group 1)
===============================================================================
Generates publication-quality dark-mode comparative benchmark charts.
===============================================================================
"""

import os
import matplotlib.pyplot as plt
import numpy as np

def generate_hardware_comparison_chart(output_path):
    # Set dark aesthetic matching the presentation deck
    plt.style.use('dark_background')
    fig, axs = plt.subplots(2, 2, figsize=(16, 11), dpi=300)
    fig.patch.set_facecolor('#070b14')

    categories = ['RTX 3050 Mobile\n(4GB / 6GB)', 'RTX 4060 Mobile\n(8GB Laptop)', 'Cloud NVIDIA H100\n(80GB SXM5)']
    colors = ['#ff4b4b', '#f59e0b', '#00f2fe']

    # Custom helper for bar annotations
    def style_ax(ax, title, ylabel):
        ax.set_facecolor('#0d1424')
        ax.set_title(title, fontsize=14, fontweight='bold', color='#ffffff', pad=14)
        ax.set_ylabel(ylabel, fontsize=11, fontweight='semibold', color='#94a3b8')
        ax.tick_params(colors='#94a3b8', labelsize=10)
        ax.grid(axis='y', linestyle='--', alpha=0.2, color='#38bdf8')
        for spine in ax.spines.values():
            spine.set_color('#1e293b')
            spine.set_linewidth(1.2)

    # 1. Memory Bandwidth (GB/s)
    ax1 = axs[0, 0]
    bw_vals = [192, 272, 3350]
    bars1 = ax1.bar(categories, bw_vals, color=colors, width=0.55, edgecolor='#ffffff', linewidth=0.8)
    style_ax(ax1, "1. Memory Bandwidth (Physical Data Pipeline)", "Bandwidth (GB/s)")
    ax1.set_ylim(0, 3800)
    for bar, val in zip(bars1, bw_vals):
        y = bar.get_height()
        label = f"{val:,} GB/s"
        if val == 3350:
            label += "\n(12.3x vs 4060)"
        ax1.text(bar.get_x() + bar.get_width()/2, y + 90, label, ha='center', va='bottom', fontsize=10, fontweight='bold', color='#ffffff')

    # 2. Real Fine-Tuning Throughput (Samples / Sec)
    ax2 = axs[0, 1]
    ft_vals = [0.0, 5.4, 147.2]
    bars2 = ax2.bar(categories, ft_vals, color=colors, width=0.55, edgecolor='#ffffff', linewidth=0.8)
    style_ax(ax2, "2. Qwen-2.5 3B Fine-Tuning Throughput (MCA QA)", "Throughput (Samples / Sec)")
    ax2.set_ylim(0, 175)
    for bar, val in zip(bars2, ft_vals):
        y = bar.get_height()
        if val == 0:
            label = "CRASH\n(CUDA OOM)"
            ax2.text(bar.get_x() + bar.get_width()/2, 8, label, ha='center', va='bottom', fontsize=10, fontweight='bold', color='#ff4b4b')
        else:
            label = f"{val:.1f} smp/s"
            if val > 100:
                label += "\n(27.3x Speedup)"
            ax2.text(bar.get_x() + bar.get_width()/2, y + 4, label, ha='center', va='bottom', fontsize=10, fontweight='bold', color='#ffffff')

    # 3. 1 Epoch Training Latency (Seconds - Lower is Better)
    ax3 = axs[1, 0]
    time_vals = [0, 64.0, 2.3]  # 0 indicates crash/failed
    bars3 = ax3.bar(categories, time_vals, color=colors, width=0.55, edgecolor='#ffffff', linewidth=0.8)
    style_ax(ax3, "3. 1 Complete Epoch Completion Time (332 QA)", "Wall-Clock Time (Seconds - Lower is Better)")
    ax3.set_ylim(0, 80)
    for bar, val in zip(bars3, time_vals):
        y = bar.get_height()
        if val == 0:
            label = "OOM CRASH\n(Cannot Run)"
            ax3.text(bar.get_x() + bar.get_width()/2, 5, label, ha='center', va='bottom', fontsize=10, fontweight='bold', color='#ff4b4b')
        elif val > 10:
            ax3.text(bar.get_x() + bar.get_width()/2, y + 2, f"{val:.1f}s (01:04 min)\n(Batch 1 Sequential)", ha='center', va='bottom', fontsize=10, fontweight='bold', color='#f59e0b')
        else:
            ax3.text(bar.get_x() + bar.get_width()/2, y + 2, f"{val:.1f}s flat!\n(27.8x Faster)", ha='center', va='bottom', fontsize=10, fontweight='bold', color='#00ff87')

    # 4. 16-User Concurrent Enterprise Serving (Tokens / Sec)
    ax4 = axs[1, 1]
    serv_vals = [0.0, 75.2, 1480.5]
    bars4 = ax4.bar(categories, serv_vals, color=colors, width=0.55, edgecolor='#ffffff', linewidth=0.8)
    style_ax(ax4, "4. 16-User Concurrent Inference Throughput", "Aggregate Throughput (Tokens / Sec)")
    ax4.set_ylim(0, 1750)
    for bar, val in zip(bars4, serv_vals):
        y = bar.get_height()
        if val == 0:
            label = "CRASH\n(KV-Cache OOM)"
            ax4.text(bar.get_x() + bar.get_width()/2, 50, label, ha='center', va='bottom', fontsize=10, fontweight='bold', color='#ff4b4b')
        else:
            label = f"{val:,.1f} tok/s"
            if val > 1000:
                label += "\n(19.7x Concurrency)"
            ax4.text(bar.get_x() + bar.get_width()/2, y + 40, label, ha='center', va='bottom', fontsize=10, fontweight='bold', color='#ffffff')

    plt.suptitle("HARDWARE BENCHMARK MATRIX: ENTRY LAPTOP vs. MID LAPTOP vs. CLOUD H100\nCSIT805: Cloud Infrastructure & Services • Empirical Lab Results", 
                 fontsize=16, fontweight='bold', color='#38bdf8', y=0.98)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"✅ Generated hardware comparison chart: {output_path}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir) if os.path.basename(script_dir) == "hands_on_demo" else script_dir
    target_img = os.path.join(project_root, "presentation", "assets", "hardware_benchmark_matrix.png")
    generate_hardware_comparison_chart(target_img)
