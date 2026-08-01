r"""Wrapper for SegSegForce.h

Generated with:
/workspace/core/pydis/python/ctypesgen/run.py --cpp=gcc -E /workspace/core/pydis/python/../c/calforce/SegSegForce.h /workspace/core/pydis/python/../c/calforce/SegmentStress.h /workspace/core/pydis/python/../c/calforce/StressDueToSeg.h /workspace/core/pydis/python/../c/calforce/SegSegForce_SBN1.h /workspace/core/pydis/python/../c/calforce/SegSegForce_SBN1_SBA.h /workspace/core/pydis/python/../c/include/Home.h /workspace/core/pydis/python/../c/include/Init.h /workspace/core/pydis/python/../c/include/ParadisProto.h /workspace/core/pydis/python/../c/include/Util.h /workspace/core/pydis/python/../c/include/Force.h /workspace/core/pydis/python/../c/include/Timer.h /workspace/core/pydis/python/../c/include/OpList.h -l libpydis.so -o pydis_lib.py

Do not modify this file.
"""

__docformat__ = "restructuredtext"

# Begin preamble for Python

import ctypes
import sys
from ctypes import *  # noqa: F401, F403

_int_types = (ctypes.c_int16, ctypes.c_int32)
if hasattr(ctypes, "c_int64"):
    # Some builds of ctypes apparently do not have ctypes.c_int64
    # defined; it's a pretty good bet that these builds do not
    # have 64-bit pointers.
    _int_types += (ctypes.c_int64,)
for t in _int_types:
    if ctypes.sizeof(t) == ctypes.sizeof(ctypes.c_size_t):
        c_ptrdiff_t = t
del t
del _int_types



class UserString:
    def __init__(self, seq):
        if isinstance(seq, bytes):
            self.data = seq
        elif isinstance(seq, UserString):
            self.data = seq.data[:]
        else:
            self.data = str(seq).encode()

    def __bytes__(self):
        return self.data

    def __str__(self):
        return self.data.decode()

    def __repr__(self):
        return repr(self.data)

    def __int__(self):
        return int(self.data.decode())

    def __long__(self):
        return int(self.data.decode())

    def __float__(self):
        return float(self.data.decode())

    def __complex__(self):
        return complex(self.data.decode())

    def __hash__(self):
        return hash(self.data)

    def __le__(self, string):
        if isinstance(string, UserString):
            return self.data <= string.data
        else:
            return self.data <= string

    def __lt__(self, string):
        if isinstance(string, UserString):
            return self.data < string.data
        else:
            return self.data < string

    def __ge__(self, string):
        if isinstance(string, UserString):
            return self.data >= string.data
        else:
            return self.data >= string

    def __gt__(self, string):
        if isinstance(string, UserString):
            return self.data > string.data
        else:
            return self.data > string

    def __eq__(self, string):
        if isinstance(string, UserString):
            return self.data == string.data
        else:
            return self.data == string

    def __ne__(self, string):
        if isinstance(string, UserString):
            return self.data != string.data
        else:
            return self.data != string

    def __contains__(self, char):
        return char in self.data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.__class__(self.data[index])

    def __getslice__(self, start, end):
        start = max(start, 0)
        end = max(end, 0)
        return self.__class__(self.data[start:end])

    def __add__(self, other):
        if isinstance(other, UserString):
            return self.__class__(self.data + other.data)
        elif isinstance(other, bytes):
            return self.__class__(self.data + other)
        else:
            return self.__class__(self.data + str(other).encode())

    def __radd__(self, other):
        if isinstance(other, bytes):
            return self.__class__(other + self.data)
        else:
            return self.__class__(str(other).encode() + self.data)

    def __mul__(self, n):
        return self.__class__(self.data * n)

    __rmul__ = __mul__

    def __mod__(self, args):
        return self.__class__(self.data % args)

    # the following methods are defined in alphabetical order:
    def capitalize(self):
        return self.__class__(self.data.capitalize())

    def center(self, width, *args):
        return self.__class__(self.data.center(width, *args))

    def count(self, sub, start=0, end=sys.maxsize):
        return self.data.count(sub, start, end)

    def decode(self, encoding=None, errors=None):  # XXX improve this?
        if encoding:
            if errors:
                return self.__class__(self.data.decode(encoding, errors))
            else:
                return self.__class__(self.data.decode(encoding))
        else:
            return self.__class__(self.data.decode())

    def encode(self, encoding=None, errors=None):  # XXX improve this?
        if encoding:
            if errors:
                return self.__class__(self.data.encode(encoding, errors))
            else:
                return self.__class__(self.data.encode(encoding))
        else:
            return self.__class__(self.data.encode())

    def endswith(self, suffix, start=0, end=sys.maxsize):
        return self.data.endswith(suffix, start, end)

    def expandtabs(self, tabsize=8):
        return self.__class__(self.data.expandtabs(tabsize))

    def find(self, sub, start=0, end=sys.maxsize):
        return self.data.find(sub, start, end)

    def index(self, sub, start=0, end=sys.maxsize):
        return self.data.index(sub, start, end)

    def isalpha(self):
        return self.data.isalpha()

    def isalnum(self):
        return self.data.isalnum()

    def isdecimal(self):
        return self.data.isdecimal()

    def isdigit(self):
        return self.data.isdigit()

    def islower(self):
        return self.data.islower()

    def isnumeric(self):
        return self.data.isnumeric()

    def isspace(self):
        return self.data.isspace()

    def istitle(self):
        return self.data.istitle()

    def isupper(self):
        return self.data.isupper()

    def join(self, seq):
        return self.data.join(seq)

    def ljust(self, width, *args):
        return self.__class__(self.data.ljust(width, *args))

    def lower(self):
        return self.__class__(self.data.lower())

    def lstrip(self, chars=None):
        return self.__class__(self.data.lstrip(chars))

    def partition(self, sep):
        return self.data.partition(sep)

    def replace(self, old, new, maxsplit=-1):
        return self.__class__(self.data.replace(old, new, maxsplit))

    def rfind(self, sub, start=0, end=sys.maxsize):
        return self.data.rfind(sub, start, end)

    def rindex(self, sub, start=0, end=sys.maxsize):
        return self.data.rindex(sub, start, end)

    def rjust(self, width, *args):
        return self.__class__(self.data.rjust(width, *args))

    def rpartition(self, sep):
        return self.data.rpartition(sep)

    def rstrip(self, chars=None):
        return self.__class__(self.data.rstrip(chars))

    def split(self, sep=None, maxsplit=-1):
        return self.data.split(sep, maxsplit)

    def rsplit(self, sep=None, maxsplit=-1):
        return self.data.rsplit(sep, maxsplit)

    def splitlines(self, keepends=0):
        return self.data.splitlines(keepends)

    def startswith(self, prefix, start=0, end=sys.maxsize):
        return self.data.startswith(prefix, start, end)

    def strip(self, chars=None):
        return self.__class__(self.data.strip(chars))

    def swapcase(self):
        return self.__class__(self.data.swapcase())

    def title(self):
        return self.__class__(self.data.title())

    def translate(self, *args):
        return self.__class__(self.data.translate(*args))

    def upper(self):
        return self.__class__(self.data.upper())

    def zfill(self, width):
        return self.__class__(self.data.zfill(width))


class MutableString(UserString):
    """mutable string objects

    Python strings are immutable objects.  This has the advantage, that
    strings may be used as dictionary keys.  If this property isn't needed
    and you insist on changing string values in place instead, you may cheat
    and use MutableString.

    But the purpose of this class is an educational one: to prevent
    people from inventing their own mutable string class derived
    from UserString and than forget thereby to remove (override) the
    __hash__ method inherited from UserString.  This would lead to
    errors that would be very hard to track down.

    A faster and better solution is to rewrite your program using lists."""

    def __init__(self, string=""):
        self.data = string

    def __hash__(self):
        raise TypeError("unhashable type (it is mutable)")

    def __setitem__(self, index, sub):
        if index < 0:
            index += len(self.data)
        if index < 0 or index >= len(self.data):
            raise IndexError
        self.data = self.data[:index] + sub + self.data[index + 1 :]

    def __delitem__(self, index):
        if index < 0:
            index += len(self.data)
        if index < 0 or index >= len(self.data):
            raise IndexError
        self.data = self.data[:index] + self.data[index + 1 :]

    def __setslice__(self, start, end, sub):
        start = max(start, 0)
        end = max(end, 0)
        if isinstance(sub, UserString):
            self.data = self.data[:start] + sub.data + self.data[end:]
        elif isinstance(sub, bytes):
            self.data = self.data[:start] + sub + self.data[end:]
        else:
            self.data = self.data[:start] + str(sub).encode() + self.data[end:]

    def __delslice__(self, start, end):
        start = max(start, 0)
        end = max(end, 0)
        self.data = self.data[:start] + self.data[end:]

    def immutable(self):
        return UserString(self.data)

    def __iadd__(self, other):
        if isinstance(other, UserString):
            self.data += other.data
        elif isinstance(other, bytes):
            self.data += other
        else:
            self.data += str(other).encode()
        return self

    def __imul__(self, n):
        self.data *= n
        return self


class String(MutableString, ctypes.Union):
    _fields_ = [("raw", ctypes.POINTER(ctypes.c_char)), ("data", ctypes.c_char_p)]

    def __init__(self, obj=b""):
        if isinstance(obj, (bytes, UserString)):
            self.data = bytes(obj)
        else:
            self.raw = obj

    def __len__(self):
        return self.data and len(self.data) or 0

    def from_param(cls, obj):
        # Convert None or 0
        if obj is None or obj == 0:
            return cls(ctypes.POINTER(ctypes.c_char)())

        # Convert from String
        elif isinstance(obj, String):
            return obj

        # Convert from bytes
        elif isinstance(obj, bytes):
            return cls(obj)

        # Convert from str
        elif isinstance(obj, str):
            return cls(obj.encode())

        # Convert from c_char_p
        elif isinstance(obj, ctypes.c_char_p):
            return obj

        # Convert from POINTER(ctypes.c_char)
        elif isinstance(obj, ctypes.POINTER(ctypes.c_char)):
            return obj

        # Convert from raw pointer
        elif isinstance(obj, int):
            return cls(ctypes.cast(obj, ctypes.POINTER(ctypes.c_char)))

        # Convert from ctypes.c_char array
        elif isinstance(obj, ctypes.c_char * len(obj)):
            return obj

        # Convert from object
        else:
            return String.from_param(obj._as_parameter_)

    from_param = classmethod(from_param)


def ReturnString(obj, func=None, arguments=None):
    return String.from_param(obj)


# As of ctypes 1.0, ctypes does not support custom error-checking
# functions on callbacks, nor does it support custom datatypes on
# callbacks, so we must ensure that all callbacks return
# primitive datatypes.
#
# Non-primitive return values wrapped with UNCHECKED won't be
# typechecked, and will be converted to ctypes.c_void_p.
def UNCHECKED(type):
    if hasattr(type, "_type_") and isinstance(type._type_, str) and type._type_ != "P":
        return type
    else:
        return ctypes.c_void_p


# ctypes doesn't have direct support for variadic functions, so we have to write
# our own wrapper class
class _variadic_function(object):
    def __init__(self, func, restype, argtypes, errcheck):
        self.func = func
        self.func.restype = restype
        self.argtypes = argtypes
        if errcheck:
            self.func.errcheck = errcheck

    def _as_parameter_(self):
        # So we can pass this variadic function as a function pointer
        return self.func

    def __call__(self, *args):
        fixed_args = []
        i = 0
        for argtype in self.argtypes:
            # Typecheck what we can
            fixed_args.append(argtype.from_param(args[i]))
            i += 1
        return self.func(*fixed_args + list(args[i:]))


def ord_if_char(value):
    """
    Simple helper used for casts to simple builtin types:  if the argument is a
    string type, it will be converted to it's ordinal value.

    This function will raise an exception if the argument is string with more
    than one characters.
    """
    return ord(value) if (isinstance(value, bytes) or isinstance(value, str)) else value

# End preamble

_libs = {}
_libdirs = []

# Begin loader

"""
Load libraries - appropriately for all our supported platforms
"""
# ----------------------------------------------------------------------------
# Copyright (c) 2008 David James
# Copyright (c) 2006-2008 Alex Holkner
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of pyglet nor the names of its
#    contributors may be used to endorse or promote products
#    derived from this software without specific prior written
#    permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------

import ctypes
import ctypes.util
import glob
import os.path
import platform
import re
import sys


def _environ_path(name):
    """Split an environment variable into a path-like list elements"""
    if name in os.environ:
        return os.environ[name].split(":")
    return []


class LibraryLoader:
    """
    A base class For loading of libraries ;-)
    Subclasses load libraries for specific platforms.
    """

    # library names formatted specifically for platforms
    name_formats = ["%s"]

    class Lookup:
        """Looking up calling conventions for a platform"""

        mode = ctypes.DEFAULT_MODE

        def __init__(self, path):
            super(LibraryLoader.Lookup, self).__init__()
            self.access = dict(cdecl=ctypes.CDLL(path, self.mode))

        def get(self, name, calling_convention="cdecl"):
            """Return the given name according to the selected calling convention"""
            if calling_convention not in self.access:
                raise LookupError(
                    "Unknown calling convention '{}' for function '{}'".format(
                        calling_convention, name
                    )
                )
            return getattr(self.access[calling_convention], name)

        def has(self, name, calling_convention="cdecl"):
            """Return True if this given calling convention finds the given 'name'"""
            if calling_convention not in self.access:
                return False
            return hasattr(self.access[calling_convention], name)

        def __getattr__(self, name):
            return getattr(self.access["cdecl"], name)

    def __init__(self):
        self.other_dirs = []

    def __call__(self, libname):
        """Given the name of a library, load it."""
        paths = self.getpaths(libname)

        for path in paths:
            # noinspection PyBroadException
            try:
                return self.Lookup(path)
            except Exception:  # pylint: disable=broad-except
                pass

        raise ImportError("Could not load %s." % libname)

    def getpaths(self, libname):
        """Return a list of paths where the library might be found."""
        if os.path.isabs(libname):
            yield libname
        else:
            # search through a prioritized series of locations for the library

            # we first search any specific directories identified by user
            for dir_i in self.other_dirs:
                for fmt in self.name_formats:
                    # dir_i should be absolute already
                    yield os.path.join(dir_i, fmt % libname)

            # check if this code is even stored in a physical file
            try:
                this_file = __file__
            except NameError:
                this_file = None

            # then we search the directory where the generated python interface is stored
            if this_file is not None:
                for fmt in self.name_formats:
                    yield os.path.abspath(os.path.join(os.path.dirname(__file__), fmt % libname))

            # now, use the ctypes tools to try to find the library
            for fmt in self.name_formats:
                path = ctypes.util.find_library(fmt % libname)
                if path:
                    yield path

            # then we search all paths identified as platform-specific lib paths
            for path in self.getplatformpaths(libname):
                yield path

            # Finally, we'll try the users current working directory
            for fmt in self.name_formats:
                yield os.path.abspath(os.path.join(os.path.curdir, fmt % libname))

    def getplatformpaths(self, _libname):  # pylint: disable=no-self-use
        """Return all the library paths available in this platform"""
        return []


# Darwin (Mac OS X)


class DarwinLibraryLoader(LibraryLoader):
    """Library loader for MacOS"""

    name_formats = [
        "lib%s.dylib",
        "lib%s.so",
        "lib%s.bundle",
        "%s.dylib",
        "%s.so",
        "%s.bundle",
        "%s",
    ]

    class Lookup(LibraryLoader.Lookup):
        """
        Looking up library files for this platform (Darwin aka MacOS)
        """

        # Darwin requires dlopen to be called with mode RTLD_GLOBAL instead
        # of the default RTLD_LOCAL.  Without this, you end up with
        # libraries not being loadable, resulting in "Symbol not found"
        # errors
        mode = ctypes.RTLD_GLOBAL

    def getplatformpaths(self, libname):
        if os.path.pathsep in libname:
            names = [libname]
        else:
            names = [fmt % libname for fmt in self.name_formats]

        for directory in self.getdirs(libname):
            for name in names:
                yield os.path.join(directory, name)

    @staticmethod
    def getdirs(libname):
        """Implements the dylib search as specified in Apple documentation:

        http://developer.apple.com/documentation/DeveloperTools/Conceptual/
            DynamicLibraries/Articles/DynamicLibraryUsageGuidelines.html

        Before commencing the standard search, the method first checks
        the bundle's ``Frameworks`` directory if the application is running
        within a bundle (OS X .app).
        """

        dyld_fallback_library_path = _environ_path("DYLD_FALLBACK_LIBRARY_PATH")
        if not dyld_fallback_library_path:
            dyld_fallback_library_path = [
                os.path.expanduser("~/lib"),
                "/usr/local/lib",
                "/usr/lib",
            ]

        dirs = []

        if "/" in libname:
            dirs.extend(_environ_path("DYLD_LIBRARY_PATH"))
        else:
            dirs.extend(_environ_path("LD_LIBRARY_PATH"))
            dirs.extend(_environ_path("DYLD_LIBRARY_PATH"))
            dirs.extend(_environ_path("LD_RUN_PATH"))

        if hasattr(sys, "frozen") and getattr(sys, "frozen") == "macosx_app":
            dirs.append(os.path.join(os.environ["RESOURCEPATH"], "..", "Frameworks"))

        dirs.extend(dyld_fallback_library_path)

        return dirs


# Posix


class PosixLibraryLoader(LibraryLoader):
    """Library loader for POSIX-like systems (including Linux)"""

    _ld_so_cache = None

    _include = re.compile(r"^\s*include\s+(?P<pattern>.*)")

    name_formats = ["lib%s.so", "%s.so", "%s"]

    class _Directories(dict):
        """Deal with directories"""

        def __init__(self):
            dict.__init__(self)
            self.order = 0

        def add(self, directory):
            """Add a directory to our current set of directories"""
            if len(directory) > 1:
                directory = directory.rstrip(os.path.sep)
            # only adds and updates order if exists and not already in set
            if not os.path.exists(directory):
                return
            order = self.setdefault(directory, self.order)
            if order == self.order:
                self.order += 1

        def extend(self, directories):
            """Add a list of directories to our set"""
            for a_dir in directories:
                self.add(a_dir)

        def ordered(self):
            """Sort the list of directories"""
            return (i[0] for i in sorted(self.items(), key=lambda d: d[1]))

    def _get_ld_so_conf_dirs(self, conf, dirs):
        """
        Recursive function to help parse all ld.so.conf files, including proper
        handling of the `include` directive.
        """

        try:
            with open(conf) as fileobj:
                for dirname in fileobj:
                    dirname = dirname.strip()
                    if not dirname:
                        continue

                    match = self._include.match(dirname)
                    if not match:
                        dirs.add(dirname)
                    else:
                        for dir2 in glob.glob(match.group("pattern")):
                            self._get_ld_so_conf_dirs(dir2, dirs)
        except IOError:
            pass

    def _create_ld_so_cache(self):
        # Recreate search path followed by ld.so.  This is going to be
        # slow to build, and incorrect (ld.so uses ld.so.cache, which may
        # not be up-to-date).  Used only as fallback for distros without
        # /sbin/ldconfig.
        #
        # We assume the DT_RPATH and DT_RUNPATH binary sections are omitted.

        directories = self._Directories()
        for name in (
            "LD_LIBRARY_PATH",
            "SHLIB_PATH",  # HP-UX
            "LIBPATH",  # OS/2, AIX
            "LIBRARY_PATH",  # BE/OS
        ):
            if name in os.environ:
                directories.extend(os.environ[name].split(os.pathsep))

        self._get_ld_so_conf_dirs("/etc/ld.so.conf", directories)

        bitage = platform.architecture()[0]

        unix_lib_dirs_list = []
        if bitage.startswith("64"):
            # prefer 64 bit if that is our arch
            unix_lib_dirs_list += ["/lib64", "/usr/lib64"]

        # must include standard libs, since those paths are also used by 64 bit
        # installs
        unix_lib_dirs_list += ["/lib", "/usr/lib"]
        if sys.platform.startswith("linux"):
            # Try and support multiarch work in Ubuntu
            # https://wiki.ubuntu.com/MultiarchSpec
            if bitage.startswith("32"):
                # Assume Intel/AMD x86 compat
                unix_lib_dirs_list += ["/lib/i386-linux-gnu", "/usr/lib/i386-linux-gnu"]
            elif bitage.startswith("64"):
                # Assume Intel/AMD x86 compatible
                unix_lib_dirs_list += [
                    "/lib/x86_64-linux-gnu",
                    "/usr/lib/x86_64-linux-gnu",
                ]
            else:
                # guess...
                unix_lib_dirs_list += glob.glob("/lib/*linux-gnu")
        directories.extend(unix_lib_dirs_list)

        cache = {}
        lib_re = re.compile(r"lib(.*)\.s[ol]")
        # ext_re = re.compile(r"\.s[ol]$")
        for our_dir in directories.ordered():
            try:
                for path in glob.glob("%s/*.s[ol]*" % our_dir):
                    file = os.path.basename(path)

                    # Index by filename
                    cache_i = cache.setdefault(file, set())
                    cache_i.add(path)

                    # Index by library name
                    match = lib_re.match(file)
                    if match:
                        library = match.group(1)
                        cache_i = cache.setdefault(library, set())
                        cache_i.add(path)
            except OSError:
                pass

        self._ld_so_cache = cache

    def getplatformpaths(self, libname):
        if self._ld_so_cache is None:
            self._create_ld_so_cache()

        result = self._ld_so_cache.get(libname, set())
        for i in result:
            # we iterate through all found paths for library, since we may have
            # actually found multiple architectures or other library types that
            # may not load
            yield i


# Windows


class WindowsLibraryLoader(LibraryLoader):
    """Library loader for Microsoft Windows"""

    name_formats = ["%s.dll", "lib%s.dll", "%slib.dll", "%s"]

    class Lookup(LibraryLoader.Lookup):
        """Lookup class for Windows libraries..."""

        def __init__(self, path):
            super(WindowsLibraryLoader.Lookup, self).__init__(path)
            self.access["stdcall"] = ctypes.windll.LoadLibrary(path)


# Platform switching

# If your value of sys.platform does not appear in this dict, please contact
# the Ctypesgen maintainers.

loaderclass = {
    "darwin": DarwinLibraryLoader,
    "cygwin": WindowsLibraryLoader,
    "win32": WindowsLibraryLoader,
    "msys": WindowsLibraryLoader,
}

load_library = loaderclass.get(sys.platform, PosixLibraryLoader)()


def add_library_search_dirs(other_dirs):
    """
    Add libraries to search paths.
    If library paths are relative, convert them to absolute with respect to this
    file's directory
    """
    for path in other_dirs:
        if not os.path.isabs(path):
            path = os.path.abspath(path)
        load_library.other_dirs.append(path)


del loaderclass

# End loader

add_library_search_dirs([])

# Begin libraries
_libs["libpydis.so"] = load_library("libpydis.so")

# 1 libraries
# End libraries

# No modules

__off_t = c_long# /usr/include/x86_64-linux-gnu/bits/types.h: 152

__off64_t = c_long# /usr/include/x86_64-linux-gnu/bits/types.h: 153

__time_t = c_long# /usr/include/x86_64-linux-gnu/bits/types.h: 160

__suseconds_t = c_long# /usr/include/x86_64-linux-gnu/bits/types.h: 162

# /workspace/core/pydis/c/calforce/SegSegForce.h: 4
if _libs["libpydis.so"].has("SpecialSegSegForce", "cdecl"):
    SpecialSegSegForce = _libs["libpydis.so"].get("SpecialSegSegForce", "cdecl")
    SpecialSegSegForce.argtypes = [c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_int, c_int, POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double)]
    SpecialSegSegForce.restype = None

# /workspace/core/pydis/c/calforce/SegSegForce.h: 18
if _libs["libpydis.so"].has("SpecialSegSegForceHalf", "cdecl"):
    SpecialSegSegForceHalf = _libs["libpydis.so"].get("SpecialSegSegForceHalf", "cdecl")
    SpecialSegSegForceHalf.argtypes = [c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double)]
    SpecialSegSegForceHalf.restype = None

# /workspace/core/pydis/c/calforce/SegSegForce.h: 29
if _libs["libpydis.so"].has("SegSegForceIsotropic", "cdecl"):
    SegSegForceIsotropic = _libs["libpydis.so"].get("SegSegForceIsotropic", "cdecl")
    SegSegForceIsotropic.argtypes = [c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_int, c_int, POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double)]
    SegSegForceIsotropic.restype = None

# /workspace/core/pydis/c/calforce/SegSegForce.h: 42
if _libs["libpydis.so"].has("SegSegForce", "cdecl"):
    SegSegForce = _libs["libpydis.so"].get("SegSegForce", "cdecl")
    SegSegForce.argtypes = [c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_int, c_int, POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double)]
    SegSegForce.restype = None

# /workspace/core/pydis/c/calforce/SegmentStress.h: 4
if _libs["libpydis.so"].has("SegmentStress", "cdecl"):
    SegmentStress = _libs["libpydis.so"].get("SegmentStress", "cdecl")
    SegmentStress.argtypes = [c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, (c_double * int(3)) * int(3)]
    SegmentStress.restype = None

# /workspace/core/pydis/c/calforce/StressDueToSeg.h: 4
if _libs["libpydis.so"].has("StressDueToSeg", "cdecl"):
    StressDueToSeg = _libs["libpydis.so"].get("StressDueToSeg", "cdecl")
    StressDueToSeg.argtypes = [c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, POINTER(c_double)]
    StressDueToSeg.restype = None

# /workspace/core/pydis/c/calforce/SegSegForce_SBN1.h: 4
if _libs["libpydis.so"].has("SegSegForce_SBN1", "cdecl"):
    SegSegForce_SBN1 = _libs["libpydis.so"].get("SegSegForce_SBN1", "cdecl")
    SegSegForce_SBN1.argtypes = [c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_int, POINTER(c_double), POINTER(c_double), c_int, c_int, POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double)]
    SegSegForce_SBN1.restype = None

# /workspace/core/pydis/c/calforce/SegSegForce.h: 4
if _libs["libpydis.so"].has("SpecialSegSegForce", "cdecl"):
    SpecialSegSegForce = _libs["libpydis.so"].get("SpecialSegSegForce", "cdecl")
    SpecialSegSegForce.argtypes = [c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_int, c_int, POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double)]
    SpecialSegSegForce.restype = None

# /workspace/core/pydis/c/calforce/SegSegForce.h: 18
if _libs["libpydis.so"].has("SpecialSegSegForceHalf", "cdecl"):
    SpecialSegSegForceHalf = _libs["libpydis.so"].get("SpecialSegSegForceHalf", "cdecl")
    SpecialSegSegForceHalf.argtypes = [c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double)]
    SpecialSegSegForceHalf.restype = None

# /workspace/core/pydis/c/calforce/SegSegForce.h: 29
if _libs["libpydis.so"].has("SegSegForceIsotropic", "cdecl"):
    SegSegForceIsotropic = _libs["libpydis.so"].get("SegSegForceIsotropic", "cdecl")
    SegSegForceIsotropic.argtypes = [c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_int, c_int, POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double)]
    SegSegForceIsotropic.restype = None

# /workspace/core/pydis/c/calforce/SegSegForce.h: 42
if _libs["libpydis.so"].has("SegSegForce", "cdecl"):
    SegSegForce = _libs["libpydis.so"].get("SegSegForce", "cdecl")
    SegSegForce.argtypes = [c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_int, c_int, POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double)]
    SegSegForce.restype = None

# /workspace/core/pydis/c/calforce/SegSegForce_SBN1.h: 4
if _libs["libpydis.so"].has("SegSegForce_SBN1", "cdecl"):
    SegSegForce_SBN1 = _libs["libpydis.so"].get("SegSegForce_SBN1", "cdecl")
    SegSegForce_SBN1.argtypes = [c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_int, POINTER(c_double), POINTER(c_double), c_int, c_int, POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double)]
    SegSegForce_SBN1.restype = None

# /workspace/core/pydis/c/calforce/SegSegForce_SBN1_SBA.h: 6
if _libs["libpydis.so"].has("SegSegForce_SBN1_SBA", "cdecl"):
    SegSegForce_SBN1_SBA = _libs["libpydis.so"].get("SegSegForce_SBN1_SBA", "cdecl")
    SegSegForce_SBN1_SBA.argtypes = [c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_int, POINTER(c_double), POINTER(c_double), c_int, c_int, POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double)]
    SegSegForce_SBN1_SBA.restype = None

# /usr/include/x86_64-linux-gnu/bits/types/struct_FILE.h: 49
class struct__IO_FILE(Structure):
    pass

FILE = struct__IO_FILE# /usr/include/x86_64-linux-gnu/bits/types/FILE.h: 7

# /usr/include/x86_64-linux-gnu/bits/types/struct_FILE.h: 36
class struct__IO_marker(Structure):
    pass

# /usr/include/x86_64-linux-gnu/bits/types/struct_FILE.h: 37
class struct__IO_codecvt(Structure):
    pass

# /usr/include/x86_64-linux-gnu/bits/types/struct_FILE.h: 38
class struct__IO_wide_data(Structure):
    pass

_IO_lock_t = None# /usr/include/x86_64-linux-gnu/bits/types/struct_FILE.h: 43

struct__IO_FILE.__slots__ = [
    '_flags',
    '_IO_read_ptr',
    '_IO_read_end',
    '_IO_read_base',
    '_IO_write_base',
    '_IO_write_ptr',
    '_IO_write_end',
    '_IO_buf_base',
    '_IO_buf_end',
    '_IO_save_base',
    '_IO_backup_base',
    '_IO_save_end',
    '_markers',
    '_chain',
    '_fileno',
    '_flags2',
    '_old_offset',
    '_cur_column',
    '_vtable_offset',
    '_shortbuf',
    '_lock',
    '_offset',
    '_codecvt',
    '_wide_data',
    '_freeres_list',
    '_freeres_buf',
    '__pad5',
    '_mode',
    '_unused2',
]
struct__IO_FILE._fields_ = [
    ('_flags', c_int),
    ('_IO_read_ptr', String),
    ('_IO_read_end', String),
    ('_IO_read_base', String),
    ('_IO_write_base', String),
    ('_IO_write_ptr', String),
    ('_IO_write_end', String),
    ('_IO_buf_base', String),
    ('_IO_buf_end', String),
    ('_IO_save_base', String),
    ('_IO_backup_base', String),
    ('_IO_save_end', String),
    ('_markers', POINTER(struct__IO_marker)),
    ('_chain', POINTER(struct__IO_FILE)),
    ('_fileno', c_int),
    ('_flags2', c_int),
    ('_old_offset', __off_t),
    ('_cur_column', c_ushort),
    ('_vtable_offset', c_char),
    ('_shortbuf', c_char * int(1)),
    ('_lock', POINTER(_IO_lock_t)),
    ('_offset', __off64_t),
    ('_codecvt', POINTER(struct__IO_codecvt)),
    ('_wide_data', POINTER(struct__IO_wide_data)),
    ('_freeres_list', POINTER(struct__IO_FILE)),
    ('_freeres_buf', POINTER(None)),
    ('__pad5', c_size_t),
    ('_mode', c_int),
    ('_unused2', c_char * int((((15 * sizeof(c_int)) - (4 * sizeof(POINTER(None)))) - sizeof(c_size_t)))),
]

# /usr/include/x86_64-linux-gnu/bits/types/struct_timeval.h: 8
class struct_timeval(Structure):
    pass

struct_timeval.__slots__ = [
    'tv_sec',
    'tv_usec',
]
struct_timeval._fields_ = [
    ('tv_sec', __time_t),
    ('tv_usec', __suseconds_t),
]

# /workspace/core/pydis/c/include/Cell.h: 15
class struct__cell(Structure):
    pass

Cell_t = struct__cell# /workspace/core/pydis/c/include/Typedefs.h: 21

# /workspace/core/pydis/c/include/Home.h: 175
class struct__home(Structure):
    pass

Home_t = struct__home# /workspace/core/pydis/c/include/Typedefs.h: 23

# /workspace/core/pydis/c/include/InData.h: 23
class struct__indata(Structure):
    pass

InData_t = struct__indata# /workspace/core/pydis/c/include/Typedefs.h: 24

# /workspace/core/pydis/c/include/MirrorDomain.h: 17
class struct__mirrordomain(Structure):
    pass

MirrorDomain_t = struct__mirrordomain# /workspace/core/pydis/c/include/Typedefs.h: 26

# /workspace/core/pydis/c/include/Node.h: 46
class struct__node(Structure):
    pass

Node_t = struct__node# /workspace/core/pydis/c/include/Typedefs.h: 27

# /workspace/core/pydis/c/include/Node.h: 151
class struct__nodeblock(Structure):
    pass

NodeBlock_t = struct__nodeblock# /workspace/core/pydis/c/include/Typedefs.h: 28

# /workspace/core/pydis/c/include/OpList.h: 18
class struct__operate(Structure):
    pass

Operate_t = struct__operate# /workspace/core/pydis/c/include/Typedefs.h: 29

# /workspace/core/pydis/c/include/Param.h: 25
class struct__param(Structure):
    pass

Param_t = struct__param# /workspace/core/pydis/c/include/Typedefs.h: 35

# /workspace/core/pydis/c/include/RemoteDomain.h: 14
class struct__remotedomain(Structure):
    pass

RemoteDomain_t = struct__remotedomain# /workspace/core/pydis/c/include/Typedefs.h: 36

# /workspace/core/pydis/c/include/Tag.h: 12
class struct__tag(Structure):
    pass

Tag_t = struct__tag# /workspace/core/pydis/c/include/Typedefs.h: 38

# /workspace/core/pydis/c/include/Timer.h: 12
class struct__timer(Structure):
    pass

Timer_t = struct__timer# /workspace/core/pydis/c/include/Typedefs.h: 39

# /workspace/core/pydis/c/include/Home.h: 140
class struct__segmentpair(Structure):
    pass

enum_anon_24 = c_int# /workspace/core/pydis/c/include/Typedefs.h: 47

BoundType_t = enum_anon_24# /workspace/core/pydis/c/include/Typedefs.h: 47

enum_anon_25 = c_int# /workspace/core/pydis/c/include/Typedefs.h: 72

OpType_t = enum_anon_25# /workspace/core/pydis/c/include/Typedefs.h: 72

# /workspace/core/pydis/c/include/Typedefs.h: 83
class struct_anon_26(Structure):
    pass

struct_anon_26.__slots__ = [
    'node',
    'next',
]
struct_anon_26._fields_ = [
    ('node', POINTER(Node_t)),
    ('next', c_int),
]

C2Qent_t = struct_anon_26# /workspace/core/pydis/c/include/Typedefs.h: 83

# /workspace/core/pydis/c/include/Typedefs.h: 115
class struct_anon_28(Structure):
    pass

struct_anon_28.__slots__ = [
    'varName',
    'valType',
    'valCnt',
    'flags',
    'valList',
]
struct_anon_28._fields_ = [
    ('varName', c_char * int(256)),
    ('valType', c_int),
    ('valCnt', c_int),
    ('flags', c_int),
    ('valList', POINTER(None)),
]

VarData_t = struct_anon_28# /workspace/core/pydis/c/include/Typedefs.h: 115

# /workspace/core/pydis/c/include/Typedefs.h: 121
class struct_anon_29(Structure):
    pass

struct_anon_29.__slots__ = [
    'paramCnt',
    'varList',
]
struct_anon_29._fields_ = [
    ('paramCnt', c_int),
    ('varList', POINTER(VarData_t)),
]

ParamList_t = struct_anon_29# /workspace/core/pydis/c/include/Typedefs.h: 121

struct__tag.__slots__ = [
    'domainID',
    'index',
]
struct__tag._fields_ = [
    ('domainID', c_int),
    ('index', c_int),
]

# /workspace/core/pydis/c/include/ParadisProto.h: 39
if _libs["libpydis.so"].has("Getline", "cdecl"):
    Getline = _libs["libpydis.so"].get("Getline", "cdecl")
    Getline.argtypes = [String, c_int, POINTER(FILE)]
    Getline.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 43
if _libs["libpydis.so"].has("StressDueToSeg", "cdecl"):
    StressDueToSeg = _libs["libpydis.so"].get("StressDueToSeg", "cdecl")
    StressDueToSeg.argtypes = [c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, POINTER(c_double)]
    StressDueToSeg.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 50
if _libs["libpydis.so"].has("SegmentStress", "cdecl"):
    SegmentStress = _libs["libpydis.so"].get("SegmentStress", "cdecl")
    SegmentStress.argtypes = [c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, (c_double * int(3)) * int(3)]
    SegmentStress.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 58
if _libs["libpydis.so"].has("AddTagMapping", "cdecl"):
    AddTagMapping = _libs["libpydis.so"].get("AddTagMapping", "cdecl")
    AddTagMapping.argtypes = [POINTER(Home_t), POINTER(Tag_t), POINTER(Tag_t)]
    AddTagMapping.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 59
if _libs["libpydis.so"].has("GetVelocityStatistics", "cdecl"):
    GetVelocityStatistics = _libs["libpydis.so"].get("GetVelocityStatistics", "cdecl")
    GetVelocityStatistics.argtypes = [POINTER(Home_t)]
    GetVelocityStatistics.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 60
if _libs["libpydis.so"].has("AssignNodeToCell", "cdecl"):
    AssignNodeToCell = _libs["libpydis.so"].get("AssignNodeToCell", "cdecl")
    AssignNodeToCell.argtypes = [POINTER(Home_t), POINTER(Node_t)]
    AssignNodeToCell.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 61
if _libs["libpydis.so"].has("TrapezoidIntegrator", "cdecl"):
    TrapezoidIntegrator = _libs["libpydis.so"].get("TrapezoidIntegrator", "cdecl")
    TrapezoidIntegrator.argtypes = [POINTER(Home_t)]
    TrapezoidIntegrator.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 67
if _libs["libpydis.so"].has("BroadcastDecomp", "cdecl"):
    BroadcastDecomp = _libs["libpydis.so"].get("BroadcastDecomp", "cdecl")
    BroadcastDecomp.argtypes = [POINTER(Home_t), POINTER(None)]
    BroadcastDecomp.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 68
if _libs["libpydis.so"].has("CalcNodeVelocities", "cdecl"):
    CalcNodeVelocities = _libs["libpydis.so"].get("CalcNodeVelocities", "cdecl")
    CalcNodeVelocities.argtypes = [POINTER(Home_t), c_int, c_int]
    CalcNodeVelocities.restype = c_int

# /workspace/core/pydis/c/include/ParadisProto.h: 69
if _libs["libpydis.so"].has("CellCharge", "cdecl"):
    CellCharge = _libs["libpydis.so"].get("CellCharge", "cdecl")
    CellCharge.argtypes = [POINTER(Home_t)]
    CellCharge.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 70
if _libs["libpydis.so"].has("CrossSlip", "cdecl"):
    CrossSlip = _libs["libpydis.so"].get("CrossSlip", "cdecl")
    CrossSlip.argtypes = [POINTER(Home_t)]
    CrossSlip.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 71
if _libs["libpydis.so"].has("CrossSlipBCC", "cdecl"):
    CrossSlipBCC = _libs["libpydis.so"].get("CrossSlipBCC", "cdecl")
    CrossSlipBCC.argtypes = [POINTER(Home_t)]
    CrossSlipBCC.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 72
if _libs["libpydis.so"].has("CrossSlipFCC", "cdecl"):
    CrossSlipFCC = _libs["libpydis.so"].get("CrossSlipFCC", "cdecl")
    CrossSlipFCC.argtypes = [POINTER(Home_t)]
    CrossSlipFCC.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 73
if _libs["libpydis.so"].has("ThermalActivation", "cdecl"):
    ThermalActivation = _libs["libpydis.so"].get("ThermalActivation", "cdecl")
    ThermalActivation.argtypes = [POINTER(Param_t), c_double, c_double]
    ThermalActivation.restype = c_int

# /workspace/core/pydis/c/include/ParadisProto.h: 74
if _libs["libpydis.so"].has("EnergyBarrierCrossSlipFCC", "cdecl"):
    EnergyBarrierCrossSlipFCC = _libs["libpydis.so"].get("EnergyBarrierCrossSlipFCC", "cdecl")
    EnergyBarrierCrossSlipFCC.argtypes = [POINTER(Home_t), POINTER(Node_t), c_double * int(3), c_double * int(3), c_double * int(3), POINTER(c_double)]
    EnergyBarrierCrossSlipFCC.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 75
if _libs["libpydis.so"].has("DeltaPlasticStrain", "cdecl"):
    DeltaPlasticStrain = _libs["libpydis.so"].get("DeltaPlasticStrain", "cdecl")
    DeltaPlasticStrain.argtypes = [POINTER(Home_t)]
    DeltaPlasticStrain.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 76
if _libs["libpydis.so"].has("DeltaPlasticStrain_BCC", "cdecl"):
    DeltaPlasticStrain_BCC = _libs["libpydis.so"].get("DeltaPlasticStrain_BCC", "cdecl")
    DeltaPlasticStrain_BCC.argtypes = [POINTER(Home_t)]
    DeltaPlasticStrain_BCC.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 77
if _libs["libpydis.so"].has("DeltaPlasticStrain_FCC", "cdecl"):
    DeltaPlasticStrain_FCC = _libs["libpydis.so"].get("DeltaPlasticStrain_FCC", "cdecl")
    DeltaPlasticStrain_FCC.argtypes = [POINTER(Home_t)]
    DeltaPlasticStrain_FCC.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 78
if _libs["libpydis.so"].has("DistributeTagMaps", "cdecl"):
    DistributeTagMaps = _libs["libpydis.so"].get("DistributeTagMaps", "cdecl")
    DistributeTagMaps.argtypes = [POINTER(Home_t)]
    DistributeTagMaps.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 79
if _libs["libpydis.so"].has("FindPreciseGlidePlane", "cdecl"):
    FindPreciseGlidePlane = _libs["libpydis.so"].get("FindPreciseGlidePlane", "cdecl")
    FindPreciseGlidePlane.argtypes = [POINTER(Home_t), c_double * int(3), c_double * int(3), c_double * int(3)]
    FindPreciseGlidePlane.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 81
if _libs["libpydis.so"].has("FixGlideViolations", "cdecl"):
    FixGlideViolations = _libs["libpydis.so"].get("FixGlideViolations", "cdecl")
    FixGlideViolations.argtypes = [POINTER(Home_t), POINTER(Tag_t), c_double * int(3)]
    FixGlideViolations.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 82
if _libs["libpydis.so"].has("FixRemesh", "cdecl"):
    FixRemesh = _libs["libpydis.so"].get("FixRemesh", "cdecl")
    FixRemesh.argtypes = [POINTER(Home_t)]
    FixRemesh.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 83
if _libs["libpydis.so"].has("ForwardEulerIntegrator", "cdecl"):
    ForwardEulerIntegrator = _libs["libpydis.so"].get("ForwardEulerIntegrator", "cdecl")
    ForwardEulerIntegrator.argtypes = [POINTER(Home_t)]
    ForwardEulerIntegrator.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 84
if _libs["libpydis.so"].has("FreeCellCenters", "cdecl"):
    FreeCellCenters = _libs["libpydis.so"].get("FreeCellCenters", "cdecl")
    FreeCellCenters.argtypes = []
    FreeCellCenters.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 85
if _libs["libpydis.so"].has("FreeCorrectionTable", "cdecl"):
    FreeCorrectionTable = _libs["libpydis.so"].get("FreeCorrectionTable", "cdecl")
    FreeCorrectionTable.argtypes = []
    FreeCorrectionTable.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 86
if _libs["libpydis.so"].has("FreeInitArrays", "cdecl"):
    FreeInitArrays = _libs["libpydis.so"].get("FreeInitArrays", "cdecl")
    FreeInitArrays.argtypes = [POINTER(Home_t), POINTER(InData_t)]
    FreeInitArrays.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 87
if _libs["libpydis.so"].has("FreeInNodeArray", "cdecl"):
    FreeInNodeArray = _libs["libpydis.so"].get("FreeInNodeArray", "cdecl")
    FreeInNodeArray.argtypes = [POINTER(InData_t), c_int]
    FreeInNodeArray.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 88
if _libs["libpydis.so"].has("FreeRijm", "cdecl"):
    FreeRijm = _libs["libpydis.so"].get("FreeRijm", "cdecl")
    FreeRijm.argtypes = []
    FreeRijm.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 89
if _libs["libpydis.so"].has("FreeRijmPBC", "cdecl"):
    FreeRijmPBC = _libs["libpydis.so"].get("FreeRijmPBC", "cdecl")
    FreeRijmPBC.argtypes = []
    FreeRijmPBC.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 90
if _libs["libpydis.so"].has("GenerateOutput", "cdecl"):
    GenerateOutput = _libs["libpydis.so"].get("GenerateOutput", "cdecl")
    GenerateOutput.argtypes = [POINTER(Home_t), c_int]
    GenerateOutput.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 91
if _libs["libpydis.so"].has("GetDensityDelta", "cdecl"):
    GetDensityDelta = _libs["libpydis.so"].get("GetDensityDelta", "cdecl")
    GetDensityDelta.argtypes = [POINTER(Home_t)]
    GetDensityDelta.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 92
if _libs["libpydis.so"].has("GetMinDist", "cdecl"):
    GetMinDist = _libs["libpydis.so"].get("GetMinDist", "cdecl")
    GetMinDist.argtypes = [c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double)]
    GetMinDist.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 98
if _libs["libpydis.so"].has("GetMinDist2", "cdecl"):
    GetMinDist2 = _libs["libpydis.so"].get("GetMinDist2", "cdecl")
    GetMinDist2.argtypes = [c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double)]
    GetMinDist2.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 104
if _libs["libpydis.so"].has("GetNbrCoords", "cdecl"):
    GetNbrCoords = _libs["libpydis.so"].get("GetNbrCoords", "cdecl")
    GetNbrCoords.argtypes = [POINTER(Home_t), POINTER(Node_t), c_int, POINTER(c_double), POINTER(c_double), POINTER(c_double)]
    GetNbrCoords.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 106
if _libs["libpydis.so"].has("GetParallelIOGroup", "cdecl"):
    GetParallelIOGroup = _libs["libpydis.so"].get("GetParallelIOGroup", "cdecl")
    GetParallelIOGroup.argtypes = [POINTER(Home_t)]
    GetParallelIOGroup.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 107
if _libs["libpydis.so"].has("HandleCollisions", "cdecl"):
    HandleCollisions = _libs["libpydis.so"].get("HandleCollisions", "cdecl")
    HandleCollisions.argtypes = [POINTER(Home_t)]
    HandleCollisions.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 108
if _libs["libpydis.so"].has("PredictiveCollisions", "cdecl"):
    PredictiveCollisions = _libs["libpydis.so"].get("PredictiveCollisions", "cdecl")
    PredictiveCollisions.argtypes = [POINTER(Home_t)]
    PredictiveCollisions.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 109
if _libs["libpydis.so"].has("ProximityCollisions", "cdecl"):
    ProximityCollisions = _libs["libpydis.so"].get("ProximityCollisions", "cdecl")
    ProximityCollisions.argtypes = [POINTER(Home_t)]
    ProximityCollisions.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 118
if _libs["libpydis.so"].has("HeapAdd", "cdecl"):
    HeapAdd = _libs["libpydis.so"].get("HeapAdd", "cdecl")
    HeapAdd.argtypes = [POINTER(POINTER(c_int)), POINTER(c_int), POINTER(c_int), c_int]
    HeapAdd.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 119
if _libs["libpydis.so"].has("HeapRemove", "cdecl"):
    HeapRemove = _libs["libpydis.so"].get("HeapRemove", "cdecl")
    HeapRemove.argtypes = [POINTER(c_int), POINTER(c_int)]
    HeapRemove.restype = c_int

# /workspace/core/pydis/c/include/ParadisProto.h: 120
if _libs["libpydis.so"].has("InitRemoteDomains", "cdecl"):
    InitRemoteDomains = _libs["libpydis.so"].get("InitRemoteDomains", "cdecl")
    InitRemoteDomains.argtypes = [POINTER(Home_t)]
    InitRemoteDomains.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 121
if _libs["libpydis.so"].has("InputSanity", "cdecl"):
    InputSanity = _libs["libpydis.so"].get("InputSanity", "cdecl")
    InputSanity.argtypes = [POINTER(Home_t)]
    InputSanity.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 122
if _libs["libpydis.so"].has("isCollinear", "cdecl"):
    isCollinear = _libs["libpydis.so"].get("isCollinear", "cdecl")
    isCollinear.argtypes = [c_double, c_double, c_double, c_double, c_double, c_double]
    isCollinear.restype = c_int

# /workspace/core/pydis/c/include/ParadisProto.h: 123
if _libs["libpydis.so"].has("LoadCurve", "cdecl"):
    LoadCurve = _libs["libpydis.so"].get("LoadCurve", "cdecl")
    LoadCurve.argtypes = [POINTER(Home_t), (c_double * int(3)) * int(3)]
    LoadCurve.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 124
if _libs["libpydis.so"].has("Migrate", "cdecl"):
    Migrate = _libs["libpydis.so"].get("Migrate", "cdecl")
    Migrate.argtypes = [POINTER(Home_t)]
    Migrate.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 125
if _libs["libpydis.so"].has("NodeOwnsSeg", "cdecl"):
    NodeOwnsSeg = _libs["libpydis.so"].get("NodeOwnsSeg", "cdecl")
    NodeOwnsSeg.argtypes = [POINTER(Home_t), POINTER(Node_t), POINTER(Node_t)]
    NodeOwnsSeg.restype = c_int

# /workspace/core/pydis/c/include/ParadisProto.h: 126
if _libs["libpydis.so"].has("ParadisStep", "cdecl"):
    ParadisStep = _libs["libpydis.so"].get("ParadisStep", "cdecl")
    ParadisStep.argtypes = [POINTER(Home_t)]
    ParadisStep.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 127
if _libs["libpydis.so"].has("ParadisFinish", "cdecl"):
    ParadisFinish = _libs["libpydis.so"].get("ParadisFinish", "cdecl")
    ParadisFinish.argtypes = [POINTER(Home_t)]
    ParadisFinish.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 128
if _libs["libpydis.so"].has("PickScrewGlidePlane", "cdecl"):
    PickScrewGlidePlane = _libs["libpydis.so"].get("PickScrewGlidePlane", "cdecl")
    PickScrewGlidePlane.argtypes = [POINTER(Home_t), c_double * int(3), c_double * int(3)]
    PickScrewGlidePlane.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 130
if _libs["libpydis.so"].has("ReadNodeDataFile", "cdecl"):
    ReadNodeDataFile = _libs["libpydis.so"].get("ReadNodeDataFile", "cdecl")
    ReadNodeDataFile.argtypes = [POINTER(Home_t), POINTER(InData_t), String]
    ReadNodeDataFile.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 131
if _libs["libpydis.so"].has("FreeAllNodes", "cdecl"):
    FreeAllNodes = _libs["libpydis.so"].get("FreeAllNodes", "cdecl")
    FreeAllNodes.argtypes = [POINTER(Home_t)]
    FreeAllNodes.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 132
if _libs["libpydis.so"].has("RecycleAllNodes", "cdecl"):
    RecycleAllNodes = _libs["libpydis.so"].get("RecycleAllNodes", "cdecl")
    RecycleAllNodes.argtypes = [POINTER(Home_t)]
    RecycleAllNodes.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 133
if _libs["libpydis.so"].has("ReadDataFile", "cdecl"):
    ReadDataFile = _libs["libpydis.so"].get("ReadDataFile", "cdecl")
    ReadDataFile.argtypes = [POINTER(Home_t), String]
    ReadDataFile.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 134
if _libs["libpydis.so"].has("RemapArmTag", "cdecl"):
    RemapArmTag = _libs["libpydis.so"].get("RemapArmTag", "cdecl")
    RemapArmTag.argtypes = [POINTER(Home_t), POINTER(Tag_t), POINTER(Tag_t)]
    RemapArmTag.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 135
if _libs["libpydis.so"].has("Remesh", "cdecl"):
    Remesh = _libs["libpydis.so"].get("Remesh", "cdecl")
    Remesh.argtypes = [POINTER(Home_t)]
    Remesh.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 136
if _libs["libpydis.so"].has("RemeshRule_2", "cdecl"):
    RemeshRule_2 = _libs["libpydis.so"].get("RemeshRule_2", "cdecl")
    RemeshRule_2.argtypes = [POINTER(Home_t)]
    RemeshRule_2.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 137
if _libs["libpydis.so"].has("RemeshRule_3", "cdecl"):
    RemeshRule_3 = _libs["libpydis.so"].get("RemeshRule_3", "cdecl")
    RemeshRule_3.argtypes = [POINTER(Home_t)]
    RemeshRule_3.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 138
if _libs["libpydis.so"].has("ResetGlidePlanes", "cdecl"):
    ResetGlidePlanes = _libs["libpydis.so"].get("ResetGlidePlanes", "cdecl")
    ResetGlidePlanes.argtypes = [POINTER(Home_t)]
    ResetGlidePlanes.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 139
if _libs["libpydis.so"].has("SetLatestRestart", "cdecl"):
    SetLatestRestart = _libs["libpydis.so"].get("SetLatestRestart", "cdecl")
    SetLatestRestart.argtypes = [String]
    SetLatestRestart.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 140
if _libs["libpydis.so"].has("SortNodesForCollision", "cdecl"):
    SortNodesForCollision = _libs["libpydis.so"].get("SortNodesForCollision", "cdecl")
    SortNodesForCollision.argtypes = [POINTER(Home_t)]
    SortNodesForCollision.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 144
if _libs["libpydis.so"].has("Tecplot", "cdecl"):
    Tecplot = _libs["libpydis.so"].get("Tecplot", "cdecl")
    Tecplot.argtypes = [POINTER(Home_t), String, c_int, c_int, c_int, c_int, c_int]
    Tecplot.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 146
if _libs["libpydis.so"].has("TestGlidePlanes", "cdecl"):
    TestGlidePlanes = _libs["libpydis.so"].get("TestGlidePlanes", "cdecl")
    TestGlidePlanes.argtypes = [POINTER(Home_t), POINTER(Node_t), c_double * int(3), c_int, POINTER(c_int)]
    TestGlidePlanes.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 147
if _libs["libpydis.so"].has("UniformDecomp", "cdecl"):
    UniformDecomp = _libs["libpydis.so"].get("UniformDecomp", "cdecl")
    UniformDecomp.argtypes = [POINTER(Home_t), POINTER(POINTER(None))]
    UniformDecomp.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 148
if _libs["libpydis.so"].has("WriteVelocity", "cdecl"):
    WriteVelocity = _libs["libpydis.so"].get("WriteVelocity", "cdecl")
    WriteVelocity.argtypes = [POINTER(Home_t), String, c_int, c_int, c_int, c_int]
    WriteVelocity.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 150
if _libs["libpydis.so"].has("WriteForce", "cdecl"):
    WriteForce = _libs["libpydis.so"].get("WriteForce", "cdecl")
    WriteForce.argtypes = [POINTER(Home_t), String, c_int, c_int, c_int, c_int]
    WriteForce.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 152
if _libs["libpydis.so"].has("WriteVisit", "cdecl"):
    WriteVisit = _libs["libpydis.so"].get("WriteVisit", "cdecl")
    WriteVisit.argtypes = [POINTER(Home_t), String, c_int, c_int, POINTER(c_int), POINTER(c_int)]
    WriteVisit.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 154
if _libs["libpydis.so"].has("WriteVisitMetaDataFile", "cdecl"):
    WriteVisitMetaDataFile = _libs["libpydis.so"].get("WriteVisitMetaDataFile", "cdecl")
    WriteVisitMetaDataFile.argtypes = [POINTER(Home_t), String, POINTER(c_int)]
    WriteVisitMetaDataFile.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 156
if _libs["libpydis.so"].has("WriteParaview", "cdecl"):
    WriteParaview = _libs["libpydis.so"].get("WriteParaview", "cdecl")
    WriteParaview.argtypes = [POINTER(Home_t), String, c_int, c_int]
    WriteParaview.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 164
if _libs["libpydis.so"].has("SaveCrossSlipInfo", "cdecl"):
    SaveCrossSlipInfo = _libs["libpydis.so"].get("SaveCrossSlipInfo", "cdecl")
    SaveCrossSlipInfo.argtypes = [POINTER(Node_t), POINTER(Node_t), POINTER(Node_t), c_int, c_int, (c_double * int(3)) * int(4), c_double * int(3), c_double * int(3), c_double * int(3)]
    SaveCrossSlipInfo.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 168
if _libs["libpydis.so"].has("ResetPosition", "cdecl"):
    ResetPosition = _libs["libpydis.so"].get("ResetPosition", "cdecl")
    ResetPosition.argtypes = [POINTER(Param_t), POINTER(Node_t), c_double * int(3)]
    ResetPosition.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 169
if _libs["libpydis.so"].has("RestoreCrossSlipForce", "cdecl"):
    RestoreCrossSlipForce = _libs["libpydis.so"].get("RestoreCrossSlipForce", "cdecl")
    RestoreCrossSlipForce.argtypes = [POINTER(Node_t), POINTER(Node_t), POINTER(Node_t), c_int, c_int, (c_double * int(3)) * int(4)]
    RestoreCrossSlipForce.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 173
if _libs["libpydis.so"].has("RequestNewNativeNodeTag", "cdecl"):
    RequestNewNativeNodeTag = _libs["libpydis.so"].get("RequestNewNativeNodeTag", "cdecl")
    RequestNewNativeNodeTag.argtypes = [POINTER(Home_t), POINTER(Tag_t)]
    RequestNewNativeNodeTag.restype = POINTER(Node_t)

# /workspace/core/pydis/c/include/ParadisProto.h: 174
if _libs["libpydis.so"].has("AddNodesFromArray", "cdecl"):
    AddNodesFromArray = _libs["libpydis.so"].get("AddNodesFromArray", "cdecl")
    AddNodesFromArray.argtypes = [POINTER(Home_t), POINTER(c_double)]
    AddNodesFromArray.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 175
if _libs["libpydis.so"].has("ReleaseMemory", "cdecl"):
    ReleaseMemory = _libs["libpydis.so"].get("ReleaseMemory", "cdecl")
    ReleaseMemory.argtypes = [POINTER(Home_t)]
    ReleaseMemory.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 177
if _libs["libpydis.so"].has("ParadisInit_lean", "cdecl"):
    ParadisInit_lean = _libs["libpydis.so"].get("ParadisInit_lean", "cdecl")
    ParadisInit_lean.argtypes = [POINTER(POINTER(Home_t))]
    ParadisInit_lean.restype = None

# /workspace/core/pydis/c/include/ParadisProto.h: 178
if _libs["libpydis.so"].has("Initialize_lean", "cdecl"):
    Initialize_lean = _libs["libpydis.so"].get("Initialize_lean", "cdecl")
    Initialize_lean.argtypes = [POINTER(Home_t)]
    Initialize_lean.restype = None

# /workspace/core/pydis/c/include/FM.h: 42
class struct__fmcell(Structure):
    pass

FMCell_t = struct__fmcell# /workspace/core/pydis/c/include/FM.h: 39

# /workspace/core/pydis/c/include/FM.h: 71
class struct__fmlayer(Structure):
    pass

FMLayer_t = struct__fmlayer# /workspace/core/pydis/c/include/FM.h: 40

struct__fmcell.__slots__ = [
    'cellID',
    'owningDom',
    'domCnt',
    'domList',
    'cellCtr',
    'mpCoeff',
    'taylorCoeff',
    'next',
    'prev',
]
struct__fmcell._fields_ = [
    ('cellID', c_int),
    ('owningDom', c_int),
    ('domCnt', c_int),
    ('domList', POINTER(c_int)),
    ('cellCtr', c_double * int(3)),
    ('mpCoeff', POINTER(c_double)),
    ('taylorCoeff', POINTER(c_double)),
    ('next', POINTER(FMCell_t)),
    ('prev', POINTER(FMCell_t)),
]

struct__fmlayer.__slots__ = [
    'lDim',
    'cellSize',
    'ownedCnt',
    'ownedMin',
    'ownedMax',
    'intersectCnt',
    'intersectMin',
    'intersectMax',
    'domBuf',
    'fmUpPassSendDomCnt',
    'fmUpPassSendDomList',
    'fmUpPassRecvDomCnt',
    'fmUpPassRecvDomList',
    'fmDownPassSendDomCnt',
    'fmDownPassSendDomList',
    'fmDownPassRecvDomCnt',
    'fmDownPassRecvDomList',
    'cellList',
    'numCells',
    'cellTable',
]
struct__fmlayer._fields_ = [
    ('lDim', c_int * int(3)),
    ('cellSize', c_double * int(3)),
    ('ownedCnt', c_int),
    ('ownedMin', c_int * int(3)),
    ('ownedMax', c_int * int(3)),
    ('intersectCnt', c_int),
    ('intersectMin', c_int * int(3)),
    ('intersectMax', c_int * int(3)),
    ('domBuf', POINTER(c_int)),
    ('fmUpPassSendDomCnt', c_int),
    ('fmUpPassSendDomList', POINTER(c_int)),
    ('fmUpPassRecvDomCnt', c_int),
    ('fmUpPassRecvDomList', POINTER(c_int)),
    ('fmDownPassSendDomCnt', c_int),
    ('fmDownPassSendDomList', POINTER(c_int)),
    ('fmDownPassRecvDomCnt', c_int),
    ('fmDownPassRecvDomList', POINTER(c_int)),
    ('cellList', POINTER(c_int)),
    ('numCells', c_int),
    ('cellTable', POINTER(FMCell_t) * int(97)),
]

struct__node.__slots__ = [
    'flags',
    'x',
    'y',
    'z',
    'fX',
    'fY',
    'fZ',
    'vX',
    'vY',
    'vZ',
    'oldx',
    'oldy',
    'oldz',
    'oldvX',
    'oldvY',
    'oldvZ',
    'currvX',
    'currvY',
    'currvZ',
    'myTag',
    'numNbrs',
    'nbrTag',
    'armfx',
    'armfy',
    'armfz',
    'burgX',
    'burgY',
    'burgZ',
    'nx',
    'ny',
    'nz',
    'sigbLoc',
    'sigbRem',
    'armCoordIndex',
    'constraint',
    'cellIdx',
    'cell2Idx',
    'cell2QentIdx',
    'native',
    'next',
    'nextInCell',
    'sgnv',
]
struct__node._fields_ = [
    ('flags', c_int),
    ('x', c_double),
    ('y', c_double),
    ('z', c_double),
    ('fX', c_double),
    ('fY', c_double),
    ('fZ', c_double),
    ('vX', c_double),
    ('vY', c_double),
    ('vZ', c_double),
    ('oldx', c_double),
    ('oldy', c_double),
    ('oldz', c_double),
    ('oldvX', c_double),
    ('oldvY', c_double),
    ('oldvZ', c_double),
    ('currvX', c_double),
    ('currvY', c_double),
    ('currvZ', c_double),
    ('myTag', Tag_t),
    ('numNbrs', c_int),
    ('nbrTag', POINTER(Tag_t)),
    ('armfx', POINTER(c_double)),
    ('armfy', POINTER(c_double)),
    ('armfz', POINTER(c_double)),
    ('burgX', POINTER(c_double)),
    ('burgY', POINTER(c_double)),
    ('burgZ', POINTER(c_double)),
    ('nx', POINTER(c_double)),
    ('ny', POINTER(c_double)),
    ('nz', POINTER(c_double)),
    ('sigbLoc', POINTER(c_double)),
    ('sigbRem', POINTER(c_double)),
    ('armCoordIndex', POINTER(c_int)),
    ('constraint', c_int),
    ('cellIdx', c_int),
    ('cell2Idx', c_int),
    ('cell2QentIdx', c_int),
    ('native', c_int),
    ('next', POINTER(Node_t)),
    ('nextInCell', POINTER(Node_t)),
    ('sgnv', c_int),
]

struct__nodeblock.__slots__ = [
    'next',
    'nodes',
]
struct__nodeblock._fields_ = [
    ('next', POINTER(NodeBlock_t)),
    ('nodes', POINTER(Node_t)),
]

struct__param.__slots__ = [
    'nXdoms',
    'nYdoms',
    'nZdoms',
    'nXcells',
    'nYcells',
    'nZcells',
    'iCellNatMin',
    'iCellNatMax',
    'jCellNatMin',
    'jCellNatMax',
    'kCellNatMin',
    'kCellNatMax',
    'xBoundType',
    'yBoundType',
    'zBoundType',
    'xBoundMin',
    'xBoundMax',
    'yBoundMin',
    'yBoundMax',
    'zBoundMin',
    'zBoundMax',
    'minSideX',
    'maxSideX',
    'minSideY',
    'maxSideY',
    'minSideZ',
    'maxSideZ',
    'decompType',
    'DLBfreq',
    'numDLBCycles',
    'cycleStart',
    'maxstep',
    'timeStart',
    'timeNow',
    'timestepIntegrator',
    'deltaTT',
    'realdt',
    'nextDT',
    'maxDT',
    'dtIncrementFact',
    'dtDecrementFact',
    'dtExponent',
    'dtVariableAdjustment',
    'rTol',
    'rmax',
    'inSubcycling',
    'minSeg',
    'maxSeg',
    'remeshRule',
    'collisionMethod',
    'remeshAreaMax',
    'remeshAreaMin',
    'splitMultiNodeFreq',
    'fmEnabled',
    'fmNumLayers',
    'fmMPOrder',
    'fmTaylorOrder',
    'fmNumPoints',
    'fmCorrectionTbl',
    'Rijmfile',
    'RijmPBCfile',
    'TempK',
    'loadType',
    'appliedStress',
    'appliedStressRate',
    'eRate',
    'indxErate',
    'edotdir',
    'sRate',
    'cTimeOld',
    'netCyclicStrain',
    'dCyclicStrain',
    'numLoadCycle',
    'eAmp',
    'useLabFrame',
    'labFrameXDir',
    'labFrameYDir',
    'labFrameZDir',
    'mobilityLaw',
    'mobilityType',
    'materialType',
    'vacancyConc',
    'vacancyConcEquilibrium',
    'shearModulus',
    'pois',
    'burgMag',
    'YoungsModulus',
    'rc',
    'Ecore',
    'enforceGlidePlanes',
    'allowFuzzyGlidePlanes',
    'enableCrossSlip',
    'mobilityFunc',
    'MobScrew',
    'MobEdge',
    'MobClimb',
    'MobGlide',
    'MobLine',
    'FricStress',
    'sessileburgspec',
    'sessilelinespec',
    'includeInertia',
    'massDensity',
    'thermalCrossSlip',
    'CRS_A',
    'CRS_T0',
    'pre_Cge',
    'CRScount_zipper',
    'CRScount_bothScrew',
    'vAverage',
    'vStDev',
    'dirname',
    'writeBinRestart',
    'doBinRead',
    'numIOGroups',
    'skipIO',
    'armfile',
    'armfilefreq',
    'armfilecounter',
    'armfiledt',
    'armfiletime',
    'fluxfile',
    'fluxfreq',
    'fluxcounter',
    'fluxdt',
    'fluxtime',
    'fragfile',
    'fragfreq',
    'fragcounter',
    'fragdt',
    'fragtime',
    'gnuplot',
    'gnuplotfreq',
    'gnuplotcounter',
    'gnuplotdt',
    'gnuplottime',
    'polefigfile',
    'polefigfreq',
    'polefigcounter',
    'polefigdt',
    'polefigtime',
    'povray',
    'povrayfreq',
    'povraycounter',
    'povraydt',
    'povraytime',
    'atomeye',
    'atomeyefreq',
    'atomeyecounter',
    'atomeyedt',
    'atomeyetime',
    'atomeyesegradius',
    'psfile',
    'psfilefreq',
    'psfiledt',
    'psfiletime',
    'savecn',
    'savecnfreq',
    'savecncounter',
    'savecndt',
    'savecntime',
    'saveprop',
    'savepropfreq',
    'savepropdt',
    'saveproptime',
    'savetimers',
    'savetimersfreq',
    'savetimerscounter',
    'savetimersdt',
    'savetimerstime',
    'savedensityspec',
    'tecplot',
    'tecplotfreq',
    'tecplotcounter',
    'tecplotdt',
    'tecplottime',
    'paraview',
    'paraviewfreq',
    'paraviewcounter',
    'paraviewdt',
    'paraviewtime',
    'velfile',
    'velfilefreq',
    'velfilecounter',
    'velfiledt',
    'velfiletime',
    'writeForce',
    'writeForceFreq',
    'writeForceCounter',
    'writeForceDT',
    'writeForceTime',
    'linkfile',
    'linkfilefreq',
    'linkfilecounter',
    'linkfiledt',
    'linkfiletime',
    'writeVisit',
    'writeVisitFreq',
    'writeVisitCounter',
    'writeVisitSegments',
    'writeVisitSegmentsAsText',
    'writeVisitNodes',
    'writeVisitNodesAsText',
    'writeVisitDT',
    'writeVisitTime',
    'winDefaultsFile',
    'Lx',
    'Ly',
    'Lz',
    'invLx',
    'invLy',
    'invLz',
    'springConst',
    'rann',
    'numBurgGroups',
    'partialDisloDensity',
    'disloDensity',
    'delSegLength',
    'densityChange',
    'TensionFactor',
    'elasticinteraction',
    'delpStrain',
    'delSig',
    'totpStn',
    'delpSpin',
    'totpSpn',
    'totstraintensor',
    'totedgepStrain',
    'totscrewpStrain',
    'dedgepStrain',
    'dscrewpStrain',
    'Ltot',
    'fluxtot',
    'dLtot',
    'dfluxtot',
    'FCC_Ltot',
    'FCC_fluxtot',
    'FCC_dLtot',
    'FCC_dfluxtot',
    'imgstrgrid',
    'node_data_file',
    'dataFileVersion',
    'numFileSegments',
    'nodeCount',
    'dataDecompType',
    'dataDecompGeometry',
    'minCoordinates',
    'maxCoordinates',
    'simVol',
    'burgVolFactor',
    'maxNumThreads',
    'strainTimeData',
]
struct__param._fields_ = [
    ('nXdoms', c_int),
    ('nYdoms', c_int),
    ('nZdoms', c_int),
    ('nXcells', c_int),
    ('nYcells', c_int),
    ('nZcells', c_int),
    ('iCellNatMin', c_int),
    ('iCellNatMax', c_int),
    ('jCellNatMin', c_int),
    ('jCellNatMax', c_int),
    ('kCellNatMin', c_int),
    ('kCellNatMax', c_int),
    ('xBoundType', BoundType_t),
    ('yBoundType', BoundType_t),
    ('zBoundType', BoundType_t),
    ('xBoundMin', c_double),
    ('xBoundMax', c_double),
    ('yBoundMin', c_double),
    ('yBoundMax', c_double),
    ('zBoundMin', c_double),
    ('zBoundMax', c_double),
    ('minSideX', c_double),
    ('maxSideX', c_double),
    ('minSideY', c_double),
    ('maxSideY', c_double),
    ('minSideZ', c_double),
    ('maxSideZ', c_double),
    ('decompType', c_int),
    ('DLBfreq', c_int),
    ('numDLBCycles', c_int),
    ('cycleStart', c_int),
    ('maxstep', c_int),
    ('timeStart', c_double),
    ('timeNow', c_double),
    ('timestepIntegrator', c_char * int(256)),
    ('deltaTT', c_double),
    ('realdt', c_double),
    ('nextDT', c_double),
    ('maxDT', c_double),
    ('dtIncrementFact', c_double),
    ('dtDecrementFact', c_double),
    ('dtExponent', c_double),
    ('dtVariableAdjustment', c_int),
    ('rTol', c_double),
    ('rmax', c_double),
    ('inSubcycling', c_int),
    ('minSeg', c_double),
    ('maxSeg', c_double),
    ('remeshRule', c_int),
    ('collisionMethod', c_int),
    ('remeshAreaMax', c_double),
    ('remeshAreaMin', c_double),
    ('splitMultiNodeFreq', c_int),
    ('fmEnabled', c_int),
    ('fmNumLayers', c_int),
    ('fmMPOrder', c_int),
    ('fmTaylorOrder', c_int),
    ('fmNumPoints', c_int),
    ('fmCorrectionTbl', c_char * int(256)),
    ('Rijmfile', c_char * int(256)),
    ('RijmPBCfile', c_char * int(256)),
    ('TempK', c_double),
    ('loadType', c_int),
    ('appliedStress', c_double * int(6)),
    ('appliedStressRate', c_double * int(6)),
    ('eRate', c_double),
    ('indxErate', c_int),
    ('edotdir', c_double * int(3)),
    ('sRate', c_double),
    ('cTimeOld', c_double),
    ('netCyclicStrain', c_double),
    ('dCyclicStrain', c_double),
    ('numLoadCycle', c_int),
    ('eAmp', c_double),
    ('useLabFrame', c_int),
    ('labFrameXDir', c_double * int(3)),
    ('labFrameYDir', c_double * int(3)),
    ('labFrameZDir', c_double * int(3)),
    ('mobilityLaw', c_char * int(256)),
    ('mobilityType', c_int),
    ('materialType', c_int),
    ('vacancyConc', c_double),
    ('vacancyConcEquilibrium', c_double),
    ('shearModulus', c_double),
    ('pois', c_double),
    ('burgMag', c_double),
    ('YoungsModulus', c_double),
    ('rc', c_double),
    ('Ecore', c_double),
    ('enforceGlidePlanes', c_int),
    ('allowFuzzyGlidePlanes', c_int),
    ('enableCrossSlip', c_int),
    ('mobilityFunc', CFUNCTYPE(UNCHECKED(c_int), POINTER(Home_t), POINTER(Node_t))),
    ('MobScrew', c_double),
    ('MobEdge', c_double),
    ('MobClimb', c_double),
    ('MobGlide', c_double),
    ('MobLine', c_double),
    ('FricStress', c_double),
    ('sessileburgspec', c_double * int(30)),
    ('sessilelinespec', c_double * int(30)),
    ('includeInertia', c_int),
    ('massDensity', c_double),
    ('thermalCrossSlip', c_int),
    ('CRS_A', c_double),
    ('CRS_T0', c_double),
    ('pre_Cge', c_double),
    ('CRScount_zipper', c_int),
    ('CRScount_bothScrew', c_int),
    ('vAverage', c_double),
    ('vStDev', c_double),
    ('dirname', c_char * int(256)),
    ('writeBinRestart', c_int),
    ('doBinRead', c_int),
    ('numIOGroups', c_int),
    ('skipIO', c_int),
    ('armfile', c_int),
    ('armfilefreq', c_int),
    ('armfilecounter', c_int),
    ('armfiledt', c_double),
    ('armfiletime', c_double),
    ('fluxfile', c_int),
    ('fluxfreq', c_int),
    ('fluxcounter', c_int),
    ('fluxdt', c_double),
    ('fluxtime', c_double),
    ('fragfile', c_int),
    ('fragfreq', c_int),
    ('fragcounter', c_int),
    ('fragdt', c_double),
    ('fragtime', c_double),
    ('gnuplot', c_int),
    ('gnuplotfreq', c_int),
    ('gnuplotcounter', c_int),
    ('gnuplotdt', c_double),
    ('gnuplottime', c_double),
    ('polefigfile', c_int),
    ('polefigfreq', c_int),
    ('polefigcounter', c_int),
    ('polefigdt', c_double),
    ('polefigtime', c_double),
    ('povray', c_int),
    ('povrayfreq', c_int),
    ('povraycounter', c_int),
    ('povraydt', c_double),
    ('povraytime', c_double),
    ('atomeye', c_int),
    ('atomeyefreq', c_int),
    ('atomeyecounter', c_int),
    ('atomeyedt', c_double),
    ('atomeyetime', c_double),
    ('atomeyesegradius', c_double),
    ('psfile', c_int),
    ('psfilefreq', c_int),
    ('psfiledt', c_double),
    ('psfiletime', c_double),
    ('savecn', c_int),
    ('savecnfreq', c_int),
    ('savecncounter', c_int),
    ('savecndt', c_double),
    ('savecntime', c_double),
    ('saveprop', c_int),
    ('savepropfreq', c_int),
    ('savepropdt', c_double),
    ('saveproptime', c_double),
    ('savetimers', c_int),
    ('savetimersfreq', c_int),
    ('savetimerscounter', c_int),
    ('savetimersdt', c_double),
    ('savetimerstime', c_double),
    ('savedensityspec', c_int * int(3)),
    ('tecplot', c_int),
    ('tecplotfreq', c_int),
    ('tecplotcounter', c_int),
    ('tecplotdt', c_double),
    ('tecplottime', c_double),
    ('paraview', c_int),
    ('paraviewfreq', c_int),
    ('paraviewcounter', c_int),
    ('paraviewdt', c_double),
    ('paraviewtime', c_double),
    ('velfile', c_int),
    ('velfilefreq', c_int),
    ('velfilecounter', c_int),
    ('velfiledt', c_double),
    ('velfiletime', c_double),
    ('writeForce', c_int),
    ('writeForceFreq', c_int),
    ('writeForceCounter', c_int),
    ('writeForceDT', c_double),
    ('writeForceTime', c_double),
    ('linkfile', c_int),
    ('linkfilefreq', c_int),
    ('linkfilecounter', c_int),
    ('linkfiledt', c_double),
    ('linkfiletime', c_double),
    ('writeVisit', c_int),
    ('writeVisitFreq', c_int),
    ('writeVisitCounter', c_int),
    ('writeVisitSegments', c_int),
    ('writeVisitSegmentsAsText', c_int),
    ('writeVisitNodes', c_int),
    ('writeVisitNodesAsText', c_int),
    ('writeVisitDT', c_double),
    ('writeVisitTime', c_double),
    ('winDefaultsFile', c_char * int(256)),
    ('Lx', c_double),
    ('Ly', c_double),
    ('Lz', c_double),
    ('invLx', c_double),
    ('invLy', c_double),
    ('invLz', c_double),
    ('springConst', c_double),
    ('rann', c_double),
    ('numBurgGroups', c_int),
    ('partialDisloDensity', POINTER(c_double)),
    ('disloDensity', c_double),
    ('delSegLength', c_double),
    ('densityChange', c_double * int(14)),
    ('TensionFactor', c_double),
    ('elasticinteraction', c_int),
    ('delpStrain', c_double * int(6)),
    ('delSig', c_double * int(6)),
    ('totpStn', c_double * int(6)),
    ('delpSpin', c_double * int(6)),
    ('totpSpn', c_double * int(6)),
    ('totstraintensor', c_double * int(6)),
    ('totedgepStrain', c_double * int(6)),
    ('totscrewpStrain', c_double * int(6)),
    ('dedgepStrain', c_double * int(6)),
    ('dscrewpStrain', c_double * int(6)),
    ('Ltot', (c_double * int(4)) * int(4)),
    ('fluxtot', (c_double * int(7)) * int(4)),
    ('dLtot', (c_double * int(4)) * int(4)),
    ('dfluxtot', (c_double * int(7)) * int(4)),
    ('FCC_Ltot', (c_double * int(4)) * int(6)),
    ('FCC_fluxtot', (c_double * int(7)) * int(6)),
    ('FCC_dLtot', (c_double * int(4)) * int(6)),
    ('FCC_dfluxtot', (c_double * int(7)) * int(6)),
    ('imgstrgrid', c_int * int(6)),
    ('node_data_file', c_char * int(256)),
    ('dataFileVersion', c_int),
    ('numFileSegments', c_int),
    ('nodeCount', c_int),
    ('dataDecompType', c_int),
    ('dataDecompGeometry', c_int * int(3)),
    ('minCoordinates', c_double * int(3)),
    ('maxCoordinates', c_double * int(3)),
    ('simVol', c_double),
    ('burgVolFactor', c_double),
    ('maxNumThreads', c_int),
    ('strainTimeData', c_char * int(256)),
]

struct__cell.__slots__ = [
    'nodeQ',
    'nodeCount',
    'nbrList',
    'nbrCount',
    'domains',
    'domCount',
    'baseIdx',
    'xShift',
    'yShift',
    'zShift',
    'xIndex',
    'yIndex',
    'zIndex',
]
struct__cell._fields_ = [
    ('nodeQ', POINTER(Node_t)),
    ('nodeCount', c_int),
    ('nbrList', POINTER(c_int)),
    ('nbrCount', c_int),
    ('domains', POINTER(c_int)),
    ('domCount', c_int),
    ('baseIdx', c_int),
    ('xShift', c_double),
    ('yShift', c_double),
    ('zShift', c_double),
    ('xIndex', c_int),
    ('yIndex', c_int),
    ('zIndex', c_int),
]

struct__remotedomain.__slots__ = [
    'domainIdx',
    'numExpCells',
    'expCells',
    'maxTagIndex',
    'nodeKeys',
    'inBufLen',
    'inBuf',
    'outBufLen',
    'outBuf',
]
struct__remotedomain._fields_ = [
    ('domainIdx', c_int),
    ('numExpCells', c_int),
    ('expCells', POINTER(c_int)),
    ('maxTagIndex', c_int),
    ('nodeKeys', POINTER(POINTER(Node_t))),
    ('inBufLen', c_int),
    ('inBuf', String),
    ('outBufLen', c_int),
    ('outBuf', String),
]

struct__mirrordomain.__slots__ = [
    'nodeKeys',
    'newNodeKeyPtr',
    'armX',
    'armY',
    'armZ',
]
struct__mirrordomain._fields_ = [
    ('nodeKeys', POINTER(POINTER(Node_t))),
    ('newNodeKeyPtr', c_int),
    ('armX', POINTER(c_double)),
    ('armY', POINTER(c_double)),
    ('armZ', POINTER(c_double)),
]

struct__operate.__slots__ = [
    'type',
    'dom1',
    'idx1',
    'dom2',
    'idx2',
    'dom3',
    'idx3',
    'bx',
    'by',
    'bz',
    'x',
    'y',
    'z',
    'nx',
    'ny',
    'nz',
]
struct__operate._fields_ = [
    ('type', OpType_t),
    ('dom1', c_int),
    ('idx1', c_int),
    ('dom2', c_int),
    ('idx2', c_int),
    ('dom3', c_int),
    ('idx3', c_int),
    ('bx', c_double),
    ('by', c_double),
    ('bz', c_double),
    ('x', c_double),
    ('y', c_double),
    ('z', c_double),
    ('nx', c_double),
    ('ny', c_double),
    ('nz', c_double),
]

# /workspace/core/pydis/c/include/OpList.h: 61
if _libs["libpydis.so"].has("AddOp", "cdecl"):
    AddOp = _libs["libpydis.so"].get("AddOp", "cdecl")
    AddOp.argtypes = [POINTER(Home_t), OpType_t, c_int, c_int, c_int, c_int, c_int, c_int, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double]
    AddOp.restype = None

# /workspace/core/pydis/c/include/OpList.h: 65
if _libs["libpydis.so"].has("ClearOpList", "cdecl"):
    ClearOpList = _libs["libpydis.so"].get("ClearOpList", "cdecl")
    ClearOpList.argtypes = [POINTER(Home_t)]
    ClearOpList.restype = None

# /workspace/core/pydis/c/include/OpList.h: 66
if _libs["libpydis.so"].has("ExtendOpList", "cdecl"):
    ExtendOpList = _libs["libpydis.so"].get("ExtendOpList", "cdecl")
    ExtendOpList.argtypes = [POINTER(Home_t)]
    ExtendOpList.restype = None

# /workspace/core/pydis/c/include/OpList.h: 67
if _libs["libpydis.so"].has("FreeOpList", "cdecl"):
    FreeOpList = _libs["libpydis.so"].get("FreeOpList", "cdecl")
    FreeOpList.argtypes = [POINTER(Home_t)]
    FreeOpList.restype = None

# /workspace/core/pydis/c/include/OpList.h: 68
if _libs["libpydis.so"].has("InitOpList", "cdecl"):
    InitOpList = _libs["libpydis.so"].get("InitOpList", "cdecl")
    InitOpList.argtypes = [POINTER(Home_t)]
    InitOpList.restype = None

# /workspace/core/pydis/c/include/OpList.h: 69
if _libs["libpydis.so"].has("PrintOpList", "cdecl"):
    PrintOpList = _libs["libpydis.so"].get("PrintOpList", "cdecl")
    PrintOpList.argtypes = [POINTER(Home_t)]
    PrintOpList.restype = None

struct__timer.__slots__ = [
    'startTime',
    'incr',
    'accum',
    'save',
    'started',
    'name',
]
struct__timer._fields_ = [
    ('startTime', c_double),
    ('incr', c_double),
    ('accum', c_double),
    ('save', c_double),
    ('started', c_int),
    ('name', String),
]

enum_anon_32 = c_int# /workspace/core/pydis/c/include/Timer.h: 23

TOTAL_TIME = 0# /workspace/core/pydis/c/include/Timer.h: 23

INITIALIZE = (TOTAL_TIME + 1)# /workspace/core/pydis/c/include/Timer.h: 23

TIME_INTEGRATE = (INITIALIZE + 1)# /workspace/core/pydis/c/include/Timer.h: 23

SORT_NATIVE_NODES = (TIME_INTEGRATE + 1)# /workspace/core/pydis/c/include/Timer.h: 23

COMM_SEND_GHOSTS = (SORT_NATIVE_NODES + 1)# /workspace/core/pydis/c/include/Timer.h: 23

GHOST_COMM_BARRIER = (COMM_SEND_GHOSTS + 1)# /workspace/core/pydis/c/include/Timer.h: 23

CELL_CHARGE = (GHOST_COMM_BARRIER + 1)# /workspace/core/pydis/c/include/Timer.h: 23

CELL_CHARGE_BARRIER = (CELL_CHARGE + 1)# /workspace/core/pydis/c/include/Timer.h: 23

CALC_FORCE = (CELL_CHARGE_BARRIER + 1)# /workspace/core/pydis/c/include/Timer.h: 23

LOCAL_FORCE = (CALC_FORCE + 1)# /workspace/core/pydis/c/include/Timer.h: 23

REMOTE_FORCE = (LOCAL_FORCE + 1)# /workspace/core/pydis/c/include/Timer.h: 23

CALC_FORCE_BARRIER = (REMOTE_FORCE + 1)# /workspace/core/pydis/c/include/Timer.h: 23

CALC_VELOCITY = (CALC_FORCE_BARRIER + 1)# /workspace/core/pydis/c/include/Timer.h: 23

CALC_VELOCITY_BARRIER = (CALC_VELOCITY + 1)# /workspace/core/pydis/c/include/Timer.h: 23

COMM_SEND_VELOCITY = (CALC_VELOCITY_BARRIER + 1)# /workspace/core/pydis/c/include/Timer.h: 23

SPLIT_MULTI_NODES = (COMM_SEND_VELOCITY + 1)# /workspace/core/pydis/c/include/Timer.h: 23

COLLISION_HANDLING = (SPLIT_MULTI_NODES + 1)# /workspace/core/pydis/c/include/Timer.h: 23

POST_COLLISION_BARRIER = (COLLISION_HANDLING + 1)# /workspace/core/pydis/c/include/Timer.h: 23

COL_SEND_REMESH = (POST_COLLISION_BARRIER + 1)# /workspace/core/pydis/c/include/Timer.h: 23

COL_FIX_REMESH = (COL_SEND_REMESH + 1)# /workspace/core/pydis/c/include/Timer.h: 23

COL_FORCE_UPDATE = (COL_FIX_REMESH + 1)# /workspace/core/pydis/c/include/Timer.h: 23

GENERATE_IO = (COL_FORCE_UPDATE + 1)# /workspace/core/pydis/c/include/Timer.h: 23

PLOT = (GENERATE_IO + 1)# /workspace/core/pydis/c/include/Timer.h: 23

IO_BARRIER = (PLOT + 1)# /workspace/core/pydis/c/include/Timer.h: 23

REMESH_START_BARRIER = (IO_BARRIER + 1)# /workspace/core/pydis/c/include/Timer.h: 23

REMESH = (REMESH_START_BARRIER + 1)# /workspace/core/pydis/c/include/Timer.h: 23

SEND_REMESH = (REMESH + 1)# /workspace/core/pydis/c/include/Timer.h: 23

FIX_REMESH = (SEND_REMESH + 1)# /workspace/core/pydis/c/include/Timer.h: 23

FORCE_UPDATE_REMESH = (FIX_REMESH + 1)# /workspace/core/pydis/c/include/Timer.h: 23

REMESH_END_BARRIER = (FORCE_UPDATE_REMESH + 1)# /workspace/core/pydis/c/include/Timer.h: 23

MIGRATION = (REMESH_END_BARRIER + 1)# /workspace/core/pydis/c/include/Timer.h: 23

MIGRATION_BARRIER = (MIGRATION + 1)# /workspace/core/pydis/c/include/Timer.h: 23

LOADCURVE = (MIGRATION_BARRIER + 1)# /workspace/core/pydis/c/include/Timer.h: 23

LOAD_BALANCE = (LOADCURVE + 1)# /workspace/core/pydis/c/include/Timer.h: 23

SEGFORCE_COMM = (LOAD_BALANCE + 1)# /workspace/core/pydis/c/include/Timer.h: 23

TIMER_BLOCK_SIZE = (SEGFORCE_COMM + 1)# /workspace/core/pydis/c/include/Timer.h: 23

# /workspace/core/pydis/c/include/Timer.h: 75
if _libs["libpydis.so"].has("TimeAtRestart", "cdecl"):
    TimeAtRestart = _libs["libpydis.so"].get("TimeAtRestart", "cdecl")
    TimeAtRestart.argtypes = [POINTER(Home_t), c_int]
    TimeAtRestart.restype = None

# /workspace/core/pydis/c/include/Timer.h: 76
if _libs["libpydis.so"].has("TimerClear", "cdecl"):
    TimerClear = _libs["libpydis.so"].get("TimerClear", "cdecl")
    TimerClear.argtypes = [POINTER(Home_t), c_int]
    TimerClear.restype = None

# /workspace/core/pydis/c/include/Timer.h: 77
if _libs["libpydis.so"].has("TimerClearAll", "cdecl"):
    TimerClearAll = _libs["libpydis.so"].get("TimerClearAll", "cdecl")
    TimerClearAll.argtypes = [POINTER(Home_t)]
    TimerClearAll.restype = None

# /workspace/core/pydis/c/include/Timer.h: 78
if _libs["libpydis.so"].has("TimerInit", "cdecl"):
    TimerInit = _libs["libpydis.so"].get("TimerInit", "cdecl")
    TimerInit.argtypes = [POINTER(Home_t)]
    TimerInit.restype = None

# /workspace/core/pydis/c/include/Timer.h: 79
if _libs["libpydis.so"].has("TimerInitDLBReset", "cdecl"):
    TimerInitDLBReset = _libs["libpydis.so"].get("TimerInitDLBReset", "cdecl")
    TimerInitDLBReset.argtypes = [POINTER(Home_t)]
    TimerInitDLBReset.restype = None

# /workspace/core/pydis/c/include/Timer.h: 80
if _libs["libpydis.so"].has("TimerPrint", "cdecl"):
    TimerPrint = _libs["libpydis.so"].get("TimerPrint", "cdecl")
    TimerPrint.argtypes = [POINTER(Home_t)]
    TimerPrint.restype = None

# /workspace/core/pydis/c/include/Timer.h: 81
if _libs["libpydis.so"].has("TimerReinitialize", "cdecl"):
    TimerReinitialize = _libs["libpydis.so"].get("TimerReinitialize", "cdecl")
    TimerReinitialize.argtypes = [POINTER(Home_t)]
    TimerReinitialize.restype = None

# /workspace/core/pydis/c/include/Timer.h: 82
if _libs["libpydis.so"].has("TimerStart", "cdecl"):
    TimerStart = _libs["libpydis.so"].get("TimerStart", "cdecl")
    TimerStart.argtypes = [POINTER(Home_t), c_int]
    TimerStart.restype = None

# /workspace/core/pydis/c/include/Timer.h: 83
if _libs["libpydis.so"].has("TimerStop", "cdecl"):
    TimerStop = _libs["libpydis.so"].get("TimerStop", "cdecl")
    TimerStop.argtypes = [POINTER(Home_t), c_int]
    TimerStop.restype = None

# /workspace/core/pydis/c/include/Timer.h: 84
if _libs["libpydis.so"].has("TimerSave", "cdecl"):
    TimerSave = _libs["libpydis.so"].get("TimerSave", "cdecl")
    TimerSave.argtypes = [POINTER(Home_t), c_int]
    TimerSave.restype = None

# /workspace/core/pydis/c/include/Util.h: 29
if _libs["libpydis.so"].has("DecodeCellIdx", "cdecl"):
    DecodeCellIdx = _libs["libpydis.so"].get("DecodeCellIdx", "cdecl")
    DecodeCellIdx.argtypes = [POINTER(Home_t), c_int, POINTER(c_int), POINTER(c_int), POINTER(c_int)]
    DecodeCellIdx.restype = None

# /workspace/core/pydis/c/include/Util.h: 30
if _libs["libpydis.so"].has("DecodeCell2Idx", "cdecl"):
    DecodeCell2Idx = _libs["libpydis.so"].get("DecodeCell2Idx", "cdecl")
    DecodeCell2Idx.argtypes = [POINTER(Home_t), c_int, POINTER(c_int), POINTER(c_int), POINTER(c_int)]
    DecodeCell2Idx.restype = None

# /workspace/core/pydis/c/include/Util.h: 31
if _libs["libpydis.so"].has("DecodeDomainIdx", "cdecl"):
    DecodeDomainIdx = _libs["libpydis.so"].get("DecodeDomainIdx", "cdecl")
    DecodeDomainIdx.argtypes = [POINTER(Home_t), c_int, POINTER(c_int), POINTER(c_int), POINTER(c_int)]
    DecodeDomainIdx.restype = None

# /workspace/core/pydis/c/include/Util.h: 33
if _libs["libpydis.so"].has("EncodeCellIdx", "cdecl"):
    EncodeCellIdx = _libs["libpydis.so"].get("EncodeCellIdx", "cdecl")
    EncodeCellIdx.argtypes = [POINTER(Home_t), c_int, c_int, c_int]
    EncodeCellIdx.restype = c_int

# /workspace/core/pydis/c/include/Util.h: 34
if _libs["libpydis.so"].has("EncodeCell2Idx", "cdecl"):
    EncodeCell2Idx = _libs["libpydis.so"].get("EncodeCell2Idx", "cdecl")
    EncodeCell2Idx.argtypes = [POINTER(Home_t), c_int, c_int, c_int]
    EncodeCell2Idx.restype = c_int

# /workspace/core/pydis/c/include/Util.h: 35
if _libs["libpydis.so"].has("EncodeDomainIdx", "cdecl"):
    EncodeDomainIdx = _libs["libpydis.so"].get("EncodeDomainIdx", "cdecl")
    EncodeDomainIdx.argtypes = [POINTER(Home_t), c_int, c_int, c_int]
    EncodeDomainIdx.restype = c_int

# /workspace/core/pydis/c/include/Util.h: 41
if _libs["libpydis.so"].has("cross", "cdecl"):
    cross = _libs["libpydis.so"].get("cross", "cdecl")
    cross.argtypes = [c_double * int(3), c_double * int(3), c_double * int(3)]
    cross.restype = None

# /workspace/core/pydis/c/include/Util.h: 42
if _libs["libpydis.so"].has("CSpline", "cdecl"):
    CSpline = _libs["libpydis.so"].get("CSpline", "cdecl")
    CSpline.argtypes = [POINTER(c_double), POINTER(c_double), POINTER(c_double), c_int]
    CSpline.restype = None

# /workspace/core/pydis/c/include/Util.h: 43
if _libs["libpydis.so"].has("CSplint", "cdecl"):
    CSplint = _libs["libpydis.so"].get("CSplint", "cdecl")
    CSplint.argtypes = [POINTER(c_double), POINTER(c_double), POINTER(c_double), c_int, c_double, POINTER(c_double)]
    CSplint.restype = None

# /workspace/core/pydis/c/include/Util.h: 45
if _libs["libpydis.so"].has("DecompVec", "cdecl"):
    DecompVec = _libs["libpydis.so"].get("DecompVec", "cdecl")
    DecompVec.argtypes = [c_double * int(3), c_double * int(3), c_double * int(3), c_double * int(2)]
    DecompVec.restype = None

# /workspace/core/pydis/c/include/Util.h: 46
if _libs["libpydis.so"].has("FindAbsMax", "cdecl"):
    FindAbsMax = _libs["libpydis.so"].get("FindAbsMax", "cdecl")
    FindAbsMax.argtypes = [POINTER(c_double), c_int, POINTER(c_double), POINTER(c_int)]
    FindAbsMax.restype = None

# /workspace/core/pydis/c/include/Util.h: 48
if _libs["libpydis.so"].has("FindAbsMin", "cdecl"):
    FindAbsMin = _libs["libpydis.so"].get("FindAbsMin", "cdecl")
    FindAbsMin.argtypes = [POINTER(c_double), c_int, POINTER(c_double), POINTER(c_int)]
    FindAbsMin.restype = None

# /workspace/core/pydis/c/include/Util.h: 50
if _libs["libpydis.so"].has("FindMax", "cdecl"):
    FindMax = _libs["libpydis.so"].get("FindMax", "cdecl")
    FindMax.argtypes = [POINTER(c_double), c_int, POINTER(c_double), POINTER(c_int)]
    FindMax.restype = None

# /workspace/core/pydis/c/include/Util.h: 52
if _libs["libpydis.so"].has("FindMin", "cdecl"):
    FindMin = _libs["libpydis.so"].get("FindMin", "cdecl")
    FindMin.argtypes = [POINTER(c_double), c_int, POINTER(c_double), POINTER(c_int)]
    FindMin.restype = None

# /workspace/core/pydis/c/include/Util.h: 54
if _libs["libpydis.so"].has("GetPlaneNormFromPoints", "cdecl"):
    GetPlaneNormFromPoints = _libs["libpydis.so"].get("GetPlaneNormFromPoints", "cdecl")
    GetPlaneNormFromPoints.argtypes = [c_double * int(3), c_double * int(3), c_double * int(3), c_double * int(3)]
    GetPlaneNormFromPoints.restype = None

# /workspace/core/pydis/c/include/Util.h: 56
if _libs["libpydis.so"].has("GetUnitVector", "cdecl"):
    GetUnitVector = _libs["libpydis.so"].get("GetUnitVector", "cdecl")
    GetUnitVector.argtypes = [c_int, c_double, c_double, c_double, c_double, c_double, c_double, POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double)]
    GetUnitVector.restype = None

# /workspace/core/pydis/c/include/Util.h: 59
if _libs["libpydis.so"].has("InterpolateL", "cdecl"):
    InterpolateL = _libs["libpydis.so"].get("InterpolateL", "cdecl")
    InterpolateL.argtypes = [POINTER(c_double), POINTER(c_double), c_int, c_double, POINTER(c_double)]
    InterpolateL.restype = None

# /workspace/core/pydis/c/include/Util.h: 60
if _libs["libpydis.so"].has("InterpolateBL", "cdecl"):
    InterpolateBL = _libs["libpydis.so"].get("InterpolateBL", "cdecl")
    InterpolateBL.argtypes = [POINTER(c_double), POINTER(c_double), POINTER(c_double), c_int, c_double, c_double, POINTER(c_double)]
    InterpolateBL.restype = c_int

# /workspace/core/pydis/c/include/Util.h: 62
if _libs["libpydis.so"].has("Normal", "cdecl"):
    Normal = _libs["libpydis.so"].get("Normal", "cdecl")
    Normal.argtypes = [c_double * int(3)]
    Normal.restype = c_double

# /workspace/core/pydis/c/include/Util.h: 63
if _libs["libpydis.so"].has("Normalize", "cdecl"):
    Normalize = _libs["libpydis.so"].get("Normalize", "cdecl")
    Normalize.argtypes = [POINTER(c_double), POINTER(c_double), POINTER(c_double)]
    Normalize.restype = None

# /workspace/core/pydis/c/include/Util.h: 64
if _libs["libpydis.so"].has("NormalizeVec", "cdecl"):
    NormalizeVec = _libs["libpydis.so"].get("NormalizeVec", "cdecl")
    NormalizeVec.argtypes = [c_double * int(3)]
    NormalizeVec.restype = None

# /workspace/core/pydis/c/include/Util.h: 65
if _libs["libpydis.so"].has("NormalizedCrossVector", "cdecl"):
    NormalizedCrossVector = _libs["libpydis.so"].get("NormalizedCrossVector", "cdecl")
    NormalizedCrossVector.argtypes = [c_double * int(3), c_double * int(3), c_double * int(3)]
    NormalizedCrossVector.restype = None

# /workspace/core/pydis/c/include/Util.h: 66
if _libs["libpydis.so"].has("Orthogonalize", "cdecl"):
    Orthogonalize = _libs["libpydis.so"].get("Orthogonalize", "cdecl")
    Orthogonalize.argtypes = [POINTER(c_double), POINTER(c_double), POINTER(c_double), c_double, c_double, c_double]
    Orthogonalize.restype = None

# /workspace/core/pydis/c/include/Util.h: 68
if _libs["libpydis.so"].has("xvector", "cdecl"):
    xvector = _libs["libpydis.so"].get("xvector", "cdecl")
    xvector.argtypes = [c_double, c_double, c_double, c_double, c_double, c_double, POINTER(c_double), POINTER(c_double), POINTER(c_double)]
    xvector.restype = None

# /workspace/core/pydis/c/include/Util.h: 76
if _libs["libpydis.so"].has("AllocNodeArms", "cdecl"):
    AllocNodeArms = _libs["libpydis.so"].get("AllocNodeArms", "cdecl")
    AllocNodeArms.argtypes = [POINTER(Node_t), c_int]
    AllocNodeArms.restype = None

# /workspace/core/pydis/c/include/Util.h: 77
if _libs["libpydis.so"].has("FreeNode", "cdecl"):
    FreeNode = _libs["libpydis.so"].get("FreeNode", "cdecl")
    FreeNode.argtypes = [POINTER(Home_t), c_int]
    FreeNode.restype = None

# /workspace/core/pydis/c/include/Util.h: 78
if _libs["libpydis.so"].has("FreeNodeArms", "cdecl"):
    FreeNodeArms = _libs["libpydis.so"].get("FreeNodeArms", "cdecl")
    FreeNodeArms.argtypes = [POINTER(Node_t)]
    FreeNodeArms.restype = None

# /workspace/core/pydis/c/include/Util.h: 82
if _libs["libpydis.so"].has("GetNeighborNode", "cdecl"):
    GetNeighborNode = _libs["libpydis.so"].get("GetNeighborNode", "cdecl")
    GetNeighborNode.argtypes = [POINTER(Home_t), POINTER(Node_t), c_int]
    GetNeighborNode.restype = POINTER(Node_t)

# /workspace/core/pydis/c/include/Util.h: 84
if _libs["libpydis.so"].has("GetNodeFromIndex", "cdecl"):
    GetNodeFromIndex = _libs["libpydis.so"].get("GetNodeFromIndex", "cdecl")
    GetNodeFromIndex.argtypes = [POINTER(Home_t), c_int, c_int]
    GetNodeFromIndex.restype = POINTER(Node_t)

# /workspace/core/pydis/c/include/Util.h: 85
if _libs["libpydis.so"].has("GetNodeFromTag", "cdecl"):
    GetNodeFromTag = _libs["libpydis.so"].get("GetNodeFromTag", "cdecl")
    GetNodeFromTag.argtypes = [POINTER(Home_t), Tag_t]
    GetNodeFromTag.restype = POINTER(Node_t)

# /workspace/core/pydis/c/include/Util.h: 86
if _libs["libpydis.so"].has("InsertArm", "cdecl"):
    InsertArm = _libs["libpydis.so"].get("InsertArm", "cdecl")
    InsertArm.argtypes = [POINTER(Home_t), POINTER(Node_t), POINTER(Tag_t), c_double, c_double, c_double, c_double, c_double, c_double, c_int]
    InsertArm.restype = None

# /workspace/core/pydis/c/include/Util.h: 89
if _libs["libpydis.so"].has("MarkNodeForceObsolete", "cdecl"):
    MarkNodeForceObsolete = _libs["libpydis.so"].get("MarkNodeForceObsolete", "cdecl")
    MarkNodeForceObsolete.argtypes = [POINTER(Home_t), POINTER(Node_t)]
    MarkNodeForceObsolete.restype = None

# /workspace/core/pydis/c/include/Util.h: 90
if _libs["libpydis.so"].has("PrintNode", "cdecl"):
    PrintNode = _libs["libpydis.so"].get("PrintNode", "cdecl")
    PrintNode.argtypes = [POINTER(Node_t)]
    PrintNode.restype = None

# /workspace/core/pydis/c/include/Util.h: 91
if _libs["libpydis.so"].has("ReallocNodeArms", "cdecl"):
    ReallocNodeArms = _libs["libpydis.so"].get("ReallocNodeArms", "cdecl")
    ReallocNodeArms.argtypes = [POINTER(Node_t), c_int]
    ReallocNodeArms.restype = None

# /workspace/core/pydis/c/include/Util.h: 92
if _libs["libpydis.so"].has("RemoveNode", "cdecl"):
    RemoveNode = _libs["libpydis.so"].get("RemoveNode", "cdecl")
    RemoveNode.argtypes = [POINTER(Home_t), POINTER(Node_t), c_int]
    RemoveNode.restype = None

# /workspace/core/pydis/c/include/Util.h: 93
if _libs["libpydis.so"].has("RepositionNode", "cdecl"):
    RepositionNode = _libs["libpydis.so"].get("RepositionNode", "cdecl")
    RepositionNode.argtypes = [POINTER(Home_t), c_double * int(3), POINTER(Tag_t), c_int]
    RepositionNode.restype = None

# /workspace/core/pydis/c/include/Util.h: 94
if _libs["libpydis.so"].has("ResetNodeArmForce", "cdecl"):
    ResetNodeArmForce = _libs["libpydis.so"].get("ResetNodeArmForce", "cdecl")
    ResetNodeArmForce.argtypes = [POINTER(Home_t), POINTER(Node_t)]
    ResetNodeArmForce.restype = None

# /workspace/core/pydis/c/include/Util.h: 95
if _libs["libpydis.so"].has("SubtractSegForce", "cdecl"):
    SubtractSegForce = _libs["libpydis.so"].get("SubtractSegForce", "cdecl")
    SubtractSegForce.argtypes = [POINTER(Home_t), POINTER(Node_t), POINTER(Node_t)]
    SubtractSegForce.restype = None

# /workspace/core/pydis/c/include/Util.h: 101
if _libs["libpydis.so"].has("GetFreeNodeTag", "cdecl"):
    GetFreeNodeTag = _libs["libpydis.so"].get("GetFreeNodeTag", "cdecl")
    GetFreeNodeTag.argtypes = [POINTER(Home_t)]
    GetFreeNodeTag.restype = c_int

# /workspace/core/pydis/c/include/Util.h: 102
if _libs["libpydis.so"].has("GetRecycledNodeTag", "cdecl"):
    GetRecycledNodeTag = _libs["libpydis.so"].get("GetRecycledNodeTag", "cdecl")
    GetRecycledNodeTag.argtypes = [POINTER(Home_t)]
    GetRecycledNodeTag.restype = c_int

# /workspace/core/pydis/c/include/Util.h: 103
if _libs["libpydis.so"].has("RecycleNodeTag", "cdecl"):
    RecycleNodeTag = _libs["libpydis.so"].get("RecycleNodeTag", "cdecl")
    RecycleNodeTag.argtypes = [POINTER(Home_t), c_int]
    RecycleNodeTag.restype = None

# /workspace/core/pydis/c/include/Util.h: 109
if _libs["libpydis.so"].has("FoldBox", "cdecl"):
    FoldBox = _libs["libpydis.so"].get("FoldBox", "cdecl")
    FoldBox.argtypes = [POINTER(Param_t), POINTER(c_double), POINTER(c_double), POINTER(c_double)]
    FoldBox.restype = None

# /workspace/core/pydis/c/include/Util.h: 110
if _libs["libpydis.so"].has("PBCPOSITION", "cdecl"):
    PBCPOSITION = _libs["libpydis.so"].get("PBCPOSITION", "cdecl")
    PBCPOSITION.argtypes = [POINTER(Param_t), c_double, c_double, c_double, POINTER(c_double), POINTER(c_double), POINTER(c_double)]
    PBCPOSITION.restype = None

# /workspace/core/pydis/c/include/Util.h: 112
if _libs["libpydis.so"].has("ZImage", "cdecl"):
    ZImage = _libs["libpydis.so"].get("ZImage", "cdecl")
    ZImage.argtypes = [POINTER(Param_t), POINTER(c_double), POINTER(c_double), POINTER(c_double)]
    ZImage.restype = None

# /workspace/core/pydis/c/include/Util.h: 118
if _libs["libpydis.so"].has("ChangeArmBurg", "cdecl"):
    ChangeArmBurg = _libs["libpydis.so"].get("ChangeArmBurg", "cdecl")
    ChangeArmBurg.argtypes = [POINTER(Home_t), POINTER(Node_t), POINTER(Tag_t), c_double, c_double, c_double, c_double, c_double, c_double, c_int, c_double]
    ChangeArmBurg.restype = None

# /workspace/core/pydis/c/include/Util.h: 121
if _libs["libpydis.so"].has("ChangeConnection", "cdecl"):
    ChangeConnection = _libs["libpydis.so"].get("ChangeConnection", "cdecl")
    ChangeConnection.argtypes = [POINTER(Home_t), POINTER(Node_t), POINTER(Tag_t), POINTER(Tag_t), c_int]
    ChangeConnection.restype = c_int

# /workspace/core/pydis/c/include/Util.h: 123
if _libs["libpydis.so"].has("CompressArmLists", "cdecl"):
    CompressArmLists = _libs["libpydis.so"].get("CompressArmLists", "cdecl")
    CompressArmLists.argtypes = [POINTER(Node_t)]
    CompressArmLists.restype = None

# /workspace/core/pydis/c/include/Util.h: 127
if _libs["libpydis.so"].has("GetArmID", "cdecl"):
    GetArmID = _libs["libpydis.so"].get("GetArmID", "cdecl")
    GetArmID.argtypes = [POINTER(Home_t), POINTER(Node_t), POINTER(Node_t)]
    GetArmID.restype = c_int

# /workspace/core/pydis/c/include/Util.h: 129
if _libs["libpydis.so"].has("GetBurgersVectorNormal", "cdecl"):
    GetBurgersVectorNormal = _libs["libpydis.so"].get("GetBurgersVectorNormal", "cdecl")
    GetBurgersVectorNormal.argtypes = [POINTER(Home_t), POINTER(Node_t), POINTER(Node_t), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double)]
    GetBurgersVectorNormal.restype = None

# /workspace/core/pydis/c/include/Util.h: 132
if _libs["libpydis.so"].has("RecalcSegGlidePlane", "cdecl"):
    RecalcSegGlidePlane = _libs["libpydis.so"].get("RecalcSegGlidePlane", "cdecl")
    RecalcSegGlidePlane.argtypes = [POINTER(Home_t), POINTER(Node_t), POINTER(Node_t), c_int]
    RecalcSegGlidePlane.restype = None

# /workspace/core/pydis/c/include/Util.h: 134
if _libs["libpydis.so"].has("ResetGlidePlane", "cdecl"):
    ResetGlidePlane = _libs["libpydis.so"].get("ResetGlidePlane", "cdecl")
    ResetGlidePlane.argtypes = [POINTER(Home_t), c_double * int(3), POINTER(Tag_t), POINTER(Tag_t), c_int]
    ResetGlidePlane.restype = None

# /workspace/core/pydis/c/include/Util.h: 136
if _libs["libpydis.so"].has("ResetSegForces", "cdecl"):
    ResetSegForces = _libs["libpydis.so"].get("ResetSegForces", "cdecl")
    ResetSegForces.argtypes = [POINTER(Home_t), POINTER(Node_t), POINTER(Tag_t), c_double, c_double, c_double, c_int]
    ResetSegForces.restype = None

# /workspace/core/pydis/c/include/Util.h: 138
if _libs["libpydis.so"].has("ResetSegForces2", "cdecl"):
    ResetSegForces2 = _libs["libpydis.so"].get("ResetSegForces2", "cdecl")
    ResetSegForces2.argtypes = [POINTER(Home_t), POINTER(Node_t), POINTER(Tag_t), c_double, c_double, c_double, c_double, c_double, c_double, c_int]
    ResetSegForces2.restype = None

# /workspace/core/pydis/c/include/Util.h: 141
if _libs["libpydis.so"].has("ResetNodalVelocity", "cdecl"):
    ResetNodalVelocity = _libs["libpydis.so"].get("ResetNodalVelocity", "cdecl")
    ResetNodalVelocity.argtypes = [POINTER(Home_t), POINTER(Node_t), c_double, c_double, c_double, c_int]
    ResetNodalVelocity.restype = None

# /workspace/core/pydis/c/include/Util.h: 148
if _libs["libpydis.so"].has("CollisionNodeOrder", "cdecl"):
    CollisionNodeOrder = _libs["libpydis.so"].get("CollisionNodeOrder", "cdecl")
    CollisionNodeOrder.argtypes = [POINTER(Home_t), POINTER(Tag_t), POINTER(Tag_t)]
    CollisionNodeOrder.restype = c_int

# /workspace/core/pydis/c/include/Util.h: 149
if _libs["libpydis.so"].has("DomainOwnsSeg", "cdecl"):
    DomainOwnsSeg = _libs["libpydis.so"].get("DomainOwnsSeg", "cdecl")
    DomainOwnsSeg.argtypes = [POINTER(Home_t), c_int, c_int, POINTER(Tag_t)]
    DomainOwnsSeg.restype = c_int

# /workspace/core/pydis/c/include/Util.h: 150
if _libs["libpydis.so"].has("NodeCmpByTag", "cdecl"):
    NodeCmpByTag = _libs["libpydis.so"].get("NodeCmpByTag", "cdecl")
    NodeCmpByTag.argtypes = [POINTER(None), POINTER(None)]
    NodeCmpByTag.restype = c_int

# /workspace/core/pydis/c/include/Util.h: 154
if _libs["libpydis.so"].has("OrderNodes", "cdecl"):
    OrderNodes = _libs["libpydis.so"].get("OrderNodes", "cdecl")
    OrderNodes.argtypes = [POINTER(None), POINTER(None)]
    OrderNodes.restype = c_int

# /workspace/core/pydis/c/include/Util.h: 156
if _libs["libpydis.so"].has("OrderTags", "cdecl"):
    OrderTags = _libs["libpydis.so"].get("OrderTags", "cdecl")
    OrderTags.argtypes = [POINTER(None), POINTER(None)]
    OrderTags.restype = c_int

# /workspace/core/pydis/c/include/Util.h: 157
if _libs["libpydis.so"].has("SortNativeNodes", "cdecl"):
    SortNativeNodes = _libs["libpydis.so"].get("SortNativeNodes", "cdecl")
    SortNativeNodes.argtypes = [POINTER(Home_t)]
    SortNativeNodes.restype = None

# /workspace/core/pydis/c/include/Util.h: 163
if _libs["libpydis.so"].has("CreateFragmentList", "cdecl"):
    CreateFragmentList = _libs["libpydis.so"].get("CreateFragmentList", "cdecl")
    CreateFragmentList.argtypes = [POINTER(Home_t), POINTER(c_int)]
    CreateFragmentList.restype = POINTER(c_ubyte)
    CreateFragmentList.errcheck = lambda v,*a : cast(v, c_void_p)

# /workspace/core/pydis/c/include/Util.h: 171
for _lib in _libs.values():
    if _lib.has("Fatal", "cdecl"):
        _func = _lib.get("Fatal", "cdecl")
        _restype = None
        _errcheck = None
        _argtypes = [String]
        Fatal = _variadic_function(_func,_restype,_argtypes,_errcheck)

# /workspace/core/pydis/c/include/Util.h: 175
if _libs["libpydis.so"].has("Plot", "cdecl"):
    Plot = _libs["libpydis.so"].get("Plot", "cdecl")
    Plot.argtypes = [POINTER(Home_t), c_int, c_int]
    Plot.restype = None

# /workspace/core/pydis/c/include/Util.h: 176
if _libs["libpydis.so"].has("WriteArms", "cdecl"):
    WriteArms = _libs["libpydis.so"].get("WriteArms", "cdecl")
    WriteArms.argtypes = [POINTER(Home_t), String, c_int, c_int, c_int, c_int]
    WriteArms.restype = None

# /workspace/core/pydis/c/include/Util.h: 178
if _libs["libpydis.so"].has("WriteDensFlux", "cdecl"):
    WriteDensFlux = _libs["libpydis.so"].get("WriteDensFlux", "cdecl")
    WriteDensFlux.argtypes = [String, POINTER(Home_t)]
    WriteDensFlux.restype = None

# /workspace/core/pydis/c/include/Util.h: 179
if _libs["libpydis.so"].has("WriteDensityField", "cdecl"):
    WriteDensityField = _libs["libpydis.so"].get("WriteDensityField", "cdecl")
    WriteDensityField.argtypes = [POINTER(Home_t), String]
    WriteDensityField.restype = None

# /workspace/core/pydis/c/include/Util.h: 180
if _libs["libpydis.so"].has("WriteFragments", "cdecl"):
    WriteFragments = _libs["libpydis.so"].get("WriteFragments", "cdecl")
    WriteFragments.argtypes = [POINTER(Home_t), String, c_int, c_int, c_int, c_int, POINTER(POINTER(None)), c_int]
    WriteFragments.restype = None

# /workspace/core/pydis/c/include/Util.h: 183
if _libs["libpydis.so"].has("WritePoleFig", "cdecl"):
    WritePoleFig = _libs["libpydis.so"].get("WritePoleFig", "cdecl")
    WritePoleFig.argtypes = [POINTER(Home_t), String, c_int, c_int, c_int, c_int]
    WritePoleFig.restype = None

# /workspace/core/pydis/c/include/Util.h: 185
if _libs["libpydis.so"].has("WritePovray", "cdecl"):
    WritePovray = _libs["libpydis.so"].get("WritePovray", "cdecl")
    WritePovray.argtypes = [POINTER(Home_t), String, c_int, c_int, c_int, c_int]
    WritePovray.restype = None

# /workspace/core/pydis/c/include/Util.h: 187
if _libs["libpydis.so"].has("WriteAtomEye", "cdecl"):
    WriteAtomEye = _libs["libpydis.so"].get("WriteAtomEye", "cdecl")
    WriteAtomEye.argtypes = [POINTER(Home_t), String, c_int, c_int, c_int, c_int]
    WriteAtomEye.restype = None

# /workspace/core/pydis/c/include/Util.h: 195
if _libs["libpydis.so"].has("FindCellCenter", "cdecl"):
    FindCellCenter = _libs["libpydis.so"].get("FindCellCenter", "cdecl")
    FindCellCenter.argtypes = [POINTER(Param_t), c_double, c_double, c_double, c_int, POINTER(c_double), POINTER(c_double), POINTER(c_double)]
    FindCellCenter.restype = None

# /workspace/core/pydis/c/include/Util.h: 198
if _libs["libpydis.so"].has("LocateCell", "cdecl"):
    LocateCell = _libs["libpydis.so"].get("LocateCell", "cdecl")
    LocateCell.argtypes = [POINTER(Home_t), POINTER(c_int), c_double * int(3)]
    LocateCell.restype = None

# /workspace/core/pydis/c/include/Util.h: 199
if _libs["libpydis.so"].has("Meminfo", "cdecl"):
    Meminfo = _libs["libpydis.so"].get("Meminfo", "cdecl")
    Meminfo.argtypes = [POINTER(c_int)]
    Meminfo.restype = None

# /workspace/core/pydis/c/include/Util.h: 200
if _libs["libpydis.so"].has("NodeHasSessileBurg", "cdecl"):
    NodeHasSessileBurg = _libs["libpydis.so"].get("NodeHasSessileBurg", "cdecl")
    NodeHasSessileBurg.argtypes = [POINTER(Home_t), POINTER(Node_t)]
    NodeHasSessileBurg.restype = c_int

# /workspace/core/pydis/c/include/Util.h: 201
if _libs["libpydis.so"].has("NodePinned", "cdecl"):
    NodePinned = _libs["libpydis.so"].get("NodePinned", "cdecl")
    NodePinned.argtypes = [POINTER(Home_t), POINTER(Node_t), c_int, (c_double * int(3)) * int(3)]
    NodePinned.restype = c_int

# /workspace/core/pydis/c/include/Util.h: 203
if _libs["libpydis.so"].has("randm", "cdecl"):
    randm = _libs["libpydis.so"].get("randm", "cdecl")
    randm.argtypes = [POINTER(c_int)]
    randm.restype = c_double

# /workspace/core/pydis/c/include/Util.h: 204
if _libs["libpydis.so"].has("ReadTabulatedData", "cdecl"):
    ReadTabulatedData = _libs["libpydis.so"].get("ReadTabulatedData", "cdecl")
    ReadTabulatedData.argtypes = [String, c_int, POINTER(POINTER(POINTER(c_double))), POINTER(c_int)]
    ReadTabulatedData.restype = None

# /workspace/core/pydis/c/include/Util.h: 206
if _libs["libpydis.so"].has("ReadRijm", "cdecl"):
    ReadRijm = _libs["libpydis.so"].get("ReadRijm", "cdecl")
    ReadRijm.argtypes = [POINTER(Home_t)]
    ReadRijm.restype = None

# /workspace/core/pydis/c/include/Util.h: 207
if _libs["libpydis.so"].has("ReadRijmPBC", "cdecl"):
    ReadRijmPBC = _libs["libpydis.so"].get("ReadRijmPBC", "cdecl")
    ReadRijmPBC.argtypes = [POINTER(Home_t)]
    ReadRijmPBC.restype = None

# /workspace/core/pydis/c/include/Util.h: 208
if _libs["libpydis.so"].has("Sign", "cdecl"):
    Sign = _libs["libpydis.so"].get("Sign", "cdecl")
    Sign.argtypes = [c_double]
    Sign.restype = c_int

# /workspace/core/pydis/c/include/Util.h: 209
if _libs["libpydis.so"].has("testdeWitStress2", "cdecl"):
    testdeWitStress2 = _libs["libpydis.so"].get("testdeWitStress2", "cdecl")
    testdeWitStress2.argtypes = []
    testdeWitStress2.restype = None

# /workspace/core/pydis/c/include/Util.h: 210
if _libs["libpydis.so"].has("Uniq", "cdecl"):
    Uniq = _libs["libpydis.so"].get("Uniq", "cdecl")
    Uniq.argtypes = [POINTER(c_int), POINTER(c_int)]
    Uniq.restype = None

# /workspace/core/pydis/c/include/Util.h: 212
if _libs["libpydis.so"].has("Write_Node_Force_Vel", "cdecl"):
    Write_Node_Force_Vel = _libs["libpydis.so"].get("Write_Node_Force_Vel", "cdecl")
    Write_Node_Force_Vel.argtypes = [POINTER(Home_t), String, c_int]
    Write_Node_Force_Vel.restype = None

struct__indata.__slots__ = [
    'param',
    'node',
    'nodeCount',
    'burgX',
    'burgY',
    'burgZ',
    'nburg',
    'decomp',
]
struct__indata._fields_ = [
    ('param', POINTER(Param_t)),
    ('node', POINTER(Node_t)),
    ('nodeCount', c_int),
    ('burgX', POINTER(c_double)),
    ('burgY', POINTER(c_double)),
    ('burgZ', POINTER(c_double)),
    ('nburg', c_int),
    ('decomp', POINTER(None)),
]

# /workspace/core/pydis/c/include/Init.h: 13
if _libs["libpydis.so"].has("SetBoxSize", "cdecl"):
    SetBoxSize = _libs["libpydis.so"].get("SetBoxSize", "cdecl")
    SetBoxSize.argtypes = [POINTER(Param_t)]
    SetBoxSize.restype = None

# /workspace/core/pydis/c/include/Init.h: 14
if _libs["libpydis.so"].has("InitRecycleNodeHeap", "cdecl"):
    InitRecycleNodeHeap = _libs["libpydis.so"].get("InitRecycleNodeHeap", "cdecl")
    InitRecycleNodeHeap.argtypes = [POINTER(Home_t)]
    InitRecycleNodeHeap.restype = None

# /workspace/core/pydis/c/include/Init.h: 15
if _libs["libpydis.so"].has("InitCellDomains", "cdecl"):
    InitCellDomains = _libs["libpydis.so"].get("InitCellDomains", "cdecl")
    InitCellDomains.argtypes = [POINTER(Home_t)]
    InitCellDomains.restype = None

# /workspace/core/pydis/c/include/Init.h: 16
if _libs["libpydis.so"].has("InitCellNatives", "cdecl"):
    InitCellNatives = _libs["libpydis.so"].get("InitCellNatives", "cdecl")
    InitCellNatives.argtypes = [POINTER(Home_t)]
    InitCellNatives.restype = None

# /workspace/core/pydis/c/include/Init.h: 17
if _libs["libpydis.so"].has("InitCellNeighbors", "cdecl"):
    InitCellNeighbors = _libs["libpydis.so"].get("InitCellNeighbors", "cdecl")
    InitCellNeighbors.argtypes = [POINTER(Home_t)]
    InitCellNeighbors.restype = None

# /workspace/core/pydis/c/include/Init.h: 18
if _libs["libpydis.so"].has("InitHome", "cdecl"):
    InitHome = _libs["libpydis.so"].get("InitHome", "cdecl")
    InitHome.argtypes = []
    InitHome.restype = POINTER(Home_t)

# /workspace/core/pydis/c/include/Init.h: 19
if _libs["libpydis.so"].has("Initialize", "cdecl"):
    Initialize = _libs["libpydis.so"].get("Initialize", "cdecl")
    Initialize.argtypes = [POINTER(Home_t), c_int, POINTER(POINTER(c_char))]
    Initialize.restype = None

# /workspace/core/pydis/c/include/Init.h: 20
if _libs["libpydis.so"].has("OpenDir", "cdecl"):
    OpenDir = _libs["libpydis.so"].get("OpenDir", "cdecl")
    OpenDir.argtypes = [POINTER(Home_t)]
    OpenDir.restype = c_int

# /workspace/core/pydis/c/include/Init.h: 21
if _libs["libpydis.so"].has("ParadisInit", "cdecl"):
    ParadisInit = _libs["libpydis.so"].get("ParadisInit", "cdecl")
    ParadisInit.argtypes = [c_int, POINTER(POINTER(c_char)), POINTER(POINTER(Home_t))]
    ParadisInit.restype = None

# /workspace/core/pydis/c/include/Init.h: 22
if _libs["libpydis.so"].has("RecvInitialNodeData", "cdecl"):
    RecvInitialNodeData = _libs["libpydis.so"].get("RecvInitialNodeData", "cdecl")
    RecvInitialNodeData.argtypes = [POINTER(Home_t)]
    RecvInitialNodeData.restype = None

# /workspace/core/pydis/c/include/Init.h: 23
if _libs["libpydis.so"].has("SendInitialNodeData", "cdecl"):
    SendInitialNodeData = _libs["libpydis.so"].get("SendInitialNodeData", "cdecl")
    SendInitialNodeData.argtypes = [POINTER(Home_t), POINTER(InData_t), POINTER(c_int), POINTER(POINTER(c_int)), POINTER(c_int), POINTER(c_int)]
    SendInitialNodeData.restype = None

# /workspace/core/pydis/c/include/Init.h: 25
if _libs["libpydis.so"].has("SetRemainingDefaults", "cdecl"):
    SetRemainingDefaults = _libs["libpydis.so"].get("SetRemainingDefaults", "cdecl")
    SetRemainingDefaults.argtypes = [POINTER(Home_t)]
    SetRemainingDefaults.restype = None

# /workspace/core/pydis/c/include/Force.h: 16
if _libs["libpydis.so"].has("AddtoArmForce", "cdecl"):
    AddtoArmForce = _libs["libpydis.so"].get("AddtoArmForce", "cdecl")
    AddtoArmForce.argtypes = [POINTER(Node_t), c_int, c_double * int(3)]
    AddtoArmForce.restype = None

# /workspace/core/pydis/c/include/Force.h: 17
if _libs["libpydis.so"].has("AddtoNodeForce", "cdecl"):
    AddtoNodeForce = _libs["libpydis.so"].get("AddtoNodeForce", "cdecl")
    AddtoNodeForce.argtypes = [POINTER(Node_t), c_double * int(3)]
    AddtoNodeForce.restype = None

# /workspace/core/pydis/c/include/Force.h: 18
if _libs["libpydis.so"].has("ComputeForces", "cdecl"):
    ComputeForces = _libs["libpydis.so"].get("ComputeForces", "cdecl")
    ComputeForces.argtypes = [POINTER(Home_t), POINTER(Node_t), POINTER(Node_t), POINTER(Node_t), POINTER(Node_t), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double)]
    ComputeForces.restype = None

# /workspace/core/pydis/c/include/Force.h: 21
if _libs["libpydis.so"].has("ComputeSegSigbRem", "cdecl"):
    ComputeSegSigbRem = _libs["libpydis.so"].get("ComputeSegSigbRem", "cdecl")
    ComputeSegSigbRem.argtypes = [POINTER(Home_t), c_int]
    ComputeSegSigbRem.restype = None

# /workspace/core/pydis/c/include/Force.h: 22
if _libs["libpydis.so"].has("deWitInteraction", "cdecl"):
    deWitInteraction = _libs["libpydis.so"].get("deWitInteraction", "cdecl")
    deWitInteraction.argtypes = [c_double, c_double, POINTER(c_double * int(3)), c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, POINTER(c_double), POINTER(c_double), POINTER(c_double)]
    deWitInteraction.restype = None

# /workspace/core/pydis/c/include/Force.h: 27
if _libs["libpydis.so"].has("dSegImgStress", "cdecl"):
    dSegImgStress = _libs["libpydis.so"].get("dSegImgStress", "cdecl")
    dSegImgStress.argtypes = [POINTER(Home_t), POINTER(c_double * int(3)), c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_int]
    dSegImgStress.restype = None

# /workspace/core/pydis/c/include/Force.h: 32
if _libs["libpydis.so"].has("EstRefinementForces", "cdecl"):
    EstRefinementForces = _libs["libpydis.so"].get("EstRefinementForces", "cdecl")
    EstRefinementForces.argtypes = [POINTER(Home_t), POINTER(Node_t), POINTER(Node_t), c_double * int(3), c_double * int(3), c_double * int(3), c_double * int(3), c_double * int(3), c_double * int(3)]
    EstRefinementForces.restype = None

# /workspace/core/pydis/c/include/Force.h: 35
if _libs["libpydis.so"].has("EstCoarsenForces", "cdecl"):
    EstCoarsenForces = _libs["libpydis.so"].get("EstCoarsenForces", "cdecl")
    EstCoarsenForces.argtypes = [POINTER(Home_t), POINTER(Node_t), POINTER(Node_t), POINTER(Node_t), c_double * int(3), c_double * int(3)]
    EstCoarsenForces.restype = None

# /workspace/core/pydis/c/include/Force.h: 37
if _libs["libpydis.so"].has("ExtPKForce", "cdecl"):
    ExtPKForce = _libs["libpydis.so"].get("ExtPKForce", "cdecl")
    ExtPKForce.argtypes = [(c_double * int(3)) * int(3), c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double * int(3), c_double * int(3)]
    ExtPKForce.restype = None

# /workspace/core/pydis/c/include/Force.h: 40
if _libs["libpydis.so"].has("FindFSegComb", "cdecl"):
    FindFSegComb = _libs["libpydis.so"].get("FindFSegComb", "cdecl")
    FindFSegComb.argtypes = [POINTER(Home_t), c_double * int(3), c_double * int(3), c_double * int(3), c_double * int(3), c_double * int(3), c_double * int(3), c_double * int(3), c_double * int(3), c_double * int(3), c_double * int(3), c_double * int(3)]
    FindFSegComb.restype = None

# /workspace/core/pydis/c/include/Force.h: 44
if _libs["libpydis.so"].has("FindSubFSeg", "cdecl"):
    FindSubFSeg = _libs["libpydis.so"].get("FindSubFSeg", "cdecl")
    FindSubFSeg.argtypes = [POINTER(Home_t), c_double * int(3), c_double * int(3), c_double * int(3), c_double * int(3), c_double * int(3), c_double * int(3), c_double * int(3), c_double * int(3), c_double * int(3), c_double * int(3)]
    FindSubFSeg.restype = None

# /workspace/core/pydis/c/include/Force.h: 48
if _libs["libpydis.so"].has("GetFieldPointStress", "cdecl"):
    GetFieldPointStress = _libs["libpydis.so"].get("GetFieldPointStress", "cdecl")
    GetFieldPointStress.argtypes = [POINTER(Home_t), c_double, c_double, c_double, (c_double * int(3)) * int(3)]
    GetFieldPointStress.restype = None

# /workspace/core/pydis/c/include/Force.h: 50
if _libs["libpydis.so"].has("GetFieldPointStressRem", "cdecl"):
    GetFieldPointStressRem = _libs["libpydis.so"].get("GetFieldPointStressRem", "cdecl")
    GetFieldPointStressRem.argtypes = [POINTER(Home_t), c_double, c_double, c_double, c_int, c_int, c_int, (c_double * int(3)) * int(3)]
    GetFieldPointStressRem.restype = None

# /workspace/core/pydis/c/include/Force.h: 53
if _libs["libpydis.so"].has("LineTensionForce", "cdecl"):
    LineTensionForce = _libs["libpydis.so"].get("LineTensionForce", "cdecl")
    LineTensionForce.argtypes = [POINTER(Home_t), c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double * int(3), c_double * int(3)]
    LineTensionForce.restype = None

# /workspace/core/pydis/c/include/Force.h: 56
if _libs["libpydis.so"].has("LocalSegForces", "cdecl"):
    LocalSegForces = _libs["libpydis.so"].get("LocalSegForces", "cdecl")
    LocalSegForces.argtypes = [POINTER(Home_t), c_int]
    LocalSegForces.restype = None

# /workspace/core/pydis/c/include/Force.h: 57
if _libs["libpydis.so"].has("NodeForce", "cdecl"):
    NodeForce = _libs["libpydis.so"].get("NodeForce", "cdecl")
    NodeForce.argtypes = [POINTER(Home_t), c_int]
    NodeForce.restype = None

# /workspace/core/pydis/c/include/Force.h: 58
if _libs["libpydis.so"].has("OsmoticForce", "cdecl"):
    OsmoticForce = _libs["libpydis.so"].get("OsmoticForce", "cdecl")
    OsmoticForce.argtypes = [POINTER(Home_t), c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double * int(3), c_double * int(3)]
    OsmoticForce.restype = None

# /workspace/core/pydis/c/include/Force.h: 61
if _libs["libpydis.so"].has("PKForce", "cdecl"):
    PKForce = _libs["libpydis.so"].get("PKForce", "cdecl")
    PKForce.argtypes = [c_double * int(3), c_double, c_double, c_double, c_double, c_double, c_double, c_double * int(3), c_double * int(3)]
    PKForce.restype = None

# /workspace/core/pydis/c/include/Force.h: 64
if _libs["libpydis.so"].has("ReevaluateForces", "cdecl"):
    ReevaluateForces = _libs["libpydis.so"].get("ReevaluateForces", "cdecl")
    ReevaluateForces.argtypes = [POINTER(Home_t)]
    ReevaluateForces.restype = None

# /workspace/core/pydis/c/include/Force.h: 72
if _libs["libpydis.so"].has("SegmentSigb", "cdecl"):
    SegmentSigb = _libs["libpydis.so"].get("SegmentSigb", "cdecl")
    SegmentSigb.argtypes = [c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double * int(3)]
    SegmentSigb.restype = None

# /workspace/core/pydis/c/include/Force.h: 77
if _libs["libpydis.so"].has("SegSegForceIsotropic", "cdecl"):
    SegSegForceIsotropic = _libs["libpydis.so"].get("SegSegForceIsotropic", "cdecl")
    SegSegForceIsotropic.argtypes = [c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_int, c_int, POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double)]
    SegSegForceIsotropic.restype = None

# /workspace/core/pydis/c/include/Force.h: 89
if _libs["libpydis.so"].has("SegSegForce_SBN1", "cdecl"):
    SegSegForce_SBN1 = _libs["libpydis.so"].get("SegSegForce_SBN1", "cdecl")
    SegSegForce_SBN1.argtypes = [c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_int, POINTER(c_double), POINTER(c_double), c_int, c_int, POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double)]
    SegSegForce_SBN1.restype = None

# /workspace/core/pydis/c/include/Force.h: 102
if _libs["libpydis.so"].has("SegSegForce_SBN1_SBA", "cdecl"):
    SegSegForce_SBN1_SBA = _libs["libpydis.so"].get("SegSegForce_SBN1_SBA", "cdecl")
    SegSegForce_SBN1_SBA.argtypes = [c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_int, c_int, c_int, POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double)]
    SegSegForce_SBN1_SBA.restype = None

# /workspace/core/pydis/c/include/Force.h: 114
if _libs["libpydis.so"].has("SegSegForce", "cdecl"):
    SegSegForce = _libs["libpydis.so"].get("SegSegForce", "cdecl")
    SegSegForce.argtypes = [c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_int, c_int, POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double)]
    SegSegForce.restype = None

# /workspace/core/pydis/c/include/Force.h: 126
if _libs["libpydis.so"].has("SelfForce", "cdecl"):
    SelfForce = _libs["libpydis.so"].get("SelfForce", "cdecl")
    SelfForce.argtypes = [c_int, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double * int(3), c_double * int(3)]
    SelfForce.restype = None

# /workspace/core/pydis/c/include/Force.h: 130
if _libs["libpydis.so"].has("SemiInfiniteSegSegForce", "cdecl"):
    SemiInfiniteSegSegForce = _libs["libpydis.so"].get("SemiInfiniteSegSegForce", "cdecl")
    SemiInfiniteSegSegForce.argtypes = [c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, c_double, POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double)]
    SemiInfiniteSegSegForce.restype = None

# /workspace/core/pydis/c/include/Force.h: 140
if _libs["libpydis.so"].has("SetOneNodeForce", "cdecl"):
    SetOneNodeForce = _libs["libpydis.so"].get("SetOneNodeForce", "cdecl")
    SetOneNodeForce.argtypes = [POINTER(Home_t), POINTER(Node_t)]
    SetOneNodeForce.restype = None

# /workspace/core/pydis/c/include/Force.h: 141
if _libs["libpydis.so"].has("ZeroNodeForces", "cdecl"):
    ZeroNodeForces = _libs["libpydis.so"].get("ZeroNodeForces", "cdecl")
    ZeroNodeForces.argtypes = [POINTER(Home_t), c_int]
    ZeroNodeForces.restype = None

# /workspace/core/pydis/c/include/Home.h: 125
class struct_anon_33(Structure):
    pass

struct_anon_33.__slots__ = [
    'oldTag',
    'newTag',
]
struct_anon_33._fields_ = [
    ('oldTag', Tag_t),
    ('newTag', Tag_t),
]

TagMap_t = struct_anon_33# /workspace/core/pydis/c/include/Home.h: 125

# /workspace/core/pydis/c/include/Home.h: 137
class struct_anon_34(Structure):
    pass

struct_anon_34.__slots__ = [
    'forcesSet',
    'f1',
    'f2',
    'node1',
    'node2',
]
struct_anon_34._fields_ = [
    ('forcesSet', c_int),
    ('f1', c_double * int(3)),
    ('f2', c_double * int(3)),
    ('node1', POINTER(Node_t)),
    ('node2', POINTER(Node_t)),
]

Segment_t = struct_anon_34# /workspace/core/pydis/c/include/Home.h: 137

struct__segmentpair.__slots__ = [
    'seg1',
    'seg2',
    'setSeg1Forces',
    'setSeg2Forces',
]
struct__segmentpair._fields_ = [
    ('seg1', POINTER(Segment_t)),
    ('seg2', POINTER(Segment_t)),
    ('setSeg1Forces', c_int),
    ('setSeg2Forces', c_int),
]

# /workspace/core/pydis/c/include/Home.h: 170
class struct_anon_35(Structure):
    pass

struct_anon_35.__slots__ = [
    'numBurgVectors',
    'numPlanes',
    'numPlanesPerBurg',
    'burgFirstPlaneIndex',
    'burgList',
    'planeList',
]
struct_anon_35._fields_ = [
    ('numBurgVectors', c_int),
    ('numPlanes', c_int),
    ('numPlanesPerBurg', POINTER(c_int)),
    ('burgFirstPlaneIndex', POINTER(c_int)),
    ('burgList', POINTER(c_double * int(3))),
    ('planeList', POINTER(c_double * int(3))),
]

BurgInfo_t = struct_anon_35# /workspace/core/pydis/c/include/Home.h: 170

struct__home.__slots__ = [
    'myDomain',
    'numDomains',
    'cycle',
    'lastCycle',
    'param',
    'ctrlParamList',
    'dataParamList',
    'nativeNodeQ',
    'ghostNodeQ',
    'freeNodeQ',
    'lastFreeNode',
    'lastGhostNode',
    'nodeBlockQ',
    'nodeKeys',
    'newNodeKeyPtr',
    'newNodeKeyMax',
    'recycledNodeHeap',
    'recycledNodeHeapSize',
    'recycledNodeHeapEnts',
    'cellList',
    'cellCount',
    'nativeCellCount',
    'firstTime_FMInit',
    'cellKeys',
    'remoteDomainCount',
    'secondaryRemoteDomainCount',
    'remoteDomains',
    'remoteDomainKeys',
    'decomp',
    'domXmin',
    'domXmax',
    'domYmin',
    'domYmax',
    'domZmin',
    'domZmax',
    'xMaxLevel',
    'yMaxLevel',
    'zMaxLevel',
    'burgX',
    'burgY',
    'burgZ',
    'nburg',
    'mirrorDomainKeys',
    'currentMirrors',
    'inBuf',
    'outBuf',
    'opList',
    'OpCount',
    'OpListLen',
    'rcvOpList',
    'rcvOpCount',
    'timers',
    'cell2',
    'cell2QentArray',
    'cell2nx',
    'cell2ny',
    'cell2nz',
    'cellCharge',
    'tagMap',
    'tagMapSize',
    'tagMapEnts',
    'glPositions',
    'glWeights',
    'fmLayer',
    'fmNumMPCoeff',
    'fmNumTaylorCoeff',
    'cycleForceCalcCount',
    'rotMatrix',
    'rotMatrixInverse',
    'burgData',
    'ioGroupNum',
    'firstInIOGroup',
    'lastInIOGroup',
    'prevInIOGroup',
    'nextInIOGroup',
    'isFirstInIOGroup',
    'isLastInIOGroup',
    'clock_time_beg',
]
struct__home._fields_ = [
    ('myDomain', c_int),
    ('numDomains', c_int),
    ('cycle', c_int),
    ('lastCycle', c_int),
    ('param', POINTER(Param_t)),
    ('ctrlParamList', POINTER(ParamList_t)),
    ('dataParamList', POINTER(ParamList_t)),
    ('nativeNodeQ', POINTER(Node_t)),
    ('ghostNodeQ', POINTER(Node_t)),
    ('freeNodeQ', POINTER(Node_t)),
    ('lastFreeNode', POINTER(Node_t)),
    ('lastGhostNode', POINTER(Node_t)),
    ('nodeBlockQ', POINTER(NodeBlock_t)),
    ('nodeKeys', POINTER(POINTER(Node_t))),
    ('newNodeKeyPtr', c_int),
    ('newNodeKeyMax', c_int),
    ('recycledNodeHeap', POINTER(c_int)),
    ('recycledNodeHeapSize', c_int),
    ('recycledNodeHeapEnts', c_int),
    ('cellList', POINTER(c_int)),
    ('cellCount', c_int),
    ('nativeCellCount', c_int),
    ('firstTime_FMInit', c_int),
    ('cellKeys', POINTER(POINTER(Cell_t))),
    ('remoteDomainCount', c_int),
    ('secondaryRemoteDomainCount', c_int),
    ('remoteDomains', POINTER(c_int)),
    ('remoteDomainKeys', POINTER(POINTER(RemoteDomain_t))),
    ('decomp', POINTER(None)),
    ('domXmin', c_double),
    ('domXmax', c_double),
    ('domYmin', c_double),
    ('domYmax', c_double),
    ('domZmin', c_double),
    ('domZmax', c_double),
    ('xMaxLevel', c_int),
    ('yMaxLevel', c_int),
    ('zMaxLevel', c_int),
    ('burgX', POINTER(c_double)),
    ('burgY', POINTER(c_double)),
    ('burgZ', POINTER(c_double)),
    ('nburg', c_int),
    ('mirrorDomainKeys', POINTER(POINTER(MirrorDomain_t))),
    ('currentMirrors', c_int),
    ('inBuf', String),
    ('outBuf', String),
    ('opList', POINTER(Operate_t)),
    ('OpCount', c_int),
    ('OpListLen', c_int),
    ('rcvOpList', POINTER(Operate_t)),
    ('rcvOpCount', c_int),
    ('timers', POINTER(Timer_t)),
    ('cell2', POINTER(c_int)),
    ('cell2QentArray', POINTER(C2Qent_t)),
    ('cell2nx', c_int),
    ('cell2ny', c_int),
    ('cell2nz', c_int),
    ('cellCharge', POINTER(c_double)),
    ('tagMap', POINTER(TagMap_t)),
    ('tagMapSize', c_int),
    ('tagMapEnts', c_int),
    ('glPositions', POINTER(c_double)),
    ('glWeights', POINTER(c_double)),
    ('fmLayer', POINTER(FMLayer_t)),
    ('fmNumMPCoeff', c_int),
    ('fmNumTaylorCoeff', c_int),
    ('cycleForceCalcCount', c_int),
    ('rotMatrix', (c_double * int(3)) * int(3)),
    ('rotMatrixInverse', (c_double * int(3)) * int(3)),
    ('burgData', BurgInfo_t),
    ('ioGroupNum', c_int),
    ('firstInIOGroup', c_int),
    ('lastInIOGroup', c_int),
    ('prevInIOGroup', c_int),
    ('nextInIOGroup', c_int),
    ('isFirstInIOGroup', c_int),
    ('isLastInIOGroup', c_int),
    ('clock_time_beg', struct_timeval),
]

# /workspace/core/pydis/c/include/Home.h: 480
if _libs["libpydis.so"].has("AddNode", "cdecl"):
    AddNode = _libs["libpydis.so"].get("AddNode", "cdecl")
    AddNode.argtypes = [POINTER(Home_t), POINTER(Node_t), POINTER(Node_t), POINTER(Node_t)]
    AddNode.restype = None

# /workspace/core/pydis/c/include/Home.h: 481
if _libs["libpydis.so"].has("CommSendMirrorNodes", "cdecl"):
    CommSendMirrorNodes = _libs["libpydis.so"].get("CommSendMirrorNodes", "cdecl")
    CommSendMirrorNodes.argtypes = [POINTER(Home_t), c_int]
    CommSendMirrorNodes.restype = None

# /workspace/core/pydis/c/include/Home.h: 482
if _libs["libpydis.so"].has("Connected", "cdecl"):
    Connected = _libs["libpydis.so"].get("Connected", "cdecl")
    Connected.argtypes = [POINTER(Node_t), POINTER(Node_t), POINTER(c_int)]
    Connected.restype = c_int

# /workspace/core/pydis/c/include/Home.h: 483
if _libs["libpydis.so"].has("GetNewNativeNode", "cdecl"):
    GetNewNativeNode = _libs["libpydis.so"].get("GetNewNativeNode", "cdecl")
    GetNewNativeNode.argtypes = [POINTER(Home_t)]
    GetNewNativeNode.restype = POINTER(Node_t)

# /workspace/core/pydis/c/include/Home.h: 484
if _libs["libpydis.so"].has("GetNewGhostNode", "cdecl"):
    GetNewGhostNode = _libs["libpydis.so"].get("GetNewGhostNode", "cdecl")
    GetNewGhostNode.argtypes = [POINTER(Home_t), c_int, c_int]
    GetNewGhostNode.restype = POINTER(Node_t)

# /workspace/core/pydis/c/include/Home.h: 485
if _libs["libpydis.so"].has("Gnuplot", "cdecl"):
    Gnuplot = _libs["libpydis.so"].get("Gnuplot", "cdecl")
    Gnuplot.argtypes = [POINTER(Home_t), String, c_int, c_int, c_int, c_int]
    Gnuplot.restype = None

real8 = c_double# /workspace/core/pydis/c/calforce/SegSegForce.h: 2

real8 = c_double# /workspace/core/pydis/c/calforce/SegmentStress.h: 2

real8 = c_double# /workspace/core/pydis/c/calforce/StressDueToSeg.h: 2

real8 = c_double# /workspace/core/pydis/c/calforce/SegSegForce_SBN1.h: 2

real8 = c_double# /workspace/core/pydis/c/calforce/SegSegForce.h: 2

real8 = c_double# /workspace/core/pydis/c/calforce/SegSegForce_SBN1.h: 2

real8 = c_double# /workspace/core/pydis/c/calforce/SegSegForce_SBN1_SBA.h: 4

# /workspace/core/pydis/c/include/ParadisProto.h: 18
def MAX(a, b):
    return (a > b) and a or b

# /workspace/core/pydis/c/include/ParadisProto.h: 22
def MIN(a, b):
    return (a < b) and a or b

# /workspace/core/pydis/c/include/OpList.h: 16
try:
    OpBlock_Count = 500
except:
    pass

# /workspace/core/pydis/c/include/Util.h: 14
def DotProduct(vec1, vec2):
    return ((((vec1 [0]) * (vec2 [0])) + ((vec1 [1]) * (vec2 [1]))) + ((vec1 [2]) * (vec2 [2])))

_home = struct__home# /workspace/core/pydis/c/include/Home.h: 175

_operate = struct__operate# /workspace/core/pydis/c/include/OpList.h: 18

_timer = struct__timer# /workspace/core/pydis/c/include/Timer.h: 12

_segmentpair = struct__segmentpair# /workspace/core/pydis/c/include/Home.h: 140

# No inserted files

# No prefix-stripping

