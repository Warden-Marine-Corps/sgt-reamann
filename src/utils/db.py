import aiomysql
import datetime
import os
from typing import List, Tuple
from data.event import Event


#logger
import logging
logger = logging.getLogger(__name__)

async def init_db_pool():
    pool : aiomysql.Pool = await aiomysql.create_pool(
        host=os.getenv("DATABASE_HOST", "localhost"),
        port=int(os.getenv("DATABASE_PORT", 3306)),
        user=os.getenv("DATABASE_USER", "root"),
        password=os.getenv("DATABASE_PASSWORD", None),
        db=os.getenv("DATABASE_NAME", "db_reamann"),
        minsize=1,   # minimale Anzahl Verbindungen
        maxsize=10,   # maximale Anzahl Verbindungen
        autocommit=True
    )
    logger.info("Connected to {host} DB!")
    return pool

async def save_event(pool : aiomysql.Pool, event: Event) -> int:
    async with pool.acquire() as conn:      # Verbindung aus dem Pool holen #ab hier hat alles die selbe connection
        conn : aiomysql.Connection
        async with conn.cursor() as cur:    # Cursor öffnen 
            cur : aiomysql.Cursor
            await cur.execute(
                """
                INSERT INTO Event (
                    event_name, event_date, event_description, min_user_count, max_user_count,
                    event_picture, guild_id, channel_id, role_id, message_id, creator_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (event.event_name, event.event_datetime, event.event_description, event.min_user, event.max_user, event.event_image, event.guild_id, event.channel_id, event.role_id, event.message_id, event.creator_id))

            await conn.commit()             # Änderungen speichern

            #die neue erstellte ID holen
            event_id = cur.lastrowid
            event.event_id = event_id
            return event_id
        
async def get_event(pool : aiomysql.Pool, event_id: int)-> Event:
    async with pool.acquire() as conn:
        conn : aiomysql.Connection
        async with conn.cursor() as cur:  
            cur : aiomysql.Cursor
            await cur.execute(
                """
                    SELECT * FROM Event
                    WHERE event_id = %s
                """,(event_id))
            rows : list= await cur.fetchall()
            event = Event(*(rows[0]))
            return event #unique id -> es gibt nur ein event

async def get_all_events(pool: aiomysql.Pool, user_id: int, time: datetime) -> List[Event]:
    """get all the events a user is participant in"""
    async with pool.acquire() as conn:
        conn : aiomysql.Connection
        async with conn.cursor() as cur:  
            cur : aiomysql.Cursor
            await cur.execute(
                """
                    SELECT E.* 
                    FROM `Event` E
                    JOIN Participant P
                    ON E.event_id = P.event_id
                    WHERE P.user_id = %s
                    AND E.event_date >= %s
                """,(user_id, time))
            rows : list[tuple]= await cur.fetchall()
            events: List[Event] = [Event(*row) for row in rows] 
            return events

async def get_all_current_events(pool: aiomysql.Pool, time: datetime.datetime) -> List[Event]: 
    """get all of the current events"""
    async with pool.acquire() as conn:
        conn : aiomysql.Connection
        async with conn.cursor() as cur:  
            cur : aiomysql.Cursor
            await cur.execute(
                """
                    SELECT * 
                    FROM `Event` 
                    WHERE event_date >= %s
                """,(time))
            rows : list[tuple]= await cur.fetchall()
            events: List[Event] = [Event(*row) for row in rows] 
            return events

async def save_participant(pool : aiomysql.Pool, event_id: int, user_id: int, type: int = 0) -> int:
    async with pool.acquire() as conn:      # Verbindung aus dem Pool holen #ab hier hat alles die selbe connection
        conn : aiomysql.Connection
        async with conn.cursor() as cur:    # Cursor öffnen 
            cur : aiomysql.Cursor
            await cur.execute(
                """
                INSERT INTO Participant (event_id, user_id, participant_type) 
                VALUES (%s, %s, %s)
                """,
                (event_id, user_id, type))
            await conn.commit()  # Änderungen speichern
            
            participant_id = cur.lastrowid
            return participant_id

async def remove_participant(pool: aiomysql.Pool, event_id: int, user_id: int):
    async with pool.acquire() as conn:
        conn : aiomysql.Connection
        async with conn.cursor() as cur:
            cur : aiomysql.Cursor
            await cur.execute(
                """
                DELETE FROM Participant
                WHERE event_id = %s AND user_id = %s
                """,
                (event_id, user_id)
            )
            await conn.commit()
        
async def get_all_participants(pool: aiomysql.Pool, event_id: int) -> list[int]:
    """get all user_ids that are paticipating in a event"""
    async with pool.acquire() as conn:
        conn : aiomysql.Connection
        async with conn.cursor() as cur:  
            cur : aiomysql.Cursor
            await cur.execute(
                """
                    SELECT user_id FROM Participant
                    WHERE event_id = %s
                """,(event_id))
            rows : list[(int,)]= await cur.fetchall() #returns list an tupels
            user_ids: list[int] = [r[0] for r in rows]
            return user_ids
        
async def is_user_in_event(pool: aiomysql.Pool, user_id: int, event_id: int) -> bool:
    async with pool.acquire() as conn:
        conn : aiomysql.Connection
        async with conn.cursor() as cur:
            cur : aiomysql.Cursor
            await cur.execute(
                """
                SELECT 1
                FROM Participant
                WHERE user_id = %s AND event_id = %s
                LIMIT 1
                """,
                (user_id, event_id)
            )
            return await cur.fetchone() is not None
            
async def save_bot_command(pool: aiomysql.Pool, command_name : str, command_description: str):
    async with pool.acquire() as conn:
        conn : aiomysql.Connection
        async with conn.cursor() as cur:
            cur : aiomysql.Cursor
            await cur.execute(
                "INSERT INTO BotCommands (command_name, command_description) VALUES (%s, %s)", (command_name, command_description)
            )
            await conn.commit()

async def save_list_bot_commands(pool: aiomysql.Pool, commands: list[Tuple[str, str]]):
    async with pool.acquire() as conn:
        conn : aiomysql.Connection
        async with conn.cursor() as cur:
            cur : aiomysql.Cursor
            await cur.executemany(
                "INSERT INTO BotCommands (command_name, command_description) VALUES (%s, %s)", commands
            )
            await conn.commit()

async def reset_bot_commands(pool: aiomysql.Pool):
    async with pool.acquire() as conn:
        conn : aiomysql.Connection
        async with conn.cursor() as cur:
            cur : aiomysql.Cursor
            #await cur.execute("TRUNCATE TABLE BotCommands") #reset table with only BotCommands Table
            await cur.execute("DELETE FROM BotCommands")
            await cur.execute("ALTER TABLE BotCommands AUTO_INCREMENT = 1") #reset auto increment counter
            await conn.commit()