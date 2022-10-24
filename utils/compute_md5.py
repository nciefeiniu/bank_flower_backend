# !/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib


def get_md5(content: str) -> str:
    if not content:
        return ''
    md5hash = hashlib.md5(content.encode())
    return md5hash.hexdigest()


if __name__ == '__main__':
    print(get_md5('afwafawfa'))