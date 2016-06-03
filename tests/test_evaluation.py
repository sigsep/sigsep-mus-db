import pytest
import dsdtools


def user_function1(track):
    '''Pass'''

    # return any number of targets
    estimates = {
        'vocals': track.audio,
        'accompaniment': track.audio,
    }
    return estimates


@pytest.mark.parametrize(
    "method",
    [
        'mir_eval',
        pytest.mark.xfail('not_a_function', raises=ValueError)
    ]
)
def test_evaluate(method):

    dsd = dsdtools.DB(root_dir="data/DSD100subset", evaluation=method)

    # process dsd but do not save the results
    assert dsd.evaluate(
        user_function=user_function1,
        ids=1
    )
