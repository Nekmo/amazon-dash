import os
import sys
import unittest

from amazon_dash.audio import WavAudio
from ._compat import patch
from amazon_dash.exceptions import AudioError

if sys.version_info < (3,2):
    FileNotFoundError = OSError


class TestWavAudio(unittest.TestCase):
    file = 'hack.wav'

    @patch('amazon_dash.audio.get_pyaudio_module')
    @patch('amazon_dash.audio.wave')
    def test_pyaudio(self, m1, m2):
        p = m2.return_value.PyAudio.return_value
        stream = p.open.return_value
        stream.is_active.return_value = False
        WavAudio(self.file, 'pyaudio').play()
        stream.stop_stream.assert_called_once()
        p.terminate.assert_called_once()

    @patch('amazon_dash.audio.subprocess.check_call')
    def test_sox(self, m):
        WavAudio(self.file, 'sox').play()
        m.assert_called_once_with(['play', self.file])

    @patch('amazon_dash.audio.get_pyaudio_module')
    def test_get_best_play_method_pyaudio(self, m):
        wav_audio = WavAudio(self.file)
        self.assertEqual(wav_audio.best_play_method, wav_audio.play_pyaudio)

    @patch('amazon_dash.audio.get_pyaudio_module', side_effect=ImportError)
    @patch('amazon_dash.audio.subprocess.check_call')
    def test_get_best_play_method_sox(self, m1, m2):
        wav_audio = WavAudio(self.file)
        self.assertEqual(wav_audio.best_play_method, wav_audio.play_sox)

    @patch('amazon_dash.audio.get_pyaudio_module', side_effect=ImportError)
    @patch('amazon_dash.audio.subprocess.check_call', side_effect=FileNotFoundError)
    def test_get_best_play_method_error(self, m1, m2):
        with self.assertRaises(AudioError):
            WavAudio(self.file).get_best_play_method()

    @patch.object(WavAudio, 'play')
    def test_loop(self, m):
        wav_audio = WavAudio(self.file)
        wav_audio.loop_play(1)
        m.assert_called_once()
