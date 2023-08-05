# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""Base abstract class for metadata builders."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import abc
_ABC = abc.ABCMeta('ABC', (object,), {'__slots__': ()})


class MetadataBuilder(_ABC):
  """Abstract base class for metadata builders."""

  @abc.abstractmethod
  def save_model_with_metadata(self, filepath: str):
    """Saves the model with metadata."""

  @abc.abstractmethod
  def get_metadata(self):
    """Returns the current metadata as a dictionary."""
