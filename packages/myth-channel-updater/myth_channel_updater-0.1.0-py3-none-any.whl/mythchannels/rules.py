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

import yaml

from .channel import Channel
from .rule import Rule


class Rules:
    def __init__(self, fn: str) -> None:
        with open(fn) as yaml_fp:
            self.rules = [Rule(r["match"], r["set"]) for r
                          in yaml.safe_load(yaml_fp)]

    def match(self, channel: Channel) -> bool:
        r = [rule.match(channel) for rule in self.rules]
        return any(r)
