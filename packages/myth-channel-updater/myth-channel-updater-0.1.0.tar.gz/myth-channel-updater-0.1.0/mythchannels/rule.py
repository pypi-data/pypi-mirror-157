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

import re
from typing import Any, Dict

from .channel import Channel


class Rule:
    def __init__(self, matchers: Dict[str, Any],
                 setters: Dict[str, Any]) -> None:
        self.matchers = matchers
        self.setters = setters

    def match(self, channel: Channel) -> bool:
        for matcher in self.matchers:
            if "__" in matcher:
                field, comp = matcher.split("__")
            else:
                field = matcher
                comp = "eq"

            value = getattr(channel, field)

            if comp == "eq":
                if isinstance(value, str) \
                   and isinstance(self.matchers[matcher], str):
                    if value.lower() != self.matchers[matcher].lower():
                        return False
                elif value != self.matchers[matcher]:
                    return False
            elif comp == "neq":
                if isinstance(value, str) \
                   and isinstance(self.matchers[matcher], str):
                    if value.lower() == self.matchers[matcher].lower():
                        return False
                elif value == self.matchers[matcher]:
                    return False
            elif comp == "re":
                if re.match(self.matchers[matcher],
                            value, re.IGNORECASE) is None:
                    return False
            else:
                raise ValueError(f"Unknown comparison operator: {comp}")

        for setter in self.setters:
            channel[setter] = self.setters[setter]

        return True
