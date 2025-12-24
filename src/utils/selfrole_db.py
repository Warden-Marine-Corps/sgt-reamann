import os
import aiomysql

#utils/ datatypes
from data.selfroleblock import SelfRoleBlock

#logger
import logging
logger = logging.getLogger(__name__)

pool : aiomysql.Pool = None  # Will be set externally

async def load_role_config(guild_id: int) -> list[SelfRoleBlock]:
    async with pool.acquire() as conn:
        conn : aiomysql.Connection
        async with conn.cursor() as cur:  
            cur : aiomysql.Cursor
            await cur.execute(
                """
                    SELECT * FROM SelfRoleBlock
                    WHERE guild_id = %s
                """,(guild_id))
            rows : list = await cur.fetchall()
            if not rows: #no config found in DB
                logger.info(f"No SelfRoleBlock found for guild_id: {guild_id}") #this could be an error or just no config set yet
                return []

            selfroleblocks: list[SelfRoleBlock] = []
            for block in rows:
                self_role_block_id, message, guild_id = block
                roles = await load_roles_for_block(self_role_block_id)

                selfroleblock = SelfRoleBlock(self_role_block_id, message, guild_id, roles)
                selfroleblocks.append(selfroleblock)    
            return selfroleblocks
        
async def load_roles_for_block(self_role_block_id: int) -> list[dict]:
    async with pool.acquire() as conn:
        conn : aiomysql.Connection
        async with conn.cursor() as cur:  
            cur : aiomysql.Cursor
            await cur.execute(
                """
                    SELECT role_id, name, emoji FROM SelfRoleRole
                    WHERE self_role_block_id = %s
                """,(self_role_block_id))
            rows : list[tuple]= await cur.fetchall()
            roles: list[dict] = [{"role_id": row[0], "name": row[1], "emoji": str(row[2])} for row in rows] 
            return roles
        
async def save_new_role_config(guild_id: int, message: str, roles: list[dict]) -> int:
    async with pool.acquire() as conn:      # Verbindung aus dem Pool holen #ab hier hat alles die selbe connection
        conn : aiomysql.Connection
        async with conn.cursor() as cur:    # Cursor öffnen 
            cur : aiomysql.Cursor

            # INSERT SelfRoleBlock
            await cur.execute(
                """
                INSERT INTO SelfRoleBlock (
                    guild_id, message
                ) VALUES (%s, %s)
                """,
                (guild_id, message))

            self_role_block_id = cur.lastrowid

            # Insert new roles SelfRoleRole
            for role in roles:
                await cur.execute(
                    """
                    INSERT INTO SelfRoleRole (
                        self_role_block_id, role_id, name, emoji
                    ) VALUES (%s, %s, %s, %s)
                    """,
                    (self_role_block_id, role["role_id"], role["name"], str(role.get("emoji", None)))
                )

            await conn.commit()  # Änderungen speichern
            return self_role_block_id

async def save_role_config(self_role_block: SelfRoleBlock) -> None:
    async with pool.acquire() as conn: 
        conn : aiomysql.Connection
        async with conn.cursor() as cur:
            cur : aiomysql.Cursor

            # Update SelfRoleBlock message
            await cur.execute(
                """
                UPDATE SelfRoleBlock
                SET message = %s
                WHERE self_role_block_id = %s
                """,
                (self_role_block.message, self_role_block.self_role_block_id)
            )

            # Delete existing roles
            await cur.execute(
                """
                DELETE FROM SelfRoleRole
                WHERE self_role_block_id = %s
                """,
                (self_role_block.self_role_block_id,)
            )

            # Insert new roles
            for role in self_role_block.roles:
                await cur.execute(
                    """
                    INSERT INTO SelfRoleRole (
                        self_role_block_id, role_id, name, emoji
                    ) VALUES (%s, %s, %s, %s)
                    """,
                    (self_role_block.self_role_block_id, role["role_id"], role["name"], str(role.get("emoji", None)))
                )
            await conn.commit()  # Änderungen speichern

async def clear_role_config(guild_id: int) -> None:
    async with pool.acquire() as conn:
        conn : aiomysql.Connection
        async with conn.cursor() as cur:
            cur : aiomysql.Cursor

            # Get all self_role_block_ids to delete associated roles
            await cur.execute(
                """
                SELECT self_role_block_id FROM SelfRoleBlock
                WHERE guild_id = %s
                """,
                (guild_id,)
            )
            rows = await cur.fetchall()
            for row in rows:
                if row:
                    self_role_block_id = row[0]
                    # Delete associated roles
                    await cur.execute(
                        """
                        DELETE FROM SelfRoleRole
                        WHERE self_role_block_id = %s
                        """,
                        (self_role_block_id,)
                    )

                    # Delete SelfRoleBlock
                    await cur.execute(
                        """
                        DELETE FROM SelfRoleBlock
                        WHERE self_role_block_id = %s
                        """,
                        (self_role_block_id,)
                    )

                await conn.commit()  # Änderungen speichern