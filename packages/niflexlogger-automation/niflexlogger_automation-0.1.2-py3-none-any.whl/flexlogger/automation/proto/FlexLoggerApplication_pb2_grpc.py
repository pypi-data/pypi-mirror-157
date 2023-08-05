# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from flexlogger.automation.proto import FlexLoggerApplication_pb2 as flexlogger_dot_automation_dot_proto_dot_FlexLoggerApplication__pb2


class FlexLoggerApplicationStub(object):
    """Service interface for the server application.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.OpenProject = channel.unary_unary(
                '/national_instruments.flex_logger.automation.protocols.FlexLoggerApplication/OpenProject',
                request_serializer=flexlogger_dot_automation_dot_proto_dot_FlexLoggerApplication__pb2.OpenProjectRequest.SerializeToString,
                response_deserializer=flexlogger_dot_automation_dot_proto_dot_FlexLoggerApplication__pb2.OpenProjectResponse.FromString,
                )
        self.GetActiveProject = channel.unary_unary(
                '/national_instruments.flex_logger.automation.protocols.FlexLoggerApplication/GetActiveProject',
                request_serializer=flexlogger_dot_automation_dot_proto_dot_FlexLoggerApplication__pb2.GetActiveProjectRequest.SerializeToString,
                response_deserializer=flexlogger_dot_automation_dot_proto_dot_FlexLoggerApplication__pb2.GetActiveProjectResponse.FromString,
                )


class FlexLoggerApplicationServicer(object):
    """Service interface for the server application.
    """

    def OpenProject(self, request, context):
        """RPC call to open an existing project on the server.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetActiveProject(self, request, context):
        """RPC call to get the currently active (open) project from the server.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_FlexLoggerApplicationServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'OpenProject': grpc.unary_unary_rpc_method_handler(
                    servicer.OpenProject,
                    request_deserializer=flexlogger_dot_automation_dot_proto_dot_FlexLoggerApplication__pb2.OpenProjectRequest.FromString,
                    response_serializer=flexlogger_dot_automation_dot_proto_dot_FlexLoggerApplication__pb2.OpenProjectResponse.SerializeToString,
            ),
            'GetActiveProject': grpc.unary_unary_rpc_method_handler(
                    servicer.GetActiveProject,
                    request_deserializer=flexlogger_dot_automation_dot_proto_dot_FlexLoggerApplication__pb2.GetActiveProjectRequest.FromString,
                    response_serializer=flexlogger_dot_automation_dot_proto_dot_FlexLoggerApplication__pb2.GetActiveProjectResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'national_instruments.flex_logger.automation.protocols.FlexLoggerApplication', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class FlexLoggerApplication(object):
    """Service interface for the server application.
    """

    @staticmethod
    def OpenProject(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/national_instruments.flex_logger.automation.protocols.FlexLoggerApplication/OpenProject',
            flexlogger_dot_automation_dot_proto_dot_FlexLoggerApplication__pb2.OpenProjectRequest.SerializeToString,
            flexlogger_dot_automation_dot_proto_dot_FlexLoggerApplication__pb2.OpenProjectResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetActiveProject(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/national_instruments.flex_logger.automation.protocols.FlexLoggerApplication/GetActiveProject',
            flexlogger_dot_automation_dot_proto_dot_FlexLoggerApplication__pb2.GetActiveProjectRequest.SerializeToString,
            flexlogger_dot_automation_dot_proto_dot_FlexLoggerApplication__pb2.GetActiveProjectResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
