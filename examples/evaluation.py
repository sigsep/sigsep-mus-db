"""
script that demonstrate the use of musdb for evaluating separation results of musdb

"""

import musdb
import museval


def mix_as_estimate(track):
    """
    Mix the audio as an array.

    Args:
        track: (bool): write your description
    """
    # get the mixture path for external processing
    track.path

    # get the sample rate
    track.rate

    # return any number of targets
    estimates = {
        'vocals': track.audio,
        'accompaniment': track.audio,
    }

    return estimates


# initiate musdb
mus = musdb.DB(download=True)

for track in mus:
    estimates = mix_as_estimate(track)
    scores = museval.eval_mus_track(track, estimates)
    print(scores)
