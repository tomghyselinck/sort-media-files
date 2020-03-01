=================
Media File Sorter
=================

Tool to sort all kinds of media files.

This project initially started out of two scripts:

#. Sort media files like the Nextcloud client on an Android smartphone does.
#. Sort restored (media) files from a broken disk/partition/file system
   (using Testdisk_/PhotoRec_)

.. _Testdisk: https://www.cgsecurity.org/wiki/TestDisk
.. _PhotoRec: https://www.cgsecurity.org/wiki/PhotoRec

Usage
=====

.. code-block:: console

   $ python3 sort_media_files.py --help
   usage: sort_media_files.py [-h] --source-files SOURCE_FILES --destination-dir
                              DEST_DIR [--move] [--separate] [--no-rename]
                              [--dryrun]

   Sort image files like Nexcloud Android client does on a smartphone.

   optional arguments:
   -h, --help            show this help message and exit
   --source-files SOURCE_FILES
   --destination-dir DEST_DIR
   --move
   --separate
   --no-rename
   --dryrun

If you find this project doesn't work for you,
please feel free to file an issue or PR!

To-do list
==========

- Search for ``TODO`` in `source code`_ ;-)

.. _source code: ./sort_media_files.py

References
==========

MediaInfo Tool and Library
--------------------------

This project uses ``MediaInfoDLL3`` Python Library from MediaArea's MediaInfo:

- Homepage: https://mediaarea.net/MediaInfo
- GitHub: https://github.com/MediaArea/MediaInfoLib
- Releases: https://github.com/MediaArea/MediaInfoLib/releases

- Debian packages: https://packages.debian.org/buster/python3-mediainfodll

Contributor References
~~~~~~~~~~~~~~~~~~~~~~

Library definition:

- https://github.com/MediaArea/MediaInfoLib/blob/master/Source/MediaInfoDLL/MediaInfoDLL3.py

Examples:

- https://github.com/MediaArea/MediaInfoLib/blob/master/Source/Example/HowToUse_Dll3.py

Wrapped Interface:

- https://github.com/MediaArea/MediaInfoLib/blob/master/Source/MediaInfo/MediaInfo.h

Wrapped Constants:

- https://github.com/MediaArea/MediaInfoLib/blob/master/Source/MediaInfo/MediaInfo_Const.h

ExifRead
--------

And older code part of this project also uses ``exifread`` python library:

- https://github.com/ianare/exif-py (https://pypi.org/project/ExifRead/)

Media tags
----------

- https://exiftool.org/TagNames/
   - Pictures
      - https://exiftool.org/TagNames/JPEG.html
      - https://exiftool.org/TagNames/PNG.html
      - https://exiftool.org/TagNames/GIF.html
      - https://exiftool.org/TagNames/BMP.html

      - https://exiftool.org/TagNames/EXIF.html
      - https://exiftool.org/TagNames/IPTC.html
      - https://exiftool.org/TagNames/XMP.html
      - https://exiftool.org/TagNames/Microsoft.html
   - Audio
      - https://exiftool.org/TagNames/MPEG.html

      - https://exiftool.org/TagNames/ID3.html
   - Video
      - https://exiftool.org/TagNames/QuickTime.html
      - https://exiftool.org/TagNames/M2TS.html
      - https://exiftool.org/TagNames/H264.html

      - https://exiftool.org/TagNames/MPEG.html


Alternatives
============

Similar projects
----------------

There are lots of similar projects available on the web.
Please feel free to check out those if this script doesn't fit your needs:

- https://pypi.org/search/?q=exif&page=2

Some examples:

- https://github.com/erjoalgo/exiftimestamper (https://pypi.org/project/exiftimestamper/)
- https://github.com/dwardu89/photo_sorter (https://pypi.org/project/photo-org/)
- https://github.com/iamtio/photosorter (https://pypi.org/project/photosorter/
- https://github.com/wiso/pysortexif (https://pypi.org/project/pysortexif/)

More mature/extensive projects
------------------------------

- https://github.com/jmathai/elodie (https://pypi.org/project/elodie/)
   - Photo management tool: https://getelodie.com/

- https://exiftool.org/ (Perl library + command-line application)

