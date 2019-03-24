from .audio_classes import MultiTrack, Source, Target
from os import path as op
import multiprocessing
import soundfile as sf
import urllib.request
import collections
import numpy as np
import signal
import functools
import zipfile
import yaml
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

    subsets : list[str], optional
        select a _musdb_ subset `train` or `test`.
        Default `None` loads both sets.
    
    dur : float, optional
        set the read duration of the tracks, defaults to `None` (all)

    random_start : boolean, optional
        selects a random start/seek position of the file. Works together with `dur not None`

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
            self.setup = yaml.safe_load(f)

        self.sources_names = list(self.setup['sources'].keys())
        self.targets_names = list(self.setup['targets'].keys())
        self.is_wav = is_wav
        self.load_mus_tracks(subsets=subsets)

    def __getitem__(self, index):
        return self.tracks[index]

    def __len__(self):
        return len(self.tracks)

    def get_tracks_by_names(self, track_names):
        """Returns musdb track objects by track name

        Can be used to filter the musdb tracks for 
        a validation subset by trackname

        Parameters
        == == == == ==
        track_names : list[str], optional
            select tracks by a given `str` or list of tracknames

        Returns
        -------
        list[Track]
            return a list of ``Track`` Objects
        """
        if isinstance(names, str):
            names = [names]
        return [t for t in self.tracks if t.name in names]

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
                    # parse pcm tracks and sort by name
                    for track_name in sorted(folders):

                        track_folder = op.join(subset_folder, track_name)
                        # create new mus track
                        track = MultiTrack(
                            name=track_name,
                            path=op.join(
                                track_folder,
                                self.setup['mixture']
                            ),
                            subset=subset,
                            is_wav=self.is_wav,
                            stem_id=self.setup['stem_ids']['mixture']
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
                                    track,
                                    name=src,
                                    path=abs_path,
                                    stem_id=self.setup['stem_ids'][src],
                                )
                        track.sources = sources
                        track.targets = self.create_targets(track)

                        # add track to list of tracks
                        tracks.append(track)
                else:
                    # parse stem files
                    for track_name in sorted(files):
                        if 'stem' in track_name and track_name.endswith(
                            '.mp4'
                        ):
                            # create new mus track
                            track = MultiTrack(
                                name=track_name,
                                path=op.join(subset_folder, track_name),
                                subset=subset,
                                stem_id=self.setup['stem_ids']['mixture'],
                                is_wav=self.is_wav,
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
                                        track,
                                        name=src,
                                        path=abs_path,
                                        stem_id=self.setup['stem_ids'][src],
                                    )
                            track.sources = sources

                            # add targets to track
                            track.targets = self.create_targets(track)
                            tracks.append(track)

        self.tracks = tracks

    def create_targets(self, track):
        # add targets to track
        targets=collections.OrderedDict()
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
                    target_sources.append(track.sources[source])
                    # add sources to target
            if target_sources:
                targets[name] = Target(track, sources=target_sources, name=name)

        return targets

    def save_estimates(
        self,
        user_estimates,
        track,
        estimates_dir,
        write_stems=False
    ):
        """Writes `user_estimates` to disk while recreating the musdb file structure in that folder.

        Parameters
        ==========
        user_estimates : Dict[np.array]
            the target estimates.
        track : Track,
            musdb track object
        estimates_dir : str,
            output folder name where to save the estimates.
        """
        track_estimate_dir = op.join(
            estimates_dir, track.subset, track.name
        )
        if not os.path.exists(track_estimate_dir):
            os.makedirs(track_estimate_dir)

        # write out tracks to disk
        if write_stems:
            pass
            # to be implemented
        else:            
            for target, estimate in list(user_estimates.items()):
                target_path = op.join(track_estimate_dir, target + '.wav')
                sf.write(target_path, estimate, track.rate)

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

        print('Downloading MUSDB 7s Sample Dataset to %s...' % self.root_dir)
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
