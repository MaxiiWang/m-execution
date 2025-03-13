from config import Config

class Conn:
    methods = {}

conn = Conn()

if Config.DB_TYPE == 'MYSQL':
    from common.db.mysql import write_to_mariaDB, read_from_mariaDB, update_mariaDB, delete_from_mariaDB, write_many_to_mariaDB
    conn.methods = {
        'write': write_to_mariaDB,
        'write_many': write_many_to_mariaDB,
        'read': read_from_mariaDB,
        'update': update_mariaDB,
        'delete': delete_from_mariaDB
    }

if Config.DB_TYPE == 'iDOP':
    from common.db.idop import write_to_iDOP, read_from_iDOP, update_iDOP, delete_from_iDOP, get_schema
    conn.methods = {
        'write': write_to_iDOP,
        'read': read_from_iDOP,
        'update': update_iDOP,
        'delete': delete_from_iDOP,
        'get_schema': get_schema
    }