
class SelfRoleBlock:
    self_role_block_id: int
    guild_id: int
    message: str
    roles: list[dict]

    def __init__(self, self_role_block_id: int, message: str, guild_id: int, roles: list[dict]):
        self.self_role_block_id = self_role_block_id
        self.guild_id = guild_id
        self.message = message
        self.roles = roles

rolebutton = {
    "role_id": int,
    "name": str,
    "emoji": str | int | None
}