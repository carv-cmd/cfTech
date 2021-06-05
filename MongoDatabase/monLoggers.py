import logging
from pymongo.monitoring import CommandListener
from pymongo.monitoring import ServerListener
from pymongo.monitoring import ServerHeartbeatListener
from pymongo.monitoring import TopologyListener
from pymongo.monitoring import ConnectionPoolListener
from pymongo.monitoring import register

__all__ = ['logging']


class CommandLogger(CommandListener):
    def started(self, event):
        logging.info("* CMD(_{0.command_name}_, _requestID[{0.request_id}]) "
                     "-> START{0.connection_id}".format(event))

    def succeeded(self, event):
        logging.info("* CMD(_{0.command_name}_, _requestID[{0.request_id}]) "
                     "-> SUCCESS{0.connection_id} "
                     "in {0.duration_micros}ms\n".format(event))

    def failed(self, event):
        logging.info("* CMD(_{0.command_name}_, _requestID[{0.request_id}]) "
                     "-> FAILED{0.connection_id} "
                     "in {0.duration_micros}ms".format(event))


class ServerLogger(ServerListener):
    def opened(self, event):
        logging.info(">>> Server{0.server_address} "
                     "-> Added to topology('{0.topology_id}')\n".format(event))

    def description_changed(self, event):
        previous_server_type = event.previous_description.server_type
        new_server_type = event.new_description.server_type
        if new_server_type != previous_server_type:
            logging.info(">>> Server{0.server_address}.type(Changed): "
                         "{0.previous_description.server_type_name} ->"
                         "{0.new_description.server_type_name}".format(event))

    def closed(self, event):
        logging.info(">>> Server{0.server_address} "
                     "-> Removed from topology({0.topology_id})".format(event))


class HeartbeatLogger(ServerHeartbeatListener):
    def started(self, event):
        logging.info(">>> PING sent to server {0.connection_id}".format(event))

    def succeeded(self, event):
        logging.info(">>> PING Server{0.connection_id} "
                     "-> PONGED -> {0.reply.document}".format(event))

    def failed(self, event):
        logging.warning(">>> PING to Server:[{0.connection_id}] "
                        "-> NOT PONGED -> {0.reply}".format(event))


class TopologyLogger(TopologyListener):
    def opened(self, event):
        logging.info(">>> Topology(id='{0.topology_id}') -> Opened".format(event))

    def description_changed(self, event):
        logging.info(">>> TopologyDescriptionUpdated(id='{0.topology_id}')".format(event))
        previous_topology_type = event.previous_description.topology_type
        new_topology_type = event.new_description.topology_type
        if new_topology_type != previous_topology_type:
            logging.info(">>> Topology(id='{0.topology_id}').type(Changed) "
                         "-> {0.new_description.topology_type_name} -> "
                         "{0.new_description.topology_type_name}".format(event))
        if not event.new_description.has_writable_server():
            logging.warning('>>> No <WRITEABLE> servers available!!!')
        if not event.new_description.has_readable_server():
            logging.warning(">>> No <READABLE> servers available!!!")

    def closed(self, event):
        logging.info('>>> Topology(id={0.topology_id}) -> Closed')


class ConnectionPoolLogger(ConnectionPoolListener):
    def pool_created(self, event):
        logging.info(">>> [Pool: {0.address}] Created".format(event))

    def pool_cleared(self, event):
        logging.info(">>> [Pool: {0.address}] Cleared".format(event))

    def pool_closed(self, event):
        logging.info(">>> [Pool: {0.address}] Closed".format(event))

    def connection_created(self, event):
        logging.info(">>> [Pool: {0.address}]|[Conn: #{0.connection_id}] "
                     "-> Connection Created".format(event))

    def connection_ready(self, event):
        logging.info(">>> [Pool: {0.address}]|[Conn: #{0.connection_id}] "
                     "-> Connection Successfully Initialized".format(event))

    def connection_closed(self, event):
        logging.info(">>> [Pool: {0.address}]|[Conn: #{0.connection_id}] "
                     "-> ConnectionClose.reason -> {0.reason}".format(event))

    def connection_check_out_started(self, event):
        logging.info(">>> [Pool: {0.address}] Connection Check Out Started".format(event))

    def connection_check_out_failed(self, event):
        logging.info(">>> [Pool: {0.address}] Connection Check Out Failed "
                     "-> Reason -> {0.reason}".format(event))

    def connection_checked_out(self, event):
        logging.info(">>> [Pool: {0.address}]|[Conn: #{0.connection_id}] "
                     "-> Connection Checked Out of Pool".format(event))

    def connection_checked_in(self, event):
        logging.info(">>> [Pool: {0.address}]|[Conn: #{0.connection_id}] "
                     "-> Connection Checked Out of Pool".format(event))


register(ServerLogger())
register(CommandLogger())
# register(TopologyLogger())
# register(HeartbeatLogger())
# register(ConnectionPoolLogger())
