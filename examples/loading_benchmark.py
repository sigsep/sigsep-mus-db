"""
script that yields small excerpts from the musdb train subset to benchmark the loading performance
For the stem dataset, the decoding is the main bottleneck which is why it is quite slow to load
User can excpect performance of about:

    * stem.mp4: 20 excerpts per second (without multithreading)
    * wav: 1000 excerpts per second 


"""

import musdb
import tqdm
import numpy as np

# initiate musdb
mus = musdb.DB(download=True, is_wav=False)

def excerpt_gen(
    mus, 
    chunk_duration=1.0,
    chunk_hop=1.0
):
    """yield non overlapping segments from audio without loading tracks to memory
    """
    for track in mus:
        for pos in np.arange(0, track.duration - chunk_duration, chunk_hop):
            # set chunk start
            track.chunk_start = pos
            # set chunk duration
            track.chunk_duration = chunk_duration
            # load chunk
            audio = track.targets['drums'].audio
            yield audio


for audio in tqdm.tqdm(excerpt_gen(mus)):
    audio.mean()
