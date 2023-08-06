from typing import List

from eyja.hubs.base_hub import BaseHub
from eyja.hubs.config_hub import ConfigHub
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

from eyja_influxdb.models import TimePoint


class InfluxDBHub(BaseHub):
    bucket: str
    org: str
    client: InfluxDBClient

    @classmethod
    async def init(cls):
        host = ConfigHub.get('influxdb.host')
        token = ConfigHub.get('influxdb.token')
        cls.org = ConfigHub.get('influxdb.org')
        cls.bucket = ConfigHub.get('influxdb.bucket')

        cls.client = InfluxDBClient(
            url=host,
            token=token,
        )

        return await super().init()

    @classmethod
    async def send(cls, points: List[TimePoint]):
        write_api = cls.client.write_api(write_options=SYNCHRONOUS)

        write_api.write(cls.bucket, cls.org, [p.get_point() for p in points])
