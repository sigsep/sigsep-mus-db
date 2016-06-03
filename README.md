# dsdtools

[![Build Status](https://travis-ci.org/faroit/dsdtools.svg?branch=master)](https://travis-ci.org/faroit/dsdtools)

A python package to parse and process the __demixing secrets dataset (DSD)__ as part of the [Signal Separation Evaluation Campaign (SISEC)](https://sisec.inria.fr/)

## Installation

```bash
pip install dsdtools
```

## Usage

This package should nicely integrate with your existing  python code, thus makes it easy to participate in the [SISEC MUS tasks](https://sisec.inria.fr/professionally-produced-music-recordings).

## DSD100 Dataset / Subset

A link to the complete dataset is found [here](https://sisec.inria.fr/professionally-produced-music-recordings). For testing and development we provide a subset of the dsd100 [for direct download here](https://www.loria.fr/~aliutkus/DSD100subset.zip). It has the same file and folder structure as well as the same audio file formats but consists of only 4 tracks of 30s each.

### Providing a compatible function

 The core of this package is calling a user-provided function that separates the mixtures from the DSD into several estimated target sources.

- The function will take an DSD ```Track``` object which can be used from inside your algorithm.
- Participants can access:

 - ```Track.audio```, representing the stereo mixture as an ```np.ndarray``` of ```shape=(nun_sampl, 2)```
 - ```Track.rate```, the sample rate
 - ```Track.path```, the absolute path of the mixture which might be handy to process with external applications, so that participants don't need to write out temporary wav files.

- The provided function needs to return a python ```Dict``` which consists of target name (```key```) and the estimated target as audio arrays with same shape as the mixture (```value```).
- It is the choice of the users which target sources they want to provide for a given mixture. Supported targets are ```['vocals', 'accompaniment', 'drums', 'bass', 'other']```.
- Please make sure that the returned estimates do have the same sample rate as the mixture track.

Here is an example for such a function separating the mixture into a __vocals__ and __accompaniment__ track:

```python
def my_function(track):

    # get the audio mixture as numpy array shape=(nun_sampl, 2)
    track.audio

    # compute voc_array, acc_array
    # ...

    return {
        'vocals': voc_array,
        'accompaniment': acc_array
    }
```

### Create estimates for SiSEC evaluation

#### Setting up dsdtools

Simply import the dsdtools package in your main python function:

```python
import dsdtools

dsd = dsdtools.DB(
    root_dir='path/to/dsdtools',
)
```

The ```root_dir``` is the path to the dsdtools dataset folder. It can also be set system-wide. Just ```export DSD_PATH=/path/to/dsdtools``` inside your terminal.

#### Test if your separation function generates valid output

Before you run the full dsdtools, which might take very long, participants can test their separation function by running:
```python
dsd.test(my_function)
```
This test makes sure the user provided output is compatible to the dsdtools framework. The function returns `True` if the test succeeds.

#### Processing the full dsdtools

To process all 100 DSD tracks and saves the results to the folder ```estimates_dir```:

```python
dsd.run(my_function, estimates_dir="path/to/estimates")
```

#### Processing training and testing subsets separately

Algorithms which make use of machine learning techniques can use the training subset and then apply the algorithm on the test data:

```python
dsd.run(my_training_function, subsets="train")
dsd.run(my_test_function, subsets="test")
```

#### Processing single or multiple dsdtools items

```python
dsd.run(my_function, ids=30)
dsd.run(my_function, ids=[1, 2, 3])
dsd.run(my_function, ids=range(90, 99))
```

Note, that the provided list of ids can be overridden if the user sets a terminal environment variable ```dsdtools_ID=1```.

#### Use multiple cores

##### Python Multiprocessing

To speed up the processing, `run` can make use of multiple CPUs:

```python
dsd.run(my_function, parallel=True, cpus=4)
```

Note: We use the python builtin multiprocessing package, which sometimes is unable to parallelize the user provided function to [PicklingError](http://stackoverflow.com/a/8805244).

##### GNU Parallel

> [GNU parallel](http://www.gnu.org/software/parallel) is a shell tool for executing jobs in parallel using one or more computers. A job can be a single command or a small script that has to be run for each of the lines in the input. The typical input is a list of files, a list of hosts, a list of users, a list of URLs, or a list of tables. A job can also be a command that reads from a pipe. GNU parallel can then split the input and pipe it into commands in parallel.

By running only one ```id``` in each python process the dsdtools set can easily be processed with GNU parallel using multiple CPUs without any further modifications to your code:

```bash
parallel --bar 'dsdtools_ID={0} python dsdtools_main.py' ::: {0..99}  
```

## Compute the bss_eval measures

The official SISEC evaluation relies on _MATLAB_ because currently there does not exist a [bss_eval](http://bass-db.gforge.inria.fr/bss_eval/) implementation for python which produces identical results.
Therefore please run ```dsd100_only_eval.m``` from the [dsdtools Matlab scripts](https://github.com/faroit/dsd100mat) after you have processed and saved your estimates with _dsdtools_.

## Full code Example

```python
import dsdtools

def my_function(track):
    '''My fancy BSS algorithm'''

    # get the audio mixture as numpy array shape=(num_sampl, 2)
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


# initiate dsdtools
dsd = dsdtools.DB(root_dir="./Volumes/Data/dsdtools")

# verify if my_function works correctly
if dsd.test(my_function):
    print "my_function is valid"

# this might take 3 days to finish
dsd.run(my_function, estimates_dir="path/to/estimates")

```

## References

If you use this package, please reference the following paper

```tex
@inproceedings{SiSEC2015,
  TITLE = {{The 2015 Signal Separation Evaluation Campaign}},
  AUTHOR = {N. Ono and Z. Rafii and D. Kitamura and N. Ito and A. Liutkus},
  BOOKTITLE = {{International Conference on Latent Variable Analysis and Signal Separation  (LVA/ICA)}},
  ADDRESS = {Liberec, France},
  SERIES = {Latent Variable Analysis and Signal Separation},
  VOLUME = {9237},
  PAGES = {387-395},
  YEAR = {2015},
  MONTH = Aug,
}
```
