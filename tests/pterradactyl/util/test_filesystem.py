import unittest
import os
from pterradactyl.util.filesystem import ensure_directory, ensure_executable, sync_local_tf_plugins, get_target_path
from mock import patch


class TestFileSystemUtil(unittest.TestCase):

    def test_ensure_directory(self):
        test_path = 'test_path1/test_path2'
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            result_path = ensure_directory(test_path)
            assert result_path == test_path
            mock_mkdir.assert_called()

    def test_ensure_executable(self):
        test_path = 'test_path1/test_path2'
        with patch('os.stat') as mock_stat:
            with patch('os.chmod') as mock_chmod:
                result_path = ensure_executable(test_path)
                assert result_path == test_path
                mock_stat.assert_called_with(result_path)
                mock_chmod.assert_called()

    def test_get_target_path(self):
        domain = "domain"
        owner = "owner"
        plugin_name = "foo"
        plugin = "terraform-provider-" + plugin_name
        version = "0.1.0"
        arch = "linux"

        result_path = get_target_path(domain, owner, plugin, version, arch)
        assert result_path == os.path.join(os.path.expanduser('~'), ".terraform.d/plugins", domain, owner, plugin_name,
                                           version, arch)

    def test_sync_local_tf_plugins(self):
        domain = "domain"
        owner = "owner"
        plugin_name = "foo"
        plugin = "terraform-provider-" + plugin_name
        version = "0.1.0"
        arch = "linux"
        source_dir = "some_file"
        target_path = get_target_path(domain, owner, plugin, version, arch)
        with patch('os.path.exists', return_value=True) as mock_exists:
            with patch('os.makedirs') as mock_makedirs:
                with patch('pterradactyl.util.filesystem.copy') as mock_copy:
                    sync_local_tf_plugins(source_dir, domain, owner, plugin, version, arch)
                    assert mock_exists(target_path) == True
                    mock_copy.assert_called_with(source_dir, target_path)

    def test_sync_local_tf_plugins_target_dir_doesnot_exist(self):
        domain = "domain"
        owner = "owner"
        plugin_name = "foo"
        plugin = "terraform-provider-" + plugin_name
        version = "0.1.0"
        arch = "linux"
        source_dir = "some_file"
        target_path = get_target_path(domain, owner, plugin, version, arch)
        with patch('os.path.exists', return_value=False):
            with patch('os.makedirs') as mock_makedirs:
                with patch('pterradactyl.util.filesystem.copy') as mock_copy:
                    sync_local_tf_plugins(source_dir, domain, owner, plugin, version, arch)
                    mock_copy.assert_called_with(source_dir, target_path)
                    mock_makedirs.assert_called_with(target_path)
