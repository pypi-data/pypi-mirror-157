import sys
import socket
import subprocess
import pytest
from . import proc
from . import tcp
from ...concurrency import iter_queue
from ...client.elogbook import IcatElogbookClient
from ...client.metadata import IcatMetadataClient


__all__ = [
    "icat_data_dir",
    "stomp_server",
    "icat_subscriber",
    "icatplus_server",
    "icat_logbook_subscriber",
    "icat_publisher",
    "activemq_rest_server",
    "icat_backend",
    "elogbook_client",
    "elogbook_ebs_client",
    "icat_metadata_client",
]


@pytest.fixture
def icat_data_dir(tmpdir):
    """Directory where the ICAT dataset backend icat_subscriber can store state."""
    path = tmpdir / "datasets"
    path.mkdir()
    yield path


@pytest.fixture
def stomp_server():
    """One of the ICAT backends (for dataset metadata)"""
    port = tcp.get_open_port()
    # Add arguments ["--debug", "TEXT"] for debugging
    p = subprocess.Popen(["coilmq", "-b", "0.0.0.0", "-p", str(port)])
    tcp.wait_tcp_online("localhost", port)
    try:
        yield "localhost", port
    finally:
        proc.wait_terminate(p)


@pytest.fixture
def icat_subscriber(stomp_server, icat_data_dir):
    """Receive messages from the stomp_server backend"""
    with tcp.tcp_message_server() as (port_out, messages):
        host, port = stomp_server
        p = subprocess.Popen(
            [
                sys.executable,
                "-u",
                "-m",
                "pyicat_plus.tests.servers.stomp_subscriber",
                f"--host={host}",
                f"--port={port}",
                f"--port_out={port_out}",
                "--queue=/queue/icatIngest",
                f"--icat_data_dir={icat_data_dir}",
            ]
        )
        try:
            assert messages.get(timeout=5) == "LISTENING"
            yield messages
        finally:
            proc.wait_terminate(p)


@pytest.fixture
def icatplus_server(icat_subscriber, icat_data_dir):
    """ICAT backend for the e-logbook and dataset queries.
    The STOMP subscriber is needed to save dataset location in files
    so that the icatplus_server can use those to be aware of the datasets.
    """
    with tcp.tcp_message_server("json") as (port_out, messages):
        port = tcp.get_open_port()
        p = subprocess.Popen(
            [
                sys.executable,
                "-u",
                "-m",
                "pyicat_plus.tests.servers.icatplus_server",
                f"--port={port}",
                f"--port_out={port_out}",
                f"--icat_data_dir={icat_data_dir}",
            ]
        )
        tcp.wait_tcp_online("localhost", port)
        try:
            assert messages.get(timeout=5) == {"STATUS": "LISTENING"}
            yield port, messages
        finally:
            proc.wait_terminate(p)


@pytest.fixture
def icat_logbook_subscriber(icatplus_server):
    """Receive messages from the icatplus_server backend"""
    _, messages = icatplus_server
    try:
        yield messages
        assert messages.empty(), "not all messages have been validated"
    finally:
        messages.put(StopIteration)
        for msg in iter_queue(messages):
            print(f"\nUnvalidated message: {msg}")


@pytest.fixture
def icat_publisher(stomp_server):
    """Sends messages to the /queue/icatIngest queue of stomp_server"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port_in = tcp.get_open_port()
    sock.bind(("localhost", port_in))
    sock.listen()

    # Redirect messages from socket to STOMP server
    host, port = stomp_server
    p = subprocess.Popen(
        [
            sys.executable,
            "-u",
            "-m",
            "pyicat_plus.tests.servers.stomp_publisher",
            f"--host={host}",
            f"--port={port}",
            f"--port_in={port_in}",
            "--queue=/queue/icatIngest",
        ]
    )
    try:
        conn, addr = sock.accept()
        with conn:
            yield conn
    finally:
        sock.close()
        proc.wait_terminate(p)


@pytest.fixture
def activemq_rest_server():
    """One of the ICAT backends (for queue monitoring)"""
    port = tcp.get_open_port()
    p = subprocess.Popen(
        [
            sys.executable,
            "-u",
            "-m",
            "pyicat_plus.tests.servers.activemq_rest_server",
            f"--port={port}",
        ]
    )
    tcp.wait_tcp_online("localhost", port)
    try:
        yield "localhost", port
    finally:
        proc.wait_terminate(p)


@pytest.fixture
def icat_backend(stomp_server, activemq_rest_server, icatplus_server):
    """Starts all icat backends"""
    host, port = stomp_server
    metadata_urls = [f"{host}:{port}"]
    port, _ = icatplus_server
    elogbook_url = f"http://localhost:{port}"
    host, port = activemq_rest_server
    metadata_queue_monitor_port = port
    icat_servers = {
        "metadata_urls": metadata_urls,
        "elogbook_url": elogbook_url,
        "metadata_queue_monitor_port": metadata_queue_monitor_port,
        "elogbook_timeout": 5,
        "feedback_timeout": 5,
        "queue_timeout": 5,
    }
    yield icat_servers


@pytest.fixture
def elogbook_client(icatplus_server):
    """Client to publish e-logbook messages and a queue that
    receives everything the ICAT backend receives.
    """
    port, messages = icatplus_server
    client = IcatElogbookClient(f"http://localhost:{port}")
    yield client, messages


@pytest.fixture
def elogbook_ebs_client(icatplus_server):
    """Client to publish e-logbook messages and a queue that
    receives everything the ICAT backend receives.
    """
    port, messages = icatplus_server
    client = IcatElogbookClient(
        f"http://localhost:{port}",
        tags=["testtag", "machine"],
        software="testsoft",
        source="ebs",
        type="broadcast",
    )
    yield client, messages


@pytest.fixture
def icat_metadata_client(stomp_server, activemq_rest_server, icat_subscriber):
    """Client to publish ICAT metadata and a queue that
    receives everything the ICAT backend receives.
    """
    _, jport = activemq_rest_server
    host, port = stomp_server
    messages = icat_subscriber
    client = IcatMetadataClient([f"{host}:{port}"], monitor_port=jport)
    yield client, messages
