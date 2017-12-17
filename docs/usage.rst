Usage
=====

This package should nicely integrate with your existing python code,
thus makes it easy to participate in the `MUSDB
tasks <https://sisec.inria.fr/home/2018-professionally-produced-music-recordings>`__.
The core of this package is calling a user-provided function that
separates the mixtures from the musdb into several estimated target
sources.


Providing a compatible function
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The core of this package consists of calling a user-provided function
which separates the mixtures from the musdb into estimated target
sources.

-  The function will take an musdb ``Track`` object which can be used
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

Setting up musdb
'''''''''''''''''''

Simply import the musdb package in your main python function:

.. code:: python

   import musdb

   mus = musdb.DB(
       root_dir='path/to/musdb/',
   )

The ``root_dir`` is the path to the musdb dataset folder. Instead of
``root_dir`` it can also be set system-wide. Just
``export MUSDB_PATH=/path/to/musdb`` inside your terminal environment.

Test if your separation function generates valid output
'''''''''''''''''''''''''''''''''''''''''''''''''''''''

Before you run the full 150 tracks, which might take very long, participants
can test their separation function by running:

.. code:: python

   mus.test(my_function)

This test makes sure the user provided output is compatible to the
musdb framework. The function returns ``True`` if the test succeeds.

Processing the full musdb
''''''''''''''''''''''''''

To process all 150 musdb tracks and saves the results to the
``estimates_dir``:

.. code:: python

    mus.run(my_function, estimates_dir="path/to/estimates")

Processing training and testing subsets separately
''''''''''''''''''''''''''''''''''''''''''''''''''

Algorithms which make use of machine learning techniques can use the
training subset and then apply the algorithm on the test data:

.. code:: python

    mus.run(my_training_function, subsets="Dev")
    mus.run(my_test_function, subsets="Test")


Access the reference signals / targets
''''''''''''''''''''''''''''''''''''''

For supervised learning you can use the provided reference sources by loading the `track.targets` dictionary.
E.g. to access the vocal reference from a track:

.. code:: python

    track.targets['vocals'].audio


Use multiple cores
''''''''''''''''''

Python Multiprocessing
""""""""""""""""""""""

To speed up the processing, ``run`` can make use of multiple CPUs:

.. code:: python

    mus.run(my_function, parallel=True, cpus=4)

Note: We use the python builtin multiprocessing package, which sometimes
is unable to parallelize the user provided function to
`PicklingError <http://stackoverflow.com/a/8805244>`__.
