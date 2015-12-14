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
        if self._rate is None and self._audio is None:
            self._check_and_read()
        return self._audio

    @property
    def rate(self):
        """int: sample rate in Hz
        """
        if self._rate is None and self._audio is None:
            self._check_and_read()
        return self._rate

    @audio.setter
    def audio(self, array):
        self._audio = array

    @rate.setter
    def rate(self, rate):
        self._rate = rate

    def _check_and_read(self):
        if os.path.exists(self.path):
            audio, rate = sf.read(self.path, always_2d=True)
            self._rate = rate
            self._audio = audio
        else:
            print "Oops! %s cannot be loaded" % self.path
            self._rate = None
            self._audio = None

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
        self._audio = None
        self._rate = None

    @property
    def audio(self):
        """array_like: [shape=(num_samples, num_channels)]
        """
        if self._audio is None:
            mix_list = []*len(self.sources)
            for source in self.sources:
                if source.audio is not None:
                    mix_list.append(
                        source.gain * source.audio
                    )
            self._audio = np.sum(np.array(mix_list), axis=0)
        return self._audio

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

    targets : list[Target]
        list of mixted Targets for this Track

    sources : list[Source]
        list of ``Source`` objects for this ``Track``

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
        if self._rate is None and self._audio is None:
            self._check_and_read()
        return self._audio

    @property
    def rate(self):
        """int: sample rate in Hz
        """
        if self._rate is None and self._audio is None:
            self._check_and_read()
        return self._rate

    @audio.setter
    def audio(self, array):
        self._audio = array

    @rate.setter
    def rate(self, rate):
        self._rate = rate

    def _check_and_read(self):
        if os.path.exists(self.path):
            audio, rate = sf.read(self.path, always_2d=True)
            self._rate = rate
            self._audio = audio
        else:
            print "Oops!  File cannot be loaded"
            self._rate = None
            self._audio = None

    def __repr__(self):
        return "%s (%s)" % (self.name, self.path)
