# Copyright 2019 PrivateStorage.io, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Tests for ``_zkapauthorizer._base64``.
"""

from base64 import urlsafe_b64encode

from hypothesis import given
from hypothesis.strategies import binary
from testtools import TestCase
from testtools.matchers import Equals

from .._base64 import urlsafe_b64decode


class Base64Tests(TestCase):
    """
    Tests for ``urlsafe_b64decode``.
    """

    @given(binary())
    def test_roundtrip(self, bytestring):
        """
        Byte strings round-trip through ``base64.urlsafe_b64encode`` and
        ``urlsafe_b64decode``.
        """
        self.assertThat(
            urlsafe_b64decode(urlsafe_b64encode(bytestring)),
            Equals(bytestring),
        )
