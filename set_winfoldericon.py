# -*- coding: utf-8 -*-
#
# Copyright (c) 2024~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

import os
import ctypes
from configparser import ConfigParser

import win32api
from PIL import Image


def set_file_attributes(path: str, *,
                        system: None | bool = None,
                        hidden: None | bool = None,
                        readonly: None | bool = None):
    '''
    A helper function for setting file attributes.
    '''

    def set_flag(current: int, flag: int, is_set: bool):
        return current | flag if is_set else current & (~flag)

    # for all attributes,
    # see https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getfileattributesw

    attr = win32api.GetFileAttributes(path)

    if readonly is not None:
        attr = set_flag(attr, 1, readonly)
    if hidden is not None:
        attr = set_flag(attr, 2, hidden)
    if system is not None:
        attr = set_flag(attr, 4, system)

    win32api.SetFileAttributes(path, attr)


def convert_ico(src: str, dst: str, *, to_square: bool = False):
    '''
    A helper function for convert image file to bitmap icon file.

    The `dst` must endswith `.ico`.
    '''
    if not dst.endswith('.ico'):
        raise ValueError('`dst` must endswith `.ico`')

    def sizize(size: int):
        return (size, size)

    sizes = list(map(sizize, (16, 24, 32, 40, 48, 64, 96, 128, 192, 256)))

    img = Image.open(src)

    if to_square:
        new_size = max(*img.size)
        x = round((new_size - img.size[0]) / 2)
        y = round((new_size - img.size[1]) / 2)
        boximg = Image.new("RGBA", (new_size, new_size), (0, 0, 0, 0))
        boximg.paste(img.convert("RGBA"), (x, y))
        img = boximg

    img.save(dst, bitmap_format="bmp", sizes=sizes)


def notify_shell():
    '''
    A helper function for notify windows shell refresh icon.
    '''
    # see https://learn.microsoft.com/zh-cn/windows/win32/api/shlobj_core/nf-shlobj_core-shchangenotify
    # alsosee https://github.com/demberto/FolderIkon/blob/master/folderikon/notify_shell.py
    SHCNE_ASSOCCHANGED = 0x08000000
    SHCNF_IDLIST = 0x0000
    ctypes.windll.shell32.SHChangeNotify(
        SHCNE_ASSOCCHANGED, SHCNF_IDLIST, 0, 0)


def set_foldericon(folder_path: str, icon_path: str, *, notify_shell: bool = True):
    # step1: create ini
    inipath = os.path.join(folder_path, 'desktop.ini')
    if not os.path.exists(inipath):
        config = ConfigParser()
        config.optionxform = lambda option: option
        config['.ShellClassInfo'] = {
            'IconResource': f'{os.path.relpath(icon_path, folder_path)},0'
        }
        with open(inipath, 'a') as stream:
            config.write(stream)

    # step2: update attribute,
    # see http://msdn.microsoft.com/en-us/library/cc144102(VS.85).aspx
    set_file_attributes(inipath, system=True, hidden=True)
    set_file_attributes(folder_path, system=True)

    # step3: notify shell
    if notify_shell:
        notify_shell()


__all__ = [
    'set_foldericon',
    'convert_ico',
    'set_file_attributes', # allows user to change the icon file attributes,
    'notify_shell',
]
