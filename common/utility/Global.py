# Global.py
import json
import requests
from config import Config
from uuid import uuid4

class G:
    test = 0
    _db_data = None

    @classmethod
    def get_tag_by_name(cls, name):
        print(cls._db_data)
        return cls._db_data[name]
    
    @classmethod
    def get_app_id(cls):
        return Config.APP_ID
    
    @classmethod
    def get_uuid(cls):
        return str(uuid4().hex)

    @staticmethod
    def init():
        url = Config.DFOps_SERVER_URL + "api/fabric/secondaryDikube"
        tenant_id = Config.TENANT_ID
        app_id = Config.APP_ID

        res = requests.get(url, headers={
            "tenantId": tenant_id,
            "appId": app_id
        })

        data = res.json()['data']

        ret = {}
        for item in data:
            ret[item['tableName']] = item['tag']

        G._db_data = ret    
