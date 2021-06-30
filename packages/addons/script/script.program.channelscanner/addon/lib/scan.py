from api import Api
from channel import RFChannel
from ui import busy

import re

import xbmc
from xbmcgui import DialogProgress
from time import sleep

from threading import Thread, Lock


BASE_MUX_CONFIG = {
    "enabled": 1, "epg": 1, "delsys": "DVBT", "frequency": 0, "bandwidth": "6MHz",
    "constellation": "AUTO", "transmission_mode": "AUTO", "guard_interval": "AUTO", "hierarchy": "AUTO",
    "fec_hi": "AUTO", "fec_lo": "AUTO", "plp_id": -1, "scan_state": 0, "charset": "ISO-8859-1",
    "tsid_zero": True, "pmt_06_ac3": 0, "eit_tsid_nocheck": False, "sid_filter": 0
}

BASE_SERVICE_NODE = {
    "services": '', "encrypted": False, "merge_same_name": False,
    "check_availability": False, "type_tags": True, "provider_tags": True, "network_tags": True
}


class ChannelScanner(Thread):
    def __init__(self, _from, to, api=Api()):
        super(ChannelScanner, self).__init__()

        self.api = api
        self.range_start = _from
        self.range_end = to
        self.succeeded = False

        self.lock = Lock()
        self.__active = True

    def get_hardware_adapter(self):
        _ = self.api.hardware.query(action='tree', uuid='root')()[0]
        return self.api.hardware.query(action='tree', uuid=_['uuid'])()[0]['uuid']

    def get_tv_network(self):
        networks = self.api.networks.query(action='grid')()['entries']
        for net in networks:
            if 'TDTCuba' in net['networkname']:
                return net['uuid']
        else:
            return None

    def create_tv_network(self):
        config = {
            'networkname': 'TDTCuba', 'bouquet': False, 'scanfile': '', 
            'autodiscovery': 1, 'ignore_chnum': False, 'charset': 'ISO-8859-1'
        }

        return self.api.networks.query(action='create', klass='dvb_network_dvbt', conf=config)()['uuid']

    def enable_adapter_and_network(self, network, adapter):
        node = {'enabled': True, 'networks': [network], 'uuid': adapter}
        self.api.database.query(action='save', node=node)()

    def get_existing_mux_frequencies(self):
        return [_['frequency'] for _ in self.api.muxes.query(action='grid')()['entries']]

    @staticmethod
    def build_mux_info(frequency_Hz):
        BASE_MUX_CONFIG['frequency'] = frequency_Hz
        return BASE_MUX_CONFIG

    def create_required_muxes(self, network, channel_range_start, channel_range_end):
        muxes = [RFChannel(number=_) for _ in range(channel_range_start, channel_range_end + 1)]

        existing_mux_frequencies = [_['frequency'] for _ in self.api.muxes.query(action='grid')()['entries']]
        required_mux_frequencies = [_.frequencyHz() for _ in muxes if _.frequencyHz() not in existing_mux_frequencies]

        for mux in required_mux_frequencies:
            self.api.networks.query(action='mux_create', conf=self.build_mux_info(mux), uuid=network)()

        return muxes

    def build_mux_frequency_lookup(self, required):
        temp = [_.frequencyHz() for _ in required]
        full = {_['uuid']: int(_['frequency']) for _ in self.api.muxes.query(action='grid')()['entries']}
        reqs = [(k, v) for k, v in full.items() if v in temp]
        reqs.sort(key=lambda x: x[1])

        return full, reqs

    def is_mux_scan_complete(self, mux_uuid):
        for item in self.api.muxes.query(action='grid')()['entries']:
            if item['uuid'] == mux_uuid:
                return item['scan_state'] == 0

    def build_scan_update_info(self, current, total):
        return (current * 100 / total, 'Progreso: %d/%d' % (current, total))

    def set_progress_listener(self, listener):
        self.progress_listener = listener

    def do_scan(self, muxes):
        scan_size = len(muxes)

        self.progress_listener.send(*self.build_scan_update_info(0, scan_size))

        for index, (mux_uuid, freq) in enumerate(muxes):
            self.api.database.query(action='save', node={'uuid': mux_uuid, 'scan_state': 2})()

            while not (self.is_mux_scan_complete(mux_uuid) or not self.active()):
                sleep(1)

            if not self.active():
                return

            self.progress_listener.send(*self.build_scan_update_info(index + 1, scan_size))

        self.progress_listener.no_cancel()
        self.progress_listener.send(100, 'Espere...')

    def clean_mux_info(self, required_muxes):
        services_to_clear = [(_['uuid'], _['channel']) for _ in self.api.services.query(action='grid', sort='multiplex')()['entries'] if _['multiplex_uuid'] in required_muxes]

        for service_uuid, channel_list_uuid in services_to_clear:
            self.api.database.query(action='delete', uuid=channel_list_uuid)()
            self.api.database.query(action='delete', uuid=service_uuid)()

    def get_services_to_map(self):
        return [_['uuid'] for _ in self.api.services.query(action='grid', sort='multiplex')()['entries'] if not _['channel']]

    @staticmethod
    def build_service_mapping_info(services):
        BASE_SERVICE_NODE['services'] = re.sub(' ', '', re.sub("'", '"', re.sub("u\'", '"', str(services))))
        return BASE_SERVICE_NODE

    def is_mapping_completed(self):
        _ = self.api.service_mapper.query(action='status')()
        return (_['ignore'] + _['ok'] + _['fail']) >= _['total']

    def map_services(self, services):
        self.api.service_mapper.query(action='save', node=self.build_service_mapping_info(services))()

        while not self.is_mapping_completed():
            sleep(1)

        sleep(3)

    @staticmethod
    def index_for(index_dict, tags, mux):
        for key in tags:
            try:
                next_index = index_dict[key][mux]
                index_dict[key][mux] += 1
                return next_index
            except KeyError:
                continue
        else:
            return 0

    def set_channel_numbering(self, mux_reference):
        services = self.api.services.query(action='grid', sort='multiplex')()['entries']
        services_to_be_named = [(_['uuid'], _['multiplex_uuid'], _['channel'][-1], _['sid']) for _ in services if _['channel']]
        services_to_be_named.sort(key=lambda _: _[3])

        # get this to know if we are dealing with radio or tv
        tags = self.api.channel_tags.query(action='list')()['entries']

        current_index = {_['key']: {k: 1 for k in mux_reference} for _ in tags if _['val'] in ('Radio channels', 'TV channels')}

        channels = self.api.channels.query(action='grid')()['entries']
        channels_tags = {_['uuid']: _['tags'] for _ in channels}

        # create numbering
        for _, mux_id, channel_id, _ in services_to_be_named:
            mux_channel = RFChannel(frequencyHz=mux_reference[mux_id])
            index = self.index_for(current_index, channels_tags[channel_id], mux_id)

            number = '.'.join((str(mux_channel.number), str(index),))

            self.api.database.query(action='save', node={'uuid': channel_id, 'number': number})()

    def clear_connections(self):
        self.api.connections.query(action='cancel', id='all')()

    def run(self):
        self.clear_connections()

        adapter = self.get_hardware_adapter()
        network = self.get_tv_network() or self.create_tv_network()

        self.enable_adapter_and_network(network, adapter)
        required_muxes = self.create_required_muxes(network, self.range_start, self.range_end)

        reference, required = self.build_mux_frequency_lookup(required_muxes)
        self.clean_mux_info(required)
        self.do_scan(required)

        new_services = self.get_services_to_map()
        if new_services and self.active():
            with busy():
                self.map_services(new_services)
                self.set_channel_numbering(reference)
            self.succeeded = True
        else:
            self.succeeded = False

        self.progress_listener.close()

    def active(self):
        self.lock.acquire()
        value = self.__active
        self.lock.release()

        return value

    def stop(self):
        self.lock.acquire()
        self.__active = False
        self.lock.release()
