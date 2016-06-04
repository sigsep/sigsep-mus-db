from __future__ import print_function
import pytest
import dsdtools.audio_classes as ac
import dsdtools
import numpy as np


@pytest.fixture(params=['data/DSD100subset'])
def dsd(request):
    return dsdtools.DB(root_dir=request.param)


def test_targets(dsd):

    tracks = dsd.load_dsd_tracks(ids=1)

    for track in tracks:
        for key, target in track.targets.items():
            print(target)
            assert target.audio.shape > 0


def test_rates(dsd):

    tracks = dsd.load_dsd_tracks(ids=1)

    for track in tracks:
        assert track.rate == 44100
        assert track.audio.shape > 0
        for key, source in track.sources.items():
            assert source.rate == 44100
            assert source.audio.shape > 0


def test_source(dsd):

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


def test_track(dsd):

    with pytest.raises(ValueError):
        track = ac.Track(name="test", path="None")
        track.audio

    with pytest.raises(ValueError):
        track = ac.Track(name="test", path="None")
        track.rate

    track.audio = np.zeros((2, 44100))
    assert track.audio.shape == (2, 44100)

    track.rate = 44100
    assert track.rate == 44100

    print(track)
