import dsdtools


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


# initiate dsdtools
dsd = dsdtools.DB(
    root_dir="../data/dsdtoolssubset",
)

# verify if my_function works correctly
if dsd.test(my_function):
    print "my_function is valid"

dsd.run(
    my_function,
    estimates_dir='./Estimates'
)
