#!/usr/bin/env python3
"""Установка python на deb-based системах.

Актуальная версия - https://www.python.org/ftp/python
"""

import os


def install(python_ver: str) -> None:
    """Устанавливает python.

    :param python_ver: версия python для установки
    """
    os.system("sudo apt -y install build-essential zlib1g-dev libncurses5-dev")
    os.system("sudo apt -y install libgdbm-dev libnss3-dev libsqlite3-dev")
    os.system("sudo apt -y install libssl-dev libsqlite3-dev libreadline-dev")
    os.system("sudo apt -y install libffi-dev libbz2-dev liblzma-dev")

    os.system("mkdir ~/temp ")
    os.system("cd ~/temp")
    os.system(
        f"wget https://www.python.org/ftp/python/{python_ver}/"
        f"Python-{python_ver}.tgz",
    )
    os.system(
        f"tar -xf Python-{python_ver}.tgz && cd Python-{python_ver} || exit",
    )
    os.system('./configure --enable-optimizations && make -j "$(nproc)"')
    os.system("sudo make altinstall")
