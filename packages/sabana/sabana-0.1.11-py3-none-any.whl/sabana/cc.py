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
from os.path import basename, exists
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


# Note: Try to follow:
#       https://www.gnu.org/software/make/manual/html_node/Implicit-Variables.html
class Build:
    """
    Build: provides a handler to interact with Sabana's Build service
    """

    __endpoint = "https://build.sabana.io"
    __supported_march = ["rv32im"]

    def __init__(self, march=None):
        if march not in Build.__supported_march:
            raise BuildError("Architecture not supported")
        else:
            self.march = march

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
        self.files_list = {}
        self.cflags_list = []
        self.ldflags_list = []

    def file(self, path, flags=None):
        if not exists(path):
            raise BuildError("ERROR: File does not exist")
        else:
            if path not in self.files_list:
                self.files_list[path] = []
            if isinstance(flags, str):
                self.files_list[path].extend(flags.split())

    def cflags(self, flags):
        if isinstance(flags, str):
            flags_list = flags.split()
            for flag in flags_list:
                if "march" not in flag:
                    self.cflags_list.append(flag)
                else:
                    print("WARNING: ignoring march flag provided with cflags")

    def ldflags(self, flags):
        if isinstance(flags, str):
            flags_list = flags.split()
            for flag in flags_list:
                if "march" not in flag:
                    self.ldflags_list.append(flag)
                else:
                    print("WARNING: ignoring march flag provided with ldflags")
        else:
            raise BuildError("ERROR: Expecting flags as string")

    def compile(self):
        result = {}
        url = f"{self.__endpoint}/api/v0/cc"

        # Create in memory
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode="w:gz") as tar:
            for path in self.files_list:
                # Using filter to make a flat tar file
                tar.add(path, filter=flatten_name)

        tarbytes = base64.b64encode(buffer.getvalue())
        tarstr = tarbytes.decode("utf-8")
        req = {
            "tar": tarstr,
            "cflags": self.cflags_list,
            "ldflags": self.ldflags_list,
            "arch": self.march,
            "version": "11.1.0",
        }

        for file in self.files_list:
            req[basename(file)] = self.files_list[file]

        try:
            res = post(req, url, self.access_token, self.id_token)
        except TokenError as e:
            print(login_msg)
            raise BuildError(login_msg)
        except PostError as e:
            raise BuildError("Failed executing the program: {}".format(e))
        else:
            if "program" in res.keys() and ".dasm" in res.keys():
                prog_bytes = base64.b64decode(res["program"].encode("utf-8"))
                result["binarray"] = np.frombuffer(prog_bytes, dtype=np.uint8)
                result["objdump"] = res[".dasm"]
                return result
            else:
                raise BuildError("ERROR: bad response from server")
