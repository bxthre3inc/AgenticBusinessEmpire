import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from AgenticBusinessEmpire.core.db import RQE
from AgenticBusinessEmpire.agents.workforce_registry import WORKFORCE_ROSTER

async def hydrate():
    print("🌌 Initializing AgentOS Database...")
    await RQE.init_db()
    
    print(f"👥 Hydrating Workforce with {len(WORKFORCE_ROSTER)} agents...")
    for agent in WORKFORCE_ROSTER:
        # Use the workforce_manager's logic or direct SQL
        # employee_id, company_id, department_id, employee_type, name, role, status
        await RQE.execute("""
            INSERT INTO workforce (employee_id, company_id, department_id, employee_type, name, role, status, metadata)
            VALUES ($1, $2, $3, $4, $5, $6, 'idle', $7)
            ON CONFLICT (employee_id) DO UPDATE SET 
                role=$8, 
                department_id=$9,
                metadata=$10
        """, 
        agent["id"], 
        "tenant_zero", 
        agent["department"], 
        "agentic", 
        agent["role"], 
        agent["role"],
        agent["persona"],
        agent["role"], # $8
        agent["department"], # $9
        agent["persona"], # $10
        fetch=False)
        print(f"  [+] Hydrated: {agent['role']} ({agent['id']})")

    print("\n✅ Workforce Hydration Complete.")

if __name__ == "__main__":
    asyncio.run(hydrate())
