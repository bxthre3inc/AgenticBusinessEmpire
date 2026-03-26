"""
ctc_engine.py — AgentOS Zero-Latency Mandate
Calculates Compute-Time-to-Completion (CTC) for agentic handoffs.
Formula: ETA = T_exec + T_wait
"""
import time
import random

from AgentOS.core.db import RQE

async def calculate_ctc(action: str, prompt_len: int, expected_output_tokens: int = 512) -> dict:
    """
    Predictive CTC calculation using historical metrics.
    Fallbacks to baseline if no history exists.
    """
    history = await RQE.get_performance_stats(action, limit=5)
    
    if history:
        # Calculate moving average
        avg_ms_per_token = sum(h["elapsed_ms"] / (h["output_tokens"] or 1) for h in history) / len(history)
        avg_wait_ms = sum(h["elapsed_ms"] - (h["output_tokens"] * avg_ms_per_token) for h in history) / len(history)
        
        t_exec = (expected_output_tokens * avg_ms_per_token) / 1000.0
        t_wait = max(0.2, avg_wait_ms / 1000.0)
    else:
        # Baseline: 45 tokens/sec, 1.2s latency
        t_exec = expected_output_tokens / 45.0
        t_wait = 1.2 + (prompt_len / 1000.0) * 0.5
    
    total_sec = t_exec + t_wait
    
    # Format to human readable
    if total_sec < 60:
        human_readable = f"{round(total_sec, 1)} seconds"
    elif total_sec < 3600:
        human_readable = f"{round(total_sec / 60.0, 1)} minutes"
    else:
        human_readable = f"{round(total_sec / 3600.0, 1)} hours"
        
    return {
        "t_exec": round(t_exec, 3),
        "t_wait": round(t_wait, 3),
        "total_sec": round(total_sec, 3),
        "eta_human": human_readable,
        "source": "live_metrics" if history else "baseline_projection"
    }

def inject_ctc_header(response: dict, prompt: str) -> dict:
    """Inject the CTC header into the response dict."""
    ctc = calculate_ctc(len(prompt))
    response["_ctc_eta"] = ctc["eta_human"]
    response["_compute_metrics"] = {
        "execution_volume": "T+ tokens",
        "wait_state": "Async Buffer",
        "cycle_count": "N Cycles"
    }
    return response
