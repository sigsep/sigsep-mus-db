import os
import pytest
import musdb
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
    # initiate musdb

    mus = musdb.DB(root_dir='data/MUS-STEMS-SAMPLE')
    tracks = mus.load_mus_tracks()

    assert len(tracks) == 2

    for track in tracks:
        assert track.audio.shape[1] > 0

    # load only the dev set
    tracks = mus.load_mus_tracks(subsets='train')

    assert len(tracks) == 1

    # load only the dev set
    tracks = mus.load_mus_tracks(subsets=['train', 'test'])

    assert len(tracks) == 2


@pytest.fixture(params=['data/MUS-STEMS-SAMPLE'])
def mus(request):
    return musdb.DB(root_dir=request.param)


@pytest.mark.parametrize(
    "path",
    [
        pytest.mark.xfail(None, raises=RuntimeError),
        pytest.mark.xfail("wrong/path", raises=IOError),
        "data/MUS-STEMS-SAMPLE",
    ]
)
def test_env(path):

    if path is not None:
        os.environ["MUSDB_PATH"] = path

    assert musdb.DB()


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
def test_user_functions_test(func, mus):
    assert mus.test(user_function=func)


@pytest.mark.parametrize(
    "func",
    [
        user_function1,
        pytest.mark.xfail(user_function2, raises=ValueError),
        pytest.mark.xfail(user_function3, raises=ValueError),
        pytest.mark.xfail(user_function4, raises=ValueError),
    ]
)
def test_run(func, mus):

    # process mus but do not save the results
    assert mus.run(
        user_function=func
    )

    assert mus.run(
        user_function=func,
        estimates_dir='./Estimates'
    )


def test_parallel(mus):

    assert mus.run(
        user_function=user_function1,
        parallel=True,
        cpus=1
    )
