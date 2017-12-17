from __future__ import print_function
import os
import soundfile as sf
import numpy as np
import stempeg


class Source(object):
    """
    An audio Target which is a linear mixture of several sources

    Attributes
    ----------
    name : str
        Name of this source
    stem_id : int
        If part of a stem file, the stem/substream ID is set here.
    path : str
        Absolute path to audio file
    gain : float
        Mixing weight for this source
    """
    def __init__(self, name=None, path=None, stem_id=None):
        self.name = name
        self.path = path
        self.stem_id = stem_id
        self.gain = 1.0
        self._audio = None
        self._rate = None

    @property
    def audio(self):
        """array_like: [shape=(num_samples, num_channels)]
        """
        # return cached audio if explicitly set by setter
        if self._audio is not None:
            return self._audio
        # read from disk to save RAM otherwise
        else:
            if os.path.exists(self.path):
                if self.stem_id is not None:
                    audio, rate = stempeg.read_stems(
                        filename=self.path, stem_id=self.stem_id
                    )
                else:
                    audio, rate = sf.read(self.path, always_2d=True)
                self._rate = rate
                return audio
            else:
                self._rate = None
                self._audio = None
                raise ValueError("Oops! %s cannot be loaded" % self.path)

    @property
    def rate(self):
        """int: sample rate in Hz
        """

        # load audio to set rate
        if self._rate is None:
            if os.path.exists(self.path):
                if self.stem_id is not None:
                    audio, rate = stempeg.read_stems(
                        filename=self.path, stem_id=self.stem_id
                    )
                else:
                    audio, rate = sf.read(self.path, always_2d=True)
                self._rate = rate
                return rate
            else:
                self._rate = None
                self._audio = None
                raise ValueError("Oops! %s cannot be loaded" % self.path)
        return self._rate

    @audio.setter
    def audio(self, array):
        self._audio = array

    @rate.setter
    def rate(self, rate):
        self._rate = rate

    def __repr__(self):
        return self.path


# Target Track from musdb DB mixed from several DSDSource Tracks
class Target(object):
    """
    An audio Target which is a linear mixture of several sources

    Attributes
    ----------
    sources : list[Source]
        list of ``Source`` objects for this ``Target``
    """
    def __init__(self, sources):
        self.sources = sources  # List of DSDSources

    @property
    def audio(self):
        """array_like: [shape=(num_samples, num_channels)]

        mixes audio for targets on the fly
        """
        mix_list = []*len(self.sources)
        for source in self.sources:
            audio = source.audio
            if audio is not None:
                mix_list.append(
                    source.gain * audio
                )
        return np.sum(np.array(mix_list), axis=0)

    def __repr__(self):
        parts = []
        for source in self.sources:
            parts.append(source.name)
        return '+'.join(parts)


# musdb Track which has many targets and sources
class Track(object):
    """
    An audio Track which is mixture of several sources
    and provides several targets

    Attributes
    ----------
    name : str
        Track name

    path : str
        Absolute path of mixture audio file

    stem_id : int
        If part of a stem file, the stem/substream ID is set here.

    subset : {'train', 'test'}
        belongs to subset

    targets : OrderedDict
        OrderedDict of mixted Targets for this Track

    sources : Dict
        Dict of ``Source`` objects for this ``Track``

    """
    def __init__(
        self,
        name,
        stem_id=None,
        track_artist=None,
        track_title=None,
        subset=None,
        path=None
    ):
        self.name = os.path.splitext(name)[0].split('.stem')[0]
        try:
            split_name = name.split(' - ')
            self.artist = split_name[0]
            self.title = split_name[1]
        except ValueError:
            self.artist = track_artist
            self.title = track_title

        self.path = path
        self.subset = subset
        self.stem_id = stem_id
        self.targets = None
        self.sources = None
        self._audio = None
        self._stems = None
        self._rate = None

    @property
    def stems(self):
        """array_like: [shape=(stems, num_samples, num_channels)]
        """

        # return cached audio it explicitly set bet setter
        if self._stems is not None:
            return self._stems
        # read from disk to save RAM otherwise
        else:
            if os.path.exists(self.path):
                S, rate = stempeg.read_stems(filename=self.path)
                self._rate = rate
                return S


    @property
    def audio(self):
        """array_like: [shape=(num_samples, num_channels)]
        """

        # return cached audio it explicitly set by setter
        if self._audio is not None:
            return self._audio
        # read from disk to save RAM otherwise
        else:
            if os.path.exists(self.path):
                if self.stem_id is not None:
                    audio, rate = stempeg.read_stems(
                        filename=self.path,
                        stem_id=self.stem_id
                    )
                else:
                    audio, rate = sf.read(self.path, always_2d=True)
                self._rate = rate
                return audio
            else:
                self._rate = None
                self._audio = None
                raise ValueError("Oops! %s cannot be loaded" % self.path)

    @property
    def rate(self):
        """int: sample rate in Hz
        """

        # load audio to set rate
        if self._rate is None:
            if os.path.exists(self.path):
                if self.stem_id is not None:
                    audio, rate = stempeg.read_stems(
                        filename=self.path, stem_id=self.stem_id
                    )
                else:
                    audio, rate = sf.read(self.path, always_2d=True)
                self._rate = rate
                return rate
            else:
                self._rate = None
                self._audio = None
                raise ValueError("Oops! %s cannot be loaded" % self.path)
        return self._rate

    @audio.setter
    def audio(self, array):
        self._audio = array

    @rate.setter
    def rate(self, rate):
        self._rate = rate

    def __repr__(self):
        return "\n%s" % (self.name)
