import os
import pytest
import dsdtools
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


def user_function5(track):
    '''fails because output is not a dict'''

    # return any number of targets
    return track.audio


def test_file_loading():
    # initiate dsdtools

    dsd = dsdtools.DB(root_dir="data/DSD100subset")
    tracks = dsd.load_dsd_tracks()

    assert len(tracks) == 4

    for track in tracks:
        assert track.audio.shape[1] > 0

    # load only the dev set
    tracks = dsd.load_dsd_tracks(subsets='Dev')

    assert len(tracks) == 2

    # load only the dev set
    tracks = dsd.load_dsd_tracks(subsets=['Dev', 'Test'])

    assert len(tracks) == 4

    # load only a single id
    tracks = dsd.load_dsd_tracks(ids=1)

    assert len(tracks) == 1


@pytest.fixture(params=['data/DSD100subset'])
def dsd(request):
    return dsdtools.DB(root_dir=request.param)


@pytest.mark.parametrize(
    "path",
    [
        pytest.mark.xfail(None, raises=RuntimeError),
        pytest.mark.xfail("wrong/path", raises=IOError),
        "data/DSD100subset",
    ]
)
def test_env(path):

    if path is not None:
        os.environ["DSD_PATH"] = path

    assert dsdtools.DB()


@pytest.mark.parametrize(
    "func",
    [
        user_function1,
        pytest.mark.xfail(user_function2, raises=ValueError),
        pytest.mark.xfail(user_function3, raises=ValueError),
        pytest.mark.xfail(user_function4, raises=ValueError),
        pytest.mark.xfail(user_function5, raises=ValueError),
        pytest.mark.xfail("not_a_function", raises=TypeError),
    ]
)
def test_user_functions_test(func, dsd):
    assert dsd.test(user_function=func)


@pytest.mark.parametrize(
    "func",
    [
        user_function1,
        pytest.mark.xfail(user_function2, raises=ValueError),
        pytest.mark.xfail(user_function3, raises=ValueError),
        pytest.mark.xfail(user_function4, raises=ValueError),
    ]
)
def test_run(func, dsd):

    # process dsd but do not save the results
    assert dsd.run(
        user_function=func
    )

    assert dsd.run(
        user_function=func,
        estimates_dir='./Estimates'
    )

    dsd.run(estimates_dir='./Estimates')


def test_parallel(dsd):

    assert dsd.run(
        user_function=user_function1,
        parallel=True,
        cpus=1
    )
