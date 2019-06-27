# musdb

[![Build Status](https://travis-ci.org/sigsep/sigsep-mus-db.svg?branch=master)](https://travis-ci.org/sigsep/sigsep-mus-db)
[![Coverage Status](https://coveralls.io/repos/github/sigsep/sigsep-mus-db/badge.svg?branch=master)](https://coveralls.io/github/sigsep/sigsep-mus-db?branch=master)
[![Latest Version](https://img.shields.io/pypi/v/musdb.svg)](https://pypi.python.org/pypi/musdb/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/musdb.svg)](https://pypi.python.org/pypi/musdb/)
[![Docs Status](https://readthedocs.org/projects/musdb/badge/?version=latest)](https://musdb.readthedocs.org/en/latest/)


A python package to parse and process the [MUSDB18 dataset](https://sigsep.github.io/musdb) as part of the [MUS task](https://sisec.inria.fr/home/2018-professionally-produced-music-recordings/) of the [Signal Separation Evaluation Campaign (SISEC)](https://sisec.inria.fr/).

## Download Dataset

_MUSDB18_ automatically downloads and use 7 seconds previews for easy and quick access or prototyping. The full dataset, however need to be downloaded [via Zenodo](https://sigsep.github.io/musdb).

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

#### Using WAV files (Optional)

If you want to use WAV files (e.g. for faster audio decoding), `musdb` also supports parsing and processing pre-decoded PCM/wav files. `musdb.tools.musdb_convert(...)` decodes the stem dataset into wav into a new location. This script can be used from the command line by

```
musdbconvert path/to/musdb-stems-root path/to/new/musdb/root
```

If you don't want to use python, we also provide [docker based scripts](https://github.com/sigsep/sigsep-mus-io) to decode the dataset to WAV files.

__When you use the decoded MUSDB, use the `is_wav` parameter when initializing the dataset.__

## Usage

This package nicely integrates with your existing python numpy, tensorflow or pytorch code.

### Setting up musdb

Import the musdb package in your main python function and iterate over the musdb tracks:

```python
import musdb
mus = musdb.DB(root='path/to/musdb', download=True)
mus[0].audio
```

The ```root``` is the path to the musdb dataset folder. Instead of ```root``` it can also be set system-wide. Just ```export MUSDB_PATH=/path/to/musdb``` inside your bash environment.

### MUSDB tracks

The `mus` object consists of a list of musdb ```Track``` objects which makes it easy to parse the multitrack dataset in a pythonic way.

 - ```Track.name```, the track name, consisting of `Track.artist` and `Track.title`.
 - ```Track.path```, the absolute path of the mixture which might be handy to process with external applications.
 - ```Track.audio```, stereo mixture as an numpy array of shape `(nb_samples, 2)`
 - ```Track.rate```, the sample rate of the mixture.
 - ```Track.sources```, a dictionary of sources used for this track.
 - ```Track.stems```, an numpy tensor of all five stereo sources of shape `(5, nb_samples, 2)`. The stems are always in the following order: `['mixture', 'drums', 'bass', 'other', 'vocals']`,
 - ```Track.targets```, a dictionary of targets used for this track.
Note that for MUSDB, the sources and targets differ only in the existence of the `accompaniment`, which is the sum of all sources, except for the vocals. MUSDB supports the following targets: `['mixture', 'drums', 'bass', 'other', 'vocals', 'accompaniment', 'linear_mixture']`.

### Iterate over MUSDB18 tracks

Thus, iterating over all tracks, and accessing the audio data of the mixture and of an target sources, is as simple as...

```python
for track in mus:
    train(track.audio, track.targets['vocals'].audio)
```

#### Processing training and testing subsets separately

Supervised separation methods leveraging machine learning could use the training subset and then apply the algorithm on the test data:

```python
mus_train = musdb.DB(subsets="train")
mus_test = musdb.DB(subsets="test")
```

#### Use train / validation split

If you want to access individual tracks, you can access the `mus` tracks list by its indices, e.g. `mus[2:]`. To foster reproducible research, we provide a fixed validation dataset. 

```python
mus_train = musdb.DB(subsets="train", split='train')
mus_valid = musdb.DB(subsets="train", split='valid')
```

The list of validation tracks can be edited using the [`mus.setup['validation_tracks']`](https://github.com/sigsep/sigsep-mus-tools/blob/b283da5b8f24e84172a60a06bb8f3dacd57aa6cd/musdb/configs/mus.yaml) object.

## Training Deep Neural Networks with `musdb`

Writing an efficient dataset generator varies across different deep learning frameworks. A very simple näive generator that

* draws random tracks with replacement
* draws random chunks of fixed length with replacement

can be easily implemented using musdbs `track.chunk_start` and `track.chunk_duration` properties which efficiently seeks to the chunk part and does not load the full audio.

```python
while True:
    track = random.choice(mus.tracks)
    track.chunk_duration = 5.0
    track.chunk_start = random.uniform(0, track.duration - self.seq_duration)
    x = track.audio.T
    y = track.targets['vocals'].audio.T
    yield x, y
```

#### Evaluation

To Evaluate a musdb track using the popular BSSEval metrics, you can use our [museval](https://github.com/sigsep/sigsep-mus-eval) package. After `pip install musdb` evaluation of a single `track`, can be done by

```python
import museval
# provide an estimate
estimates = {
    'vocals': np.random.random(track.audio.shape),
    'accompaniment': np.random.random(track.audio.shape)
}
# evaluates using BSSEval v4, and writes results to `./eval`
print(museval.eval_mus_track(track, estimates, output_dir="./eval")
```

To process all 150 MUS tracks and saves the results to the folder ```estimates_dir```:


## Baselines

### Oracles
For oracle methods, please check out our [open unmix oracle separation methods](https://github.com/sigsep/sigsep-mus-oracle).
This will show you how oracle performance is computed and gives indications for an upper bound for the quality of the separation.

### Open-Unmix

We provide a state-of-the-art deep learning based separation method for PyTorch, Tensorflow and NNable at [open.unmix.app](https://open.unmix.app).

## Frequently Asked Questions

##### The mixture is not exactly the sum of its sources, is that intended?

This is not a bug. Since we adopted the STEMS format, we used AAC compression. Here the residual noise of the mixture is different from the sum of the residual noises of the sources. This difference does not significantly affect separation performance.

```python
track.targets['linear_mixture'].audio
```

## Citations

<details><summary>If you use the MUSDB dataset for your research - Cite the MUSDB18 Dataset</summary>
<p>

```latex
@misc{MUSDB18,
  author       = {Rafii, Zafar and
                  Liutkus, Antoine and
                  Fabian-Robert St{\"o}ter and
                  Mimilakis, Stylianos Ioannis and
                  Bittner, Rachel},
  title        = {The {MUSDB18} corpus for music separation},
  month        = dec,
  year         = 2017,
  doi          = {10.5281/zenodo.1117372},
  url          = {https://doi.org/10.5281/zenodo.1117372}
}
```

</p>
</details>


<details><summary>If compare your results with SiSEC 2018 Participants - Cite the SiSEC 2018 LVA/ICA Paper</summary>
<p>

```latex
@inproceedings{SiSEC18,
  author="St{\"o}ter, Fabian-Robert and Liutkus, Antoine and Ito, Nobutaka",
  title="The 2018 Signal Separation Evaluation Campaign",
  booktitle="Latent Variable Analysis and Signal Separation:
  14th International Conference, LVA/ICA 2018, Surrey, UK",
  year="2018",
  pages="293--305"
}
```

</p>
</details>

## License

MIT 