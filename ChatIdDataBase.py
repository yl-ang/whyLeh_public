import sqlite3

class ChatIdDataBase:

    def __init__(self, dbname="chatID.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False)

    def setup(self):
        tblstmt = "CREATE TABLE IF NOT EXISTS chatID_DB (module TEXT, chatID INTEGER, dailyPrompt TEXT)"
        moduleidx = "CREATE INDEX IF NOT EXISTS moduleidx ON chatID_DB (module ASC)"
        chatidx = "CREATE INDEX IF NOT EXISTS chatidx ON chatID_DB (chatID ASC)"
        dailyPromptidx = "CREATE INDEX IF NOT EXISTS dailyPromptidx ON chatID_DB (dailyPrompt ASC)"
        self.conn.execute(tblstmt)
        self.conn.execute(moduleidx)
        self.conn.execute(chatidx)
        self.conn.execute(dailyPromptidx)
        self.conn.commit()

    def add_chatID(self, module, chatID, dailyPrompt):
        stmt = "INSERT INTO chatID_DB (module, chatID, dailyPrompt) VALUES (?, ?, ?)"
        args = (module, chatID, dailyPrompt)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_chatID(self, module):
        stmt = "SELECT chatID FROM chatID_DB WHERE module= (?)"
        args = (module, )
        return [x for x in self.conn.execute(stmt, args)][0]

    def get_module(self, chatID):
        stmt = "SELECT module FROM chatID_DB WHERE chatID= (?)"
        args = (chatID, )
        return [x for x in self.conn.execute(stmt, args)][0]

    def check_chat_id(self, chatID):
        stmt = "SELECT module FROM chatID_DB WHERE chatID= (?)"
        args = (chatID, )
        lst = [x for x in self.conn.execute(stmt, args)]
        return len(lst) > 0

    def update_daily_prompt(self, chatID, dailyPromptUpdate):
        stmt = 'UPDATE chatID_DB SET dailyPrompt= (?) WHERE chatID= (?)'
        args = (dailyPromptUpdate, chatID)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_chatID_daily_prompt(self):
        stmt = "SELECT chatID FROM chatID_DB WHERE dailyPrompt= (?)"
        dailyPrompt = "True"
        args = (dailyPrompt, )
        return [x for x in self.conn.execute(stmt, args)]