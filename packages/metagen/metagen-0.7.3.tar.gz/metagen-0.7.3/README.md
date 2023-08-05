# About

**metagen** is a command line utility to ease generation of
[`metadata.xml` files](https://devmanual.gentoo.org/ebuild-writing/misc-files/metadata/index.html)
for Gentoo packages.
It is licensed under the
[GPL v2 license](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)
and hosted at
[gitweb.gentoo.org](https://gitweb.gentoo.org/proj/metagen.git/).
Please use [Gentoo's Bugzilla](https://bugs.gentoo.org/)
to report bugs about **metagen**.


# Example

```
# metagen -e 'somebody@gentoo.org' -n 'Some Body' -t person -f -q
./metadata.xml written

# cat metadata.xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE pkgmetadata SYSTEM 'https://www.gentoo.org/dtd/metadata.dtd'>
<pkgmetadata>
        <maintainer type="person">
                <email>somebody@gentoo.org</email>
                <name>Some Body</name>
        </maintainer>
</pkgmetadata>
```


# Usage

```
# metagen --help
usage: metagen [-h] [--version] [--email EMAIL] [--name NAME] [--echangelog]
               [--desc DESC] [--type TYPE] [--long LONG] [--output OUTPUT]
               [--force] [--verbose] [--quiet] [-Q]

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit

maintainer arguments:
  --email EMAIL, -e EMAIL
                        Maintainer's email address
  --name NAME, -n NAME  Maintainer's name
  --echangelog, -m      Use name and email address from ECHANGELOG_USER
                        environmental variable. This is a shortcut for -e
                        <email> -n <name>
  --desc DESC, -d DESC  Description of maintainership
  --type TYPE, -t TYPE  Maintainer type as of GLEP 67; valid values are:
                        "person", "project", "unknown"

package arguments:
  --long LONG, -l LONG  Long description of package.

operation arguments:
  --output OUTPUT, -o OUTPUT
                        Specify location of output file.
  --force, -f           Force overwrite of existing metadata.
  --verbose, -v         Verbose. Output of file to stdout. (default)
  --quiet, -q           Squelch output of file to stdout.
  -Q                    Do not write file to disk.
```
