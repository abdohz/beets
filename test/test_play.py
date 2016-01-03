# -*- coding: utf-8 -*-

"""Tests for the play plugin"""

from __future__ import (division, absolute_import, print_function,
                        unicode_literals)

import os

from mock import patch, ANY

from test._common import unittest
from test.helper import TestHelper, control_stdin

from beets.ui import UserError

class PlayPluginTest(unittest.TestCase, TestHelper):
    def setUp(self):
        self.setup_beets()
        self.load_plugins('play')
        self.item = self.add_item(album='a nice älbum', title='aNiceTitle')
        self.lib.add_album([self.item])
        self.open_patcher = patch('beetsplug.play.util.interactive_open')
        self.open_mock = self.open_patcher.start()

    def tearDown(self):
        self.open_patcher.stop()
        self.teardown_beets()
        self.unload_plugins()

    def do_test(self, args=('title:aNiceTitle',), expected_cmd=None, expected_playlist='{}\n'):
        self.run_command('play', *args)

        self.open_mock.assert_called_once_with(ANY, expected_cmd)
        expected_playlist_content = expected_playlist.format(self.item.path.decode('utf-8'))
        with open(self.open_mock.call_args[0][0][0], 'r') as playlist:
            self.assertEqual(expected_playlist_content, playlist.read().decode('utf-8'))

    def test_basic(self):
        self.do_test()

    def test_album_option(self):
        self.do_test(['-a', 'nice'])

    def test_args_option(self):
        self.config['play']['command'] = 'echo'

        self.do_test(['-A', 'foo', 'title:aNiceTitle'], 'echo foo')

    def test_args_option_in_middle(self):
        self.config['play']['command'] = 'echo $args other'

        self.do_test(['-A', 'foo', 'title:aNiceTitle'], 'echo foo other')

    def test_relative_to(self):
        self.config['play']['command'] = 'echo'
        self.config['play']['relative_to'] = '/something'

        self.do_test(expected_cmd='echo', expected_playlist='..{}\n')

    def test_use_folders(self):
        self.config['play']['use_folders'] = True
        self.run_command('play', '-a', 'nice')

        self.open_mock.assert_called_once_with(ANY, None)
        playlist = open(self.open_mock.call_args[0][0][0], 'r')
        self.assertEqual('{}\n'.format(
            os.path.dirname(self.item.path.decode('utf-8'))),
            playlist.read().decode('utf-8'))

    def test_raw(self):
        self.config['play']['raw'] = True

        self.run_command('play', 'nice')

        self.open_mock.assert_called_once_with([self.item.path], None)

    def test_not_found(self):
        self.run_command('play', 'not found')

        self.open_mock.assert_not_called()

    def test_warning_threshold(self):
        self.config['play']['warning_treshold'] = 1
        item2 = self.add_item(title='another NiceTitle')

        with control_stdin("a"):
            self.run_command('play', 'nice')

        self.open_mock.assert_not_called()

    def test_command_failed(self):
        self.open_mock.side_effect = OSError("some reason")

        with self.assertRaises(UserError):
            self.run_command('play', 'title:aNiceTitle')

def suite():
    return unittest.TestLoader().loadTestsFromName(__name__)

if __name__ == b'__main__':
    unittest.main(defaultTest='suite')
