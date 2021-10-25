import logging

from pymongo.monitoring import CommandListener
from pymongo.monitoring import ServerListener
from pymongo.monitoring import ServerHeartbeatListener
from pymongo.monitoring import TopologyListener
from pymongo.monitoring import ConnectionPoolListener

__all__ = ['event_listeners']

logger = logging.getLogger(__name__)

# logger.setLevel(logging.DEBUG)
#
# _monHandle = logging.StreamHandler()
# _monHandle.setLevel(logging.INFO)
# # _monFmt = '\033[38;5;118m> %(threadName)-9s[<%(asctime)s>] %(message)s'
# _monFmt = '\033[38;5;118m> %(name)-9s[<%(asctime)s>] - %(message)s'
# _monFormat = logging.Formatter(fmt=_monFmt, datefmt="%H:%M:%S")
#
# _monHandle.setFormatter(_monFormat)
# logger.addHandler(_monHandle)


class CommandLogger(CommandListener):

    def started(self, event):
        logger.info("* CMD(<{0.command_name}>, _requestID[{0.request_id}]) "
                    "-> START{0.connection_id}".format(event))

    def succeeded(self, event):
        logger.info("* CMD(<{0.command_name}>, _requestID[{0.request_id}]) "
                    "-> SUCCESS{0.connection_id}"
                    ":[<{0.duration_micros}>:microseconds]".format(event))

    def failed(self, event):
        logger.info("* CMD(<{0.command_name}>, _requestID[{0.request_id}]) "
                    "-> FAILED{0.connection_id} "
                    "in {0.duration_micros}ms".format(event))


class ServerLogger(ServerListener):

    def opened(self, event):
        logger.info(">>> Server{0.server_address} "
                    "-> Added to topology('{0.topology_id}')\n".format(event))

    def description_changed(self, event):
        previous_server_type = event.previous_description.server_type
        new_server_type = event.new_description.server_type
        if new_server_type != previous_server_type:
            logger.info(">>> Server{0.server_address}.type(Changed): "
                        "{0.previous_description.server_type_name} -> "
                        "{0.new_description.server_type_name}".format(event))

    def closed(self, event):
        logger.info(">>> Server{0.server_address} "
                    "-> Removed from topology({0.topology_id})".format(event))


class HeartbeatLogger(ServerHeartbeatListener):

    def started(self, event):
        logger.info("- PINGING{0.connection_id}. . .".format(event))

    def succeeded(self, event):
        logger.info("- ping_to{0.connection_id}: was PONGED({0.reply.document})".format(event))

    def failed(self, event):
        logger.warning("ping_to{0.connection_id}: NOT PONGED({0.reply})".format(event))


class TopologyLogger(TopologyListener):

    def opened(self, event):
        logger.info("> Topology(id='{0.topology_id}') >>> Opened".format(event))

    def description_changed(self, event):
        logger.info("> TopologyDescriptionUpdated(id='{0.topology_id}')".format(event))
        previous_topology_type = event.previous_description.topology_type
        new_topology_type = event.new_description.topology_type
        if new_topology_type != previous_topology_type:
            logger.info(
                "> Topology(id='{0.topology_id}').typeChanged("
                "{0.new_description.topology_type_name} >>> "
                "{0.new_description.topology_type_name}".format(event))
        if not event.new_description.has_writable_server():
            logger.info("> No <WRITEABLE> servers available!!!")
        if not event.new_description.has_readable_server():
            logger.info("> No <READABLE> servers available!!!")

    def closed(self, event):
        logger.info('>>> Topology(id={0.topology_id}) >>> Closed'.format(event))


class ConnectionPoolLogger(ConnectionPoolListener):

    def pool_created(self, event):
        logger.info("[ <pool> | {0.address} | Created ]".format(event))

    def pool_cleared(self, event):
        logger.info("[ <pool> | {0.address} | Cleared ]".format(event))

    def pool_closed(self, event):
        logger.info("[ <pool> | {0.address} | Closed ]".format(event))

    def connection_created(self, event):
        logger.info("[ <pool> | {0.address} | Conn(<{0.connection_id}>) "
                    "| Connection Created".format(event))

    def connection_ready(self, event):
        logger.info("[ <pool> | {0.address} | Conn(<{0.connection_id}>) "
                    "| Successfully Initialized ]".format(event))

    def connection_closed(self, event):
        logger.info("[ <pool> | {0.address} | ClosedConn(<{0.connection_id}>) "
                    "| Reason -> {0.reason}\n".format(event))

    def connection_check_out_started(self, event):
        logger.info("[ <pool> | {0.address} | Check Out Started ]".format(event))

    def connection_check_out_failed(self, event):
        logger.info("[ <pool> | {0.address} | ChkOutFail.reason -> {0.reason} ]".format(event))

    def connection_checked_out(self, event):
        logger.info("[ <pool> | {0.address} | Conn(<{0.connection_id}>) "
                    "| Checked Out of Pool ]\n".format(event))

    def connection_checked_in(self, event):
        logger.info("[ <pool> | {0.address} | Conn(<{0.connection_id}>) "
                    "| Checked into Pool ]".format(event))


event_listeners = [
    ServerLogger(),
    CommandLogger(),
    TopologyLogger(),
    # HeartbeatLogger(),
    ConnectionPoolLogger()
]

if __name__ == '__main__':
    # print(help())
    pass
