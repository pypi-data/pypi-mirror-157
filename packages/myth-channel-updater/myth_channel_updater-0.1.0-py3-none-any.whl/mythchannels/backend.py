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

from typing import List
from xml.dom.minidom import parseString

import requests

from .channel import Channel


class MythTVBackend:
    def __init__(self, backend: str) -> None:
        self.backend = backend

    def get_channel_info_list(self, source_id: int) -> List[Channel]:
        start = 0
        channels: List[Channel] = []
        while True:
            url_path = f"/Channel/GetChannelInfoList?SourceId={source_id}" + \
                f"&Details=true&OnlyVisible=false&StartIndex={start}&Count=100"
            r = requests.get(self.backend + url_path)
            doc = parseString(r.content)

            channelpage = [Channel(node) for node
                           in doc.getElementsByTagName("ChannelInfo")]
            channels.extend(channelpage)

            if len(channelpage) < 100:
                return channels

            start += len(channelpage)

    def update_channel(self, channel: Channel) -> None:
        data = {
                    "ATSCMajorChannel": channel.get("atsc_major_chan"),
                    "ATSCMinorChannel": channel.get("atsc_minor_chan"),
                    "CallSign": channel.get("call_sign"),
                    "ChannelID": channel.get("chan_id"),
                    "ChannelName": channel.get("channel_name"),
                    "ChannelNumber": channel.get("chan_num"),
                    "DefaultAuthority": channel.get("default_auth"),
                    "ExtraVisible": "Visible" if channel.get("extra_visible")
                                    else "NotVisible",
                    "Format": channel.get("format"),
                    "FrequencyID": channel.get("frequency_id"),
                    "Icon": channel.get("icon_url"),
                    "MplexID": channel.get("mplex_id"),
                    "ServiceID": channel.get("service_id"),
                    "SourceID": channel.get("source_id"),
                    "UseEIT": channel.get("use_eit"),
                    "XMLTVID": channel.get("xml_tv_id"),
                    "Visible": channel.get("visible"),
                }
        r = requests.post(self.backend + "/Channel/UpdateDBChannel", data)
        r.raise_for_status()
