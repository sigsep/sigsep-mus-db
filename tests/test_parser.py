import os
import pytest
import musdb
import numpy as np
import yaml


@pytest.fixture(params=[True, False])
def mus(request):
    return musdb.DB(
        root_dir='data/MUS-STEMS-SAMPLE', is_wav=request.param
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
