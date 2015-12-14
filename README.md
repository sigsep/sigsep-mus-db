# pydsd

A python package to parse and process the __demixing secrets dataset (DSD100)__ as part of the [Signal Separation Evaluation Campaign (SISEC)](https://sisec.inria.fr/)

### Installation

```bash
pip install pydsd
```

### Usage

This package allows to parse and process the _DSD100_ in python and therefore make it easy to participate in SISEC.

#### Providing a compatible function

 This function will then be used for separation the mixtures.

- The function will take an ```Track``` object which can be used in inside your algorithm.
- typically the function would want to access
 - ```Track.audio``` representing the mixture as an ```np.ndarray``` with ```shape=(nsampl, 2)```
 - ```Track.rate``` for the sample rate
 - ```Track.path``` for the absolute path of the mixture which might be handy process with external software
- The function needs to return a python ```Dict``` which includes the target name and the separated target audio with same shape as the mixture.
- It is the users choice which targets they want to provide for the given mixture.
- Please make sure that the returned estimates do have the same sample rate as the mixture track.
Here is an example for such a function

```python
def my_function(track):

    # your source separation algorithm
    # ...

    estimates = {
        'vocals': vocals_array,
        'accompaniment': accompaniment_array
    }
    return estimates
```

#### Running the SiSEC Evaluation

##### Setting up dsdeval

Simply import the dsdeval package in your main python function which has also imported your evaluation function
```python
import dsdeval

dsd = DSD100(
    root_dir=args.dsd_folder,
    user_estimates_dir='my_estimates'
)
```

The ```root_dir``` is the path to the DSD100 dataset folder. It can also be set systemwide instead. There just use  ```export DSD100_PATH=/path/to/DSD100/```. inside your terminal. If ```user_estimates_dir``` is not set, the default will be used which is inside the _DSD100_ ```root_dir```.

##### Test if your separation function generates valid output

Before you run the main evaluation which might take very long, participants can test their separation function by calling:
```python
dsd.test(my_function)
```
This test makes sure the user provided output is compatible to the dsdeval evaluation framework.

##### Processing the full DSD100

The full evaluation processes all 100 DSD tracks and saves the results to the ```user_estimates_dir```.

```python
dsd.run(my_function)
```

##### Processing training and testing subsets separately

Algorithms which make use of machine learning techniques can use the training subset and then apply the algorithm on the test data.

```python
dsd.run(my_training_function, subsets="train")
dsd.run(my_test_function, subsets="test")
```

### Compute the bss_eval measures

Currently there does not exist a [bss_eval](http://bass-db.gforge.inria.fr/bss_eval/) implementation for python which produces the exact same results; therefore we still relies on _MATLAB_.
We recommend to run ```DSD100_only_eval.m``` from the DSD100 Matlab scripts in Matlab after you have saved your estimates with __dsdeval__.

##### Optional

If you really don not want to start matlab you can run the bss_eval from python with the help of [matlab_wrapper](https://github.com/mrkrd/matlab_wrapper). For convenience this package already had implemented the matlab evaluation functions. We offer several optional methods to parse the DSD100:

```python
# Evaluate the results using matlab_wrapper and save the estimates to disk
dsd.run(my_function, save=True, evaluate=True)

# Evaluate the results using matlab_wrapper but do not save the estimates to disk
dsd.run(my_function, save=False, evaluate=True)

# Just evaluate the user_estimates folder when the estimates have already been saved to disk
# this equivalent to the matlab DSD100_only_eval.m function
dsd.run(save=False, evaluate=True)
# or simply which is the same as as last line
dsd.evaluate()

# Only pass the tracks to my_function. Ignore the results. Useful for statistics
dsd.run(my_function, save=False, evaluate=False)
```

### Full code Example

```python
import dsdeval


def my_function(dsd_track):
    '''My fancy BSS algorithm'''

    # get the audio mixture as numpy array
    dsd_track.audio

    # get the mixture path for external processing
    dsd_track.path

    # get the sample rate
    dsd_track.rate

    # return any number of targets
    estimates = {
        'vocals': vocals_array,
        'accompaniment': acc_array,
    }
    return estimates


# initiate the pydsd
dsd = dsdeval.SDS100(dsd_root="./Volumes/Data/DSD100")

# this takes 3 seconds and verifies if my_function works correctly
if dsd.test(my_function):
    print "my_function is valid"

# this takes 3 days to finish and is the actual evaluation
dsd.run(my_function)

# for the machine learning guys you want to split the subsets
dsd.run(my_training_function, subsets="train")  # this takes 1.5 days to finish
dsd.run(my_test_function, subsets="test")  # this takes 1.5 days to finish

```
