# Copyright (c) 2021, VRAI Labs and/or its affiliates. All rights reserved.
#
# This software is licensed under the Apache License, Version 2.0 (the
# "License") as published by the Apache Software Foundation.
#
# You may not use this file except in compliance with the License. You may
# obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from . import exceptions
from .supertokens import Supertokens
from .recipe import session
from typing import List, Union, Callable
from .supertokens import SupertokensConfig, InputAppInfo, AppInfo
from .recipe_module import RecipeModule
try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal


def init(app_info: InputAppInfo,
         framework: Literal['fastapi', 'flask', 'django'],
         supertokens_config: SupertokensConfig,
         recipe_list: List[Callable[[AppInfo], RecipeModule]],
         mode: Union[Literal['asgi', 'wsgi'], None] = None,
         telemetry: Union[bool, None] = None):
    return Supertokens.init(app_info, framework, supertokens_config, recipe_list, mode, telemetry)


def get_all_cors_headers():
    return Supertokens.get_instance().get_all_cors_headers()
