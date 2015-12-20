# DSD100

A python package to parse and process the __demixing secrets dataset (DSD100)__ as part of the [Signal Separation Evaluation Campaign (SISEC)](https://sisec.inria.fr/)

### Installation

```bash
pip install dsd100
```

### Usage

This package should nicely integrate with your existing code so that it can parse and process the _DSD100_ from python, thus makes it easy to participate in the [SISEC MUS tasks](https://sisec.inria.fr/professionally-produced-music-recordings).

#### Providing a compatible function

 The core of this package consists of calling a user-provided function which separates the mixtures from the DSD100 into estimated target sources.

- The function will take an DSD100 ```Track``` object which can be used from inside your algorithm.
- Participants can access
 - ```Track.audio```, representing the stereo mixture as an ```np.ndarray``` of ```shape=(nun_sampl, 2)```
 - ```Track.rate```, the sample rate
 - ```Track.path```, the absolute path of the mixture which might be handy to process with external applications, so that participants don't need to write out temporary wav files.
- The function needs to return a python ```Dict``` which consists of target name (```key```) and the estimated target as audio arrays with same shape as the mixture (```value```).
- It is the users choice which target sources they want to provide for a given mixture. Supported targets are ```['vocals', 'accompaniment', 'drums', 'bass', 'other']```.
- Please make sure that the returned estimates do have the same sample rate as the mixture track.

Here is an example for such a function separating the mixture into a __vocals__ and __accompaniment__ track.

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

#### Create estimates for SiSEC evaluation

##### Setting up dsd100

Simply import the dsd100 package in your main python function:

```python
import dsd100

dsd = dsd100.DB(
    root_dir='path/to/DSD100/',
    user_estimates_dir='my_estimates'
)
```

The ```root_dir``` is the path to the DSD100 dataset folder. It can also be set system-wide. Just ```export DSD100_PATH=/path/to/DSD100/``` inside your terminal. The  ```user_estimates_dir``` is the path to the user estimates. If it is not set, the default will be used which is inside the _DSD100_ ```root_dir```.

##### Test if your separation function generates valid output

Before you run the full DSD100, which might take very long, participants can test their separation function by running:
```python
dsd.test(my_function)
```
This test makes sure the user provided output is compatible to the DSD100 framework. The function returns `True` if the test succeeds.

##### Processing the full DSD100

To process all 100 DSD tracks and saves the results to the ```user_estimates_dir```:

```python
dsd.run(my_function)
```

##### Processing training and testing subsets separately

Algorithms which make use of machine learning techniques can use the training subset and then apply the algorithm on the test data:

```python
dsd.run(my_training_function, subsets="train")
dsd.run(my_test_function, subsets="test")
```

### Compute the bss_eval measures

The official SISEC evaluation relies on _MATLAB_ because currently there does not exist a [bss_eval](http://bass-db.gforge.inria.fr/bss_eval/) implementation for python which produces the exact same results.
Therefore please run ```DSD100_only_eval.m``` from the DSD100 Matlab scripts after you have processed and saved your estimates with _dsd100py_.

### Full code Example

```python
import dsd100

def my_function(track):
    '''My fancy BSS algorithm'''

    # get the audio mixture as numpy array shape=(nun_sampl, 2)
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


# initiate dsd100
dsd = dsd100.DB(root_dir="./Volumes/Data/DSD100")

# verify if my_function works correctly
if dsd.test(my_function):
    print "my_function is valid"

# this might take 3 days to finish
dsd.run(my_function)

# for the machine learning task you want to split the subsets
dsd.run(my_training_function, subsets="train")  # this takes 1.5 days to finish
dsd.run(my_test_function, subsets="test")  # this takes 1.5 days to finish

```

### References

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

Furthermore would like to thank [Emmanuel Vincent](http://www.loria.fr/~evincent/) for giving us the permission to use the [BSS Eval toolbox 3.0](http://bass-db.gforge.inria.fr/bss_eval/)
