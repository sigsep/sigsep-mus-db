import dsd100


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


# initiate dsd100
dsd = dsd100.DB(
    root_dir="../data/DSD100subset",
    user_estimates_dir='./Estimates'
)

# verify if my_function works correctly
if dsd.test(my_function):
    print "my_function is valid"

dsd.run(my_function)
