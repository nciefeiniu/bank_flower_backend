# !/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib

from bank.default import DEFAULT_SALT


def get_md5(content: str) -> str:
    if not content:
        return ''
    md5hash = hashlib.md5(content.encode())
    return md5hash.hexdigest()


def get_md5_salt(content: str, salt=DEFAULT_SALT):
    return get_md5(content + salt)


if __name__ == '__main__':
    print(get_md5('afwafawfa'))