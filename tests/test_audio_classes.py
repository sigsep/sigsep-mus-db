import pytest
import musdb.audio_classes as ac
import musdb
import numpy as np


@pytest.fixture(params=[True, False])
def mus(request):
    return musdb.DB(root_dir='data/MUS-STEMS-SAMPLE', is_wav=request.param)


@pytest.fixture(params=[0, 1, 2, 11.1, None])
def durs(request):
    return request.param


def test_targets(mus):
    for track in mus:
        for key, target in list(track.targets.items()):
            assert target.audio.shape


def test_rates(mus):
    for track in mus:
        assert track.rate == 44100
        assert track.audio.shape
        for key, source in list(track.sources.items()):
            assert source.rate == 44100
            assert source.audio.shape


def test_durations(mus):
    for track in mus:
        assert track.duration > 0
        assert np.allclose(track.audio.shape[0], track.duration * track.rate)


def test_dur(mus, durs):
    for track in mus:
        track.dur = durs
        if durs:
            assert np.allclose(track.audio.shape[0], durs * track.rate)


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
