from pymongo import MongoClient


class PTMongoDb(object):
    """
    reference: https://www.mongodb.com/languages/python
    tutorial: https://pymongo.readthedocs.io/en/stable/
    """
    def __init__(self, conn_string=None):
        self.conn_string = conn_string
        self.database = None
        self.table = None
        # self.conn_string = "mongodb://ptadmin:Slaj5WVdTnLPVXTb@dev-shard-00-00.azphn.mongodb.net:27017,dev-shard-00-01.azphn.mongodb.net:27017,dev-shard-00-02.azphn.mongodb.net:27017/pt-admin?authSource=admin&replicaSet=atlas-pn5t9g-shard-0&retryWrites=true&ssl=true&w=majority"

    # def create_table_if_not_existed(self, primary_key_schema, sort_key_schema=None):
    #     pass

    def put(self, primary_key, item, ttl=None):
        """
        put item into mongoDb, ttl is not supported yet
        :param primary_key: key name of <string>
        :param item: <dict>
        :param ttl: not support
        :return:
        """
        if "_id" in item:
            del item["_id"]
        resp = self.table.replace_one({"_id": primary_key}, item, upsert=True)
        return resp.upserted_id
        # existed = self.get(primary_key)
        # if existed:
        #     item.update(existed)
        #     resp = self.table.update_one({"_id": primary_key}, item)
        #     return resp
        # else:
        #     item.update({"_id": primary_key})
        #     return self.table.insert_one(item).inserted_id
        # self.table.insert_many([item])

    def get(self, primary_key):
        """
        get item from mongoDb
        :param primary_key: key name of <string>
        :return:
        """
        return self.table.find_one({"_id": primary_key})

    def delete(self, primary_key):
        """
        delete item from mongodb by primary_key
        :param primary_key: key name of <string>
        :return:
        """
        return self.table.delete_one({"_id": primary_key})

    def query(self, conditions):
        """
        query items by input conditions
        :param conditions: List<dict>
        :return:
        """
        resp = self.table.find(conditions)
        return resp

    def switch_table(self, db_name, table_name):
        # from pymongo import MongoClient
        # import pymongo

        # Provide the mongodb atlas url to connect python to mongodb using pymongo
        # CONNECTION_STRING = "mongodb://ptadmin:Slaj5WVdTnLPVXTb@dev-shard-00-00.azphn.mongodb.net:27017,dev-shard-00-01.azphn.mongodb.net:27017,dev-shard-00-02.azphn.mongodb.net:27017/pt-admin?authSource=admin&replicaSet=atlas-pn5t9g-shard-0&retryWrites=true&ssl=true&w=majority"

        # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient

        client = MongoClient(self.conn_string)

        # Create the database for our example (we will use the same database throughout the tutorial
        self.database = client[db_name]
        self.table = client[db_name][table_name]

    # collection = db["products"]


if __name__ == "__main__":
    conn_string = "mongodb://ptadmin:Slaj5WVdTnLPVXTb@dev-shard-00-00.azphn.mongodb.net:27017,dev-shard-00-01.azphn.mongodb.net:27017,dev-shard-00-02.azphn.mongodb.net:27017/pt-admin?authSource=admin&replicaSet=atlas-pn5t9g-shard-0&retryWrites=true&ssl=true&w=majority"
    mongodb = PTMongoDb(conn_string=conn_string)
    mongodb.switch_table(db_name="test", table_name="products2")
    item_1 = {
        "_id": "U1IT00003",
        "item_name": "Blender",
        "max_discount": "10%",
        "batch_number": "RR450020FRG111",
        "price": 341,
        "category": "kitchen appliance"
    }
    mongodb.put("U1IT00004", item_1)
    # collection = db["products"]
    item_details = mongodb.get("U1IT00003")

    items = mongodb.query({"item_name": "Blender"})
    for item in items:
        print(item)
    mongodb.delete("U1IT00003")
    # for item in item_details:
    #     # This does not give a very readable output
    #     print(item)
    # dbname =
    print("done")