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
from audio_classes import Track, Source, Target
import multiprocessing
import signal


class DB(object):
    """
    The DSD100 DB Object

    Parameters
    ----------
    root_dir : str, optional
        DSD100 Root path. If set to `None` it will be read
        from the `DSD100_PATH` environment variable

    subsets : str or list, optional
        select a _DSD100_ subset `Dev` or `Test` (defaults to both)

    setup_file : str, optional
        _DSD100_ Setup file in yaml format. Default is `setup.yaml`

    user_estimates_dir : str, optional
        path to the user provided estimates. Directory will be
        created if it does not exist

    evaluation : str, {None, 'bss_eval', 'mir_eval'}
        Setup evaluation module and starts matlab if bsseval is enabled

    Attributes
    ----------
    setup_file : str
        path to yaml file. default: `setup.yaml`
    root_dir : str
        DSD100 Root path. Default is `DSD100_PATH` env
    user_estimates_dir : str
        path to the user provided estimates.
    evaluation : bool
        Setup evaluation module
    mixtures_dir : str
        path to Mixture directory
    sources_dir : str
        path to Sources directory
    sources_names : list[str]
        list of names of sources
    targets_names : list[str]
        list of names of targets
    evaluator : BSSeval
        evaluator used for evaluation of estimates
    setup : Dict
        loaded yaml configuration

    Methods
    -------
    load_dsd_tracks()
        Iterates through the DSD100 folder structure and
        returns ``Track`` objects
    test(user_function)
        Test the DSD100 processing
    evaluate()
        Run the evaluation
    run(user_function=None, save=True, evaluate=False)
        Run the DSD100 processing, saving the estimates
        and optionally evaluate them

    """
    def __init__(
        self,
        root_dir=None,
        setup_file='setup.yaml',
        user_estimates_dir=None,
        evaluation=None
    ):
        if root_dir is None:
            if "DSD100_PATH" in os.environ:
                self.root_dir = os.environ["DSD100_PATH"]
            else:
                raise RuntimeError("Path to DSD100 root directory isn't set")
        else:
            self.root_dir = root_dir

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

        if evaluation is not None:
            self.evaluator = evaluate.BSSeval(evaluation)

    def load_dsd_tracks(self, subsets=['Dev', 'Test']):
        """Parses the DSD100 folder structure and yields `Track` objects

        Parameters
        ==========
        subsets : list[str], optional
            select a _DSD100_ subset `Dev` or `Test`. Defaults to both

        Returns
        -------
        list[Track]
            return a list of ``Track`` Objects
        """
        # parse all the mixtures
        tracks = []
        if op.isdir(self.mixtures_dir):
            for subset in subsets:
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

                        tracks.append(track)
            return tracks
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
        """Test the DSD100 processing

        Parameters
        ----------
        user_function : callable, optional
            function which separates the mixture into estimates. If no function
            is provided (default in `None`) estimates are loaded from disk when
            `evaluate is True`.

        Raises
        ------
        TypeError
            If the provided function handle is not callable.

        ValueError
            If the output is not compliant to the bsseval methods

        See Also
        --------
        run : Process the DSD100
        """
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
        """Run the DSD100 evaluation

        shortcut to ``run(user_function=None, save=False, evaluate=True)``
        """
        return self.run(user_function=None, save=False, evaluate=True)

    def run(
        self,
        user_function=None,
        save=True,
        evaluate=False,
        subsets=['Dev', 'Test'],
        parallel=True
    ):
        """Run the DSD100 processing

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
        subsets : list[str], optional
            select a _DSD100_ subset `Dev` or `Test`. Defaults to both

        Raises
        ------
        RuntimeError
            If the provided function handle is not callable.

        See Also
        --------
        test : Test the user provided function
        """

        if user_function is None and save:
            raise RuntimeError("Provide a function use the save feature!")

        if isinstance(subsets, basestring):
            subsets = [subsets]
        else:
            subsets = subsets

        widgets = [FormatLabel('Track %(value)d/%(max_value)d'), Bar(), ETA()]
        progress = ProgressBar(
            widgets=widgets
        )

        def init_worker():
            signal.signal(signal.SIGINT, signal.SIG_IGN)

        if user_function is None:
            # load estimates from disk
            for track in progress(self.load_dsd_tracks(subsets=subsets)):
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
        else:
            if parallel:
                pool = multiprocessing.Pool(4, init_worker)
                for estimate in pool.imap(
                    func=user_function,
                    iterable=self.load_dsd_tracks(subsets=subsets)
                ):
                    print estimate

                pool.close()
                pool.join()

            else:
                for track in progress(self.load_dsd_tracks(subsets=subsets)):
                    user_results = user_function(track)
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
        import time
        time.sleep(5)
        estimates = {
            'vocals': dsd_track.audio,
            'accompaniment': dsd_track.audio
        }
        return estimates

    dsd = DB(
        root_dir=args.dsd_folder,
    )

    # Test my_function
    dsd.test(my_function)

    # Run my_function and save the results to disk
    dsd.run(my_function)
