import unittest
import os

import requests.exceptions

from pterradactyl.util.download import extract_from_zip, extract_from_tar, download
from mock import patch
from zipfile import ZipFile
import tarfile
from os.path import basename
import pytest
import responses


class TestDownloadUtil(unittest.TestCase):

    def setUp(self):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.zip_filename = 'test.zip'
        self.tar_filename = 'test.tar'
        self.compress_files = self.base_path + "/test_resources/compress"
        self.create_zip_object(self.zip_filename, self.compress_files)
        self.create_tar_object(self.tar_filename, self.compress_files)

    def tearDown(self):
        os.remove(os.path.join(self.base_path, self.zip_filename))
        os.remove(os.path.join(self.base_path, self.tar_filename))

    def create_zip_object(self, zip_obj_name, path_to_zip):
        with ZipFile(os.path.join(self.base_path, zip_obj_name), 'w') as zipObj:
            for folderName, subfolders, filenames in os.walk(path_to_zip):
                for filename in filenames:
                    filePath = os.path.join(folderName, filename)
                    zipObj.write(filePath, basename(filePath))

    def create_tar_object(self, tar_obj_name, path_to_tar):
        with tarfile.open(os.path.join(self.base_path, tar_obj_name), 'w') as tar:
            for folderName, subfolders, filenames in os.walk(path_to_tar):
                for filename in filenames:
                    filePath = os.path.join(folderName, filename)
                    tar.add(filePath, arcname=os.path.basename(filePath))

    def test_extract_from_zip(self):
        test_file = 'test_log2'
        archive = extract_from_zip(os.path.join(self.base_path, self.zip_filename), test_file)
        assert archive.name == test_file

    def test_extract_from_non_existing_zip_should_exit(self):
        with pytest.raises(ValueError):
            extract_from_zip(os.path.join(self.base_path, self.zip_filename), 'test_non_existing_file')

    def test_extract_from_non_existing_tar_should_exit(self):
        with pytest.raises(ValueError):
            extract_from_tar(os.path.join(self.base_path, self.tar_filename), 'test_non_existing_file')

    def test_extract_from_tar(self):
        test_file = 'test_log2'
        extract_from_tar(os.path.join(self.base_path, self.tar_filename), test_file)

    @responses.activate
    def test_download_tar_url_exists(self):
        url = 'https://example.org/test.zip'
        with open(os.path.join(self.base_path, self.tar_filename), 'rb') as tar_file:
            with patch('shutil.copyfileobj'):
                responses.add(responses.GET, url,
                              body=tar_file.read(), status=200,
                              content_type='application/tar',
                              stream=True,
                              adding_headers={'Transfer-Encoding': 'chunked'})
                download(url, self.base_path, self.tar_filename)

    @responses.activate
    def test_download_non_existing_url(self):
        url = 'https://example.org/test_non_exisiting.zip'
        with open(os.path.join(self.base_path, self.zip_filename), 'rb') as zip_file:
            with pytest.raises(requests.exceptions.HTTPError) as err_msg:
                responses.add(responses.GET, url,
                              body=zip_file.read(), status=404,
                              content_type='application/octet-stream',
                              stream=True,
                              adding_headers={'Transfer-Encoding': 'chunked'})
                download(url, self.base_path, self.tar_filename)
