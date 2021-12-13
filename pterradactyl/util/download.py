import os
import shutil
import tempfile
import tarfile

from io import BytesIO
from zipfile import ZipFile
import requests


def extract_from_zip(path, filename):
    archive = ZipFile(path)

    for member in archive.namelist():
        if os.path.basename(member) == filename:
            return archive.open(member)

    raise ValueError("Could not find {} in downloaded zip file.".format(filename))


def extract_from_tar(path, filename):
    archive = tarfile.open(path)

    for member in archive.getmembers():
        if member.isfile() and os.path.basename(member.name) == filename:
            return archive.extractfile(member)

    raise ValueError("Could not find {} in downloaded tar file.".format(filename))


compressed_magic = {
    bytes([0x1f, 0x8b, 0x08]): extract_from_tar,  # gzip
    bytes([0x42, 0x5a, 0x68]): extract_from_tar,  # bz2
    bytes([0xfd, 0x37, 0x7a, 0x58, 0x5a, 0x00]): extract_from_tar,  # lzma
    bytes([0x50, 0x4b, 0x03, 0x04]): extract_from_zip  # zip
}


def download(url, dest_dir, filename, dest=None, auth_header=None):
    headers = {'Accept': 'application/octet-stream'}
    headers.update(auth_header or {})

    # TODO: Handle redirects
    with requests.Session() as session:
        response = session.get(url, stream=True, headers=headers)

        if not (response.status_code == requests.codes['ok']):
            response.raise_for_status()

        data = []
        for response_slice in response.iter_content(1024 * 1024):
            data.append(response_slice)

        data = b"".join(data)

        for signature, extract in compressed_magic.items():
            if data.startswith(signature):
                with tempfile.NamedTemporaryFile() as archive:
                    archive.write(data)
                    temp = extract(archive.name, filename)
                break
        else:
            temp = BytesIO(data)

        with open(os.path.join(dest_dir, dest or filename), 'wb+') as download:
            shutil.copyfileobj(temp, download)
