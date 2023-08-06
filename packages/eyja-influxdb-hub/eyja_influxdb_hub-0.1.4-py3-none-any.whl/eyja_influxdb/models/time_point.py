from typing import Optional, Dict

from datetime import datetime

from pydantic import BaseModel
from eyja.utils import now
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS


class TimePoint(BaseModel):
    time: Optional[datetime] = now()
    measurement: str
    tags: Dict[str, str]
    fields: Dict[str, float]

    def get_point(self):
        point = Point(self.measurement)

        for tag_name, tag_value in self.tags.items():
            point = point.tag(tag_name, tag_value)

        for field_name, field_value in self.fields.items():
            point = point.field(field_name, field_value)

        point = point.time(self.time, WritePrecision.NS)
        return point
