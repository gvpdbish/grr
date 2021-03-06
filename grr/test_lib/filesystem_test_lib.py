#!/usr/bin/env python
"""A test utilities for interacting with filesystem."""
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import platform
import subprocess
import unittest


def Command(name, args=None, system=None, message=None):
  """Executes given commend as a subprocess for testing purposes.

  If the command fails, is not available or is not compatible with the operating
  system a test case that tried to called is skipped.

  Args:
    name: A name of the command to execute (e.g. `ls`).
    args: A list of arguments for the commend (e.g. `-l`, `-a`).
    system: An operating system that the command should be compatible with.
    message: A message to skip the test with in case of a failure.

  Raises:
    SkipTest: If command execution fails.
  """
  args = args or []
  if system is not None and platform.system() != system:
    raise unittest.SkipTest("`%s` available only on `%s`" % (name, system))
  if subprocess.call(["which", name], stdout=open("/dev/null", "w")) != 0:
    raise unittest.SkipTest("`%s` command is not available" % name)
  if subprocess.call([name] + args, stdout=open("/dev/null", "w")) != 0:
    raise unittest.SkipTest(message or "`%s` call failed" % name)


def Chflags(filepath, flags=None):
  """Executes a `chflags` command with specified flags for testing purposes.

  Calling this on platforms different than macOS will skip the test.

  Args:
    filepath: A path to the file to change the flags of.
    flags: A list of flags to be changed (see `chflags` documentation).
  """
  flags = flags or []
  Command("chflags", args=[",".join(flags), filepath], system="Darwin")


def Chattr(filepath, attrs=None):
  """Executes a `chattr` command with specified attributes for testing purposes.

  Calling this on platforms different than Linux will skip the test.

  Args:
    filepath: A path to the file to change the attributes of.
    attrs: A list of attributes to be changed (see `chattr` documentation).
  """
  attrs = attrs or []
  message = "file attributes not supported by filesystem"
  Command("chattr", args=attrs + [filepath], system="Linux", message=message)


def SetExtAttr(filepath, name, value):
  """Sets an extended file attribute of a given file for testing purposes.

  Calling this on platforms different than Linux or macOS will skip the test.

  Args:
    filepath: A path to the file to set an extended attribute of.
    name: A name of the extended attribute to set.
    value: A value of the extended attribute being set.

  Raises:
    SkipTest: If called on unsupported platform.
  """
  system = platform.system()
  if system == "Linux":
    _SetExtAttrLinux(filepath, name=name, value=value)
  elif system == "Darwin":
    _SetExtAttrOsx(filepath, name=name, value=value)
  else:
    message = "setting extended attributes is not supported on `%s`" % system
    raise unittest.SkipTest(message)


def _SetExtAttrLinux(filepath, name, value):
  args = ["-n", name, "-v", value, filepath]
  message = "extended attributes not supported by filesystem"
  Command("setfattr", args=args, system="Linux", message=message)


def _SetExtAttrOsx(filepath, name, value):
  args = ["-w", name, value, filepath]
  message = "extended attributes are not supported"
  Command("xattr", args=args, system="Drawin", message=message)
