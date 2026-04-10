
import os
import re
import sys

from distutils.core import setup, Extension

# Look for Berkeley db 1.85.  Note that it is built as a different module
# name so it can be included even when later versions are available.  A very
# restrictive search is performed to avoid accidentally building this module
# with a later version of the underlying db library.  May BSD-ish Unixes
# incorporate db 1.85 symbols into libc and place the include file in
# /usr/include.

f = "/usr/include/db.h"
ext = None
if os.path.exists(f):
    data = open(f).read()
    m = re.search(r"#s*define\s+HASHVERSION\s+2\s*", data)
    if m is not None:
        # bingo - old version used hash file format version 2
        # XXX Can someone confirm this osf1 test?
        libraries = sys.platform == "osf1" and ['db'] or None
        if libraries is not None:
            ext = (Extension('bsddb185', ['bsddb185.c'],
                             libraries=libraries))
        else:
            ext = (Extension('bsddb185', ['bsddb185.c']))
    else:
        print ("Didn't find db.h with HASHVERSION == 2")
else:
    print ("Didn't find %s" % f)

if ext is not None:
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
