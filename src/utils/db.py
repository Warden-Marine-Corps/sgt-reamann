import aiomysql
import os
from typing import List, Tuple


#logger
import logging
logger = logging.getLogger(__name__)

async def init_db_pool():
    host=os.getenv("DATABASE_HOST", "localhost")
    pool : aiomysql.Pool = await aiomysql.create_pool(
        host=host,
        port=int(os.getenv("DATABASE_PORT", 3306)),
        user=os.getenv("DATABASE_USER", "root"),
        password=os.getenv("DATABASE_PASSWORD", None),
        db=os.getenv("DATABASE_NAME", "db_reamann"),
        minsize=1,   # minimale Anzahl Verbindungen
        maxsize=10,   # maximale Anzahl Verbindungen
        autocommit=True
    )
    logger.info(f"Connected to {host} DB!")
    return pool

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