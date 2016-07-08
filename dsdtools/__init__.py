from __future__ import print_function
from .audio_classes import Track, Source, Target
from . import evaluate
from os import path as op
from six.moves import map
import multiprocessing
import soundfile as sf
import collections
import numpy as np
import functools
import signal
import yaml
import glob
import tqdm
import os
import dsdtools


class DB(object):
    """
    The dsdtools DB Object

    Parameters
    ----------
    root_dir : str, optional
        dsdtools Root path. If set to `None` it will be read
        from the `DSD_PATH` environment variable

    subsets : str or list, optional
        select a _dsdtools_ subset `Dev` or `Test` (defaults to both)

    setup_file : str, optional
        _dsdtools_ Setup file in yaml format. Default is provided `dsd100.yaml`

    evaluation : str, {None, 'bss_eval', 'mir_eval'}
        Setup evaluation module and starts matlab if bsseval is enabled

    valid_ids : list[int] or int, optional
        select single or multiple _dsdtools_ items by ID that will be used
        for validation data (ie not included in the `Dev` set)

    Attributes
    ----------
    setup_file : str
        path to yaml file. default: `setup.yaml`
    root_dir : str
        dsdtools Root path. Default is `DSD_PATH` env
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
        Iterates through the dsdtools folder structure and
        returns ``Track`` objects
    test(user_function)
        Test the dsdtools processing
    evaluate()
        Run the evaluation
    run(user_function=None, estimates_dir=None, evaluate=False)
        Run the dsdtools processing, saving the estimates
        and optionally evaluate them

    """
    def __init__(
        self,
        root_dir=None,
        setup_file=None,
        evaluation=None,
        valid_ids=None,
    ):
        if root_dir is None:
            if "DSD_PATH" in os.environ:
                self.root_dir = os.environ["DSD_PATH"]
            else:
                raise RuntimeError("Variable `DSD_PATH` has not been set.")
        else:
            self.root_dir = root_dir

        if setup_file is not None:
            setup_path = op.join(self.root_dir, setup_file)
        else:
            setup_path = os.path.join(
                dsdtools.__path__[0], 'configs', 'dsd100.yaml'
            )

        with open(setup_path, 'r') as f:
            self.setup = yaml.load(f)

        self.mixtures_dir = op.join(
            self.root_dir, "Mixtures"
        )
        self.sources_dir = op.join(
            self.root_dir, "Sources"
        )

        if valid_ids is not None:
            if not isinstance(valid_ids, collections.Sequence):
                valid_ids = [valid_ids]

        self.valid_ids = valid_ids

        self.sources_names = list(self.setup['sources'].keys())
        self.targets_names = list(self.setup['targets'].keys())

        if evaluation is not None:
            self.evaluator = evaluate.BSSeval(evaluation)

    def load_dsd_tracks(self, subsets=None, ids=None):
        """Parses the dsdtools folder structure and returns `Track` objects

        Parameters
        ==========
        subsets : list[str], optional
            select a _dsdtools_ subset `Dev` or `Test`. Defaults to both
        ids : list[int] or int, optional
            select single or multiple _dsdtools_ items by ID

        Returns
        -------
        list[Track]
            return a list of ``Track`` Objects
        """
        # parse all the mixtures
        if ids is not None:
            if not isinstance(ids, collections.Sequence):
                ids = [ids]

        if subsets is not None:
            if isinstance(subsets, str):
                subsets = [subsets]
            else:
                subsets = subsets
                if all(x in ['Valid', 'Dev'] for x in subsets):
                    raise ValueError(
                        "Cannot load Valid and Dev at the same time"
                    )
        else:
            subsets = ['Dev', 'Test']

        tracks = []
        if op.isdir(self.mixtures_dir):
            for subset in subsets:

                # For validation use Dev set and filter by ids later
                if subset == 'Valid':
                    subset_folder = op.join(self.mixtures_dir, 'Dev')
                else:
                    subset_folder = op.join(self.mixtures_dir, subset)

                for _, track_folders, _ in os.walk(subset_folder):
                    for track_filename in track_folders:

                        # create new dsd Track
                        track = Track(
                            filename=track_filename,
                            path=op.join(
                                op.join(subset_folder, track_filename),
                                self.setup['mix']
                            ),
                            subset=subset
                        )

                        # add sources to track
                        sources = {}
                        for src, rel_path in list(
                            self.setup['sources'].items()
                        ):
                            # create source object
                            abs_path = op.join(
                                self.sources_dir,
                                subset,
                                track_filename,
                                rel_path
                            )
                            if os.path.exists(abs_path):
                                sources[src] = Source(
                                    name=src,
                                    path=abs_path
                                )
                        track.sources = sources

                        # add targets to track
                        targets = collections.OrderedDict()
                        for name, target_srcs in list(
                            self.setup['targets'].items()
                        ):
                            # add a list of target sources

                            target_sources = []
                            for source, gain in list(target_srcs.items()):
                                if source in list(track.sources.keys()):
                                    # add gain to source tracks
                                    track.sources[source].gain = float(gain)
                                    # add tracks to components
                                    target_sources.append(sources[source])
                            # add sources to target
                            if target_sources:
                                targets[name] = Target(sources=target_sources)
                        # add targets to track
                        track.targets = targets

                        # add track to list of tracks
                        tracks.append(track)

                # Filter tracks by valid_ids
                if self.valid_ids is not None:
                    if subset == 'Dev':
                        tracks = [t for t in tracks
                                  if t.id not in self.valid_ids]
                    if subset == 'Valid':
                        tracks = [t for t in tracks if t.id in self.valid_ids]

            if ids is not None:
                return [t for t in tracks if t.id in ids]
            else:
                return tracks

    def _save_estimates(self, user_estimates, track, estimates_dir):
        track_estimate_dir = op.join(
            estimates_dir, track.subset, track.filename
        )
        if not os.path.exists(track_estimate_dir):
            os.makedirs(track_estimate_dir)

        # write out tracks to disk
        for target, estimate in list(user_estimates.items()):
            target_path = op.join(track_estimate_dir, target + '.wav')
            sf.write(target_path, estimate, track.rate)
        pass

    def _evaluate_estimates(self, user_estimates, track):
        audio_estimates = []
        audio_reference = []
        # make sure to always build the list in the same order
        # therefore track.targets is an OrderedDict
        labels_references = []  # save the list of targets to be evaluated
        for target in list(track.targets.keys()):
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

        if audio_estimates and audio_reference:
            audio_estimates = np.array(audio_estimates)
            audio_reference = np.array(audio_reference)
            if audio_estimates.shape == audio_reference.shape:
                self.evaluator.evaluate(
                    audio_estimates, audio_reference, track.rate
                )

    def test(self, user_function):
        """Test the dsdtools processing

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
        run : Process the dsdtools
        """
        if not hasattr(user_function, '__call__'):
            raise TypeError("Please provide a function.")

        test_track = Track(filename="test")
        signal = np.random.random((66000, 2))
        test_track.audio = signal
        test_track.rate = 44100

        user_results = user_function(test_track)

        if isinstance(user_results, dict):
            for target, audio in list(user_results.items()):
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

        return True

    def evaluate(
        self, user_function=None, estimates_dir=None, *args, **kwargs
    ):
        """Run the dsdtools evaluation

        shortcut to
        ``run(
            user_function=None,
            estimates_dir=estimates_dir,
            evaluate=True
        )``
        """
        return self.run(
            user_function=user_function,
            estimates_dir=estimates_dir,
            evaluate=True,
            *args, **kwargs
        )

    def _process_function(self, track, user_function, estimates_dir, evaluate):
        # load estimates from disk instead of processing
        if user_function is None:
            track_estimate_dir = op.join(
                estimates_dir,
                track.subset,
                track.filename
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
            # call the user provided function
            user_results = user_function(track)
        if estimates_dir and not evaluate and user_function is not None:
            self._save_estimates(user_results, track, estimates_dir)
        if evaluate:
            self._evaluate_estimates(user_results, track)

    def run(
        self,
        user_function=None,
        estimates_dir=None,
        evaluate=False,
        subsets=None,
        ids=None,
        parallel=False,
        cpus=4
    ):
        """Run the dsdtools processing

        Parameters
        ----------
        user_function : callable, optional
            function which separates the mixture into estimates. If no function
            is provided (default in `None`) estimates are loaded from disk when
            `evaluate is True`.
        estimates_dir : str, optional
            path to the user provided estimates. Directory will be
            created if it does not exist. Default is `none` which means that
            the results are not saved.
        evaluate : bool, optional
            evaluate the estimates by using. Default is False
        subsets : list[str], optional
            select a _dsdtools_ subset `Dev` or `Test`. Defaults to both
        ids : list[int] or int, optional
            select single or multiple _dsdtools_ items by ID
        parallel: bool, optional
            activate multiprocessing
        cpus: int, optional
            set number of cores if `parallel` mode is active, defaults to 4

        Raises
        ------
        RuntimeError
            If the provided function handle is not callable.

        See Also
        --------
        test : Test the user provided function
        """

        if user_function is None and estimates_dir and evaluate is None:
            raise RuntimeError("Provide a function or use evaluate feature!")

        try:
            ids = int(os.environ['DSD_ID'])
        except KeyError:
            pass

        # list of tracks to be processed
        tracks = self.load_dsd_tracks(subsets=subsets, ids=ids)

        success = False
        if parallel:
            pool = multiprocessing.Pool(cpus, initializer=init_worker)
            success = list(
                tqdm.tqdm(
                    pool.imap_unordered(
                        func=functools.partial(
                            process_function_alias,
                            self,
                            user_function=user_function,
                            estimates_dir=estimates_dir,
                            evaluate=evaluate
                        ),
                        iterable=tracks,
                        chunksize=1
                    ),
                    total=len(tracks)
                )
            )

            pool.close()
            pool.join()

        else:
            success = list(
                tqdm.tqdm(
                    map(
                        lambda x: self._process_function(
                            x,
                            user_function,
                            estimates_dir,
                            evaluate
                        ),
                        tracks
                    ),
                    total=len(tracks)
                )
            )
        return success


def process_function_alias(obj, *args, **kwargs):
    return obj._process_function(*args, **kwargs)


def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)
