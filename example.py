import pysdseval

def my_function(audio, fs):
    return {"vocals": estimate_array, "accompaniment": estimate_array}

sds = pysdseval(sds_root="...")

# this takes 3 seconds and verifies if my function works correctly
sds.test(my_function)

# this takes 3 days to finish and is the actual evaluation
sds.run(my_function)

# for the machine learning guys this would be
sds.run(my_training, subset="train")  # this takes 0.3 days to finish
sds.run(my_test, subset="test")  # this takes 0.3 days to finish

# calling matlab_wrapper from python evaluate with bss_eval
sds.eval()
