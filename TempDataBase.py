
'''
When we are about to transfer the questions into the firebase storage as a text file, we will call 
the export method which will convert all the questions within the tempdb into json data structure.

This will make use of polymorphism to convert each individual question into its json representation.
'''
import sqlite3

class TempDB:

    def __init__(self, dbname="whyleh.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False)

    def setup(self):
        tblstmt = "CREATE TABLE IF NOT EXISTS items (qn_id INTEGER, module TEXT, grp_id INTEGER, message_id INTEGER, qn TEXT, author TEXT, answered TEXT, reply TEXT, individuals TEXT, time INTEGER)"

        qnIdidx = "CREATE INDEX IF NOT EXISTS qnIdidx ON items (qn_id ASC)"
        moduleidx = "CREATE INDEX IF NOT EXISTS moduleidx ON items (module ASC)"
        grpidx = "CREATE INDEX IF NOT EXISTS grpidx ON items (grp_id ASC)" 
        messgidx = "CREATE INDEX IF NOT EXISTS messgidx ON items (message_id ASC)" 
        qnidx = "CREATE INDEX IF NOT EXISTS qnidx ON items (qn ASC)"
        authoridx = "CREATE INDEX IF NOT EXISTS authoridx ON items (author ASC)"
        answeredidx = "CREATE INDEX IF NOT EXISTS answeredidx ON items (answered ASC)"
        individx = "CREATE INDEX IF NOT EXISTS individx ON items (individuals ASC)"
        timeidx = "CREATE INDEX IF NOT EXISTS timeidx ON items (time ASC)"
        
        self.conn.execute(tblstmt)
        self.conn.execute(qnIdidx)
        self.conn.execute(moduleidx)
        self.conn.execute(grpidx)
        self.conn.execute(messgidx)
        self.conn.execute(qnidx)
        self.conn.execute(authoridx)
        self.conn.execute(answeredidx)
        self.conn.execute(individx)
        self.conn.execute(timeidx)
        self.conn.commit()

    def add_question(self, qn_id, module, grp_id, message_id, qn, author, answered, reply, individuals, time):
        stmt = "INSERT INTO items (qn_id, module, grp_id, message_id, qn, author, answered, reply, individuals, time) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        args = (qn_id, module, grp_id, message_id, qn, author, answered, reply, individuals, time)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def qn_id_exist(self, qn_id):
        stmt = "SELECT 1 FROM items WHERE qn_id = (?)"
        args = (qn_id,)
        result = [x for x in self.conn.execute(stmt, args)][0][0]
        return result 

    def get_qn_id(self):
        stmt = "SELECT qn_id FROM items ORDER BY qn_id DESC LIMIT 1"
        args = ()
        return [x for x in self.conn.execute(stmt, args)]

    def get_questions(self, module):
        stmt = "SELECT qn_id,qn FROM items WHERE module= (?) ORDER BY qn_id DESC LIMIT 5"
        args = (module, )
        return [x for x in self.conn.execute(stmt, args)]
        # return self.conn.execute(stmt, args)

    def get_question_from_id(self, qn_id):
        stmt = "SELECT qn FROM items WHERE qn_id= (?)"
        args = (qn_id, )
        return [x for x in self.conn.execute(stmt, args)]

    def get_module(self, qn_id):
        stmt = "SELECT module FROM items WHERE qn_id= (?)"
        args = (qn_id, )
        return [x for x in self.conn.execute(stmt, args)]

    def update_reply(self, qn_id, reply):
        old_reply = self.get_reply(qn_id)
        stmt = 'UPDATE items SET reply= (?) WHERE qn_id= (?)'

        args = (old_reply + reply, qn_id)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def update_notification(self, qn_id, idv_id, action):
        stmt = "SELECT individuals FROM items WHERE qn_id= (?)"
        args = (qn_id, )
        #print([x for x in self.conn.execute(stmt, args)])
        unsorted_id = [x for x in self.conn.execute(stmt, args)]
        
        ids = unsorted_id[0][0]
        idv_id = str(idv_id)
        list_id = list(ids.split(" "))

        if idv_id in ids:
            if action == 'remove':
                list_id.remove(idv_id)
        else:
            if action == 'add':
                list_id.append(idv_id)
        
        print(list_id)

        string_id = ' '.join(map(str, list_id))
        print(string_id)
        update_stmt = 'UPDATE items SET individuals= (?) WHERE qn_id= (?)'
        update_args = (string_id, qn_id)
        self.conn.execute(update_stmt, update_args)
        self.conn.commit()

    def get_notification(self, qn_id, user_id):
        stmt = "SELECT individuals FROM items WHERE qn_id= (?)"
        args = (qn_id, )
        list_id = list([x for x in self.conn.execute(stmt, args)][0][0].split(" "))
        user_id = str(user_id)
        
        if user_id in list_id:
            list_id.remove(user_id)
        return list_id

    def get_message_id(self, qn_id):
        stmt = "SELECT message_id FROM items WHERE qn_id= (?)"
        args = (qn_id,)
        result = [x for x in self.conn.execute(stmt, args)][0][0]
        return result

    def get_reply(self, qn_id):
        stmt = "SELECT reply FROM items WHERE qn_id= (?)"
        args = (qn_id,)
        result = [x for x in self.conn.execute(stmt, args)][0][0]
        return result

    def get_unanswered_qns(self, module, seconds):
        stmt = "SELECT qn FROM items WHERE module= (?) AND answered = (?) AND time > (?) ORDER By qn_id DESC LIMIT 5"
        args = (module, "False", int(seconds),)
        result =  [x for x in self.conn.execute(stmt, args)]
        return result
