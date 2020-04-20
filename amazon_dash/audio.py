import subprocess
import sys
import wave
import time

from amazon_dash.exceptions import AudioError


def get_pyaudio_module():
    import pyaudio
    return pyaudio


def pyaudio_callback(wf):
    pyaudio = get_pyaudio_module()

    def wrapper(in_data, frame_count, time_info, status):
        data = wf.readframes(frame_count)
        return (data, pyaudio.paContinue)
    return wrapper


if sys.version_info < (3,2):
    FileNotFoundError = OSError


class WavAudio(object):
    _best_play_method = None

    def __init__(self, wav_file, player_name=None):
        self.wav_file = wav_file
        if player_name is not None:
            self._best_play_method = self._get_player_by_name(player_name)

    def _get_player_by_name(self, player_name):
        player = {
            'sox': self.play_sox,
            'pyaudio': self.play_pyaudio,
        }.get(player_name)
        if player is None:
            raise AudioError('Unknown player {}'.format(player_name))
        return player

    @property
    def best_play_method(self):
        if self._best_play_method is None:
            self._best_play_method = self.get_best_play_method()
        return self._best_play_method

    def get_best_play_method(self):
        try:
            get_pyaudio_module()
        except ImportError:
            pass
        else:
            return self.play_pyaudio
        try:
            subprocess.check_call(['play', '--version'])
        except FileNotFoundError:
            pass
        else:
            return self.play_sox
        raise AudioError('A audio player is not available. Install pyaudio using pip or '
                         'install sox using your distro package manager.')

    def play_sox(self):
        subprocess.check_call(['play', self.wav_file])

    def play_pyaudio(self):
        pyaudio = get_pyaudio_module()

        wf = wave.open(self.wav_file, 'rb')
        p = pyaudio.PyAudio()

        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True,
                        stream_callback=pyaudio_callback(wf))

        stream.start_stream()

        while stream.is_active():
            time.sleep(0.1)

        stream.stop_stream()
        stream.close()
        wf.close()
        p.terminate()

    def play(self):
        self.best_play_method()

    def loop_play(self, times):
        for i in range(times):
            self.play()
