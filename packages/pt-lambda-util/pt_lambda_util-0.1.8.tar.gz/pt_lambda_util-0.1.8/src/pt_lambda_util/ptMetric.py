import boto3
import logging

from botocore.exceptions import ClientError

metric = boto3.client('cloudwatch')
logger = logging.getLogger(__name__)


class PTMetric:
    def __init__(self, namespace, dimensions=None):
        self.namespace = namespace
        self.dimension_list = [{"Name": k, "Value": v} for k, v in dimensions.items()] if dimensions else None

    def put_metric_data(self, name, value, unit):
        metric_data = {
            'MetricName': name,
            'Value': value,
            'Unit': unit
        }
        if self.dimension_list:
            metric_data.update({'Dimensions': self.dimension_list})
        metric.put_metric_data(
            Namespace=self.namespace,
            MetricData=[metric_data]
        )


if __name__ == "__main__":
    dimensions = {"Application": "Diagnosis", "Module": "Spider", "FunctionName": "func_name"}
    dimension_list = [{"Name": k, "Value": v} for k,v in dimensions.items()]
    print(dimension_list)