Usage
=====

This package should nicely integrate with your existing code so that it
can parse and process the *dsdtools* from python, thus makes it easy to
participate in the `SISEC MUS
tasks <https://sisec.inria.fr/professionally-produced-music-recordings>`__.


Providing a compatible function
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The core of this package consists of calling a user-provided function
which separates the mixtures from the dsdtools into estimated target
sources.

-  The function will take an dsdtools ``Track`` object which can be used
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
-  It is the users choice which target sources they want to provide for
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

        # compute voc_array, acc_array
        # ...

        return {
            'vocals': voc_array,
            'accompaniment': acc_array
        }

Create estimates for SiSEC evaluation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Setting up dsdtools
'''''''''''''''''

Simply import the dsdtools package in your main python function:

.. code:: python

   import dsdtools

   dsd = dsdtools.DB(
       root_dir='path/to/dsdtools/',
   )

The ``root_dir`` is the path to the dsdtools dataset folder. It can also
be set system-wide. Just ``export dsdtools_PATH=/path/to/dsdtools/`` inside
your terminal. The ``user_estimates_dir`` is the path to the user
estimates. If it is not set, the default will be used which is inside
the *dsdtools* ``root_dir``.

Test if your separation function generates valid output
'''''''''''''''''''''''''''''''''''''''''''''''''''''''

Before you run the full dsdtools, which might take very long, participants
can test their separation function by running:

.. code:: python

   dsd.test(my_function)

This test makes sure the user provided output is compatible to the
dsdtools framework. The function returns ``True`` if the test succeeds.

Processing the full dsdtools
''''''''''''''''''''''''''

To process all 100 DSD tracks and saves the results to the
``dir``:

.. code:: python

    dsd.run(my_function, estimates_dir="path/to/estimates")

Processing training and testing subsets separately
''''''''''''''''''''''''''''''''''''''''''''''''''

Algorithms which make use of machine learning techniques can use the
training subset and then apply the algorithm on the test data:

.. code:: python

    dsd.run(my_training_function, subsets="Dev")
    dsd.run(my_test_function, subsets="Test")

Processing single or multiple dsdtools items
''''''''''''''''''''''''''''''''''''''''''

.. code:: python

    dsd.run(my_function, ids=30)
    dsd.run(my_function, ids=[1, 2, 3])
    dsd.run(my_function, ids=range(90, 99))

Note, that the provided list of ids can be overridden if the user sets a
terminal environment variable ``dsdtools_ID=1``.

Use multiple cores
''''''''''''''''''

Python Multiprocessing
""""""""""""""""""""""

To speed up the processing, ``run`` can make use of multiple CPUs:

.. code:: python

    dsd.run(my_function, parallel=True, cpus=4)

Note: We use the python builtin multiprocessing package, which sometimes
is unable to parallelize the user provided function to
`PicklingError <http://stackoverflow.com/a/8805244>`__.

GNU Parallel
""""""""""""

    `GNU parallel <http://www.gnu.org/software/parallel>`__ is a shell
    tool for executing jobs in parallel using one or more computers. A
    job can be a single command or a small script that has to be run for
    each of the lines in the input. The typical input is a list of
    files, a list of hosts, a list of users, a list of URLs, or a list
    of tables. A job can also be a command that reads from a pipe. GNU
    parallel can then split the input and pipe it into commands in
    parallel.

By running only one ``id`` in each python process the dsdtools set can
easily be processed with GNU parallel using multiple CPUs without any
further modifications to your code:

.. code:: bash

    parallel --bar 'dsdtools_ID={0} python dsdtools_main.py' ::: {1..100}


Compute the bss\_eval measures
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The official SISEC evaluation relies on *MATLAB* because currently there
does not exist a
`bss\_eval <http://bass-db.gforge.inria.fr/bss_eval/>`__ implementation
for python which produces indentical results. Therefore please run
``dsdtools_only_eval.m`` from the `dsdtools Matlab
scripts <https://github.com/faroit/dsdtoolsmat>`__ after you have
processed and saved your estimates with *dsdtoolspy*.


Evaluation in python
^^^^^^^^^^^^^^^^^^^^

.. warning:: Warning, this is not supported yet

If you really don't want to start MATLAB you can run the bss\_eval from
python with the help of
`matlab\_wrapper <https://github.com/mrkrd/matlab_wrapper>`__. For
convenience this package already has implemented the MATLAB evaluation
functions but does not write them to mat files yet. We offer several
optional methods to parse the dsdtools:

.. code:: python

    # Evaluate the results using matlab_wrapper and save the estimates to disk
    dsd.run(my_function, save=True, evaluate=True)

    # Evaluate the results using matlab_wrapper but do not save the estimates to disk
    dsd.run(my_function, save=False, evaluate=True)

    # Just evaluate the user_estimates folder when the estimates have already been saved to disk
    # this equivalent to the MATLAB dsdtools_only_eval.m function
    dsd.run(save=False, evaluate=True)
    # or simply which is the same as as last line
    dsd.evaluate()

    # Only pass the tracks to my_function. Ignore the results. Useful for statistics
    dsd.run(my_function, save=False, evaluate=False)
