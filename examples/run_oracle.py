from __future__ import print_function
import mustools


def my_function(track):
    '''My fancy BSS algorithm'''

    # get the audio mixture as numpy array shape=(nun_sampl, 2)
    track.audio

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

# initiate mustools
mus = mustools.DB()

# verify if my_function works correctly
if mus.test(my_function):
    print("my_function is valid")

mus.run(
    my_function,
    estimates_dir='./Estimates',
)
