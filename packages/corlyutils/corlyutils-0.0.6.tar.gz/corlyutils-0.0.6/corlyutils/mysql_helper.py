import MySQLdb
import MySQLdb.cursors


class MySQL(object):

    def __init__(self, host, user, passwd, db_name,port=3306, autocommit=True):
        self.instance = None
        self.db_name = db_name
        self.host = host
        self.user = user
        self.passwd = passwd
        self.port = port
        self.autocommit = autocommit

    @property
    def connect(self):
        dbconfig = {
            'host': self.host,
            'user': self.user,
            'passwd': self.passwd,
            'db': self.db_name,
            'charset': 'utf8mb4',
            'autocommit': self.autocommit,
            'port': self.port,
            'cursorclass': getattr(MySQLdb.cursors, 'DictCursor')
        }

        # db = MySQLdb.connect("localhost", "root", "root", "kindle_web",
        #                      charset='utf8', cursorclass=MySQLdb.cursors.DictCursor)

        return MySQLdb.connect(**dbconfig)

    @property
    def connection(self):
        """Attempts to connect to the MySQL server.

        :return: Bound MySQL connection object if successful or ``None`` if
            unsuccessful.
        """
        if not self.instance:
            self.instance = self.connect
        return self.instance

    def __exit__(self):
        self.close_connection()

    def close_connection(self):
        if self.instance:
            self.instance.close()
            self.instance = None

    def on_duplicate_update(self, table, dictData):
        dbValues = list(dictData.values())
        dumpList = list()
        for key, value in dictData.items():
            dbValues.append(value)
            dumpList.append(key + "=%s")
        sql = 'INSERT INTO `%s` (`%s`) VALUES (%s) ON DUPLICATE KEY UPDATE %s' % \
              (table, '`,`'.join(dictData.keys()), ','.join(['%s'] * len(dictData)),
               ','.join(dumpList))
        cursor = self.connection.cursor()
        try:
            cursor.execute(sql, dbValues)
        except:
            print(sql)
            raise
        self.connection.commit()
        return cursor.rowcount, cursor.lastrowid

    def insert_dict(self, table, dictData):
        cursor = self.connection.cursor()

        sql = 'INSERT INTO `%s` (`%s`) VALUES (%s)' % \
              (table, '`,`'.join(dictData.keys()), ','.join(['%s'] * len(dictData)))
        try:
            cursor.execute(sql, dictData.values())
        except:
            print(sql)
            raise
        self.connection.commit()
        return cursor.rowcount, cursor.lastrowid

    def insert_many(self, table, keys, list):
        cursor = self.connection.cursor()
        sql = 'INSERT INTO %s (%s) VALUES (%s)' % (table, ','.join(keys), ','.join(['%s'] * len(keys)))
        try:
            cursor.executemany(sql, list)
        except:
            print(cursor._executed)
            raise
        self.connection.commit()
        return cursor.rowcount

    def exe_update(self, sql, args=None):
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql, args)
            self.connection.commit()
        except:
            print(cursor._executed)
            raise
        return cursor.rowcount

    def get_all(self, sql, args=None):
        cursor = self.connection.cursor()
        cursor.execute(sql, args)
        return cursor.fetchall()

    def get_one(self, sql, args=None):
        with self.connection.cursor() as cursor:
            if args:
                cursor.execute(sql, args)
            else:
                cursor.execute(sql)
            return cursor.fetchone()

