"""
workforce_manager.py — AgentOS Onboarding Utility
Simplifies hiring and assignment of employees across the conglomerate.
"""
from AgentOS.core.db import RQE as db
import json
import logging

logger = logging.getLogger("agentos.workforce_manager")

async def add_employee(company_id: str, dept_id: str, role: str, employee_type: str = "agentic", name: str = None):
    """Add a new employee to the workforce registry."""
    employee_id = f"{employee_type}_{role.lower()}_{name.lower().replace(' ', '_') if name else 'instance'}"
    
    await db.execute("""
        INSERT INTO workforce (employee_id, company_id, department_id, employee_type, name, role)
        VALUES ($1, $2, $3, $4, $5, $6)
    """, employee_id, company_id, dept_id, employee_type, name or employee_id, role, fetch=False)
        
    logger.info(f"Hired {employee_type} as {role} in {dept_id} for {company_id}")
    return {"status": "ok", "employee_id": employee_id}

async def list_roster(company_id: str):
    """Get the full roster for a specific company."""
    return await db.execute("SELECT * FROM workforce WHERE company_id = $1", company_id)
