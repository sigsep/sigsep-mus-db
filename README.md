# musdb

[![Build Status](https://travis-ci.org/sigsep/sigsep-mus-db.svg?branch=master)](https://travis-ci.org/sigsep/sigsep-mus-db)
[![Coverage Status](https://coveralls.io/repos/github/sigsep/sigsep-mus-db/badge.svg?branch=master)](https://coveralls.io/github/sigsep/sigsep-mus-db?branch=master)
[![Latest Version](https://img.shields.io/pypi/v/musdb.svg)](https://pypi.python.org/pypi/musdb/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/musdb.svg)](https://pypi.python.org/pypi/musdb/)
[![Docs Status](https://readthedocs.org/projects/musdb/badge/?version=latest)](https://musdb.readthedocs.org/en/latest/)


A python package to parse and process the [MUSDB18 dataset](https://sigsep.github.io/musdb) as part of the [MUS task](https://sisec.inria.fr/home/2018-professionally-produced-music-recordings/) of the [Signal Separation Evaluation Campaign (SISEC)](https://sisec.inria.fr/).

## Download Dataset

_MUSDB18_ can automatically download and use 7 seconds previews for easy and quick access or prototyping. 
However, the full dataset need to be downloaded [from our website](https://sigsep.github.io/musdb).

## Installation

### Decoding

As the _MUSDB18_ is encoded as [STEMS](http://www.stems-music.com/), it
relies on ffmpeg to read the multi-stream files. We provide a python wrapper called [stempeg](https://github.com/faroit/stempeg) that allows to easily parse the dataset and decode the stem tracks on-the-fly.
Before you install _musdb_ (that includes the stempeg requirement), it is therefore required to install ffmpeg. The installation differ among operating systems.

E.g. if you use Anaconda you can install ffmpeg on Windows/Mac/Linux using the following command:

```
conda install -c conda-forge ffmpeg
```

Alternatively you can install ffmpeg manually as follows:
* Mac: use homebrew: `brew install ffmpeg`
* Ubuntu Linux: `sudo apt-get install ffmpeg `

#### Use a decoded version

If you have trouble installing stempeg or ffmpeg we also support parse and process the pre-decoded PCM/wav files. We provide [docker based scripts](https://github.com/sigsep/sigsep-mus-io) to decode the dataset to wav files.
If you want to use the decoded musdb dataset, use the `is_wav` parameter when initialsing the dataset.

```python
musdb.DB(is_wav=True)
```

### Package installation

You can install the `musdb` parsing package using pip:

```bash
pip install musdb
```

## Usage

This package should nicely integrate with your existing python code, thus makes it easy to participate in the [SISEC MUS tasks](https://sisec.inria.fr/home/2016-professionally-produced-music-recordings).

### Setting up musdb

Simply import the musdb package in your main python function:

```python
import musdb

mus = musdb.DB(root_dir='path/to/musdb')
```

The ```root_dir``` is the path to the musdb dataset folder. Instead of ```root_dir``` it can also be set system-wide. Just ```export MUSDB_PATH=/path/to/musdb``` inside your terminal environment.


```python
for track in mus:
    process(track.audio)
```

### MUSDB tracks

a MUS ```Track``` object is an object storage that makes it easy to parse the multitrack dataset.

 - ```Track.name```, the track name, consisting of `Track.artist` and `Track.title`.
 - ```Track.path```, the absolute path of the mixture which might be handy to process with external applications.
 - ```Track.audio```, representing the stereo mixture as an `np.ndarray` of `shape=(nun_sampl, 2)`
 - ```Track.rate```, the sample rate of the mixture.
 - ```Track.sources```, a dictionary of sources used for this track.
 - ```Track.targets```, a dictionary of targets used for this track.


Note that for MUSDB, the sources and targets differ only in the existance of an `accompaniment` target, which is the sum of all sources, except for the vocals. MUSDB supports the following targets:

* `vocals`, `accompaniment`, `drums`, `bass`, `other`.



#### Processing training and testing subsets separately

Algorithms which make use of machine learning techniques can use the training subset and then apply the algorithm on the test data. That way it is possible to apply different user functions for both datasets.

```python
mus = musdb.DB(subsets="train")
mus = musdb.DB(subsets="test")
```

#### Processing individual tracks

If you want to access individual tracks, e.g. to specify a validation dataset. You can manually load the track array before running your separation function.

```python
# load the training tracks
mus[0].name
```

Instead of parsing the track list, `musdb` supports loading tracks by track name, as well:

```python
mus.tracks = mus.get_tracks_by_name(["PR - Oh No", "Angels In Amplifiers - I'm Alright"])
len(mus)  # outputs 2
```

##### Access the reference signals / targets

For supervised learning you can use the provided reference sources by loading the `track.targets` dictionary.
E.g. to access the vocal reference from a track:

```python
track.targets['vocals'].audio
```

#### Save and evaluate results

To process all 150 MUS tracks and saves the results to the folder ```estimates_dir```:

## Use MUSDB ML Libraries 

t.b.a.

#### Pytorch 1.0

t.b.a.

#### Tensorflow

t.b.a.

#### Pescador

t.b.a.

## Baselines

Please check [examples of oracle separation methods](https://github.com/sigsep/sigsep-mus-oracle).
This will show you how oracle performance is computed, i.e. an upper bound for the quality of the separtion.

## Compare your Results

- 2018: Please refer to our [Submission site](https://github.com/sigsep/sigsep-mus-2018).
- 2019: t.b.a

## Frequently Asked Questions

##### The mixture is not exactly the sum of its sources, is that intended?

This is not a bug. Since we adopted the STEMS format, we used AAC compression. Here the residual noise of the mixture is different from the sum of the residual noises of the sources. This difference does not significantly affect separation performance.

## References

LVA/ICA 2018 publication t.b.a
