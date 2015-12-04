import argparse
import numpy as np
from os import path as op
import os
import soundfile as sf
import yaml


class SDSSource(object):
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


class SDSTarget():
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


class SDSTrack(object):
    def __init__(self, name, path):
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

    def _sds_tracks(self):
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
        pass

    def run(self, user_function):
        for track in self._sds_tracks():
            user_results = user_function(track)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Parse SISEC dataset')

    parser.add_argument('sds_folder', type=str, help='SDS 100 Folder')

    args = parser.parse_args()

    sds = pySDS()

    def my_function(sds_track):
        estimates = {
            'bass': sds_track.path,
            'accompaniment': sds_track.name
        }
        print sds_track.targets
        return estimates

    sds.run(my_function)
