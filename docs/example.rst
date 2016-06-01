Example
=======

.. code:: python

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
            'vocals': vocals_array,
            'accompaniment': acc_array,
        }
        return estimates


    # initiate dsd100
    dsd = dsd100.DB(root_dir="./Volumes/Data/DSD100")

    # verify if my_function works correctly
    if dsd.test(my_function):
        print "my_function is valid"

    # this might take 3 days to finish
    dsd.run(my_function, estimates_dir="path/to/estimates")

    # for the machine learning task you want to split the subsets
    dsd.run(my_training_function, subsets="train", estimates_dir="path/to/dev")  # this takes 1.5 days to finish
    dsd.run(my_test_function, subsets="test", estimates_dir="path/to/test")  # this takes 1.5 days to finish
