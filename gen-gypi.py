#!/usr/bin/env python

from subprocess import call
from shutil import rmtree

from os import path, pathsep, environ
from platform import machine

import re

script_dir        = path.dirname(path.realpath(__file__))
libsodium_dir     = script_dir
libsodium_src_dir = path.join(libsodium_dir, 'src', 'libsodium')
makefile_am       = path.join(libsodium_dir, 'Makefile.am')
sodium_gypi       = path.join(script_dir, 'sodium.gypi')
makefile          = path.join(libsodium_src_dir, 'Makefile')

def gen_makefile():
  print 'Generating libsodium Makefile to determine "define" variables.'
  autogen_cmd_code = call('./autogen.sh', cwd=libsodium_dir)
  if autogen_cmd_code != 0:
    print 'autogen failed, make sure to have automake installed: https://www.gnu.org/software/automake/'
    return

  configure_cmd_code = call('./configure', cwd=libsodium_dir)
  if configure_cmd_code != 0:
    print './configure failed, cannot continue building libsodium.'
    return

def gen_defines(src):
  defs_regex = r'-D(.*?)(?:(?=\s?-D)|$)'
  defs = re.findall(defs_regex, src)
  if defs is None:
    print 'No DEFS found in libsodium Makefile, this probably an error!'
    return

  def_str = ''

  # it's gyp so we don't care about the trailing comma
  for define in defs:
    def_str += '\'' + define.replace('\\', '') + '\', \n      '

  return def_str

def gen_sources(src):
  lines = src.splitlines()
  start_regex = re.compile("am__libsodium_la_SOURCES_DIST")
  end_regex = re.compile("am__objects_1")

  s = ''
  i = 0
  l = len(lines)
  # find the start of sources
  while (i < l and not start_regex.match(lines[i])):
    i = i + 1

  i = i + 1

  # read up to the end of sources
  while (i < l and not end_regex.match(lines[i])):
    line = lines[i].strip()
    # sometimes one line has multiple paths separated by a space
    for p in line.split(' '):
      if len(p) <= 1: continue
      s = s + '\'src/libsodium/' + p.replace('\\', '').strip() + '\',\n      '
    i = i + 1

  return s


def gen_sodium_gypi():
  if not path.isfile(makefile): gen_makefile()

  with open(makefile, 'r') as f:
    src = f.read()

  defines = gen_defines(src)
  sources = gen_sources(src)

  s = """{
  'variables': {
    'sodium_architecture': '{{{architecture}}}',
    'sodium_defines': [
      {{{defines}}}
    ],
    'sodium_sources': [
      {{{sources}}}
    ]
  }
}"""

  s = s.replace('{{{defines}}}', defines)
  s = s.replace('{{{sources}}}', sources)
  s = s.replace('{{{architecture}}}', machine())

  with open(sodium_gypi, 'w') as f:
    f.write(s)

if not path.isfile(sodium_gypi): gen_sodium_gypi()
