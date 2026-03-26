"""
workforce_manager.py — AgentOS Onboarding Utility
Simplifies hiring and assignment of employees across the conglomerate.
"""
import db
import json
import logging

logger = logging.getLogger("agentos.workforce_manager")

async def add_employee(company_id: str, dept_id: str, role: str, employee_type: str = "agentic", name: str = None):
    """Add a new employee to the workforce registry."""
    employee_id = f"{employee_type}_{role.lower()}_{name.lower().replace(' ', '_') if name else 'instance'}"
    
    async with await db.get_db() as conn:
        await conn.execute("""
            INSERT INTO workforce (employee_id, company_id, department_id, employee_type, name)
            VALUES (?, ?, ?, ?, ?)
        """, (employee_id, company_id, dept_id, employee_type, name or employee_id))
        
        await conn.commit()
        
    logger.info(f"Hired {employee_type} as {role} in {dept_id} for {company_id}")
    return {"status": "ok", "employee_id": employee_id}

async def list_roster(company_id: str):
    """Get the full roster for a specific company."""
    async with await db.get_db() as conn:
        cursor = await conn.execute(
            "SELECT * FROM workforce WHERE company_id = ?",
            (company_id,)
        )
        roster = await cursor.fetchall()
        return [dict(r) for r in roster]
