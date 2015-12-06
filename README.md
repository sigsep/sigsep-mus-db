# pydsd

A python package to parse and process the __demixing secrets dataset (DSD100)__ as part of the [Signal Separation Evaluation Campaign (SISEC)](https://sisec.inria.fr/)

## Usage

### Installation

```
pip install pydsd
```

### Code Example

```python
import dsdeval


def my_function(dsd_track):
    # do your fancy bss algorithm

    # use the tracks mixture audio as numpy array
    dsd_track.audio

    # get the path for external processing
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
dsd.run(my_training_function, subset="train")  # this takes 1.5 days to finish
dsd.run(my_test_function, subset="test")  # this takes 1.5 days to finish

```
