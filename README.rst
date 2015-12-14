dsd100
======

A python package to parse and process the **demixing secrets dataset
(DSD100)** as part of the `Signal Separation Evaluation Campaign
(SISEC) <https://sisec.inria.fr/>`__

Installation
------------

.. code:: bash

    pip install dsd100

Usage
-----

This package allows to parse and process the *DSD100* in python and
therefore make it easy to participate in the SISEC MUS tasks.

Providing a compatible function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Participants need to provide a function which separates the mixtures
into sources.

-  This function will take an ``Track`` object which can be used in
   inside your algorithm.
-  Participants can access
-  ``Track.audio`` representing the stereo mixture as an ``np.ndarray``
   with ``shape=(nun_sampl, 2)``
-  ``Track.rate``, the sample rate
-  ``Track.path`` for the absolute path of the mixture which might be
   handy process with external software
-  The function needs to return a python ``Dict`` which includes the
   target name and the separated target audio arrays with same shape as
   the mixture.
-  It is the users choice which targets/sources they want to provide for
   the given mixture. Supported targets are
   ``['vocals', 'accompaniment', 'drums', 'bass', 'other']``.
-  Please make sure that the returned estimates do have the same sample
   rate as the mixture track.

Here is an example for such a function separating the mixture into a
**vocals** and **accompaniment** track.

.. code:: python

    def my_function(track):

        # get the audio mixture as numpy array
        track.audio

        # get the mixture path for external processing
        track.path

        # get the sample rate
        track.rate

        estimates = {
            'vocals': vocals_array,
            'accompaniment': accompaniment_array
        }
        return estimates

Running the SiSEC Evaluation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Setting up dsd100
^^^^^^^^^^^^^^^^^

Simply import the dsd100 package in your main python function which has
also imported your evaluation function

.. code:: python

    import dsd100

    dsd = DSD100(
        root_dir=args.dsd_folder,
        user_estimates_dir='my_estimates'
    )

The ``root_dir`` is the path to the DSD100 dataset folder. It can also
be set system-wide instead. There just use
``export DSD100_PATH=/path/to/DSD100/``. inside your terminal. If
``user_estimates_dir`` is not set, the default will be used which is
inside the *DSD100* ``root_dir``.

Test if your separation function generates valid output
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Before you run the main evaluation which might take very long,
participants can test their separation function by running:

.. code:: python

    dsd.test(my_function)

This test makes sure the user provided output is compatible to the
dsd100 evaluation framework.

Processing the full DSD100
^^^^^^^^^^^^^^^^^^^^^^^^^^

The full evaluation processes all 100 DSD tracks and saves the results
to the ``user_estimates_dir``.

.. code:: python

    dsd.run(my_function)

Processing training and testing subsets separately
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Algorithms which make use of machine learning techniques can use the
training subset and then apply the algorithm on the test data.

.. code:: python

    dsd.run(my_training_function, subsets="train")
    dsd.run(my_test_function, subsets="test")

Compute the bss\_eval measures
------------------------------

The official SISEC evaluation still relies on *MATLAB* because currently
there does not exist a
`bss\_eval <http://bass-db.gforge.inria.fr/bss_eval/>`__ implementation
for python which produces the exact same results. We therefore recommend
to run ``DSD100_only_eval.m`` from the DSD100 Matlab scripts in Matlab
after you have saved your estimates with *dsd100*.

Full code Example
-----------------

.. code:: python

    import dsd100

    def my_function(track):
        '''My fancy BSS algorithm'''

        # get the audio mixture as numpy array
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


    # initiate the dsd100
    dsd = dsd100.SDS100(dsd_root="./Volumes/Data/DSD100")

    # this takes 3 seconds and verifies if my_function works correctly
    if dsd.test(my_function):
        print "my_function is valid"

    # this takes 3 days to finish and is the actual evaluation
    dsd.run(my_function)

    # for the machine learning guys you want to split the subsets
    dsd.run(my_training_function, subsets="train")  # this takes 1.5 days to finish
    dsd.run(my_test_function, subsets="test")  # this takes 1.5 days to finish

Evaluation in python
--------------------

**Warning, this is not supported yet**

If you really don't want to start MATLAB you can run the bss\_eval from
python with the help of
`matlab\_wrapper <https://github.com/mrkrd/matlab_wrapper>`__. For
convenience this package already has implemented the MATLAB evaluation
functions but does not write them to mat files yet. We offer several
optional methods to parse the DSD100:

.. code:: python

    # Evaluate the results using matlab_wrapper and save the estimates to disk
    dsd.run(my_function, save=True, evaluate=True)

    # Evaluate the results using matlab_wrapper but do not save the estimates to disk
    dsd.run(my_function, save=False, evaluate=True)

    # Just evaluate the user_estimates folder when the estimates have already been saved to disk
    # this equivalent to the MATLAB DSD100_only_eval.m function
    dsd.run(save=False, evaluate=True)
    # or simply which is the same as as last line
    dsd.evaluate()

    # Only pass the tracks to my_function. Ignore the results. Useful for statistics
    dsd.run(my_function, save=False, evaluate=False)
