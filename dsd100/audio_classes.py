import os
import soundfile as sf
import numpy as np


class Source(object):
    """
    An audio Target which is a linear mixture of several sources

    Attributes
    ----------
    name : str
        Name of this source
    path : str
        Absolute path to audio file
    gain : float
        Mixing weight for this source
    """
    def __init__(self, name=None, path=None):
        self.name = name
        self.path = path
        self.gain = 1.0
        self._audio = None
        self._rate = None

    @property
    def audio(self):
        """array_like: [shape=(num_samples, num_channels)]
        """

        # return cached audio it explicitly set bet setter
        if self._audio is not None:
            return self._audio
        # read from disk to save RAM otherwise
        else:
            if os.path.exists(self.path):
                audio, rate = sf.read(self.path, always_2d=True)
                self._rate = rate
                return audio
            else:
                print "Oops! %s cannot be loaded" % self.path
                self._rate = None
                self._audio = None

    @property
    def rate(self):
        """int: sample rate in Hz
        """

        # load audio to set rate
        if self._rate is None:
            self.audio()
        return self._rate

    @audio.setter
    def audio(self, array):
        self._audio = array

    @rate.setter
    def rate(self, rate):
        self._rate = rate

    def __repr__(self):
        return self.path


# Target Track from DSD100 DB mixed from several DSDSource Tracks
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
            if source.audio is not None:
                mix_list.append(
                    source.gain * source.audio
                )
        return np.sum(np.array(mix_list), axis=0)

    def __repr__(self):
        parts = []
        for source in self.sources:
            parts.append(source.name)
        return '+'.join(parts)


# DSD100 Track which has many targets and sources
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

    subset : {'Test', 'Dev'}
        belongs to subset

    targets : OrderedDict
        OrderedDict of mixted Targets for this Track

    sources : Dict
        Dict of ``Source`` objects for this ``Track``

    """
    def __init__(self, name, subset=None, path=None):
        self.name = name
        self.path = path
        self.subset = subset
        self.targets = None
        self.sources = None
        self._audio = None
        self._rate = None

    @property
    def audio(self):
        """array_like: [shape=(num_samples, num_channels)]
        """

        # return cached audio it explicitly set bet setter
        if self._audio is not None:
            return self._audio
        # read from disk to save RAM otherwise
        else:
            if os.path.exists(self.path):
                audio, rate = sf.read(self.path, always_2d=True)
                self._rate = rate
                return audio
            else:
                print "Oops! %s cannot be loaded" % self.path
                self._rate = None
                self._audio = None

    @property
    def rate(self):
        """int: sample rate in Hz
        """

        # load audio to set rate
        if self._rate is None:
            self.audio()
        return self._rate

    @audio.setter
    def audio(self, array):
        self._audio = array

    @rate.setter
    def rate(self, rate):
        self._rate = rate

    def __repr__(self):
        return "%s (%s)" % (self.name, self.path)
