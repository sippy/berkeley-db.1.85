
import os
import re
import shutil
import sys

from setuptools import setup, Extension

# Look for Berkeley db 1.85.  Note that it is built as a different module
# name so it can be included even when later versions are available.  A very
# restrictive search is performed to avoid accidentally building this module
# with a later version of the underlying db library.  May BSD-ish Unixes
# incorporate db 1.85 symbols into libc and place the include file in
# /usr/include.
#
# If the system does not provide db 1.85 (e.g. Linux, where /usr/include/db.h
# is either missing or belongs to a later Berkeley DB), compile the db 1.85
# sources from this repository directly into the extension.  Set
# BSDDB185_BUNDLED=1 to force this.

here = os.path.dirname(os.path.abspath(__file__))
top = os.path.relpath(os.path.join(here, '..'), os.getcwd())

def have_system_db185(f="/usr/include/db.h"):
    if not os.path.exists(f):
        print("Didn't find %s" % f)
        return False
    with open(f, errors='replace') as fh:
        data = fh.read()
    if re.search(r"#\s*define\s+HASHVERSION\s+2\b", data) is None:
        print("Didn't find db.h with HASHVERSION == 2")
        return False
    return True

def bundled_ext():
    srcs = {
        'hash': ('hash.c', 'hash_bigkey.c', 'hash_buf.c', 'hash_func.c',
                 'hash_log2.c', 'hash_page.c'),
        'btree': ('bt_close.c', 'bt_conv.c', 'bt_debug.c', 'bt_delete.c',
                  'bt_get.c', 'bt_open.c', 'bt_overflow.c', 'bt_page.c',
                  'bt_put.c', 'bt_search.c', 'bt_seq.c', 'bt_split.c',
                  'bt_utils.c'),
        'db': ('db.c',),
        'mpool': ('mpool.c',),
        'recno': ('rec_close.c', 'rec_delete.c', 'rec_get.c', 'rec_open.c',
                  'rec_put.c', 'rec_search.c', 'rec_seq.c', 'rec_utils.c'),
    }
    sources = ['bsddb185.c']
    for d, files in srcs.items():
        sources.extend(os.path.join(top, d, f) for f in files)
    missing = [s for s in sources if not os.path.exists(s)]
    if missing:
        sys.exit("db 1.85 sources not found (%s); build from a full "
                 "checkout of berkeley-db.1.85" % ', '.join(missing))
    # mpool.h needs CIRCLEQ_* from the 4.4BSD <sys/queue.h>, which modern
    # FreeBSD and musl don't provide; supply the bundled copy (and cdefs.h
    # where the system lacks one).
    shim = os.path.join('build', 'db185-include')
    os.makedirs(os.path.join(shim, 'sys'), exist_ok=True)
    shims = ['queue.h']
    if not os.path.exists('/usr/include/sys/cdefs.h'):
        shims.append('cdefs.h')
    for h in shims:
        shutil.copyfile(os.path.join(top, 'PORT', 'include', h),
                        os.path.join(shim, 'sys', h))
    port = os.path.join(top, 'PORT', 'linux')
    return Extension('bsddb185', sources,
                     include_dirs=[os.path.join(port, 'include'), shim],
                     define_macros=[('__DBINTERFACE_PRIVATE', None)],
                     # Keep the db 1.85 symbols (dbopen() etc.) private
                     # to the module.
                     extra_compile_args=['-fvisibility=hidden'])

if os.environ.get('BSDDB185_BUNDLED') != '1' and have_system_db185():
    # bingo - old version used hash file format version 2
    # Platforms like FreeBSD may provide dbopen() from libc, but Linux
    # needs an explicit libdb link to avoid leaving dbopen unresolved
    # until dlopen() time.
    libraries = sys.platform in ("osf1", "linux", "linux2") and ['db'] or None
    ext = Extension('bsddb185', ['bsddb185.c'], libraries=libraries)
else:
    print("Building with bundled db 1.85 sources")
    ext = bundled_ext()

setup(name='bsddb185',
      author='Skip Montanaro',
      author_email='skip@pobox.com',
      maintainer='Skip Montanaro',
      maintainer_email='skip@pobox.com',
      url='http://www.webfast.com/~skip/python/',
      download_url='http://www.webfast.com/~skip/python/bsddb185-1.1.tar.gz',
      version='1.1',
      ext_modules=[ext],
      classifiers=['Development Status :: 6 - Mature',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: Python Software Foundation License',
                   'Operating System :: MacOS',
                   'Operating System :: POSIX',
                   'Operating System :: POSIX :: BSD',
                   'Programming Language :: C',
                   'Programming Language :: Python',
                   'Topic :: Database',
                   ]
      )
