"""
escalation_handlers.py — AgentOS Escalation & Dependency Management
Handles upstream/downstream task routing and blocker signaling.
"""
import db
import json
import logging

logger = logging.getLogger("agentos.escalation_handlers")

async def escalate_task(company_id: str, task_id: int, reason: str, target_role: str = "ceo_agent"):
    """Move a task upstream to a superior due to blockers or lack of authority."""
    async with await db.get_db() as conn:
        # 1. Update task status to 'escalated'
        await conn.execute("""
            UPDATE sync_events 
            SET status = 'escalated', payload = json_set(payload, '$.escalation_reason', ?)
            WHERE id = ? AND tenant = ?
        """, (reason, task_id, company_id))
        
        # 2. Generate a new "Oversight Needed" TCO for the superior
        await conn.execute("""
            INSERT INTO sync_events (event_type, source, department_id, payload, tenant, importance)
            VALUES ('oversight_request', 'escalation_engine', 'executive', ?, ?, 9)
        """, (json.dumps({
            "original_task_id": task_id,
            "reason": reason,
            "target_role": target_role
        }), company_id))
        
        await conn.commit()
        
    logger.info(f"Task {task_id} escalated to {target_role} in {company_id}: {reason}")
    return {"status": "ok", "message": "Task Escalated Successfully"}

async def resolve_blocker(company_id: str, blocker_task_id: int, resolution_tco_id: int):
    """Signal that a dependency has been met and resume dependent tasks."""
    async with await db.get_db() as conn:
        # Mark the blocker as resolved
        await conn.execute(
            "UPDATE sync_events SET status = 'completed' WHERE id = ? AND tenant = ?",
            (blocker_task_id, company_id)
        )
        
        # Resume dependent tasks (this would require a dependency table in a full impl)
        # For now, we log the resolution.
        await conn.commit()
        
    logger.info(f"Blocker {blocker_task_id} resolved in {company_id}")
    return {"status": "ok"}
