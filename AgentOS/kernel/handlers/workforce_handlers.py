"""
workforce_handlers.py — AgentOS Workforce Management
Handles hiring, delegation, and cross-tenant communication.
"""
import json
import logging
from datetime import datetime
from task_context import TaskContext
import db

logger = logging.getLogger("agentos.workforce_handlers")

async def handle_hire(task: TaskContext) -> dict:
    """Add a new member (Agent, Human, Robot) to the workforce."""
    entity_id = task.payload.get("entity_id")
    tier = task.payload.get("tier", "agentic")
    dept = task.payload.get("department", "general")
    tenant = task.tenant
    skills = task.payload.get("skills", [])

    if not entity_id:
        return {"status": "error", "message": "entity_id is required"}

    async with await db.get_db() as conn:
        await conn.execute("""
            INSERT INTO workforce (entity_id, tier, department, tenant, skills)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(entity_id) DO UPDATE SET
                tier = excluded.tier,
                department = excluded.department,
                skills = excluded.skills,
                last_active = datetime('now')
        """, (entity_id, tier, dept, tenant, json.dumps(skills)))
        await conn.commit()

    return {"status": "ok", "message": f"Hired {tier} entity: {entity_id} into {dept}"}

async def handle_delegate(task: TaskContext) -> dict:
    """Delegate a command to another tenant or workforce member."""
    target = task.payload.get("target")
    target_tenant = task.payload.get("target_tenant")
    command = task.payload.get("command")
    args = task.payload.get("args", {})

    if not target or not command:
        return {"status": "error", "message": "target and command are required"}

    async with await db.get_db() as conn:
        await conn.execute("""
            INSERT INTO commands (issuer, target, source_tenant, target_tenant, command, args)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (task.task_id, target, task.tenant, target_tenant or task.tenant, command, json.dumps(args)))
        await conn.commit()

    return {"status": "ok", "message": f"Delegated {command} to {target} in {target_tenant or task.tenant}"}

async def handle_message(task: TaskContext) -> dict:
    """Send a secure message to another agent or department."""
    to_agent = task.payload.get("to_agent")
    target_tenant = task.payload.get("target_tenant")
    topic = task.payload.get("topic", "General")
    body = task.payload.get("body", "")

    if not to_agent:
        return {"status": "error", "message": "to_agent is required"}

    async with await db.get_db() as conn:
        await conn.execute("""
            INSERT INTO messages (from_agent, to_agent, source_tenant, target_tenant, topic, body)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ("kernel", to_agent, task.tenant, target_tenant or task.tenant, topic, body))
        await conn.commit()

    return {"status": "ok", "message": f"Message sent to {to_agent} in {target_tenant or task.tenant}"}
