from typing import Optional
import xml.etree.ElementTree as etree

from .xmlns import dataset_as_xml
from .xmlns import investigation_as_xml
from .messaging import IcatMessagingClient


class IcatMetadataClient:
    """Client for storing dataset metadata in ICAT."""

    def __init__(
        self,
        queue_urls: list,
        queue_name: str = "icatIngest",
        monitor_port: Optional[int] = None,
        timeout: Optional[float] = None,
    ):
        self._client = IcatMessagingClient(
            queue_urls, queue_name, monitor_port=monitor_port, timeout=timeout
        )

    def send_metadata(
        self,
        beamline: str,
        proposal: str,
        collection: str,
        dataset: str,
        path: str,
        metadata: dict,
        start_datetime=None,
        end_datetime=None,
    ):
        root = dataset_as_xml(
            beamline=beamline,
            proposal=proposal,
            collection=collection,
            dataset=dataset,
            path=path,
            metadata=metadata,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
        )
        self._client.send(etree.tostring(root))

    def start_investigation(self, beamline: str, proposal: str, start_datetime=None):
        root = investigation_as_xml(
            beamline=beamline, proposal=proposal, start_datetime=start_datetime
        )
        self._client.send(etree.tostring(root))

    def check_health(self):
        """Raises an exception when not healthy"""
        self._client.check_health()
