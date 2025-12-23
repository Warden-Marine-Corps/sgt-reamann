import json
from datetime import datetime
import  os
import aiomysql

from data.ticket_config import TicketConfig

DATA = "./data"
LOG_FILE = "logs/tickets.txt"
pool : aiomysql.Pool = None  # Will be set externally


def write_transcript(guild_id,filename,text):
    filename = os.path.join(DATA,str(guild_id),"transcripts",filename)
    with open(filename, "w", encoding="utf-8") as file:
            file.write(text)
    return filename

async def load_ticket_config(guild_id: int)-> TicketConfig:
    async with pool.acquire() as conn:
        conn : aiomysql.Connection
        async with conn.cursor() as cur:  
            cur : aiomysql.Cursor
            await cur.execute(
                """
                    SELECT * FROM TicketConfig
                    WHERE guild_id = %s
                """,(guild_id))
            rows : list= await cur.fetchall()
            if not rows: #no config found in DB
                return TicketConfig(0,0,0,0)
            config = TicketConfig(*rows[0][2:]) #tuple needs do be unpacked from [2:5] to remove guild_id
            return config #unique id -> es gibt nur ein config per guild
        

async def save_ticket_config(guild_id: int, config: TicketConfig) -> int:
    async with pool.acquire() as conn:      # Verbindung aus dem Pool holen #ab hier hat alles die selbe connection
        conn : aiomysql.Connection
        async with conn.cursor() as cur:    # Cursor öffnen 
            cur : aiomysql.Cursor

            #using INSERT/UPDATE Logic alterative: On Duplicate Key Update requires unique index on guild_id
            await cur.execute("SELECT ticket_config_id FROM TicketConfig WHERE guild_id = %s", (guild_id,)) 
            row = await cur.fetchone() 
            if row: 
                # UPDATE 
                await cur.execute(""" UPDATE TicketConfig SET support_role_id=%s, ticket_category_id=%s, closed_category_id=%s, log_channel_id=%s WHERE guild_id=%s """, 
                                  (config.support_role_id, config.ticket_category_id, config.closed_category_id, config.log_channel_id, guild_id))
            else: 
                # INSERT
                await cur.execute(
                    """
                    INSERT INTO TicketConfig (
                        guild_id, support_role_id, ticket_category_id, closed_category_id, log_channel_id
                    ) VALUES (%s, %s, %s, %s, %s)
                    """,
                    (guild_id, config.support_role_id, config.ticket_category_id, config.closed_category_id, config.log_channel_id))

            await conn.commit()  # Änderungen speichern

            #die neue erstellte ID holen
            config_id = cur.lastrowid
            # config.ticket_config_id = config_id
            return config_id

def log_ticket_event(guild_id, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    with open(os.path.join(DATA,str(guild_id),LOG_FILE), "a") as f:
        f.write(f"[{timestamp}] {message}\n")
