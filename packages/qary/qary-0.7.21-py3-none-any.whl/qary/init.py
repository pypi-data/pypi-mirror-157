# init.py
import json
import logging
from pathlib import Path
import shutil
from urllib.request import urlretrieve
from urllib.parse import urljoin

import pandas as pd

from qary.config import BASE_DIR, HOME_DATA_DIR, DATA_DIR  # noqa
from qary.config import SRC_DIR, SRC_DATA_DIR  # noqa
from qary.config import uri_schemes_popular  # noqa

# from qary.etl.netutils import DownloadProgressBar  # noqa

log = logging.getLogger(__name__)


DATA_URL_PREFIX = 'https://gitlab.com/tangibleai/qary/-/raw/main/src/qary/data/'
DATA_URL_SUFFIX = '?inline=false'
INIT_DATA_FILENAMES = [
    'chat/example-multilingual.v3.dialog.yml',
    'constants/nltk_stopwords_english.json',
    'constants/tlds-from-iana.csv',
    'constants/uri-schemes.xhtml.csv',
    'datasets.yml',
    'downloadable_bigdata_directory.yml',
    'eliza_doctor.txt',
    # 'chat/moia-poly-dialog-tree-simplified-chinese.v3.dialog.yml',
    'rap/rap_corpus.txt',
    'tests/dialog_parser.v2.dialog.yml',
    'testsets/unit_test_data.json',
    'log/README'
]
# cp: overwrite '/home/hobs/.qary-data.bak/chat/example-multilingual.v3.dialog.yml'? y
# cp: overwrite '/home/hobs/.qary-data.bak/constants/nltk_stopwords_english.json'? y
# cp: overwrite '/home/hobs/.qary-data.bak/constants/tlds-from-iana.csv'? y
# cp: overwrite '/home/hobs/.qary-data.bak/constants/uri-schemes.xhtml.csv'? y
# cp: overwrite '/home/hobs/.qary-data.bak/datasets.yml'? y
# cp: overwrite '/home/hobs/.qary-data.bak/doctest-save-hashes.uint64.npy.gz'? y
# cp: overwrite '/home/hobs/.qary-data.bak/eliza_doctor.txt'? y
# cp: overwrite '/home/hobs/.qary-data.bak/rap/rap_corpus.txt'? y
# cp: overwrite '/home/hobs/.qary-data.bak/tests/dialog_parser.v2.dialog.yml'? y

# FIXME: doesn't seem to be created when you start with empty ~/.qary-data dir 'log/README'
# these created by pytest during doctests etc
# cp: overwrite '/home/hobs/.qary-data.bak/downloadable_bigdata_directory.yml'? y
# cp: overwrite '/home/hobs/.qary-data.bak/history.yml'? y
# cp: overwrite '/home/hobs/.qary-data.bak/tests/dialog.txt'? y


def maybe_download(
        url=None, filename=None, filepath=None,
        destination_dir=None, expected_bytes=None,
        force=False):
    """ Download a file only if it has not yet been cached locally in ~/.qary-data/ HOME_DATA_DIR
    """
    assert filepath is None or filename is None, f"Cannot specify both filepath='{filepath}' and filename='{filename}', they are synonymous."
    filename = filepath if filename is None else filename
    log.warning(f'filename: {filename}')
    src_filepath = SRC_DATA_DIR / filename
    log.warning(f'src_filepath: {src_filepath}')
    home_filepath = HOME_DATA_DIR / filename
    log.warning(f'home_filepath: {home_filepath}')
    log.warning(f'src_filepath.is_file(): {src_filepath.is_file()}')
    if not home_filepath.parent.is_dir():
        home_filepath.parent.mkdir(exist_ok=True, parents=True)
    if filename and src_filepath.is_file():
        if home_filepath.is_file():
            return home_filepath

        log.warning(f'Need to copy {src_filepath} to {home_filepath}')
        assert src_filepath.is_file()
        shutil.copy(
            src=src_filepath,
            dst=home_filepath,
            follow_symlinks=True)
        assert home_filepath.is_file()
        return home_filepath

    if url is None:
        try:
            url = urljoin(str(DATA_URL_PREFIX), str(filename))
        except ValueError:
            log.warning('maybe_download() positional arguments deprecated. please specify url or filename (relative file path)')
            filename, url = url, None

    if filename is None and url is not None:
        filename = url.split('/')[-1].split('?')[0].split(':')[-1]
    if destination_dir is None:
        destination_dir = Path(HOME_DATA_DIR)
    filepath = destination_dir / filename
    destination_dir, filename = filepath.parent, filepath.name

    if not destination_dir.exists():
        destination_dir.mkdir(parents=True, exist_ok=True)  # FIXME add , reporthook=DownloadProgressBar())

    local_data_filepath = Path(DATA_DIR) / filename
    if local_data_filepath.is_file() and not filepath.is_file():
        # TODO: use shutil.copy() to avoid running out of memory on large files
        filepath.write_bytes(local_data_filepath.read_bytes())

    if force or not filepath.is_file():
        log.error(f"Downloading: {url} to {filepath}")
        filepath, _ = urlretrieve(str(url), str(filepath))
        log.error(f"Finished downloading '{filepath}'")

    statinfo = Path(filepath).stat()

    # FIXME: check size of existing files before downloading
    if expected_bytes is not None:
        if statinfo.st_size == expected_bytes:
            log.info(f"Found '{filename}' and verified expected {statinfo.st_size} bytes.")
        else:
            raise Exception(f"Failed to verify: '{filepath}'. Check the url: '{url}'.")
    else:
        log.info(f"Found '{filename}' ({statinfo.st_size} bytes)")

    return filepath


def download_important_data(filenames=INIT_DATA_FILENAMES, force=False):
    """ Iterate through the important data filenames and download them from gitlab to a local cache """
    for i, relpath in enumerate(filenames):
        relpath = Path(relpath)
        destination_dir = HOME_DATA_DIR / relpath.parent
        url = DATA_URL_PREFIX + str(relpath) + DATA_URL_SUFFIX
        log.warning(f'url={url}')
        log.warning(f'relpath={relpath}')
        log.warning(f'relpath.name={relpath.name}')
        maybe_download(url=url, filename=relpath.name, destination_dir=destination_dir)


download_important_data(filenames=INIT_DATA_FILENAMES)

# shutil.copytree(src=QARY_DATA_DIR, dst=conf.DATA_DIR, dirs_exist_ok=True)


LOG_DIR = Path(DATA_DIR) / 'log'
CONSTANTS_DIR = Path(DATA_DIR) / 'constants'
HISTORY_PATH = Path(DATA_DIR) / 'history.yml'
Path(LOG_DIR).mkdir(exist_ok=True)
Path(CONSTANTS_DIR).mkdir(exist_ok=True)

STOPWORDS = set(json.load((Path(DATA_DIR) / 'constants' / 'nltk_stopwords_english.json').open()))
STOPWORDS_DICT = dict(zip(STOPWORDS, [1] * len(STOPWORDS)))
QUESTIONWORDS = set('who what when were why which how'.split() + ['how come', 'why does', 'can i', 'can you', 'which way'])
QUESTION_STOPWORDS = QUESTIONWORDS | STOPWORDS

#####################################################################################
# pugnlp.constants

tld_iana = pd.read_csv(Path(DATA_DIR, 'constants', 'tlds-from-iana.csv'), encoding='utf8')
tld_iana = dict(sorted(zip((tld.strip().lstrip('.') for tld in tld_iana.domain),
                           [(sponsor.strip(), -1) for sponsor in tld_iana.sponsor]),
                       key=lambda x: len(x[0]),
                       reverse=True))
# top 20 in Google searches per day
# sorted by longest first so .com matches before .om (Oman)
tld_popular = dict(sorted([
    ('com', ('Commercial', 4860000000)),
    ('org', ('Noncommercial', 1950000000)),
    ('edu', ('US accredited postsecondary institutions', 1550000000)),
    ('gov', ('United States Government', 1060000000)),
    ('uk', ('United Kingdom', 473000000)),  # noqa
    ('net', ('Network services', 206000000)),
    ('ca', ('Canada', 165000000)),  # noqa
    ('de', ('Germany', 145000000)),  # noqa
    ('jp', ('Japan', 139000000)),  # noqa
    ('fr', ('France', 96700000)),  # noqa
    ('au', ('Australia', 91000000)),  # noqa
    ('us', ('United States', 68300000)),  # noqa
    ('ru', ('Russian Federation', 67900000)),  # noqa
    ('ch', ('Switzerland', 62100000)),  # noqa
    ('it', ('Italy', 55200000)),  # noqa
    ('nl', ('Netherlands', 45700000)),  # noqa
    ('se', ('Sweden', 39000000)),  # noqa
    ('no', ('Norway', 32300000)),  # noqa
    ('es', ('Spain', 31000000)),  # noqa
    ('mil', ('US Military', 28400000)),
    ], key=lambda x: len(x[0]), reverse=True))

uri_schemes_iana = sorted(pd.read_csv(Path(DATA_DIR, 'constants', 'uri-schemes.xhtml.csv'),
                                      index_col=0).index.values,
                          key=lambda x: len(str(x)), reverse=True)
