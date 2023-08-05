from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all


class PTTrace(object):
    def __init__(self):
        pass

    @staticmethod
    def enable_all_trace():
        patch_all()

    @staticmethod
    def record(subsegment_name):
        return xray_recorder.in_subsegment(subsegment_name)

    """
    with xray_recorder.in_subsegment("Throwing exception") as subsegment:
        subsegment.put_metadata("very_important_inforamtion", {"message": "Hello I am metadata"}, "information")
        subsegment.put_annotation("very_important_annotation", "Very very important information")
        raise Exception("Information")
    """