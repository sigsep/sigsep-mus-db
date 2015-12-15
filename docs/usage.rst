Usage
=====

This package should nicely integrate with your existing code so that it
can parse and process the *DSD100* from python, thus makes it easy to
participate in the SISEC MUS tasks.

Providing a compatible function
-------------------------------

The core of this package consists of calling a user-provided function
which separates the mixtures from the DSD100 into sources.

-  The function will take an DSD100 ``Track`` object which can be used
   from inside your algorithm.
-  Participants can access
-  ``Track.audio``, representing the stereo mixture as an ``np.ndarray``
   of ``shape=(nun_sampl, 2)``
-  ``Track.rate``, the sample rate
-  ``Track.path``, the absolute path of the mixture which might be handy
   to process with external applications, so that participants don't
   need to write out temporary wav files.
-  The function needs to return a python ``Dict`` which consists of
   target name (``key``) and the estimated target as audio arrays with
   same shape as the mixture (``value``).
-  It is the users choice which targets/sources they want to provide for
   a given mixture. Supported targets are
   ``['vocals', 'accompaniment', 'drums', 'bass', 'other']``.
-  Please make sure that the returned estimates do have the same sample
   rate as the mixture track.

Here is an example for such a function separating the mixture into a
**vocals** and **accompaniment** track.

.. code:: python

    def my_function(track):

        # get the audio mixture as numpy array shape=(nun_sampl, 2)
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
----------------------------

Setting up dsd100
^^^^^^^^^^^^^^^^^

Simply import the dsd100 package in your main python function:

.. code:: python

    import dsd100

    dsd = DSD100(
        root_dir=args.dsd_folder,
        user_estimates_dir='my_estimates'
    )

The ``root_dir`` is the path to the DSD100 dataset folder. It can also
be set system-wide. Just ``export DSD100_PATH=/path/to/DSD100/`` inside
your terminal. If ``user_estimates_dir`` is not set, the default will be
used which is inside the *DSD100* ``root_dir``.

Test if your separation function generates valid output
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Before you run the main evaluation which might take very long,
participants can test their separation function by running:

.. code:: python

    dsd.test(my_function)

This test makes sure the user provided output is compatible to the
dsd100 evaluation framework. The function returns ``True`` if the test
succeeds.

Processing the full DSD100
^^^^^^^^^^^^^^^^^^^^^^^^^^

To process all 100 DSD tracks and saves the results to the
``user_estimates_dir``:

.. code:: python

    dsd.run(my_function)

Processing training and testing subsets separately
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Algorithms which make use of machine learning techniques can use the
training subset and then apply the algorithm on the test data:

.. code:: python

    dsd.run(my_training_function, subsets="train")
    dsd.run(my_test_function, subsets="test")

Compute the bss\_eval measures
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The official SISEC evaluation relies on *MATLAB* because currently there
does not exist a
`bss\_eval <http://bass-db.gforge.inria.fr/bss_eval/>`__ implementation
for python which produces the exact same results. We therefore recommend
to run ``DSD100_only_eval.m`` from the DSD100 Matlab scripts after you
have processed and save your estimates in python.


Evaluation in python
^^^^^^^^^^^^^^^^^^^^

.. warning:: Warning, this is not supported yet

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
