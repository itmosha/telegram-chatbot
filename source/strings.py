def get_table_chat_name(message):
    id = message.chat.id
    return f'table_{-id}' if id < 0 else f'table{id}'
