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

import unittest

import responses

from mythchannels import MythTVBackend


class TestMythTVBackend(unittest.TestCase):
    @responses.activate
    def test_channels_single_page(self):
        responses.get(
            url="http://mythbackend/Channel/GetChannelInfoList?" +
                "SourceId=1&Details=true&OnlyVisible=false" +
                "&StartIndex=0&Count=100",
            body=open("mock/channel_info_list.xml").read()
        )

        backend = MythTVBackend("http://mythbackend")

        channels = backend.get_channel_info_list(1)

        self.assertEqual(1, len(channels))
        self.assertEqual("NBC5-US", channels[0].channel_name)
