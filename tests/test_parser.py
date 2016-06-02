import pytest
import dsd100
import numpy as np


def user_function1(track):
    '''Pass'''

    # return any number of targets
    estimates = {
        'vocals': track.audio,
        'accompaniment': track.audio,
    }
    return estimates


def user_function2(track):
    '''fails because of wrong shape'''

    # return any number of targets
    estimates = {
        'vocals': track.audio[:-1],
        'accompaniment': track.audio,
    }
    return estimates


def user_function3(track):
    '''fails because of wrong estimate name'''

    # return any number of targets
    estimates = {
        'triangle': track.audio,
        'accompaniment': track.audio,
    }
    return estimates


def user_function4(track):
    '''fails because of wrong type'''

    # return any number of targets
    estimates = {
        'vocals': track.audio.astype(np.int32),
    }
    return estimates


def test_fileloading():
    # initiate dsd100

    dsd = dsd100.DB(root_dir="data/DSD100subset")
    tracks = dsd.load_dsd_tracks()

    assert len(tracks) == 4


@pytest.fixture(params=['data/DSD100subset'])
def dsd(request):
    return dsd100.DB(root_dir=request.param)


@pytest.mark.parametrize(
    "func",
    [
        user_function1,
        pytest.mark.xfail(user_function2, raises=ValueError),
        pytest.mark.xfail(user_function3, raises=ValueError),
        pytest.mark.xfail(user_function4, raises=ValueError),
    ]
)
def test_user_functions(func, dsd):
    assert dsd.test(user_function=func)
