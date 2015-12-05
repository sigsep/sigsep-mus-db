import pydsd

def my_function(dsd_track):
    # do your fancy bss algorithm

    # use the tracks mixture audio as numpy array
    dsd_track.audio

    # get the path for external processing
    dsd_track.path

    # get the sample rate
    dsd_track.rate

    # return any number of targets
    estimates = {
        'vocals': vocals_array,
        'accompaniment': acc_array,
    }
    return estimates


# initiate the pydsd
dsd = pydsd(dsd_root="./dsd100")

# this takes 3 seconds and verifies if my_function works correctly
dsd.test(my_function)

# this takes 3 days to finish and is the actual evaluation
dsd.run(my_function)

# for the machine learning guys you want to split the subsets
dsd.run(my_training_function, subset="train")  # this takes 1.5 days to finish
dsd.run(my_test_function, subset="test")  # this takes 1.5 days to finish
