# musdb

[![Build Status](https://travis-ci.org/sigsep/sigsep-mus-db.svg?branch=master)](https://travis-ci.org/sigsep/sigsep-mus-db)
[![Coverage Status](https://coveralls.io/repos/github/sigsep/sigsep-mus-db/badge.svg?branch=master)](https://coveralls.io/github/sigsep/sigsep-mus-db?branch=master)
[![Latest Version](https://img.shields.io/pypi/v/musdb.svg)](https://pypi.python.org/pypi/musdb/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/musdb.svg)](https://pypi.python.org/pypi/musdb/)
[![Docs Status](https://readthedocs.org/projects/musdb/badge/?version=latest)](https://musdb.readthedocs.org/en/latest/)


A python package to parse and process the [MUSDB18 dataset](https://sigsep.github.io/musdb) as part of the [MUS task](https://sisec.inria.fr/home/2018-professionally-produced-music-recordings/) of the [Signal Separation Evaluation Campaign (SISEC)](https://sisec.inria.fr/).

## Download Dataset

_MUSDB18_ can automatically download and use 7 seconds previews for easy and quick access or prototyping. 
However, the full dataset need to be downloaded [via Zenodo](https://sigsep.github.io/musdb).

## Installation

### Package installation

You can install the `musdb` parsing package using pip:

```bash
pip install musdb
```

### Using STEMs (Default)

<img src="https://sigsep.github.io/assets/img/stems.a411b49d.png" width="300"/>

_MUSDB18_ is encoded as [STEMS](http://www.stems-music.com/) which is a multitrack audio format that uses _lossy compression_. The `musdb` package relies on FFMPEG to decode the multi-stream files. For convenience, we developed a python package called [stempeg](https://github.com/faroit/stempeg) that allows to easily parse the stem files and decode them on-the-fly.
When you install _musdb_ (which depends on _stempeg_), it is therefore necessary to also install the FFMPEG library. The installation may differ among operating systems and python distributions:

* On [Anaconda](https://anaconda.org), you can install FFMPEG using `conda install -c conda-forge ffmpeg`

Alternatively you can install FFMPEG manually as follows:

* macOS, using homebrew: `brew install ffmpeg`
* Ubuntu/Debian: `sudo apt-get install ffmpeg `

#### Load Wav files (Optional)

If you have trouble installing _stempeg_ or FFMPEG, `musdb` also supports parsing and processing pre-decoded PCM/wav files. We provide [docker based scripts](https://github.com/sigsep/sigsep-mus-io) to decode the dataset to wav files.
If you want to use the decoded musdb dataset, use the `is_wav` parameter when initializing the dataset.

## Usage

This package should nicely integrate with your existing python code, thus makes it easy to participate in the [SISEC MUS tasks](https://sisec.inria.fr/home/2016-professionally-produced-music-recordings).

### Setting up musdb

Simply import the musdb package in your main python function:

```python
import musdb
mus = musdb.DB(root_dir='path/to/musdb', is_wav=False)
```

The ```root_dir``` is the path to the musdb dataset folder. Instead of ```root_dir``` it can also be set system-wide. Just ```export MUSDB_PATH=/path/to/musdb``` inside your bash environment.

### MUSDB tracks

The `mus` object consists of a list of musdb ```Track``` objects which makes it easy to parse the multitrack dataset in a pythonic way.

 - ```Track.name```, the track name, consisting of `Track.artist` and `Track.title`.
 - ```Track.path```, the absolute path of the mixture which might be handy to process with external applications.
 - ```Track.audio```, stereo mixture as an numpy array of shape `(nb_samples, 2)`
 - ```Track.rate```, the sample rate of the mixture.
 - ```Track.sources```, a dictionary of sources used for this track.
 - ```Track.stems```, an numpy tensor of all five stereo sources of shape `(5, nb_samples, 2)`. The stems are always in the following order: `['mixture', 'drums', 'bass', 'other', 'vocals']`,
 - ```Track.targets```, a dictionary of targets used for this track.
Note that for MUSDB, the sources and targets differ only in the existence of the `accompaniment`, which is the sum of all sources, except for the vocals. MUSDB supports the following targets: `['mixture', 'drums', 'bass', 'other', 'vocals', 'accompaniment']`.

### Iterate over MUSDB18 tracks

Thus, iterating over all musdb tracks, and accessing the audio data of the mixture and of an target sources, is as simple as...

```python
for track in mus:
    train(track.audio, track.targets['vocals'].audio)
```

#### Processing training and testing subsets separately

Supervised separation methods leveraging machine learning could use the training subset and then apply the algorithm on the test data:

```python
mus = musdb.DB(subsets="train")
mus = musdb.DB(subsets="test")
```

#### Processing individual tracks

If you want to access individual tracks, e.g. to specify a validation dataset. You can manually access and modify the track list before starting your separation method.

```python
mus = musdb.DB(subsets="train")

train_tracks = mus[2:]
valid_tracks = mus[:2]
```

Instead of parsing the track list, `musdb` supports loading tracks by track name, as well:

```python
two_tracks = mus.get_tracks_by_name(["PR - Oh No", "Angels In Amplifiers - I'm Alright"])
```

#### Save results

#### Evaluation

To Evaluate a musdb track using the popular BSSEval metrics, you can install our [museval](https://github.com/sigsep/sigsep-mus-eval) package.
To evaluate a single `track`, all you need, is to provide a track estimate Dict:

```python
import museval
# provide an estimate
estimates = {
    'vocals': np.random.random(track.audio.shape),
    'accompaniment': np.random.random(track.audio.shape)
}

# evaluates using BSSEval v4, and writes results to `./eval`
scores = museval.eval_mus_track(
    track, estimates, output_dir="./eval"
)

# print nicely formatted mean scores
print(scores)
```

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
