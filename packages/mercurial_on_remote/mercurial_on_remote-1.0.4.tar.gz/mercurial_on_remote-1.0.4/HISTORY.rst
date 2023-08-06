1.0.4
~~~~~~~~~~~

Fixed incompatibility with mercurials ≥ 5.8. Manifested as:
   $ hg onremote something status
   TypeError: getpath() missing 1 required positional argument: name
Fixed also another incompatibility with mercurials ≥ 6.0 (usually
shielded by that one).

Module tested with mercurials 5.9 and 6.0 (and still works with older
mercurials).


1.0.3
~~~~~~~~~~~

Extension didn't work properly on py3.8+hg5.7 (and likely some other
py3+hg versions). Error was twofold:
- attempts to call commands with options, like
     hg onremote cauchy log -l 3 -v
  failed reporting wrong options
- while handling unrelated invalid option, like (dir instead of cwd)
     hg --dir some/where log
  hg crashed instead of reporting error

1.0.2
~~~~~~~~~~~~

Fixing various links as Atlassian killed Bitbucket.
Testing against hg 5.3 and 5.4.


1.0.1
~~~~~~~~~~~~

Initial release. Both ssh, and local paths work. Tested on wide
range of Mercurials (from 3.4 to 5.2), including py3 versions
of the latter.
