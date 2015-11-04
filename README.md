amender.py
==========

a simple script to amend compatibility issues between newest versions of [jaspersoft-studio](http://community.jaspersoft.com/project/jaspersoft-studio/releases) 
and Odoo/OpenERP module.

### run it

    ~$ ./amender.py -h

    usage: amender.py [-h] [-d DIR2WATCH] [-p PREFIX] [-r] [-v]

    optional arguments:
      -h, --help            show this help message and exit
      -d DIR2WATCH, --dir2watch DIR2WATCH
                            Directory with the .jrxml files. Default: '.'
      -p PREFIX, --prefix PREFIX
                            Prefix for the amended file. This is not sanitized so
                            be sure you do not overwrite the orignal file.
                            Default: amended-
      -r, --rec             Watch directory recursively. Default: False
      -v, --version         Print version and exit.
