.. dsdeval documentation master file, created by
   sphinx-quickstart on Mon Dec 14 10:43:11 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to dsdeval's documentation!
===================================

A python package to parse and process the **demixing secrets dataset
(DSD100)** as part of the `Signal Separation Evaluation Campaign
(SISEC) <https://sisec.inria.fr/>`__

Installation
------------

.. code:: bash

    pip install pydsd

Usage
-----

This package allows to parse and process the *DSD100* in python and
therefore make it easy to participate in SISEC.

Providing a compatible function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This function will then be used for separation the mixtures.

-  The function will take an ``Track`` object which can be used in
   inside your algorithm.
-  typically the function would want to access
-  ``Track.audio`` representing the mixture as an ``np.ndarray`` with
   ``shape=(nsampl, 2)``
-  ``Track.rate`` for the sample rate
-  ``Track.path`` for the absolute path of the mixture which might be
   handy process with external software
-  The function needs to return a python ``Dict`` which includes the
   target name and the separated target audio with same shape as the
   mixture.
-  It is the users choice which targets they want to provide for the
   given mixture.
-  Please make sure that the returned estimates do have the same sample
   rate as the mixture track. Here is an example for such a function

.. code:: python

    def my_function(track):

        # your source separation algorithm
        # ...

        estimates = {
            'vocals': vocals_array,
            'accompaniment': accompaniment_array
        }
        return estimates

Running the SiSEC Evaluation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Setting up dsdeval
^^^^^^^^^^^^^^^^^^

Simply import the dsdeval package in your main python function which has
also imported your evaluation function

.. code:: python

    import dsdeval

    dsd = DSD100(
        root_dir=args.dsd_folder,
        user_estimates_dir='my_estimates'
    )

The ``root_dir`` is the path to the DSD100 dataset folder. It can also
be set systemwide instead. There just use
``export DSD100_PATH=/path/to/DSD100/``. inside your terminal. If
``user_estimates_dir`` is not set, the default will be used which is
inside the *DSD100* ``root_dir``.

Test if your separation function generates valid output
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Before you run the main evaluation which might take very long,
participants can test their separation function by calling:

.. code:: python

    dsd.test(my_function)

This test makes sure the user provided output is compatible to the
dsdeval evaluation framework.

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

Currently there does not exist a
`bss\_eval <http://bass-db.gforge.inria.fr/bss_eval/>`__ implementation
for python which produces the exact same results; therefore we still
relies on *MATLAB*. We recommend to run ``DSD100_only_eval.m`` from the
DSD100 Matlab scripts in Matlab after you have saved your estimates with
**dsdeval**.
Contents:

.. toctree::
   :maxdepth: 3

   dsdeval
   audio_classes


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
