
"""
django-t2s -- a very simple usage django utility for t2s

Copyright (C) 2014 - Yorkie, Firmus Asia
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:
1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.
3. Neither the name of the libEtPan! project nor the names of its
   contributors may be used to endorse or promote products derived
   from this software without specific prior written permission.
 *
THIS SOFTWARE IS PROVIDED BY THE AUTHORS AND CONTRIBUTORS ``AS IS'' AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHORS OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
SUCH DAMAGE.
"""

import os
from ctypes.util import find_library
from ctypes import CDLL, cast, c_char_p, c_int, c_size_t, c_void_p

_libcfile = find_library('c') or 'libc.so.6'
libc = CDLL(_libcfile, use_errno=True)

_libopenccfile = os.environ.get('LIBOPENCC') or find_library('opencc')

if _libopenccfile:
  libopencc = CDLL(_libopenccfile, use_errno=True)
else:
  libopencc = CDLL('libopencc.so.1', use_errno=True)

libc.free.argtypes = [c_void_p]
libopencc.opencc_open.restype = c_void_p
libopencc.opencc_convert_utf8.argtypes = [c_void_p, c_char_p, c_size_t]
libopencc.opencc_convert_utf8.restype = c_void_p
libopencc.opencc_close.argtypes = [c_void_p]
libopencc.opencc_perror.argtypes = [c_char_p]
libopencc.opencc_dict_load.argtypes = [c_void_p, c_char_p, c_int]

CONFIGS = [
  'zhs2zhtw_p.ini', 'zhs2zhtw_v.ini', 'zhs2zhtw_vp.ini',
  'zht2zhtw_p.ini', 'zht2zhtw_v.ini', 'zht2zhtw_vp.ini',
  'zhtw2zhs.ini', 'zhtw2zht.ini', 'zhtw2zhcn_s.ini', 'zhtw2zhcn_t.ini',
  'zhs2zht.ini', 'zht2zhs.ini',
]

def convert(text, config='zht2zhs.ini'):
  assert config in CONFIGS
  od = libopencc.opencc_open(c_char_p(config))
  retv_i = libopencc.opencc_convert_utf8(od, text, len(text))
  if retv_i == -1:
    raise Exception('OpenCC Convert Error')
  retv_c = cast(retv_i, c_char_p)
  value = retv_c.value
  libc.free(retv_c)
  libopencc.opencc_close(od)
  return value
