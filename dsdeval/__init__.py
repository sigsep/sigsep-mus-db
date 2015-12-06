import argparse
import numpy as np
from os import path as op
import os
import soundfile as sf
import yaml
from progressbar import ProgressBar, FormatLabel, Bar, ETA


class DSDSource(object):
    def __init__(self, name=None, path=None):
        self.name = name
        self.path = path
        self.gain = 1.0
        self._audio = None
        self._rate = None

    @property
    def audio(self):
        if self._rate is None and self._audio is None:
            self._check_and_read()
        return self._audio

    @property
    def rate(self):
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
            audio, rate = sf.read(self.path)
            self._rate = rate
            self._audio = audio
        else:
            print "Oops! %s cannot be loaded" % self.path
            self._rate = None
            self._audio = None

    def __repr__(self):
        return self.path


class DSDTarget():
    def __init__(self, sources):
        self.sources = sources
        self._audio = None

    @property
    def audio(self):
        if self._audio is None:
            mix_list = []*len(self.sources)
            for source, track in self.sources.iteritems():
                if track.audio is not None:
                    mix_list.append(
                        np.array(track.gain) / len(self.sources) * track.audio
                    )
            self._audio = np.sum(np.array(mix_list), axis=0)
        return self._audio

    def __repr__(self):
        parts = []
        for key, val in self.sources.items():
            parts.append(str(key))
        return '+'.join(parts)


class DSDTrack(object):
    def __init__(self, name, path=None):
        self.name = name
        self.path = path
        self.targets = None
        self.sources = None
        self._audio = None
        self._rate = None

    @property
    def audio(self):
        if self._rate is None and self._audio is None:
            self._check_and_read()
        return self._audio

    @property
    def rate(self):
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
            audio, rate = sf.read(self.path)
            self._rate = rate
            self._audio = audio
        else:
            print "Oops!  File cannot be loaded"
            self._rate = None
            self._audio = None

    def __repr__(self):
        return "%s (%s)" % (self.name, self.path)


class DSD100(object):
    def __init__(
        self,
        root_dir=None,
        subsets=['Dev', 'Test'],
        setup_file='setup.yaml',
        estimates_dir='Estimates'
    ):

        if root_dir is None:
            if "dsd100_PATH" in os.environ:
                self.root_dir = os.environ["dsd100_PATH"]
            else:
                raise RuntimeError("Path to dsd100 root directory isn't set")
        else:
            self.root_dir = root_dir

        if isinstance(subsets, basestring):
            self.subsets = [subsets]
        else:
            self.subsets = subsets

        with open(op.join(self.root_dir, setup_file), 'r') as f:
            self.setup = yaml.load(f)

        self.mixtures_dir = op.join(self.root_dir, "Mixtures")
        self.sources_dir = op.join(self.root_dir, "Sources")
        self.estimates_dir = op.join(self.root_dir, "Estimates")

        self.sources_names = self.setup['sources'].keys()
        self.targets_names = self.setup['targets'].keys()

    def _iter_dsd_tracks(self):
        # parse all the mixtures
        if op.isdir(self.mixtures_dir):
            for subset in self.subsets:
                subset_folder = op.join(self.mixtures_dir, subset)
                for _, track_folders, _ in os.walk(subset_folder):
                    for track_name in track_folders:

                        # create new dsd Track
                        track = DSDTrack(
                            name=track_name,
                            path=op.join(
                                op.join(subset_folder, track_name),
                                self.setup['mix']
                            ),
                        )

                        # add sources to track
                        sources = {}
                        for src, rel_path in self.setup['sources'].iteritems():
                            # create source object
                            sources[src] = DSDSource(
                                name=src,
                                path=op.join(
                                    self.sources_dir,
                                    subset,
                                    track_name,
                                    rel_path
                                )
                            )
                        track.sources = sources

                        # add targets to track
                        targets = {}
                        for name, srcs in self.setup['targets'].iteritems():
                            for source, gain in srcs.iteritems():
                                # add gain to source tracks
                                track.sources[source].gain = gain
                                # add tracks to components
                                srcs[source] = self.setup['sources'][source]
                            targets[name] = DSDTarget(sources=srcs)

                        track.targets = targets

                        yield track
        else:
            print "%s not exists." % op.join("Estimates", args.mds_folder)

    def _save_estimate(self, estimates, track):
        track_estimate_dir = op.join(self.estimates_dir, track.name)
        if not os.path.exists(track_estimate_dir):
            os.makedirs(track_estimate_dir)

        # write out tracks to disk
        for target, estimate in estimates.items():
            target_path = op.join(track_estimate_dir, target + '.wav')
            sf.write(target_path, estimate, track.rate)
        pass

    def test(self, user_function):
        if not hasattr(user_function, '__call__'):
            raise TypeError("Please provide a callable function")

        test_track = DSDTrack(name="test")
        signal = np.random.random((66000, 2))
        test_track.audio = signal
        test_track.rate = 44100

        user_results = user_function(test_track)

        if isinstance(user_results, dict):
            for target, estimate in user_results.items():
                if target not in self.targets_names:
                    raise ValueError("Target '%s' not supported!" % target)

                if estimate.shape != signal.shape:
                    raise ValueError(
                        "Shape of estimate does not match input shape"
                    )

        else:
            raise ValueError("output needs to wrapped in a dict")

        print "Test passed"
        return True

    def run(self, user_function, save=True):

        widgets = [FormatLabel('Track: '), Bar(), ETA()]
        progress = ProgressBar(widgets=widgets)

        for track in self._iter_dsd_tracks():
            user_results = user_function(track)
            if save:
                self._save_estimate(user_results, track)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Parse SISEC dataset')

    parser.add_argument(
        'dsd_folder',
        nargs='?',
        default=None,
        type=str,
        help='dsd 100 Folder'
    )

    args = parser.parse_args()

    dsd = DSD100(root_dir=args.dsd_folder)

    def my_function(dsd_track):
        estimates = {
            'bass': dsd_track.audio,
            'accompaniment': dsd_track.audio
        }
        return estimates

    if dsd.test(my_function):
        dsd.run(my_function)
