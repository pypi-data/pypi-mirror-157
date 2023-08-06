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

from arjuna.tpi.helper.arjtype import NotFound

class JsonExtractor:

    def __init__(self, response):
        self.__response =  response

    @property
    def response(self):
        return self.__response

    def store(self, name, jpath, strict):
        try:
            value = self.response.json.find(jpath)
        except Exception:
            if not strict:
                value = NotFound()
            else:
                raise Exception(f"Issue in extracting value for >{name}< as no element was found using jpath >{jpath}<.")

        self.response.store[name] = value

