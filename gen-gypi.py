#!/usr/bin/env python

from subprocess import call
from shutil import rmtree

from os import path, pathsep, environ
from platform import system

import re

script_dir        = path.dirname(path.realpath(__file__))
libsodium_dir     = script_dir
libsodium_src_dir = path.join(libsodium_dir, 'src', 'libsodium')
makefile_am       = path.join(libsodium_dir, 'Makefile.am')
# defines are slightly different for Linux and mac
sodium_linux_gypi = path.join(script_dir, 'sodium.linux.gypi')
sodium_mac_gypi   = path.join(script_dir, 'sodium.mac.gypi')
makefile          = path.join(libsodium_src_dir, 'Makefile')

os = system()
is_mac = os == 'Darwin'
is_linux = os == 'Linux'

# only supporting operating systems ATM
# if we need support for things posing as such, i.e. The Doors or Windows, we'll need to update this
if not (is_mac or is_linux):
  print 'Sorry only actual operating systems are supported.'
  exit(1)

if is_mac:
  sodium_gypi = sodium_mac_gypi
else:
  sodium_gypi = sodium_linux_gypi

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


def gen_sodium_gypi(os_name):
  if not path.isfile(makefile): gen_makefile()

  with open(makefile, 'r') as f:
    src = f.read()

  sources = gen_sources(src)
  defines = gen_defines(src)

  s = """{
  # DON'T EDIT THIS FILE, RUN gen-gypi.py INSTEAD
  # contains platform specific variables (different for Linux/mac)
  # as well as needed sources for sodium dist build
  'variables': {
    'sodium_{{{os_name}}}_defines': [
      {{{defines}}}
    ],
    'sodium_{{{os_name}}}_sources': [
      {{{sources}}}
    ],

  }
}"""

  s = s.replace('{{{defines}}}', defines)
  s = s.replace('{{{sources}}}', sources)
  s = s.replace('{{{os_name}}}', os_name)

  with open(sodium_gypi, 'w') as f:
    f.write(s)


gen_sodium_gypi('mac' if is_mac else 'linux')

ran_on = 'Mac OSX' if is_mac else 'Linux'
need_on = 'Linux' if is_mac else 'Mac OSX'
print 'YOU RAN THIS SCRIPT ON %s PLEASE ENSURE THAT IT ALSO RUNS ON %s!' % (ran_on, need_on)
