Installation
============

Decoding

As the MUSDB18 is encoded as STEMS, it relies on ffmpeg to read the multi-stream files. We provide a python wrapper called stempeg that allows to easily parse the dataset and decode the stem tracks on-the-fly. Before you install musdb (that includes the stempeg requirement), it is therefore required to install ffmpeg. The installation differ among operating systems.

E.g. if you use Anaconda you can install ffmpeg on Windows/Mac/Linux using the following command:

.. code:: bash

  conda install -c conda-forge ffmpeg

Alternatively you can install ffmpeg manually as follows:

    Mac: use homebrew: brew install ffmpeg
    Ubuntu Linux: sudo apt-get install ffmpeg

Use a decoded version

If you have trouble installing stempeg or ffmpeg we also support parse and process the pre-decoded PCM/wav files. We provide `docker based scripts <https://github.com/sigsep/sigsep-mus-io>`__ to decode the dataset to wav files. If you want to use the decoded musdb dataset, use the is_wav parameter when initialising the dataset.

.. code:: python
    musdb.DB(is_wav=True)

Package installation

You can install the musdb parsing package using pip:

pip install musdb

.. code:: bash

    pip install musdb


SIGSEP-MUS Dataset / Subset
---------------------------

The dataset can be downloaded `here <https://sigsep.github.io/musdb>`__.
