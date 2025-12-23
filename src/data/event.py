import datetime

class Event:
    event_id: int | None
    event_name: str
    event_datetime: datetime.datetime
    event_description: str
    min_user: int
    max_user: int
    event_image: str
    guild_id: int
    channel_id: int
    role_id: int
    message_id: int
    creator_id: int
    
    def __init__(self, event_id: int | None, event_name: str, event_datetime: datetime.datetime, event_description: str, min_user: int, max_user: int, event_image: str, guild_id: int, channel_id: int, role_id: int, message_id: int, creator_id: int):
        self.event_id = event_id
        self.event_name = event_name
        self.event_datetime = event_datetime
        self.event_description = event_description
        self.min_user = min_user
        self.max_user = max_user
        self.event_image = event_image
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.role_id = role_id
        self.message_id = message_id
        self.creator_id = creator_id
    