# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc



class TestSpecificationDocumentStub(object):
    """Service interface for a server side test specification document.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """


class TestSpecificationDocumentServicer(object):
    """Service interface for a server side test specification document.
    """


def add_TestSpecificationDocumentServicer_to_server(servicer, server):
    rpc_method_handlers = {
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'national_instruments.flex_logger.automation.protocols.TestSpecificationDocument', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class TestSpecificationDocument(object):
    """Service interface for a server side test specification document.
    """
