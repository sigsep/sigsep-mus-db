import os
import soundfile as sf
import numpy as np
import stempeg


class Track(object):
    """
    Generic audio Track that can be wav or stem file

    Attributes
    ----------
    name : str
        Track name
    path : str
        Absolute path of mixture audio file
    stem_id : int
        stem/substream ID
    is_wav : boolean
        If stem is read from wav or mp4 stem
    subset : {'train', 'test'}
        belongs to subset
    targets : OrderedDict
        OrderedDict of mixted Targets for this Track
    sources : Dict
        Dict of ``Source`` objects for this ``Track``
    start : float
        start offset when loading the file, defaults to 0 (beginning)
    dur : float
        set duration of audio file when loading, defaults to `None` (end)
    """

    def __init__(
        self,
        path="None",
        is_wav=False,
        stem_id=None,
        subset=None,
        start=0,
        dur=None
    ):
        self.path = path
        self.subset = subset
        self.stem_id = stem_id
        self.is_wav = is_wav

        self.start = start
        self.dur = dur

        # get and store metdata
        if os.path.exists(self.path):
            if not self.is_wav:
                self.info = stempeg.Info(self.path)
                self.samples = int(self.info.samples(self.stem_id))
                self.duration = self.info.duration(self.stem_id)
                self.rate = self.info.rate(self.stem_id)
            else:
                self.info = sf.info(self.path)
                self.samples = self.info.frames
                self.duration = self.info.duration
                self.rate = self.info.samplerate
        else:
            # set to `None` if no path was set (fake file)
            self.info = None
            self.samples = None
            self.duration = None
            self.rate = None

        self._audio = None

    def __len__(self):
        return self.samples

    @property
    def audio(self):
        # return cached audio if explicitly set by setter
        if self._audio is not None:
            return self._audio
        # read from disk to save RAM otherwise
        else:
            return self.load_audio(
                self.path, self.stem_id, self.start, self.dur
            )

    @audio.setter
    def audio(self, array):
        self._audio = array

    def load_audio(self, path, stem_id, start=0, dur=None):
        """array_like: [shape=(num_samples, num_channels)]
        """
        if os.path.exists(self.path):
            if not self.is_wav:
                # read using stempeg
                audio, rate = stempeg.read_stems(
                    filename=path,
                    stem_id=stem_id,
                    start=start,
                    duration=dur,
                    info=self.info
                )
            else:
                start = int(start * self.rate)

                # check if dur is none
                if dur:
                    # stop in soundfile is calc in samples, not seconds
                    stop = start + int(dur * self.rate)
                else:
                    stop = dur

                audio, rate = sf.read(
                    path,
                    always_2d=True,
                    start=start,
                    stop=stop
                )
            self._rate = rate
            return audio
        else:
            self._rate = None
            self._audio = None
            raise ValueError("Oops! %s cannot be loaded" % path)

    def __repr__(self):
        return "%s" % (self.path)


class MultiTrack(Track):
    def __init__(
        self,
        path=None,
        name=None,
        artist=None,
        title=None,
        sources=None,
        targets=None,
        *args,
        **kwargs
    ):
        super(MultiTrack, self).__init__(path=path, *args, **kwargs)

        self.name = name
        self.path = path
        try:
            split_name = name.split(' - ')
            self.artist = split_name[0]
            self.title = split_name[1]
        except IndexError:
            self.artist = artist
            self.title = title

        self.sources = sources
        self.targets = targets
        self._stems = None

    @property
    def stems(self):
        """array_like: [shape=(stems, num_samples, num_channels)]
        """

        # return cached audio it explicitly set bet setter
        if self._stems is not None:
            return self._stems
        # read from disk to save RAM otherwise
        else:
            if not self.is_wav and os.path.exists(self.path):
                S, rate = stempeg.read_stems(
                    filename=self.path,
                    start=self.start,
                    duration=self.dur,
                    info=self.info
                )
            else:
                rate = self.rate
                S = []
                S.append(self.audio)
                # append sources in order of stem_ids
                for k, v in sorted(self.sources.items(), key=lambda x: x[1].stem_id):
                    S.append(v.audio)
                S = np.array(S)
            self._rate = rate
            return S


class Source(Track):
    """
    An audio Target which is a linear mixture of several sources

    Attributes
    ----------
    name : str
        Name of this source
    stem_id : int
        stem/substream ID is set here.
    is_wav : boolean
        If stem is read from wav or mp4 stem
    path : str
        Absolute path to audio file
    gain : float
        Mixing weight for this source
    """
    def __init__(
        self,
        multitrack, # belongs to a multitrack
        name=None,  # has its own name
        path=None,  # might have its own path
        stem_id=None,  # might have its own stem_id
        gain=1.0,
        *args,
        **kwargs
    ):
        self.multitrack = multitrack
        self.name = name
        self.path = path
        self.stem_id = stem_id
        self.gain = gain
        self._audio = None

    def __repr__(self):
        return self.path

    @property
    def audio(self):
        # return cached audio if explicitly set by setter
        if self._audio is not None:
            return self._audio
        # read from disk to save RAM otherwise
        else:
            return self.multitrack.load_audio(
                self.path, self.stem_id, self.multitrack.start, self.multitrack.dur
            )

    @audio.setter
    def audio(self, array):
        self._audio = array

    @property
    def rate(self):
        return self.multitrack.rate

# Target Track from musdb DB mixed from several musdb Tracks
class Target(Track):
    """
    An audio Target which is a linear mixture of several sources

    Attributes
    ----------
    multitrack : Track
        Track object
    """
    def __init__(
        self, 
        multitrack,  # belongs to a multitrack
        name=None,  # has its own name
    ):
        self.multitrack = multitrack
        self.name = name

    @property
    def audio(self):
        """array_like: [shape=(num_samples, num_channels)]

        mixes audio for targets on the fly
        """
        mix_list = []*len(self.multitrack.sources)
        for _, source in self.multitrack.sources.items():
            audio = source.audio
            if audio is not None:
                mix_list.append(
                    source.gain * audio
                )
        return np.sum(np.array(mix_list), axis=0)

    @property
    def rate(self):
        return self.multitrack.rate

    def __repr__(self):
        parts = []
        for source in self.multitrack.sources.keys():
            parts.append(source)
        return '+'.join(parts)
