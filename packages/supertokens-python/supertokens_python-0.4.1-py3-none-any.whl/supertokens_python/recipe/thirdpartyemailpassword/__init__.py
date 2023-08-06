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
from typing import Union, List

from .utils import InputOverrideConfig

from supertokens_python.recipe.thirdparty.provider import Provider

from .recipe import ThirdPartyEmailPasswordRecipe
from . import exceptions
from supertokens_python.recipe.thirdparty import (
    Google,
    Github,
    Apple,
    Facebook,
    Discord,
    GoogleWorkspaces
)
from ..emailpassword import InputResetPasswordUsingTokenFeature, InputSignUpFeature
from ..emailverification.utils import InputEmailVerificationConfig

Google = Google
Github = Github
Apple = Apple
Facebook = Facebook
Discord = Discord
GoogleWorkspaces = GoogleWorkspaces


def init(sign_up_feature: Union[InputSignUpFeature, None] = None,
         reset_password_using_token_feature: Union[InputResetPasswordUsingTokenFeature, None] = None,
         email_verification_feature: Union[InputEmailVerificationConfig, None] = None,
         override: Union[InputOverrideConfig, None] = None,
         providers: Union[List[Provider], None] = None):
    return ThirdPartyEmailPasswordRecipe.init(sign_up_feature, reset_password_using_token_feature,
                                              email_verification_feature,
                                              override, providers)
