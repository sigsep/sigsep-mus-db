import os
import pytest
import musdb
import numpy as np
import yaml


@pytest.fixture(params=['train', 'test', ['train', 'test'], None])
def subset(request):
    return request.param


@pytest.fixture(params=[True, False])
def mus(request, subset):
    return musdb.DB(
        root='data/MUS-STEMS-SAMPLE', is_wav=request.param, subsets=subset
    )


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


def test_file_loading(mus, subset):
    for track in mus:
        assert track.audio.shape[1] > 0
        assert track.audio.shape[-1] == 2
        assert track.stems.shape[0] == 5

    # loads only the train set
    if subset == 'train':
        assert len(mus) == 1

    # load train and test set
    if subset == ['train', 'test']:
        assert len(mus) == 2

    # load train and test set
    if subset is None:
        assert len(mus) == 2


def test_audio_regression():
    """test audio loading capabilities"""
    mus = musdb.DB(download=True)
    s = 0
    for track in mus:
        s += track.audio.sum()

    assert np.allclose(s, -24778.126983642578)


def test_download_and_validation():
    mus_all = musdb.DB(download=True)

    assert len(mus_all) == 144

    for track in mus_all:
        assert track.audio.shape[1] > 0
        assert track.audio.shape[-1] == 2
        assert track.stems.shape[0] == 5

    mus_test = musdb.DB(download=True, subsets='test', split=None)
    assert len(mus_test) == 50

    mus_train = musdb.DB(download=True, subsets='train', split='train')
    assert len(mus_train) == 80
    # test validation set
    mus_valid = musdb.DB(download=True, subsets='train', split='valid')
    assert len(mus_valid) == 14

    assert len(mus_train) == len(mus_all) - len(mus_test) - len(mus_valid)

    with pytest.raises(RuntimeError):
        mus_train = musdb.DB(download=True, split='train')
