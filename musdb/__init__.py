from .audio_classes import Track, Source, Target
from os import path as op
import multiprocessing
import soundfile as sf
import urllib.request
from .img import MAG
import collections
import numpy as np
import signal
import functools
import zipfile
import yaml
import tqdm
import musdb
import errno
import os

__version__ = "0.3.0"


class DB(object):
    """
    The musdb DB Object

    Parameters
    ----------
    root_dir : str, optional
        musdb Root path. If set to `None` it will be read
        from the `MUSDB_PATH` environment variable

    subsets : str or list, optional
        select a _musdb_ subset `train` or `test` (defaults to both)

    is_wav : boolean, optional
        expect subfolder with wav files for each source instead stems,
        defaults to `False`

    download : boolean, optional
        download sample version of MUSDB18 which includes 7s excerpts,
        defaults to `False`

    Attributes
    ----------
    setup_file : str
        path to yaml file. default: `setup.yaml`
    root_dir : str
        musdb Root path. Default is `MUSDB_PATH`. In combination with
        `download`, this path will set the download destination and set to
        '~/musdb/' by default.
    sources_dir : str
        path to Sources directory
    sources_names : list[str]
        list of names of sources
    targets_names : list[str]
        list of names of targets
    setup : Dict
        loaded yaml configuration

    Methods
    -------
    load_mus_tracks()
        Iterates through the musdb folder structure and
        returns ``Track`` objects
    test(user_function)
        Test the musdb processing
    run(user_function=None, estimates_dir=None)
        Run the musdb processing and saving the estimates

    """
    def __init__(
        self,
        root_dir=None,
        setup_file=None,
        is_wav=False,
        download=False,
        subsets=None
    ):
        if root_dir is None:
            if download:
                self.root_dir = os.path.expanduser("~/MUSDB18/MUSDB18-7")
            else:
                if "MUSDB_PATH" in os.environ:
                    self.root_dir = os.environ["MUSDB_PATH"]
                else:
                    raise RuntimeError("Variable `MUSDB_PATH` has not been set.")
        else:
            self.root_dir = root_dir

        if download:
            self.url = "https://s3.eu-west-3.amazonaws.com/sisec18.unmix.app/dataset/MUSDB18-7-STEMS.zip"
            self.download()
            if not self._check_exists():
                raise RuntimeError('Dataset not found.' +
                                   'You can use download=True to download a sample version of the dataset')

        if setup_file is not None:
            setup_path = op.join(self.root_dir, setup_file)
        else:
            setup_path = os.path.join(
                musdb.__path__[0], 'configs', 'mus.yaml'
            )

        with open(setup_path, 'r') as f:
            self.setup = yaml.load(f)

        self.sources_names = list(self.setup['sources'].keys())
        self.targets_names = list(self.setup['targets'].keys())
        self.is_wav = is_wav
        self.load_mus_tracks(subsets=subsets)

        
    def __getitem__(self, index):
        return self.tracks[index]

    def __len__(self):
        return len(self.tracks)

    def get_track_by_name(self, name):
        pass

    def load_mus_tracks(self, subsets=None):
        """Parses the musdb folder structure, returns list of `Track` objects

        Parameters
        ==========
        subsets : list[str], optional
            select a _musdb_ subset `train` or `test`.
            Default `None` loads both sets.

        Returns
        -------
        list[Track]
            return a list of ``Track`` Objects
        """

        if subsets is not None:
            if isinstance(subsets, str):
                subsets = [subsets]
            else:
                subsets = subsets
        else:
            subsets = ['train', 'test']

        tracks = []
        for subset in subsets:

            subset_folder = op.join(self.root_dir, subset)

            for _, folders, files in os.walk(subset_folder):
                if self.is_wav:
                    # parse pcm tracks
                    for track_name in sorted(folders):

                        track_folder = op.join(subset_folder, track_name)
                        # create new mus track
                        track = Track(
                            name=track_name,
                            path=op.join(
                                track_folder,
                                self.setup['mixture']
                            ),
                            subset=subset,
                            stem_id=self.setup['stem_ids']['mixture'],
                            is_wav=self.is_wav
                        )

                        # add sources to track
                        sources = {}
                        for src, source_file in list(
                            self.setup['sources'].items()
                        ):
                            # create source object
                            abs_path = op.join(
                                track_folder,
                                source_file
                            )
                            if os.path.exists(abs_path):
                                sources[src] = Source(
                                    name=src,
                                    path=abs_path,
                                    stem_id=self.setup['stem_ids'][src],
                                    is_wav=self.is_wav
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
                else:
                    # parse stem files
                    for track_name in sorted(files):
                        if 'stem' in track_name and track_name.endswith(
                            '.mp4'
                        ):
                            # create new mus track
                            track = Track(
                                name=track_name,
                                path=op.join(subset_folder, track_name),
                                subset=subset,
                                stem_id=self.setup['stem_ids']['mixture'],
                                is_wav=self.is_wav
                            )
                            # add sources to track
                            sources = {}
                            for src, source_file in list(
                                self.setup['sources'].items()
                            ):
                                # create source object
                                abs_path = op.join(
                                    subset_folder,
                                    track_name
                                )
                                if os.path.exists(abs_path):
                                    sources[src] = Source(
                                        name=src,
                                        path=abs_path,
                                        stem_id=self.setup['stem_ids'][src],
                                        is_wav=self.is_wav
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
                                        track.sources[source].gain = float(
                                            gain
                                        )
                                        # add tracks to components
                                        target_sources.append(sources[source])
                                # add sources to target
                                if target_sources:
                                    targets[name] = Target(
                                        sources=target_sources
                                    )
                            # add targets to track
                            track.targets = targets

                            # add track to list of tracks
                            tracks.append(track)

        self.tracks = tracks

    def _save_estimates(
        self,
        user_estimates,
        track,
        estimates_dir,
        write_stems=False
    ):
        track_estimate_dir = op.join(
            estimates_dir, track.subset, track.name
        )
        if not os.path.exists(track_estimate_dir):
            os.makedirs(track_estimate_dir)

        # write out tracks to disk
        for target, estimate in list(user_estimates.items()):
            target_path = op.join(track_estimate_dir, target + '.wav')
            sf.write(target_path, estimate, track.rate)
        pass

    def test(self, user_function):
        """Test the musdb user_function output

        Parameters
        ----------
        user_function : callable, optional
            function which separates the mixture into estimates.

        Raises
        ------
        TypeError
            If the provided function handle is not callable.

        ValueError
            If the output is not compliant to the bsseval methods

        See Also
        --------
        run : Process the musdb
        """
        if not hasattr(user_function, '__call__'):
            raise TypeError("Please provide a function.")

        test_track = Track(name="test - test")
        signal = np.random.random((66000, 2))
        test_track.audio = signal
        test_track.rate = 44100
        test_track.subset = 'test'

        sources = {}
        for src, _ in list(
            self.setup['sources'].items()
        ):
            source = Source(name=src)
            source.audio = signal
            source.rate = test_track.rate
            sources[src] = source
        test_track.sources = sources

        # add targets to track
        targets = collections.OrderedDict()
        for name, target_srcs in list(
            self.setup['targets'].items()
        ):
            # add a list of target sources
            target_sources = []
            for source, gain in list(target_srcs.items()):
                if source in list(test_track.sources.keys()):
                    # add gain to source tracks
                    test_track.sources[source].gain = float(gain)
                    # add tracks to components
                    target_sources.append(sources[source])
            # add sources to target
            if target_sources:
                targets[name] = Target(sources=target_sources)

        # add targets to track
        test_track.targets = targets

        user_results = user_function(test_track)

        if isinstance(user_results, dict):
            for target, audio in list(user_results.items()):
                if target not in self.targets_names:
                    raise ValueError("Target '%s' not supported!" % target)

                d = audio.dtype
                if not (
                    np.issubdtype(d, np.float32) or
                    np.issubdtype(d, np.float64)
                ):
                    raise ValueError(
                        "Estimate is not of type numpy.float32 or float64"
                    )

                if audio.shape != signal.shape:
                    raise ValueError(
                        "Shape of estimate does not match input shape"
                    )

        else:
            raise ValueError("output needs to be a dict")

        return True

    def _process_function(self, track, user_function, estimates_dir):
        user_results = user_function(track)
        if estimates_dir is not None:
            if user_results is None:
                raise ValueError("Processing did not yield any results, " +
                                 "please set estimate_dir to None")
            else:
                self._save_estimates(user_results, track, estimates_dir)

    def run(
        self,
        user_function,
        estimates_dir=None,
        subsets=None,
        parallel=False,
        cpus=4,
        progress=True
    ):
        """Run the musdb processing

        Parameters
        ----------
        user_function : callable
            function which separates the mixture into estimates.
        tracks : list[Track], optional
            select a list of tracks
        subsets : list[str], optional
            select a _musdb_ subset `train` or `test`. Defaults to both
        estimates_dir : str, optional
            path to the user provided estimates. Directory will be
            created if it does not exist. Default is `none` which means that
            the results are not saved.
        parallel: bool, optional
            activate multiprocessing
        cpus: int, optional
            set number of cores if `parallel` mode is active, defaults to 4

        Raises
        ------
        RuntimeError
            If the provided function handle is not callable.

        Returns
        -------
        results : Dict
            returns the return value of the user_function

        See Also
        --------
        test : Test the user provided function
        """

        if user_function is None:
            raise RuntimeError("Provide a function!")

        results = False
        if parallel:
            pool = multiprocessing.Pool(cpus, initializer=init_worker)
            results = list(
                tqdm.tqdm(
                    pool.imap_unordered(
                        func=functools.partial(
                            process_function_alias,
                            self,
                            user_function=user_function,
                            estimates_dir=estimates_dir
                        ),
                        iterable=self.tracks,
                        chunksize=1
                    ),
                    total=len(self),
                    disable=not progress
                )
            )

            pool.close()
            pool.join()

        else:
            results = list(
                tqdm.tqdm(
                    map(
                        lambda x: self._process_function(
                            x,
                            user_function,
                            estimates_dir
                        ),
                        self.tracks
                    ),
                    total=len(self),
                    disable=not progress
                )
            )
        return results

    def _check_exists(self):
        return os.path.exists(os.path.join(self.root_dir, "train"))

    def download(self):
        """Download the MUSDB Sample data"""
        if self._check_exists():
            return

        # download files
        try:
            os.makedirs(os.path.join(self.root_dir))
        except OSError as e:
            if e.errno == errno.EEXIST:
                pass
            else:
                raise

        print('Downloading MUSDB Sample Dataset to %s...' % self.root_dir)
        data = urllib.request.urlopen(self.url)
        filename = 'MUSDB18-7-STEMS.zip'
        file_path = os.path.join(self.root_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(data.read())
        zip_ref = zipfile.ZipFile(file_path, 'r')
        zip_ref.extractall(os.path.join(self.root_dir))
        zip_ref.close()
        os.unlink(file_path)

        print('Done!')

def process_function_alias(obj, *args, **kwargs):
    return obj._process_function(*args, **kwargs)


def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)
