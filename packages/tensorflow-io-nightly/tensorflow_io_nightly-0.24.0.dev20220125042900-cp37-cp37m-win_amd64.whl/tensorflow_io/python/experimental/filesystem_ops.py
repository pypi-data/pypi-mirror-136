# Copyright 2021 The TensorFlow Authors. All Rights Reserved.
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
# ==============================================================================
"""filesystem"""

from tensorflow_io.python.ops import core_ops


def set_configuration(scheme, key, value, name=None):
    """
    Set configuration of the file system.

    Args:
      scheme: File system scheme.
      key: The name of the configuration option.
      value: The value of the configuration option.
      name: A name for the operation (optional).

    Returns:
      None.
    """

    return core_ops.io_file_system_set_configuration(
        scheme, key=key, value=value, name=name
    )
