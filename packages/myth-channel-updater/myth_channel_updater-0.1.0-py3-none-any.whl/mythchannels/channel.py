# myth-channel-updater
# Copyright (C) 2022 Andrew Wilkinson
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# <?xml version="1.0" encoding="UTF-8"?>
# <ChannelInfo xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
#       version="1.06" serializerVersion="1.1">
#     <ChanId>1002</ChanId>
#     <ChanNum>2</ChanNum>
#     <CallSign>BBC TWO</CallSign>
#     <IconURL></IconURL>
#     <ChannelName>BBC TWO</ChannelName>
#     <MplexId>1</MplexId>
#     <TransportId>4164</TransportId>
#     <ServiceId>4287</ServiceId>
#     <NetworkId>9018</NetworkId>
#     <ATSCMajorChan>0</ATSCMajorChan>
#     <ATSCMinorChan>0</ATSCMinorChan>
#     <Format></Format>
#     <Modulation></Modulation>
#     <Frequency>490000000</Frequency>
#     <FrequencyId>23</FrequencyId>
#     <FrequencyTable>default</FrequencyTable>
#     <FineTune>0</FineTune>
#     <SIStandard>dvb</SIStandard>
#     <ChanFilters></ChanFilters>
#     <SourceId>1</SourceId>
#     <InputId>0</InputId>
#     <CommFree>0</CommFree>
#     <UseEIT>true</UseEIT>
#     <Visible>true</Visible>
#     <XMLTVID></XMLTVID>
#     <DefaultAuth>fp.bbc.co.uk</DefaultAuth>
#     <Programs/>
# </ChannelInfo>

from typing import Any

from .xml import get_text_from_tag_name


class Channel:
    def __init__(self, xml_node) -> None:
        self.chan_id = get_text_from_tag_name(xml_node, "ChanId")
        self.chan_num = get_text_from_tag_name(xml_node, "ChanNum")
        self.call_sign = get_text_from_tag_name(xml_node, "CallSign")
        self.icon_url = get_text_from_tag_name(xml_node, "IconURL")
        self.channel_name = get_text_from_tag_name(xml_node, "ChannelName")
        self.mplex_id = int(get_text_from_tag_name(xml_node, "MplexId"))
        # self.transport_id = get_text_from_tag_name(xml_node, "TransportId")
        self.service_id = int(get_text_from_tag_name(xml_node, "ServiceId"))
        # self.network_id = int(get_text_from_tag_name(xml_node, "NetworkId"))
        self.atsc_major_chan = \
            int(get_text_from_tag_name(xml_node, "ATSCMajorChan"))
        self.atsc_minor_chan = \
            int(get_text_from_tag_name(xml_node, "ATSCMinorChan"))
        self.format = get_text_from_tag_name(xml_node, "Format")
        # self.modulation = get_text_from_tag_name(xml_node, "Modulation")
        # self.frequency = int(get_text_from_tag_name(xml_node, "Frequency"))
        self.frequency_id = get_text_from_tag_name(xml_node, "FrequencyId")
        # self.frequency_table = \
        # get_text_from_tag_name(xml_node, "FrequencyTable")
        self.fine_tune = int(get_text_from_tag_name(xml_node, "FineTune"))
        # self.si_standard = get_text_from_tag_name(xml_node, "SIStandard")
        self.channel_filers = get_text_from_tag_name(xml_node, "ChanFilters")
        self.source_id = int(get_text_from_tag_name(xml_node, "SourceId"))
        self.input_id = int(get_text_from_tag_name(xml_node, "InputId"))
        self.comm_free = \
            get_text_from_tag_name(xml_node, "CommFree").lower() == "true"
        self.use_eit = \
            get_text_from_tag_name(xml_node, "UseEIT").lower() == "true"
        self.extra_visible = \
            get_text_from_tag_name(xml_node, "ExtendedVisible").lower() \
            == "visible"
        self.visible = \
            get_text_from_tag_name(xml_node, "Visible").lower() == "true"
        self.xml_tv_id = get_text_from_tag_name(xml_node, "XMLTVID")
        self.default_auth = get_text_from_tag_name(xml_node, "DefaultAuth")

        self.set_values = {}

    def get(self, __name: str) -> Any:
        if __name in self.set_values:
            return self.set_values[__name]
        else:
            return getattr(self, __name)

    def __setitem__(self, __name: str, __value: Any) -> None:
        if getattr(self, __name) != __value:
            self.set_values[__name] = __value
        elif __name in self.set_values:
            del self.set_values[__name]

    def __str__(self) -> str:
        return f"{self.chan_id} {self.chan_num} {self.channel_name}" + \
               f" {self.call_sign} ({self.source_id}:{self.service_id})"
