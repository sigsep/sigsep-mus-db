"""
Benachmark Script that yields small excerpts from the musdb train subset

For stem dataset, the decoding is the main bottleneck which is why it is quite slow to load
"""

from __future__ import print_function
import musdb
import museval
import tqdm
import numpy as np

# initiate musdb
mus = musdb.DB(download=True, subsets="train")

def excerpt_gen(
    mus, 
    excerpt_dur=1.0, 
    excerpt_hop=1.0
):
    """yield non overlapping segments from audio without loading tracks to memory
    """
    for track in mus:
        for pos in np.arange(0, track.duration - excerpt_dur, excerpt_hop):
            track.start = pos
            track.duration = excerpt_dur
            audio = track.targets['drums'].audio
            # audio = track.audio
            yield audio


for audio in tqdm.tqdm(excerpt_gen(mus)):
    audio.mean()
