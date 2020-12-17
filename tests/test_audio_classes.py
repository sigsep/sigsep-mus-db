import pytest
import musdb.audio_classes as ac
import musdb
import numpy as np


@pytest.fixture(params=[True, False])
def mus(request):
    return musdb.DB(root='data/MUS-STEMS-SAMPLE', is_wav=request.param)


@pytest.fixture(params=[0, 1, 2, 11.1, None])
def chunk_duration(request):
    return request.param


@pytest.fixture(params=[44100.0, 22050.0, 16000.0])
def sample_rate(request):
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
        # check if duration is with zero pad range of mp4 files
        # (one frame is typically 1024 samples)
        assert track.audio.shape[0] > (track.duration * track.rate - 1024) \
            and track.audio.shape[0] < (track.duration * track.rate + 1024)


def test_sample_rate(mus, sample_rate):
    track = mus[0]
    track.sample_rate = sample_rate
    track.chunk_duration = 1.0
    assert track.audio.shape[0] == sample_rate


def test_chunking(mus, chunk_duration):
    for track in mus:
        track.chunk_duration = chunk_duration
        if chunk_duration:
            assert np.allclose(
                track.audio.shape[0], chunk_duration * track.rate)
            for _, target in track.sources.items():
                assert np.allclose(
                    target.audio.shape[0], chunk_duration * track.rate)
            for _, target in track.targets.items():
                assert np.allclose(
                    target.audio.shape[0], chunk_duration * track.rate)


def test_track_artisttitle(mus):
    track = ac.MultiTrack(name="None", path="None")

    assert track.artist is None
    assert track.title is None


def test_source(mus):
    mtrack = ac.MultiTrack(name="abc123", path="None")
    with pytest.raises(ValueError):
        source = ac.Source(mtrack, name="test", path="None")
        source.audio

    source.audio = np.zeros((2, 44100))
    assert source.audio.shape == (2, 44100)


def test_track(mus):
    with pytest.raises(ValueError):
        track = ac.Track(path="None")
        track.audio

    track.audio = np.zeros((2, 44100))
    assert track.audio.shape == (2, 44100)
