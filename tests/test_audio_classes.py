from __future__ import print_function
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
            print(target)
            assert target.audio.shape


def test_rates(mus):
    tracks = mus.load_mus_tracks()

    for track in tracks:
        assert track.rate == 44100
        assert track.audio.shape
        for key, source in list(track.sources.items()):
            assert source.rate == 44100
            assert source.audio.shape


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

    print(source)


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

    print(track)
