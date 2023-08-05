# Copyright 2022 Sabana Technologies, Inc
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

import base64
import tarfile
import io
import numpy as np
import sys
from os.path import basename
from os import getenv
from sabana.common import (
    get_config,
    get_access_token,
    get_id_token,
    post,
    TokenError,
    PostError,
    login_msg,
)


class BuildError(Exception):
    pass


def flatten_name(tarinfo):
    tarinfo.name = basename(tarinfo.name)
    return tarinfo


class Build:
    """
    Build: provides a handler to interact with Sabana's Build service
    """

    __endpoint = "https://build.sabana.io"

    def __init__(self):
        try:
            config = get_config()
            self.access_token = get_access_token(config)
            self.id_token = get_id_token(config)
        except TokenError:
            self.access_token = getenv("SABANA_ACCESS_TOKEN")
            self.id_token = getenv("SABANA_ID_TOKEN")
            if not isinstance(self.access_token, str) or not isinstance(
                self.id_token, str
            ):
                print("ERROR: Could not find credentials on local file or environment.")
                print(
                    "       Use the following command to log-in using the Sabana CLI:\n"
                )
                print("sabana login\n")
                print("Alternatively setup the following environment variables:")
                print("SABANA_ACCESS_TOKEN, SABANA_ID_TOKEN")
                sys.exit(-1)
        except Exception as e:
            print("Fatal error trying to get Sabana credentials by the Build object.")
            print("Contact Sabana for support.")
            sys.exit(-1)
        self.files = []

    def file(self, path):
        self.files.append(path)

    def compile(self):
        url = f"{self.__endpoint}/api/v0/cc"

        # Create in memory
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode="w:gz") as tar:
            for path in self.files:
                # Using filter to make a flat tar file
                tar.add(path, filter=flatten_name)

        tarbytes = base64.b64encode(buffer.getvalue())
        tarstr = tarbytes.decode("utf-8")
        req = {"tar": tarstr}

        try:
            res = post(req, url, self.access_token, self.id_token)
        except TokenError as e:
            print(login_msg)
            raise BuildError(login_msg)
        except PostError as e:
            raise BuildError("Failed executing the program: {}".format(e))
        else:
            if "program" in res.keys() and ".dasm" in res.keys():
                res_list = base64.b64decode(res["program"].encode("utf-8"))
                dasm = res[".dasm"]
                return (np.frombuffer(res_list, dtype=np.uint8), dasm)
            else:
                raise BuildError("ERROR: bad response from server")
