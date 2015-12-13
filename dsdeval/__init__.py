import argparse
import numpy as np
from os import path as op
import os
import soundfile as sf
import yaml
import evaluate
import collections
import glob
from progressbar import ProgressBar, FormatLabel, Bar, ETA


# Source Track from DSD100 DB
class Source(object):
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
    def __init__(self, sources):
        self.sources = sources  # List of DSDSources
        self._audio = None
        self._rate = None

    @property
    def audio(self):
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
            audio, rate = sf.read(self.path, always_2d=True)
            self._rate = rate
            self._audio = audio
        else:
            print "Oops!  File cannot be loaded"
            self._rate = None
            self._audio = None

    def __repr__(self):
        return "%s (%s)" % (self.name, self.path)


# DSD100 DB Object which has many targets and sources
class DSD100(object):
    def __init__(
        self,
        root_dir=None,
        subsets=['Dev', 'Test'],
        setup_file='setup.yaml',
        user_estimates_dir=None,
        evaluation=False
    ):

        if root_dir is None:
            if "DSD100_PATH" in os.environ:
                self.root_dir = os.environ["DSD100_PATH"]
            else:
                raise RuntimeError("Path to DSD100 root directory isn't set")
        else:
            self.root_dir = root_dir

        if isinstance(subsets, basestring):
            self.subsets = [subsets]
        else:
            self.subsets = subsets

        with open(op.join(self.root_dir, setup_file), 'r') as f:
            self.setup = yaml.load(f)

        self.mixtures_dir = op.join(
            self.root_dir, "Mixtures"
        )
        self.sources_dir = op.join(
            self.root_dir, "Sources"
        )

        if user_estimates_dir is None:
            self.user_estimates_dir = op.join(
                self.root_dir, "Estimates"
            )
        else:
            self.user_estimates_dir = user_estimates_dir

        self.sources_names = self.setup['sources'].keys()
        self.targets_names = self.setup['targets'].keys()

        if evaluation:
            self.evaluator = evaluate.BSSeval("bsseval")

    # generator
    def _iter_dsd_tracks(self):
        """Parses the DSD100 folder structure

        Yields
        ------
        int
            Description of the anonymous integer return value.
        """
        # parse all the mixtures
        if op.isdir(self.mixtures_dir):
            for subset in self.subsets:
                subset_folder = op.join(self.mixtures_dir, subset)
                for _, track_folders, _ in os.walk(subset_folder):
                    for track_name in track_folders:

                        # create new dsd Track
                        track = Track(
                            name=track_name,
                            path=op.join(
                                op.join(subset_folder, track_name),
                                self.setup['mix']
                            ),
                            subset=subset
                        )

                        # add sources to track
                        sources = {}
                        for src, rel_path in self.setup['sources'].iteritems():
                            # create source object
                            sources[src] = Source(
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
                        targets = collections.OrderedDict()
                        for name, srcs in self.setup['targets'].iteritems():
                            # add a list of target sources
                            target_sources = []
                            for source, gain in srcs.iteritems():
                                # add gain to source tracks
                                track.sources[source].gain = float(gain)
                                # add tracks to components
                                target_sources.append(sources[source])
                            # add sources to target
                            targets[name] = Target(sources=target_sources)
                        # add targets to track
                        track.targets = targets

                        yield track
        else:
            print "%s not exists." % op.join("Estimates", args.mds_folder)

    def _save_estimates(self, user_estimates, track):
        track_estimate_dir = op.join(
            self.user_estimates_dir, track.subset, track.name
        )
        if not os.path.exists(track_estimate_dir):
            os.makedirs(track_estimate_dir)

        # write out tracks to disk
        for target, estimate in user_estimates.iteritems():
            target_path = op.join(track_estimate_dir, target + '.wav')
            sf.write(target_path, estimate, track.rate)
        pass

    def _evaluate_estimates(self, user_estimates, track):
        audio_estimates = []
        audio_reference = []
        # make sure to always build the list in the same order
        # therefore track.targets is an OrderedDict
        labels_references = []  # save the list of targets to be evaluated
        for target in track.targets.keys():
            try:
                # try to fetch the audio from the user_results of a given key
                estimate = user_estimates[target]
                # append this target name to the list of labels
                labels_references.append(target)
                # add the audio to the list of estimates
                audio_estimates.append(estimate)
                # add the audio to the list of references
                audio_reference.append(track.targets[target].audio)
            except KeyError:
                pass

        audio_estimates = np.array(audio_estimates)
        audio_reference = np.array(audio_reference)
        self.evaluator.evaluate(audio_estimates, audio_reference, track.rate)

    def test(self, user_function):
        if not hasattr(user_function, '__call__'):
            raise TypeError("Please provide a function.")

        test_track = Track(name="test")
        signal = np.random.random((66000, 2))
        test_track.audio = signal
        test_track.rate = 44100

        user_results = user_function(test_track)

        if isinstance(user_results, dict):
            for target, audio in user_results.iteritems():
                if target not in self.targets_names:
                    raise ValueError("Target '%s' not supported!" % target)

                d = audio.dtype
                if not np.issubdtype(d, float):
                    raise ValueError(
                        "Estimate is not of type numpy.float_"
                    )

                if audio.shape != signal.shape:
                    raise ValueError(
                        "Shape of estimate does not match input shape"
                    )

        else:
            raise ValueError("output needs to be a dict")

        print "Test passed"
        return True

    def evaluate(self):
        return self.run(user_function=None, save=False, evaluate=True)

    def run(self, user_function=None, save=True, evaluate=False):
        """Run the DSD100 evaluation

        Parameters
        ----------
        user_function : callable, optional
            function which separates the mixture into estimates. If no function
            is provided (default in `None`) estimates are loaded from disk when
            `evaluate is True`.
        save : bool, optional
            save the estimates to disk. Default is True.
        evaluate : bool, optional
            evaluate the estimates by using. Default is False

        Raises
        ------
        RuntimeError
            If the provided function handle is not callable.

        """

        if user_function is None and save:
            raise RuntimeError("Provide a function use the save feature!")

        widgets = [FormatLabel('Track %(value)d/%(max_value)d'), Bar(), ETA()]
        progress = ProgressBar(
            widgets=widgets,
            max_value=50*int(len(self.subsets))
        )

        for track in progress(self._iter_dsd_tracks()):
            if user_function is not None:
                user_results = user_function(track)
            else:
                # load estimates from disk
                track_estimate_dir = op.join(
                    self.user_estimates_dir,
                    track.subset,
                    track.name
                )
                user_results = {}
                for target_path in glob.glob(track_estimate_dir + '/*.wav'):
                    target_name = op.splitext(
                        os.path.basename(target_path)
                    )[0]
                    try:
                        target_audio, rate = sf.read(
                            target_path,
                            always_2d=True
                        )
                        user_results[target_name] = target_audio
                    except RuntimeError:
                        pass

            if save:
                self._save_estimates(user_results, track)
            if evaluate:
                self._evaluate_estimates(user_results, track)


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

    def my_function(dsd_track):
        estimates = {
            'vocals': dsd_track.audio,
            'accompaniment': dsd_track.audio
        }
        return estimates

    dsd = DSD100(
        root_dir=args.dsd_folder,
        user_estimates_dir='./my_estimates'
    )

    # Test my_function
    dsd.test(my_function)

    # Run my_function and save the results to disk
    dsd.run(my_function)
    dsd.run(my_function, save=True, evaluate=False)

    # Evaluate the results and save the estimates to disk
    dsd.run(my_function, save=True, evaluate=True)

    # Evaluate the results but do not save the estimates to disk
    dsd.run(my_function, save=False, evaluate=True)

    # Only pass tracks to my_function
    dsd.run(my_function, save=False, evaluate=False)

    # Just evaluate the user_estimates folder
    dsd.run(save=False, evaluate=True)
    # or simply
    dsd.evaluate()
