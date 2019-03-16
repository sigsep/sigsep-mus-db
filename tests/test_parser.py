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
    setup_path = os.path.join(
        musdb.__path__[0], 'configs', 'mus.yaml'
    )

    with open(setup_path, 'r') as f:
        setup = yaml.safe_load(f)

    for track in mus:
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
    assert len(mus) == 2

    for track in mus:
        assert track.audio.shape[1] > 0
        assert track.audio.shape[-1] == 2
        assert track.stems.shape[0] == 5

    # loads only the train set
    mus.load_mus_tracks(subsets='train')
    assert len(mus) == 1

    # load train and test set
    mus.load_mus_tracks(subsets=['train', 'test'])

    assert len(mus) == 2

    # load train and test set
    mus.load_mus_tracks(subsets=None)

    assert len(mus) == 2


@pytest.mark.parametrize(
    "func",
    [
        user_function1,
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
        user_function1,
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
