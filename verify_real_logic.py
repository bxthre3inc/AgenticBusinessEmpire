import asyncio
import time
import logging
from AgentOS.core.db import RQE
from AgentOS.kernel import inference_node, ctc_engine
from AgentOS.logic import strategy

# Setup logging to see what's happening
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verify_real")

async def verify_real_logic():
    print("\n--- Phase 4: Real Logic Verification ---")
    
    # 1. Initialize DB
    await RQE.init_db()
    print("RQE Init: OK")

    # 2. Populate some performance data by running 'ping' tasks
    print("Populating performance metrics...")
    for i in range(3):
        await inference_node.process({
            "task_id": f"PERF-TEST-{i}",
            "tenant": "tenant_zero",
            "payload": {"action": "ping"}
        })
    
    # 3. Check CTC Engine for 'live_metrics' source
    print("Verifying CTC Engine source...")
    ctc = await ctc_engine.calculate_ctc("ping", 100)
    print(f"CTC Result: {ctc}")
    assert ctc["source"] == "live_metrics"
    print("CTC Live Tracking: OK")

    # 4. Test Autonomous Evaluation (Rating Engine)
    print("Verifying Autonomous Evaluation (Rating Engine)...")
    # This should trigger its own evaluate_seed task via inference_node
    idea_task = {
        "task_id": "IDEA-VERIFY-01",
        "tenant": "tenant_zero",
        "payload": {
            "action": "idea_intake",
            "title": "Quantum Modular Sharding for Foxxd S67",
            "description": "A deep refactor of the memory layer.",
            "pipeline_source": "CHAIRMAN"
        }
    }
    
    result = await inference_node.process(idea_task)
    print(f"Idea Intake Result: {result.get('status')}")
    audit = result.get("audit", {})
    print(f"Audit Overall: {audit.get('overall')}")
    print(f"Audit Metrics: {audit.get('metrics')}")
    
    assert audit.get("overall") > 0.5
    assert audit.get("metrics", {}).get("core_fit") is not None
    print("Autonomous Strategic Evaluation: OK")

    print("\n✅ PHASE 4 VERIFICATION SUCCESSFUL")

if __name__ == "__main__":
    asyncio.run(verify_real_logic())
