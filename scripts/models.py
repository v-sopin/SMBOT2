class User:
    def __init__(self, tel_id, username, language, context, is_using, phone):
        self.tel_id = tel_id
        self.username = username
        self.language = language
        self.context = context
        self.is_using = is_using
        self.phone = phone


class Action:
    def __init__(self, type, date):
        self.type = type
        self.date = date
