from __future__ import print_function
from __future__ import division
import pytest
import musdb.audio_classes as ac
import musdb
import numpy as np


@pytest.fixture(params=[True, False])
def mus(request):
    return musdb.DB(root_dir='data/MUS-STEMS-SAMPLE', is_wav=request.param)


def test_targets(mus):
    tracks = mus.load_mus_tracks()

    for track in tracks:
        for key, target in list(track.targets.items()):
            assert target.audio.shape


def test_rates(mus):
    tracks = mus.load_mus_tracks()

    for track in tracks:
        assert track.rate == 44100
        assert track.audio.shape
        for key, source in list(track.sources.items()):
            assert source.rate == 44100
            assert source.audio.shape


def test_durations(mus):
    tracks = mus.load_mus_tracks()

    for track in tracks:
        assert track.duration > 0
        assert np.allclose(track.audio.shape[0], track.duration * track.rate)


def test_track_artisttitle(mus):
    source = ac.Track(name="abc123", path="None")

    assert source.artist is None
    assert source.title is None


def test_source(mus):
    with pytest.raises(ValueError):
        source = ac.Source(name="test", path="None")
        source.audio

    with pytest.raises(ValueError):
        source = ac.Source(name="test", path="None")
        source.rate

    source.audio = np.zeros((2, 44100))
    assert source.audio.shape == (2, 44100)

    source.rate = 44100
    assert source.rate == 44100


def test_track(mus):
    with pytest.raises(ValueError):
        track = ac.Track(name="test - test", path="None")
        track.audio

    with pytest.raises(ValueError):
        track = ac.Track(name="test - test", path="None")
        track.rate

    track.audio = np.zeros((2, 44100))
    assert track.audio.shape == (2, 44100)

    track.rate = 44100
    assert track.rate == 44100
