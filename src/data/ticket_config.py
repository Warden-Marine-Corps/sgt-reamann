
class TicketConfig:
    # ticket_config_id: int #DB PK
    # guild_id: int
    support_role_id: int
    ticket_category_id: int
    closed_category_id: int
    log_channel_id: int

    def __init__(self, support_role_id: int, ticket_category_id: int, closed_category_id: int, log_channel_id: int): #guild_id: int, 
        # self.guild_id = guild_id
        self.support_role_id = support_role_id
        self.ticket_category_id = ticket_category_id
        self.closed_category_id = closed_category_id
        self.log_channel_id = log_channel_id

