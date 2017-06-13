#!/usr/bin/env python
# coding: utf-8

# Copyright 2011-2017, Nigel Small
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


from hashlib import sha256
from random import randint

import click


def bstr(s):
    return s if isinstance(s, (bytes, bytearray)) else s.encode("utf-8")


def hex_bytes(data):
    return "".join("%02X" % b for b in bytearray(data)).encode("utf-8")


def unhex_bytes(h):
    return bytearray(int(h[i:(i + 2)], 0x10) for i in range(0, len(h), 2))


class AuthUser(object):

    #: Name of user
    user = None

    #:
    digest = None

    @classmethod
    def create(cls, user_name, password):
        inst = cls(user_name, b"SHA-256", None, None)
        inst.set_password(password)
        return inst

    @classmethod
    def load(cls, s):
        assert isinstance(s, (bytes, bytearray))
        fields = s.rstrip().split(b":")
        name = fields[0]
        hash_algorithm, digest, salt = fields[1].split(b",")
        return cls(name, hash_algorithm, unhex_bytes(digest), unhex_bytes(salt))

    def dump(self):
        return (b"%s:%s,%s,%s:" %
                (self.name, self.hash_algorithm, hex_bytes(self.digest), hex_bytes(self.salt)))

    def __init__(self, name, hash_algorithm, digest, salt):
        assert hash_algorithm == b"SHA-256"
        self.name = bstr(name)
        self.hash_algorithm = hash_algorithm
        self.digest = digest
        self.salt = salt

    def __repr__(self):
        return "<AuthUser name=%r>" % self.name

    def set_password(self, password):
        assert self.hash_algorithm == b"SHA-256"
        salt = bytearray(randint(0x00, 0xFF) for _ in range(16))
        m = sha256()
        m.update(salt)
        m.update(bstr(password))
        self.digest = m.digest()
        self.salt = salt

    def check_password(self, password):
        assert self.hash_algorithm == b"SHA-256"
        m = sha256()
        m.update(self.salt)
        m.update(bstr(password))
        return m.digest() == self.digest


class AuthFile(object):

    def __init__(self, name):
        self.name = name

    def __iter__(self):
        try:
            with open(self.name, "rb") as f:
                for line in f:
                    yield AuthUser.load(line)
        except IOError:
            pass

    def append(self, user_name, password):
        line = AuthUser.create(user_name, password).dump()
        if self.name == "-":
            print(line.decode("utf-8"))
        else:
            with open(self.name, "ab") as f:
                f.write(line)
                f.write(b"\r\n")


@click.command()
@click.argument("auth_file")
@click.argument("user_name")
@click.password_option()
def main(auth_file, user_name, password):
    try:
        AuthFile(auth_file).append(user_name, password)
    except Exception as error:
        click.secho(error.args[0], err=True)
        exit(1)
    else:
        exit(0)


if __name__ == "__main__":
    main()
