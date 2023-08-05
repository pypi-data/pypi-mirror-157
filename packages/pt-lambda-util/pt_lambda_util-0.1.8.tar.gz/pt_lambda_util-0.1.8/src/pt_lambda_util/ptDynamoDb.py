import datetime

import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')


class PTDynamoDb(object):
    def __init__(self, table_name):
        self.table_name = table_name

    def get(self, primary_key_item, sort_key_item=None):
        """
        get item from dynamoDb by primary key and sort key
        :param primary_key_item: {<KeyName>:<Value>}
        :param sort_key_item: {<KeyName>:<Value>}
        :return: dict
        """
        item = dict()
        item.update(primary_key_item)
        if sort_key_item:
            item.update(sort_key_item)
        response = dynamodb.Table(self.table_name).get_item(
            Key=item
        )
        obj = response.get("Item")
        if obj is None:
            return None
        enabled_ttl = obj.get("ExpirationTimestamp")
        if enabled_ttl:
            expired = int(datetime.datetime.utcnow().timestamp()) > item["ExpirationTimestamp"]
            if expired:
                return None
        return obj

    def put(self, primary_key_item, sort_key_item, item, ttl=None):
        """
        put item into dynamoDb, expired in ttl
        :param primary_key_item: {<KeyName>:<Value>}
        :param sort_key_item: {<KeyName>:<Value>
        :param item: dict
        :param ttl: integer in seconds
        :return:
        """
        utc_now = datetime.datetime.utcnow()
        item.update(primary_key_item)
        if sort_key_item:
            item.update(sort_key_item)
        item.update({"CreationTimestamp": int(utc_now.timestamp())})
        if ttl:
            item["ExpirationTimestamp"] = int((utc_now + datetime.timedelta(seconds=ttl)).timestamp())
        return dynamodb.Table(self.table_name).put_item(
            Item=item
        )

    def delete(self, primary_key_item, sort_key_item=None):
        """
        delete item where primary_key_name==primary_key_value and sort_key_name==sort_key_value
        :param primary_key_item:
        :param sort_key_item:
        :return:
        """
        key_item = dict()
        key_item.update(primary_key_item)
        if sort_key_item:
            key_item.update(sort_key_item)
        return dynamodb.Table(self.table_name).delete_item(
            Key=key_item
        )

    def get_or_default(self, primary_key_item, sort_key_item, default_item, ttl=None):
        """
        get item, put a default item if not existed
        :param primary_key_item:
        :param sort_key_item:
        :param default_item:
        :param ttl:
        :return:
        """
        obj = self.get(primary_key_item, sort_key_item)
        if obj is not None:
            return obj
        else:
            self.put(primary_key_item, sort_key_item, default_item, ttl)
            return self.get(primary_key_item, sort_key_item)

    def query_by_sort_key_range(self, primary_key_item, sort_key_item):
        """
        query_by_sort_key_range
        :param primary_key_item: {primary_key_name: primary_key_value}
        :param sort_key_item: {sort_key_name: {sort_key_range_start: "xxx", sort_key_range_end: "yyy}}
        :return:
        """
        primary_key_name = list(primary_key_item.items())[0][0]
        primary_key_value = list(primary_key_item.items())[0][1]
        sort_key_name = list(sort_key_item.items())[0][0]
        sort_key_range = list(sort_key_item.items())[0][1]
        sort_key_range_start = sort_key_range[0]
        sort_key_range_end = sort_key_range[1]
        response = dynamodb.Table(self.table_name).query(
            KeyConditionExpression=
            Key(primary_key_name).eq(primary_key_value) &
            Key(sort_key_name).between(sort_key_range_start, sort_key_range_end)
        )
        print("Done")
        pass

    def create_table_if_not_existed(self, primary_key_schema, sort_key_schema=None):
        """
        create_table_if_not_existed
        :param primary_key_schema: {primary_key_name: primary_key_type} -> primary_key_type: S | N | B
        :param sort_key_schema: {sort_key_name: sort_key_type}
        :return:
        """
        import time
        client = boto3.client('dynamodb')
        exists = True
        try:
            describeTableResp = client.describe_table(
                TableName=self.table_name
            )
            return self.table_name
        except Exception as ex:
            if ex.response["Error"]["Code"] == "ResourceNotFoundException":
                exists = False
            else:
                raise ex
        if not exists:
            primary_key_name = list(primary_key_schema.items())[0][0]
            primary_key_type = list(primary_key_schema.items())[0][1]
            # additional_keys = ["Timestamp", "SerialNo"]
            key_schema = [{
                "AttributeName": primary_key_name,
                "KeyType": "HASH"
            }]
            attribute_definitions = [{
                "AttributeName": primary_key_name,
                "AttributeType": primary_key_type
            }]
            if sort_key_schema:
                sort_key_name = list(sort_key_schema.items())[0][0]
                sort_key_type = list(sort_key_schema.items())[0][1]
                key_schema.extend([{"AttributeName": sort_key_name, "KeyType": "RANGE"}])
                attribute_definitions.extend([{"AttributeName": sort_key_name, "AttributeType": sort_key_type}])

            createTableResp = client.create_table(
                TableName=self.table_name,
                KeySchema=key_schema,
                AttributeDefinitions=attribute_definitions,
                ProvisionedThroughput={
                    "ReadCapacityUnits": 5,
                    "WriteCapacityUnits": 5
                }
            )
            status = "CREATING"
            while status != "ACTIVE":
                describeTableResp = client.describe_table(
                    TableName=self.table_name
                )
                status = describeTableResp["Table"]["TableStatus"]
                time.sleep(0.5)

            updateTTLResp = client.update_time_to_live(
                TableName=self.table_name,
                TimeToLiveSpecification={
                    'Enabled': True,
                    'AttributeName': 'ExpirationTimestamp'
                }
            )
            return createTableResp["TableDescription"]["TableName"]


if __name__ == "__main__":
    # db = PTDynamoDb(table_name="table_student")
    # db.create_table_if_not_existed(primary_key_schema={"No": "N"}, sort_key_schema={"Age": "N"})
    # db.put(primary_key_item={"No": 1}, sort_key_item={"Age": 10}, item={"Name": "Peter", "Score": 80})
    # obj = db.get(primary_key_item={"No": 1}, sort_key_item={"Age": 10})
    # db.delete(primary_key_item={"No": 1}, sort_key_item={"Age": 10})
    db = PTDynamoDb(table_name="amzProductDiagnosticJob")
    db.create_table_if_not_existed(primary_key_schema={"JobId": "S"}, sort_key_schema=None)
    item = db.get_or_default(primary_key_item={"JobId": "AAA"}, sort_key_item=None,
                             default_item={"IsDiagnosticJobCompleted": False, "AsinList": []})
    item["AsinList"].append("123")
    db.put(primary_key_item={"JobId": "AAA"}, sort_key_item=None, item=item)
    print(item)