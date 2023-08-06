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
from xml.dom.minidom import parseString

from mythchannels import Channel, Rule


class TestRule(unittest.TestCase):
    def setUp(self):
        doc = parseString(open("mock/channel_info_list.xml").read())

        self.channel = [Channel(node) for node
                        in doc.getElementsByTagName("ChannelInfo")][0]

    def test_default_comparison(self):
        rule = Rule({"channel_name": "NBC5-US"},
                    {"channel_name": "RuleMatched"})

        self.assertTrue(rule.match(self.channel))

    def test_default_comparison_false(self):
        rule = Rule({"channel_name": "BBC One"},
                    {"channel_name": "RuleMatched"})

        self.assertFalse(rule.match(self.channel))
