# pydsd

A python package to parse and process the __demixing secrets dataset (DSD100)__ as part of the [Signal Separation Evaluation Campaign (SISEC)](https://sisec.inria.fr/)

## Usage

### Installation

```bash
pip install pydsd
```


### Usage

#### Providing a compatible function

 This function will then be used for separation the mixtures.

- The function will take an ```Track``` object which can be used in inside your algorithm.
- typically the function would want to access
 - ```Track.audio``` representing the mixture as an ```np.ndarray``` with ```shape=(nsampl, 2)```
 - ```Track.rate``` for the sample rate
 - ```Track.path``` for the absolute path of the mixture which might be handy process with external software
- The function needs to return a python ```Dict``` which includes the target name and the separated target audio with same shape as the mixture.
- It is the users choice which targets they want to provide for the given mixture.

Here is an example for such a function

```python
def my_function(track):
    estimates = {
        'vocals': track.audio,
        'accompaniment': track.audio
    }
    return estimates
```

#### Running the SiSEC Evaluation


```python
import dsdeval
```

```python
dsd = DSD100(
    root_dir=args.dsd_folder,
    user_estimates_dir='./my_estimates'
)
```

#### Test if your separation function generates valid output
```python
dsd.test(my_function)
```

#### Run my_function and save the results to disk
```python
dsd.run(my_function)
dsd.run(my_function, save=True, evaluate=False)
```
#### Evaluate the results and save the estimates to disk
```python
dsd.run(my_function, save=True, evaluate=True)
```
#### Evaluate the results but do not save the estimates to disk
```python
dsd.run(my_function, save=False, evaluate=True)
```
#### Only pass tracks to my_function
```python
dsd.run(my_function, save=False, evaluate=False)
```
#### Just evaluate the user_estimates folder
```python
dsd.run(save=False, evaluate=True)
```
or simply
```python
dsd.evaluate()
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
dsd.run(my_training_function, subset="train")  # this takes 1.5 days to finish
dsd.run(my_test_function, subset="test")  # this takes 1.5 days to finish

```
