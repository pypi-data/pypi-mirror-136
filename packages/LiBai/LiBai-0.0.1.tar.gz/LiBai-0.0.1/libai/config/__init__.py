# coding=utf-8
# Copyright 2021 The OneFlow Authors. All rights reserved.
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

from .arguments import default_argument_parser
from .config import configurable, try_get_key
from .instantiate import instantiate
from .lazy import LazyCall, LazyConfig

__all__ = [
    "LazyCall",
    "LazyConfig",
    "instantiate",
    "default_argument_parser",
    "configurable",
    "try_get_key",
]
