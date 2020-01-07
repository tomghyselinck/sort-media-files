#!/usr/bin/env python3
#
# Requirements:
# - ( python3-mimeparse: Read MIME type )
# - python3-exif: Image TAG reading
# - python3-mediainfodll: Music/Video TAG reading
# - ( python3-pytaglib: Music/Video TAG reading )
# - ( python3-mutagen: Music/Video TAG reading )
#
# import logging
# from sys import argv, stdout
# from os import environ
#
# _DEBUG = bool(environ.get('DEBUG', False))
# logging.basicConfig(stream=stdout,
#                     level=logging.DEBUG if _DEBUG else logging.INFO,
#                     format='%(message)s')

import datetime
import exifread
import MediaInfoDLL3
import logging

from glob import iglob
from os import makedirs, stat
from os.path import basename, dirname, exists, isdir, join, splitext
from pprint import pformat
from shutil import copy2 as copy, move

_EXIF_DATETIME_ORIGINAL = 'EXIF DateTimeOriginal'
_EXIF_DATETIME_DIGITIZED = 'EXIF DateTimeDigitized'
_IMAGE_DATETIME = 'Image DateTime'

_TRY_TAGS = (_EXIF_DATETIME_ORIGINAL, _EXIF_DATETIME_DIGITIZED,
             _IMAGE_DATETIME)

_LOGGER = logging.getLogger(__name__)


def _get_mtime(input_file: str):
    file_stat = stat(input_file)
    return file_stat.st_mtime


def _get_generic_subdir(input_file: str):
    mtime = _get_mtime(input_file)
    parsed_date = datetime.date.fromtimestamp(mtime)

    return join(parsed_date.strftime('%Y'), parsed_date.strftime('%m'))


def _read_exif_info(input_file: str, try_tags: tuple = tuple()):
    with open(input_file, 'rb') as img_fd:
        exif_info = exifread.process_file(img_fd, details=False)
        _LOGGER.debug('exif_info: %s', pformat(exif_info))

        for try_tag in try_tags:
            if try_tag in exif_info:
                _LOGGER.debug('TAG \'%s\': %s', try_tag,
                              pformat(exif_info[try_tag]))
                return exif_info[try_tag]

    raise Exception('None of the TAGs ({}) available for {}'.format(
        try_tags, input_file))


def _get_image_subdir(input_file: str):
    date_time_tag = _read_exif_info(input_file, try_tags=_TRY_TAGS)

    date_time = date_time_tag.values
    _LOGGER.debug('date_time: %s', pformat(date_time))

    (date_val, time_val) = date_time.split()
    iso_date_val = date_val.replace(':', '-')

    parsed_date = datetime.date.fromisoformat(iso_date_val)
    parsed_time = datetime.time.fromisoformat(time_val)

    return join(parsed_date.strftime('%Y'), parsed_date.strftime('%m'))


def _get_image_datetime(input_file: str, *args, **kwargs):
    date_time_tag = _read_exif_info(input_file, try_tags=_TRY_TAGS)

    date_time = date_time_tag.values
    _LOGGER.debug('date_time: %s', pformat(date_time))

    (date_val, time_val) = date_time.split()
    iso_date_val = date_val.replace(':', '-')

    parsed_date = datetime.date.fromisoformat(iso_date_val)
    parsed_time = datetime.time.fromisoformat(time_val)

    # return parsed_date, parsed_time
    return datetime.datetime.combine(parsed_date, parsed_time)


def _from_rfc3339_format(datetime_str: str):
    """
    _from_rfc3339_format('2012-07-20 03:00:05+00:00')
    """
    return datetime.datetime.fromisoformat(datetime_str)


def _from_iso8601_format(datetime_str: str):
    """
    _from_iso8601_format('2014-05-19T09:19:21+0200')
    """
    return datetime.datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S%z')


# def _fromisoZoneformat(datetime_str: str):
#     """
#     _fromisoZoneformat('UTC 2014-05-19 07:19:21')
#     """
#     return datetime.datetime.strptime(datetime_str, 'UTC %Y-%m-%dT%H:%M:%S%z')


def _fromtimestring(datetime_str: str):
    if datetime_str == '':
        raise ValueError('Got empty timestamp')
        # return None

    if datetime_str.startswith('UTC '):
        parse_datetime_str = datetime_str[4:]
    else:
        parse_datetime_str = datetime_str

    try:
        return _from_iso8601_format(parse_datetime_str)
    except ValueError:
        pass

    try:
        return _from_rfc3339_format(parse_datetime_str)
    except ValueError:
        pass

    raise ValueError(f'Unsupported timestamp format: {datetime_str}')


_MEDIA_DATE_INFO = [
    'Recorded_Date',
    'Encoded_Date',
    'Tagged_Date',
]


def _get_mediainfo_datetime(input_file: str,
                            media_info: MediaInfoDLL3.MediaInfo):
    for date_info in _MEDIA_DATE_INFO:
        datetime_str = media_info.Get(MediaInfoDLL3.Stream.General, 0,
                                      date_info)
        if datetime_str != '':
            try:
                return _fromtimestring(datetime_str)
            except ValueError:
                _LOGGER.error(
                    f'Unable to parse date/time \'{date_info}\'=\'{datetime_str}\'.'
                )

    raise ValueError(
        f'No (valid) date/time info found in: {", ".join(_MEDIA_DATE_INFO)}')


_PICTURES_SUBDIR = 'Pictures'
_VIDEOS_SUBDIR = 'Videos'
_AUDIO_SUBDIR = 'Audio'
_OTHER_SUBDIR = 'Other'

# TODO: Support for other documents
#     ? MS Office documents: doc, docx, xls, xlsx, ppt, pptx, pps, ppsx, pst, ...
#     ? OpenDocument formats: odt, ods, ...
#     ? Other: pdf, swf, ...
#     ? Audio: MIDI, mp3 (audio/mpeg), ...
_MEDIA_TYPE_HANDLERS = {
    # Bitmap
    # TODO: Check if EXIF/XMP info is available
    'image/bmp': (_get_image_datetime, _PICTURES_SUBDIR),
    # GIF - Graphics Interchange Format
    # TODO: Check if EXIF/XMP info works fine
    'image/gif': (_get_image_datetime, _PICTURES_SUBDIR),
    # JPEG
    'image/jpeg': (_get_image_datetime, _PICTURES_SUBDIR),
    # PNG - Portable Network Graphic
    'image/png': (_get_image_datetime, _PICTURES_SUBDIR),
    # TIFF
    'image/tiff': (_get_image_datetime, _PICTURES_SUBDIR),
    # MPEG-4
    'audio/mp4': (_get_mediainfo_datetime, _AUDIO_SUBDIR),
    # Profiles:
    # - Base Media
    # - 3GPP Media Release 4
    'video/mp4': (_get_mediainfo_datetime, _VIDEOS_SUBDIR),
    # QuickTime
    'video/quicktime': (_get_mediainfo_datetime, _VIDEOS_SUBDIR),
    # AVI - Audio Video Interleave
    'video/vnd.avi': (_get_mediainfo_datetime, _VIDEOS_SUBDIR),
    # AMR - Adaptive Multi-Rate
    # TODO: Check if media info is available
    'audio/AMR': (_get_mediainfo_datetime, _AUDIO_SUBDIR),
    # MIDI - RIFF Musical Instrument Digital Interface
    # TODO: Check if media info is available
    # 'audio/midi': (_get_mediainfo_datetime, _AUDIO_SUBDIR),
    # MPEG Audio
    # 'audio/mpeg': (_get_mediainfo_datetime, _AUDIO_SUBDIR),
    # Wave
    # TODO: Check if media info is available
    'audio/vnd.wave': (_get_mediainfo_datetime, _AUDIO_SUBDIR),
    # Windows Media
    'audio/x-ms-wma': (_get_mediainfo_datetime, _AUDIO_SUBDIR),
    'video/x-ms-wmv': (_get_mediainfo_datetime, _VIDEOS_SUBDIR),
    # Q&D hack for MP2TS
    # ! FIXME - Should check on Format (=> BDAV) instead
    '': (_get_mediainfo_datetime, _VIDEOS_SUBDIR),
}


def _canonical_image_location(input_file: str):
    mi = MediaInfoDLL3.MediaInfo()
    result = mi.Open(input_file)
    if result != 1:
        raise Exception(f'Unable to load input file \'{input_file}\'')
    try:
        media_type = mi.Get(MediaInfoDLL3.Stream.General, 0,
                            'InternetMediaType')

        file_ext = mi.Get(MediaInfoDLL3.Stream.General, 0, 'FileExtension')
        if file_ext == '':
            file_extensions = mi.Get(MediaInfoDLL3.Stream.General, 0,
                                     'Format/Extensions')
            if file_extensions != '':
                file_ext = file_extensions.split()[0]
            _LOGGER.debug('Using file extension \'%s\' for media type \'%s\'',
                          file_ext, media_type)
        if file_ext == '':
            raise Exception(
                f'Unable to determine file extension for media type: {media_type}'
            )

        if media_type not in _MEDIA_TYPE_HANDLERS:
            raise Exception(f'Unsupported media type: {media_type}')

        get_datetime, media_subdir = _MEDIA_TYPE_HANDLERS[media_type]
        date_time: datetime.datetime = get_datetime(input_file=input_file,
                                                    media_info=mi)
    finally:
        mi.Close()

    return (
        media_subdir,
        join(date_time.strftime('%Y'), date_time.strftime('%m'),
             date_time.strftime('%d')),
        date_time.strftime('%Y-%m-%d_%H-%M-%S'),
        file_ext,
    )


def _process_input_file(input_file: str,
                        dest_dir: str,
                        separate: bool = False,
                        do_rename: bool = True,
                        process_function: callable = copy):
    if isdir(input_file):
        _LOGGER.info('Skipping directory \033[0;33m%s\033[0;m', input_file)
        return

    _LOGGER.info('Processing input file %s', input_file)

    # output_subdir = _get_image_subdir(input_file)
    # output_subdir = _get_generic_subdir(input_file)
    # output_subdir, output_file_name = _canonical_image_location(input_file)
    (
        media_subdir,
        output_subdir,
        output_file_basename,
        output_file_ext,
    ) = _canonical_image_location(input_file)
    if separate:
        output_dir = join(dest_dir, media_subdir, output_subdir)
    else:
        output_dir = join(dest_dir, output_subdir)

    if not do_rename:
        output_file_basename, output_file_ext = splitext(basename(input_file))

    output_file_name = '.'.join((output_file_basename, output_file_ext))
    output_file = join(output_dir, output_file_name)

    # if exists(output_file):
    #     raise Exception(
    #         'Output file \'{}\' already exists'.format(output_file))

    counter = 0
    while exists(output_file):
        counter += 1
        _LOGGER.info(
            'Output file \033[0;33m\'{}\'\033[0;m already exists'.format(
                output_file))
        output_file_name = '.'.join(
            (f'{output_file_basename}_{counter}', output_file_ext))
        output_file = join(output_dir, output_file_name)

    # _LOGGER.info('Copying %s to %s', input_file, output_dir)

    # makedirs(output_dir, mode=0o755, exist_ok=True)

    # # process_function(input_file, output_dir)

    process_function(input_file, output_file)


def process_media_files(source_files: str,
                        dest_dir: str,
                        separate: bool = False,
                        do_rename: bool = True,
                        process_function: callable = copy):
    input_files = iglob(source_files, recursive=True)
    for input_file in input_files:
        try:
            _process_input_file(input_file,
                                dest_dir,
                                separate=separate,
                                do_rename=do_rename,
                                process_function=process_function)
        except:
            _LOGGER.info(
                f'Failed to process \033[0;31m{input_file}\033[0;m. \033[0;33mSkipping\033[0;m.'
            )
            _LOGGER.exception(f'Failed to process {input_file}.')


def _parse_options(args: list) -> tuple:
    from argparse import ArgumentParser

    parser = ArgumentParser(
        description=
        'Sort image files link Nexcloud Andriod client does on a smartphone.')

    parser.add_argument('--source-files',
                        dest='source_files',
                        default='.',
                        required=True)

    parser.add_argument('--destination-dir', dest='dest_dir', required=True)

    parser.add_argument('--move',
                        dest='copy',
                        default=True,
                        action='store_false')

    parser.add_argument('--separate',
                        dest='separate',
                        default=False,
                        action='store_true')

    parser.add_argument('--no-rename',
                        dest='rename',
                        default=True,
                        action='store_false')

    parser.add_argument('--dryrun',
                        dest='dryrun',
                        default=False,
                        action='store_true')

    parsed_args = parser.parse_args(args=args)

    return (
        parsed_args.source_files,
        parsed_args.dest_dir,
        parsed_args.copy,
        parsed_args.separate,
        parsed_args.rename,
        parsed_args.dryrun,
    )


def _generate_process_function(is_copy: bool, is_dryrun: bool):
    if is_copy:
        _LOGGER.debug("Copying files")
        action_name = 'Copying'
        real_makedirs = makedirs
        real_process_function = copy
    else:
        _LOGGER.debug("Moving files")
        action_name = 'Moving'
        real_makedirs = makedirs
        real_process_function = move

    if is_dryrun:
        _LOGGER.info("*** DRY-RUN ***")

        def dummy_function(*args, **kwargs):
            pass

        action_name = '[DRY-RUN] ' + action_name
        real_makedirs = dummy_function
        real_process_function = dummy_function

    def process_function(input_file: str, output_file: str):
        output_dir = dirname(output_file)

        # _LOGGER.info('%s %s to %s', action_name, input_file, output_dir)
        _LOGGER.info('%s \033[0;32m%s\033[0;m to \033[0;32m%s\033[0;m',
                     action_name, input_file, output_file)

        # Create destination directory
        real_makedirs(output_dir, mode=0o755, exist_ok=True)

        # Apply the action on the file
        # real_process_function(input_file, output_dir)
        real_process_function(input_file, output_file)

    return process_function


def main():
    from sys import argv, stdout
    from os import environ

    log_debug = bool(environ.get('DEBUG', False))
    logging.basicConfig(stream=stdout,
                        level=logging.DEBUG if log_debug else logging.INFO,
                        format='%(message)s')

    [
        source_files,
        dest_dir,
        is_copy,
        separate,
        do_rename,
        is_dryrun,
    ] = _parse_options(argv[1:])

    process_function = _generate_process_function(is_copy, is_dryrun)

    process_media_files(source_files,
                        dest_dir,
                        separate=separate,
                        do_rename=do_rename,
                        process_function=process_function)


if __name__ == '__main__':
    main()
