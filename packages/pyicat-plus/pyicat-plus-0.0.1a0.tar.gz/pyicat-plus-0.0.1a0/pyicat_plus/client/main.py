from typing import Optional, List, Tuple
import numpy

from .interface import IcatClientInterface
from .interface import DatasetId
from .elogbook import IcatElogbookClient
from .metadata import IcatMetadataClient
from .investigation import IcatInvestigationClient


class IcatClient(IcatClientInterface):
    """Direct communication with ICAT: e-logbook and metadata"""

    def __init__(
        self,
        metadata_urls: list,
        elogbook_url: str,
        elogbook_token: str = "elogbook-00000000-0000-0000-0000-000000000000",
        metadata_queue: str = "icatIngest",
        metadata_queue_monitor_port: Optional[int] = None,
        elogbook_timeout: Optional[float] = None,
        feedback_timeout: Optional[float] = None,
        queue_timeout: Optional[float] = None,
        beamline: Optional[str] = None,
        proposal: Optional[str] = None,
    ):
        self.current_proposal = proposal
        self.current_beamline = beamline
        self.current_collection = None
        self.current_dataset = None
        self.current_path = None
        self.current_dataset_metadata = None

        self.elogbook_client = IcatElogbookClient(
            url=elogbook_url, api_key=elogbook_token, timeout=elogbook_timeout
        )
        self.metadata_client = IcatMetadataClient(
            queue_urls=metadata_urls,
            queue_name=metadata_queue,
            monitor_port=metadata_queue_monitor_port,
            timeout=queue_timeout,
        )
        self.investigation_client = IcatInvestigationClient(
            url=elogbook_url, api_key=elogbook_token, timeout=feedback_timeout
        )

    @property
    def current_proposal(self):
        return self.__current_proposal

    @current_proposal.setter
    def current_proposal(self, value: Optional[str]):
        self.__current_proposal = value

    @property
    def current_beamline(self):
        return self.__current_beamline

    @current_beamline.setter
    def current_beamline(self, value: Optional[str]):
        self.__current_beamline = value

    @property
    def current_dataset(self):
        return self.__current_dataset

    @current_dataset.setter
    def current_dataset(self, value: Optional[str]):
        self.__current_dataset = value

    @property
    def current_dataset_metadata(self):
        return self.__current_dataset_metadata

    @current_dataset_metadata.setter
    def current_dataset_metadata(self, value: Optional[dict]):
        self.__current_dataset_metadata = value

    @property
    def current_collection(self):
        return self.__current_collection

    @current_collection.setter
    def current_collection(self, value: Optional[str]):
        self.__current_collection = value

    @property
    def current_path(self):
        return self.__current_path

    @current_path.setter
    def current_path(self, value: Optional[str]):
        self.__current_path = value

    def send_message(
        self,
        msg: str,
        msg_type="comment",
        beamline: Optional[str] = None,
        proposal: Optional[str] = None,
        dataset: Optional[str] = None,
        beamline_only: Optional[bool] = None,
        **payload,
    ):
        if beamline_only:
            proposal = None
        elif proposal is None:
            proposal = self.current_proposal
        if beamline is None:
            beamline = self.current_beamline
        if beamline_only:
            dataset = None
        elif dataset is None:
            dataset = self.current_dataset
        self.elogbook_client.send_message(
            message=msg,
            category=msg_type,
            beamline=beamline,
            proposal=proposal,
            dataset=dataset,
            **payload,
        )

    def send_binary_data(
        self,
        data: bytes,
        mimetype: Optional[str] = None,
        beamline: Optional[str] = None,
        proposal: Optional[str] = None,
        beamline_only: Optional[bool] = None,
        **payload,
    ):
        if beamline_only:
            proposal = None
        elif proposal is None:
            proposal = self.current_proposal
        if beamline is None:
            beamline = self.current_beamline
        self.elogbook_client.send_binary_data(
            data, mimetype=mimetype, beamline=beamline, proposal=proposal, **payload
        )

    def send_text_file(
        self,
        filename: str,
        beamline: Optional[str] = None,
        proposal: Optional[str] = None,
        dataset: Optional[str] = None,
        beamline_only: Optional[bool] = None,
        **payload,
    ):
        if beamline_only:
            proposal = None
        elif proposal is None:
            proposal = self.current_proposal
        if beamline is None:
            beamline = self.current_beamline
        if beamline_only:
            dataset = None
        elif dataset is None:
            dataset = self.current_dataset
        self.elogbook_client.send_text_file(
            filename, beamline=beamline, proposal=proposal, dataset=dataset, **payload
        )

    def send_binary_file(
        self,
        filename: str,
        beamline: Optional[str] = None,
        proposal: Optional[str] = None,
        beamline_only: Optional[bool] = None,
        **payload,
    ):
        if beamline_only:
            proposal = None
        elif proposal is None:
            proposal = self.current_proposal
        if beamline is None:
            beamline = self.current_beamline
        self.elogbook_client.send_binary_file(
            filename, beamline=beamline, proposal=proposal, **payload
        )

    def start_investigation(
        self,
        beamline: Optional[str] = None,
        proposal: Optional[str] = None,
        start_datetime=None,
    ):
        if proposal is None:
            proposal = self.current_proposal
        else:
            self.current_proposal = proposal
        if beamline is None:
            beamline = self.current_beamline
        else:
            self.current_beamline = beamline
        self.metadata_client.start_investigation(
            beamline=beamline, proposal=proposal, start_datetime=start_datetime
        )

    def store_dataset(
        self,
        beamline: Optional[str] = None,
        proposal: Optional[str] = None,
        collection: Optional[str] = None,
        dataset: Optional[str] = None,
        path: Optional[str] = None,
        metadata: dict = None,
        start_datetime=None,
        end_datetime=None,
    ):
        if proposal is None:
            proposal = self.current_proposal
        if beamline is None:
            beamline = self.current_beamline
        if collection is None:
            collection = self.current_collection
        if dataset is None:
            dataset = self.current_dataset
        if path is None:
            path = self.current_path
        if metadata is None:
            metadata = self.current_dataset_metadata
        self.metadata_client.send_metadata(
            beamline=beamline,
            proposal=proposal,
            collection=collection,
            dataset=dataset,
            path=path,
            metadata=metadata,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
        )

    def investigation_info(
        self, beamline: str, proposal: str, timeout: Optional[float] = None
    ) -> Optional[dict]:
        return self.investigation_client.investigation_info(
            beamline=beamline, proposal=proposal, timeout=timeout
        )

    def registered_dataset_ids(
        self, beamline: str, proposal: str, timeout: Optional[float] = None
    ) -> Optional[List[DatasetId]]:
        return self.investigation_client.registered_dataset_ids(
            beamline=beamline, proposal=proposal, timeout=timeout
        )

    def investigation_info_string(
        self, beamline: str, proposal: str, timeout: Optional[float] = None
    ) -> str:
        info = self.investigation_info(
            beamline=beamline, proposal=proposal, timeout=timeout
        )
        if info:
            rows = [(str(k), str(v)) for k, v in info.items()]
            lengths = numpy.array([[len(s) for s in row] for row in rows])
            fmt = "   ".join(["{{:<{}}}".format(n) for n in lengths.max(axis=0)])
            infostr = "ICAT proposal time slot:\n "
            infostr += "\n ".join([fmt.format(*row) for row in rows])
        elif info is None:
            infostr = f"Proposal information currently not available ({self.reason_for_missing_information})"
        else:
            infostr = "Proposal NOT available in the data portal"
        return infostr

    def investigation_summary(
        self, beamline: str, proposal: str, timeout: Optional[float] = None
    ) -> List[Tuple]:
        info = self.investigation_info(
            beamline=beamline, proposal=proposal, timeout=timeout
        )
        keys = ["e-logbook", "data portal"]
        if info:
            rows = [(key, info[key]) for key in keys]
        elif info is None:
            rows = [
                (
                    key,
                    f"Proposal information currently not available ({self.reason_for_missing_information})",
                )
                for key in keys
            ]
        else:
            rows = [(key, "Proposal NOT available in the data portal") for key in keys]
        return rows

    @property
    def expire_datasets_on_close(self) -> bool:
        return False

    @property
    def reason_for_missing_information(self) -> str:
        return "ICAT communication timeout"
