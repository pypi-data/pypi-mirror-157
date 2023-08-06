# This file is a part of Arjuna
# Copyright 2015-2021 Rahul Verma

# Website: www.RahulVerma.net

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#   http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

class HttpCookie:

    def __init__(self, session, cookie):
        self.__cookie = cookie

    @property
    def _cookie(self):
        return self.__cookie

    @property
    def value(self):
        '''
        Value stored in this cookie.
        '''
        return self._cookie.value

    @property
    def secure(self):
        '''
        If secure flag is set for this cookie, this value is True, else False.
        '''
        return self._cookie.secure

    @property
    def httponly(self):
        '''
        If HttpOnly flag is set for this cookie, this value is True, else False.
        '''
        return self._cookie.has_nonstandard_attr("HttpOnly")
