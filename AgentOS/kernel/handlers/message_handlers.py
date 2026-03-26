"""
message_handlers.py — Bxthre3 Corporate Messenger Backend
Handles secure, hierarchical communication across the workforce.
"""
import db
import logging

logger = logging.getLogger("agentos.message_handlers")

async def send_message(company_id: str, sender_id: str, receiver_id: str, content: str):
    """Send a message to a specific employee or department head."""
    async with await db.get_db() as conn:
        await conn.execute("""
            INSERT INTO messages (company_id, sender_id, receiver_id, content)
            VALUES (?, ?, ?, ?)
        """, (company_id, sender_id, receiver_id, content))
        await conn.commit()
    
    logger.info(f"Message from {sender_id} to {receiver_id} logged in {company_id}")
    return {"status": "ok"}

async def get_messages_for_employee(company_id: str, employee_id: str):
    """Retrieve messages received by a specific employee."""
    async with await db.get_db() as conn:
        cursor = await conn.execute("""
            SELECT * FROM messages 
            WHERE company_id = ? AND (receiver_id = ? OR receiver_id = 'all')
            ORDER BY created_at DESC
        """, (company_id, employee_id))
        messages = await cursor.fetchall()
        return [dict(m) for m in messages]

async def get_departmental_chatter(company_id: str, dept_id: str):
    """Hierarchy View: Allows department heads to see chatter within their department."""
    # Logic note: This requires the workforce table to be joined to check roles
    async with await db.get_db() as conn:
        cursor = await conn.execute("""
            SELECT m.* FROM messages m
            JOIN workforce w ON m.sender_id = w.employee_id
            WHERE m.company_id = ? AND w.department_id = ?
            ORDER BY m.created_at DESC
        """, (company_id, dept_id))
        messages = await cursor.fetchall()
        return [dict(m) for m in messages]
