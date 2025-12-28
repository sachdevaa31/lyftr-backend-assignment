import sqlite3
from typing import List, Optional, Tuple
from app.models import get_db_connection, utc_now_iso


def insert_message(
    message_id: str,
    from_msisdn: str,
    to_msisdn: str,
    ts: str,
    text: Optional[str]
) -> bool:
    """
    Returns:
        True  -> message inserted (new)
        False -> duplicate message_id
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO messages (
                message_id,
                from_msisdn,
                to_msisdn,
                ts,
                text,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                message_id,
                from_msisdn,
                to_msisdn,
                ts,
                text,
                utc_now_iso()
            )
        )
        conn.commit()
        return True

    except sqlite3.IntegrityError:
        # message_id already exists (idempotent behavior)
        return False

    finally:
        conn.close()


def list_messages(
    limit: int,
    offset: int,
    from_filter: Optional[str],
    since: Optional[str],
    q: Optional[str]
) -> Tuple[List[dict], int]:
    conn = get_db_connection()
    cursor = conn.cursor()

    filters = []
    params = []

    if from_filter:
        filters.append("from_msisdn = ?")
        params.append(from_filter)

    if since:
        filters.append("ts >= ?")
        params.append(since)

    if q:
        filters.append("LOWER(text) LIKE ?")
        params.append(f"%{q.lower()}%")

    where_clause = ""
    if filters:
        where_clause = "WHERE " + " AND ".join(filters)

    # total count (without limit/offset)
    count_query = f"""
        SELECT COUNT(*) as total
        FROM messages
        {where_clause}
    """
    cursor.execute(count_query, params)
    total = cursor.fetchone()["total"]

    # data query
    data_query = f"""
        SELECT message_id, from_msisdn, to_msisdn, ts, text
        FROM messages
        {where_clause}
        ORDER BY ts ASC, message_id ASC
        LIMIT ? OFFSET ?
    """
    cursor.execute(data_query, params + [limit, offset])
    rows = cursor.fetchall()

    data = [dict(row) for row in rows]

    conn.close()
    return data, total


def get_stats():
    conn = get_db_connection()
    cursor = conn.cursor()

    # total messages
    cursor.execute("SELECT COUNT(*) as total FROM messages")
    total_messages = cursor.fetchone()["total"]

    # senders count
    cursor.execute("SELECT COUNT(DISTINCT from_msisdn) as cnt FROM messages")
    senders_count = cursor.fetchone()["cnt"]

    # messages per sender (top 10)
    cursor.execute("""
        SELECT from_msisdn as sender, COUNT(*) as count
        FROM messages
        GROUP BY from_msisdn
        ORDER BY count DESC
        LIMIT 10
    """)
    messages_per_sender = [
        {"from": row["sender"], "count": row["count"]}
        for row in cursor.fetchall()
    ]

    # first and last message timestamps
    cursor.execute("SELECT MIN(ts) as first_ts, MAX(ts) as last_ts FROM messages")
    row = cursor.fetchone()

    conn.close()

    return {
        "total_messages": total_messages,
        "senders_count": senders_count,
        "messages_per_sender": messages_per_sender,
        "first_message_ts": row["first_ts"],
        "last_message_ts": row["last_ts"],
    }