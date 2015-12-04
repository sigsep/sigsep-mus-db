import argparse
import numpy as np
from os import path as op
import os
import soundfile as sf
import yaml
from progressbar import ProgressBar, FormatLabel, Bar, ETA


class SDSSource(object):
    def __init__(self, name=None, path=None):
        self.name = name
        self.path = path
        self.gain = 1.0
        self.__audio = None
        self.__rate = None

    @property
    def audio(self):
        if self.__rate is None and self.__audio is None:
            self.__check_and_read()
        return self.__audio

    @property
    def rate(self):
        if self.__rate is None and self.__audio is None:
            self.__check_and_read()
        return self.__rate

    def __check_and_read(self):
        if os.path.exists(self.path):
            audio, rate = sf.read(self.path)
            self.__rate = rate
            self.__audio = audio
        else:
            print "Oops! %s cannot be loaded" % self.path
            self.__rate = None
            self.__audio = None

    def __repr__(self):
        return self.path


class SDSTarget():
    def __init__(self, sources):
        self.sources = sources
        self.__audio = None

    @property
    def audio(self):
        if self.__audio is None:
            mix_list = []*len(self.sources)
            for source, track in self.sources.iteritems():
                if track.audio is not None:
                    mix_list.append(
                        np.array(track.gain) / len(self.sources) * track.audio
                    )
            self.__audio = np.sum(np.array(mix_list), axis=0)
        return self.__audio

    def __repr__(self):
        parts = []
        for key, val in self.sources.items():
            parts.append(str(key))
        return '+'.join(parts)


class SDSTrack(object):
    def __init__(self, name, path=None):
        self.name = name
        self.path = path
        self.targets = None
        self.sources = None
        self.__audio = None
        self.__rate = None

    @property
    def audio(self):
        if self.__rate is None and self.__audio is None:
            self.__check_and_read()
        return self.__audio

    @property
    def rate(self):
        if self.__rate is None and self.__audio is None:
            self.__check_and_read()
        return self.__rate

    def __check_and_read(self):
        if os.path.exists(self.path):
            audio, rate = sf.read(self.path)
            self.__rate = rate
            self.__audio = audio
        else:
            print "Oops!  File cannot be loaded"
            self.__rate = None
            self.__audio = None

    def __repr__(self):
        return "%s (%s)" % (self.name, self.path)


class pySDS(object):
    def __init__(
        self,
        root_dir=None,
        subsets=['Dev', 'Test'],
        setup_file='setup.yaml'
    ):

        if root_dir is None:
            if "SDS100_PATH" in os.environ:
                self.root_dir = os.environ["SDS100_PATH"]
            else:
                raise RuntimeError("Path to SDS100 root directory isn't set")
        else:
            self.root_dir = root_dir

        if isinstance(subsets, basestring):
            self.subsets = [subsets]
        else:
            self.subsets = subsets

        with open(op.join(self.root_dir, setup_file), 'r') as f:
            self.setup = yaml.load(f)

        self.mixtures_folder = op.join(self.root_dir, "Mixtures")
        self.sources_folder = op.join(self.root_dir, "Sources")
        self.sources_names = self.setup['sources'].keys()
        self.targets_names = self.setup['targets'].keys()

    def __sds_tracks(self):
        # parse all the mixtures
        if op.isdir(self.mixtures_folder):
            for subset in self.subsets:
                subset_folder = op.join(self.mixtures_folder, subset)
                for _, track_folders, _ in os.walk(subset_folder):
                    for track_name in track_folders:

                        # create new SDS Track
                        track = SDSTrack(
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
                            sources[src] = SDSSource(
                                name=src,
                                path=op.join(
                                    self.sources_folder,
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
                            targets[name] = SDSTarget(sources=srcs)

                        track.targets = targets

                        yield track
        else:
            print "%s not exists." % op.join("Estimates", args.mds_folder)

    def _save_estimates(self):
        pass

    def test(self, user_function):
        if not hasattr(user_function, '__call__'):
            raise TypeError("Please provide a callable function")

        test_track = SDSTrack(name="test")
        signal = np.random.random((48213, 2))
        test_track.__audio = signal
        test_track.__rate = 44100

        user_results = user_function(test_track)

        if isinstance(user_results, dict):
            for target, estimate in user_results.items():
                if target not in self.targets_names:
                    raise ValueError("Target '%s' not supported!" % target)
        else:
            raise ValueError("output needs ot be a dictionary")

        print "Test passed"
        return True

    def run(self, user_function):

        widgets = [FormatLabel('Track %(value)d '), Bar(), ETA()]
        progress = ProgressBar(widgets=widgets)

        for track in progress(self.__sds_tracks()):
            user_results = user_function(track)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Parse SISEC dataset')

    parser.add_argument(
        'sds_folder',
        nargs='?',
        default=None,
        type=str,
        help='SDS 100 Folder'
    )

    args = parser.parse_args()

    sds = pySDS(root_dir=args.sds_folder)

    def my_function(sds_track):
        estimates = {
            'basss': sds_track.path,
            'accompaniment': sds_track.name
        }
        return estimates

    sds.test(my_function)
    sds.run(my_function)
