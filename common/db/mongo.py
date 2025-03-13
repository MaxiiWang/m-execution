from pymongo import MongoClient
from config import Config
from bson.objectid import ObjectId


mongo_client = MongoClient(host=Config.MONGODB_HOST, port=Config.MONGODB_PORT, username=Config.MONGODB_USER, password=Config.MONGODB_PWD)

class MongoTool(object):
    """
    mongodb操作工具类
    """

    def __init__(self, db, collection):
        self.client = mongo_client[db][collection]

    def switch_collection(self, db, collection):
        self.client = mongo_client[db][collection]

    def get_collection_names(self, db):
        return mongo_client[db].list_collection_names(session=None)
    
    def drop_collection(self, db_name, col_name):
        col = self.switch_collection(db_name, col_name)
        if self.client:
            self.client.drop()
    
    
    # 查询单条
    def get_one(self, query, fields=[]):
        """
        查询单条
        :param query:查询条件 dict
        :param fields: 查询的字段 list
        :return: 查询的数据 dict
        """
        # 指定字段
        if fields:
            filter_query = {i: 1 for i in fields}
            data = self.client.find_one(query, filter_query)
        else:
            print(query)
            data = self.client.find_one(query)

        if not data:
            return None

        return data

    # 查询多条
    async def get_many(self, query, fields=[]):
        """
        查询多条
        :param query:查询条件 dict
        :param fields: 查询的字段 list
        :return: 查询的数据 list
        """
        ret_list = []
        # 指定字段
        if fields:
            filter_query = {i: 1 for i in fields}
            data = self.client.find(query, filter_query)
        else:
            data = self.client.find(query)
        
        for item in data:
            ret_list.append(item)
            
        return ret_list
    
    # 获取不重复的值
    def get_distinct(self, field, query={}):
        """
        获取不重复的值
        :param field: 字段名 str
        :param query: 查询条件 dict
        :return: 查询的数据 list
        """
        data = self.client.distinct(field)
        return data
    
    def get_max_value(self, field, query={}):
        """
        获取最大值
        :param field: 字段名 str
        :param query: 查询条件 dict
        :return: 查询的数据 list
        """
        data = self.client.find(query).sort(field, -1).limit(1)

        value = None
        for item in data:
            value = item[field]
        return value
    
    def get_min_value(self, field, query={}):
        """
        获取最小值
        :param field: 字段名 str
        :param query: 查询条件 dict
        :return: 查询的数据 list
        """
        data = self.client.find(query).sort(field, 1).limit(1)

        value = None
        for item in data:
            value = item[field]
        return value
    
    def count(self, query={}):
        """
        获取总数
        :param query: 查询条件 dict
        :return: 查询的数据 list
        """
        data = self.client.count_documents(query)
        return data

    # 获取总页数
    def get_page_num(self, page_size, query={}):
        """
        获取总页数
        :param page_size: 分页大小 int
        :param query: 查询条件 dict
        :return: 总页数 int
        """
        # count_num = self.client.count_documents(query)
        # 这个方法在没有筛选条件下效率会快[目前数据量比较小没法直观体现]
        count_num = self.client.estimated_document_count()
        page_num = (count_num + page_size - 1) // page_size
        return page_num

    # 分页查询
    def get_page_many(self, query, page, page_size, fields=[]):
        """
        分页查询
        :param query: 查询条件 dict
        :param page: 页数 int
        :param page_size: 分页大小 int
        :param fields: 筛选只需要的字段 list
        :return:
        """
        limit = page_size
        skip = page_size * (page - 1)
        ret_list = []
        # 指定字段
        if fields:
            filter_query = {i: 1 for i in fields if i != '_id'}
            if '_id' in fields:
                filter_query.update({'_id': 0})
            data = self.client.find(query, filter_query).skip(skip).limit(limit)
        else:
            print(query, skip, limit)
            data = self.client.find(query).skip(skip).limit(limit)

        # Recursively convert the ObjectId type to str
        from common.utility.convert import rec_convert_obj_id_to_str
        for item in data:
            ret_list.append(rec_convert_obj_id_to_str(item))

        return ret_list

    # 更新第一条
    def update_one(self, query, update_data):
        """
        更新第一条
        :param query: 更新条件 dict
        :param update_data: 更新数据 dict
        :return:
        """
        self.client.update_one(query, update_data)

    # 更新多条
    def update_many(self, query, update_data):
        """
        更新多条
        :param query: 更新条件 dict
        :param update_data: 更新数据 dict
        :return:
        """
        self.client.update_many(query, update_data)

    # 删除第一条
    def delete_one(self, query):
        """
        删除第一条
        :param query: 删除条件 dict
        :return:
        """
        self.client.delete_one(query)

    # 删除多条
    def delete_many(self, query):
        """
        删除多条
        :param query: 删除条件 dict
        :return:
        """
        self.client.delete_many(query)

    # 批量写操作
    def bulk_write(self, datas, order=True):
        """
        批量写操作
        :param datas: 批量操作数据表 list
        :param order: 错误中单规则 False 当前出错继续下一条  bool
        :return:
        """
        self.client.bulk_write(datas, ordered=order)

    # 批量insert
    def insert_many(self, datas):
        """
        批量insert
        :param datas: 插入数据表 list
        :return:
        """
        self.client.insert_many(datas)

    # 单个insert
    def insert_one(self, data):
        """
        单个insert
        :param data: 单条插入数据
        :return:
        """
        return ObjectId(self.client.insert_one(data).inserted_id)