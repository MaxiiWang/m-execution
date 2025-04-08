# Global.py
import pymysql
import json
from config import Config
from uuid import uuid4

class G:
    test = 0
    _db_data = None

    @classmethod
    def get_tag_by_name(cls, name):
        # if cls._db_data is None:
        #     cls._db_data = cls._query_db()
        cls._db_data = cls._query_db()
        return name
    
    @classmethod
    def get_app_id(cls):
        return Config.APP_ID
    
    @classmethod
    def get_uuid(cls):
        return str(uuid4().hex)

    @staticmethod
    def _query_db():
        mariaDB_connection = pymysql.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PWD,
            database="app",
            cursorclass=pymysql.cursors.DictCursor  # 使用 DictCursor
        )
        cursor = mariaDB_connection.cursor()
        app_id = Config.APP_ID
        cursor.execute("SELECT * FROM app_data_config WHERE app_id = %s ORDER BY order_index ASC", (app_id,))
        result = cursor.fetchall()
        cursor.close()
        mariaDB_connection.close()
        
        config_str = ""

        for item in result:
            config_str += item['data_config']
        data_config = json.loads(config_str)

        ret = {}
        for item in data_config:
            ret[item['tableName']] = item['tag']

        return ret
    
