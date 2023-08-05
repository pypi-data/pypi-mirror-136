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

"""Utilities common for metadata builders for TF frameworks.
"""

import json
import os
from typing import Dict, Text, Any
import tensorflow as tf


def write_metadata_to_file(md_dict: Dict[Text, Any], base_path: Text):
  """Write explanation metadata json to given folder."""
  md_path = os.path.join(
      tf.compat.as_bytes(base_path),
      tf.compat.as_bytes('explanation_metadata.json'))
  with tf.io.gfile.GFile(md_path, 'w') as f:
    json.dump(md_dict, f, indent=2)
