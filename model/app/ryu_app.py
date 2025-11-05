# ryu_app.py
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet
from ryu.app.wsgi import ControllerBase, WSGIApplication, route
import json

simple_switch_instance_name = 'simple_switch_api_app'

class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    _CONTEXTS = {'wsgi': WSGIApplication}

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.wsgi = kwargs['wsgi']
        self.wsgi.register(RestAPIController, {simple_switch_instance_name: self})

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions, command=ofproto_v1_3.OFPFC_ADD):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority, 
                                match=match, instructions=inst, command=command)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        if not eth:
            return

        dst = eth.dst
        src = eth.src
        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][src] = in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
            self.add_flow(datapath, 1, match, actions)

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=msg.data)
        datapath.send_msg(out)


class RestAPIController(ControllerBase):
    def __init__(self, req, link, data, **config):
        super(RestAPIController, self).__init__(req, link, data, **config)
        self.ssb_app = data[simple_switch_instance_name]

    @route('simpleswitch', '/simpleswitch/block/{dpid}', methods=['POST'])
    def block_ip(self, req, **kwargs):
        dpid = int(kwargs['dpid'])
        try:
            body = json.loads(req.body)
            ip = body['ip']
        except:
            return Response(content_type='text/plain', text='Invalid JSON', status=400)

        datapath = self.get_datapath(dpid)
        if not datapath:
            return Response(content_type='text/plain', text='Switch not found', status=404)

        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch(eth_type=0x0800, ipv4_src=ip)
        actions = []
        self.ssb_app.add_flow(datapath, 100, match, actions)
        return Response(content_type='text/plain', text=f'Blocked {ip}')

    @route('simpleswitch', '/simpleswitch/unblock/{dpid}', methods=['POST'])
    def unblock_ip(self, req, **kwargs):
        dpid = int(kwargs['dpid'])
        try:
            body = json.loads(req.body)
            ip = body['ip']
        except:
            return Response(content_type='text/plain', text='Invalid JSON', status=400)

        datapath = self.get_datapath(dpid)
        if not datapath:
            return Response(content_type='text/plain', text='Switch not found', status=404)

        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch(eth_type=0x0800, ipv4_src=ip)
        self.ssb_app.add_flow(datapath, 100, match, [], command=ofproto.OFPFC_DELETE)
        return Response(content_type='text/plain', text=f'Unblocked {ip}')

    def get_datapath(self, dpid):
        for dp in self.ssb_app.datapath_list.values():
            if dp.id == dpid:
                return dp
        return None