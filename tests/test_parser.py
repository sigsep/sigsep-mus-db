import os
import pytest
import musdb
import numpy as np
import yaml


@pytest.fixture(params=[True, False])
def mus(request):
    return musdb.DB(root_dir='data/MUS-STEMS-SAMPLE', is_wav=request.param)


def user_function0(track):
    '''pass because output is none. Useful for training'''

    # return any number of targets
    return None


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


def user_function6(track):
    '''fails because of wrong type'''

    # return any number of targets
    estimates = {
        'vocals': track.audio.astype(np.float32),
    }
    return estimates


def test_stems(mus):
    tracks = mus.load_mus_tracks()

    setup_path = os.path.join(
        musdb.__path__[0], 'configs', 'mus.yaml'
    )

    with open(setup_path, 'r') as f:
        setup = yaml.load(f)

    for track in tracks:
        for k, v in setup['stem_ids'].items():
            if k == 'mixture':
                assert np.allclose(
                    track.audio,
                    track.stems[v]
                )
            else:
                assert np.allclose(
                    track.sources[k].audio,
                    track.stems[v]
                )


def test_file_loading(mus):
    # initiate musdb

    tracks = mus.load_mus_tracks()

    assert len(tracks) == 2

    for track in tracks:
        assert track.audio.shape[1] > 0
        assert track.audio.shape[-1] == 2
        assert track.stems.shape[0] == 5

    # loads only the train set
    tracks = mus.load_mus_tracks(subsets='train')

    assert len(tracks) == 1

    # load a single named track
    tracks = mus.load_mus_tracks(tracknames=['PR - Oh No'])

    assert len(tracks) == 1

    # load train and test set
    tracks = mus.load_mus_tracks(subsets=['train', 'test'])

    assert len(tracks) == 2

    # load train and test set
    tracks = mus.load_mus_tracks(subsets=None)

    assert len(tracks) == 2


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
        user_function6,
    ]
)
def test_user_functions_test(func, mus):
    assert mus.test(user_function=func)


@pytest.mark.parametrize(
    "func",
    [
        user_function0,
        user_function1,
        pytest.mark.xfail(user_function2, raises=ValueError),
        pytest.mark.xfail(user_function3, raises=ValueError),
        pytest.mark.xfail(user_function4, raises=ValueError),
    ]
)
def test_run(func, mus):

    # process mus but do not save the results
    assert mus.run(
        user_function=func,
        estimates_dir=None
    )


@pytest.mark.parametrize(
    "func",
    [
        pytest.mark.xfail(user_function0, raises=ValueError),
        user_function1,
        pytest.mark.xfail(user_function2, raises=ValueError),
        pytest.mark.xfail(user_function3, raises=ValueError),
        pytest.mark.xfail(user_function4, raises=ValueError),
    ]
)
def test_run_estimates(func, mus):
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
