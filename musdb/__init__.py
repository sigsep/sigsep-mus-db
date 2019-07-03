from .audio_classes import MultiTrack, Source, Target
from os import path as op
import soundfile as sf
import urllib.request
import collections
import numpy as np
import functools
import zipfile
import yaml
import musdb
import errno
import os


class DB(object):
    """
    The musdb DB Object

    Parameters
    ----------
    root : str, optional
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
        Default `None` loads `['train', 'test']`

    split : str, optional
        when subset `train` is loaded, split selects the train/validation split.
        `split='train' loads the training split, `split='valid'` loads the validation
        split. `split=None` applies no splitting.

    Attributes
    ----------
    setup_file : str
        path to yaml file. default: `setup.yaml`
    root : str
        musdb Root path. Default is `MUSDB_PATH`. In combination with
        `download`, this path will set the download destination and set to
        '~/musdb/' by default.
    sources_dir : str
        path to Sources directory
    sources_names : list[str]
        list of names of available sources
    targets_names : list[str]
        list of names of available targets
    setup : Dict
        loaded yaml configuration

    Methods
    -------
    load_mus_tracks()
        Iterates through the musdb folder structure and
        returns ``Track`` objects

    """
    def __init__(
        self,
        root=None,
        setup_file=None,
        is_wav=False,
        download=False,
        subsets=['train', 'test'],
        split=None
    ):
        if root is None:
            if download:
                self.root = os.path.expanduser("~/MUSDB18/MUSDB18-7")
            else:
                if "MUSDB_PATH" in os.environ:
                    self.root = os.environ["MUSDB_PATH"]
                else:
                    raise RuntimeError("Variable `MUSDB_PATH` has not been set.")
        else:
            self.root = os.path.expanduser(root)

        if setup_file is not None:
            setup_path = op.join(self.root, setup_file)
        else:
            setup_path = os.path.join(
                musdb.__path__[0], 'configs', 'mus.yaml'
            )

        with open(setup_path, 'r') as f:
            self.setup = yaml.safe_load(f)

        if download:
            self.url = self.setup['sample-url']
            self.download()
            if not self._check_exists():
                raise RuntimeError('Dataset not found.' +
                                   'You can use download=True to download a sample version of the dataset')


        self.sources_names = list(self.setup['sources'].keys())
        self.targets_names = list(self.setup['targets'].keys())
        self.is_wav = is_wav
        self.tracks = self.load_mus_tracks(subsets=subsets, split=split)

    def __getitem__(self, index):
        return self.tracks[index]

    def __len__(self):
        return len(self.tracks)

    def get_validation_track_indices(self, validation_track_names=None):
        """Returns validation track indices by a given list of track names

        Defaults to the builtin selection 8 validation tracks, defined in
        `mus.yaml`.

        Parameters
        == == == == ==
        validation_track_names : list[str], optional
            validation track names by a given `str` or list of tracknames

        Returns
        -------
        list[int]
            return a list of validation track indices
        """
        if validation_track_names is None:
            validation_track_names = self.setup['validation_tracks']
        
        return self.get_track_indices_by_names(validation_track_names)

    def get_track_indices_by_names(self, names):
        """Returns musdb track indices by track name

        Can be used to filter the musdb tracks for 
        a validation subset by trackname

        Parameters
        == == == == ==
        names : list[str], optional
            select tracks by a given `str` or list of tracknames

        Returns
        -------
        list[int]
            return a list of ``Track`` Objects
        """
        if isinstance(names, str):
            names = [names]
        
        return [[t.name for t in self.tracks].index(name) for name in names]

    def load_mus_tracks(self, subsets=None, split=None):
        """Parses the musdb folder structure, returns list of `Track` objects

        Parameters
        ==========
        subsets : list[str], optional
            select a _musdb_ subset `train` or `test`.
            Default `None` loads [`train, test`].
        split : str
            for subsets='train', `split='train` applies a train/validation split.
            if `split='valid`' the validation split of the training subset will be used


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
            subset_folder = op.join(self.root, subset)

            for _, folders, files in os.walk(subset_folder):
                if self.is_wav:
                    # parse pcm tracks and sort by name
                    for track_name in sorted(folders):
                        if subset == 'train':
                            if split == 'train' and track_name in self.setup['validation_tracks']:
                                continue
                            elif split == 'valid' and track_name not in self.setup['validation_tracks']:
                                continue

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
                        if not track_name.endswith('.stem.mp4'):
                            continue
                        if subset == 'train':
                            if split == 'train' and track_name.split('.stem.mp4')[0] in self.setup['validation_tracks']:
                                continue
                            elif split == 'valid' and track_name.split('.stem.mp4')[0] not in self.setup['validation_tracks']:
                                continue

                        # create new mus track
                        track = MultiTrack(
                            name=track_name.split('.stem.mp4')[0],
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

        return tracks

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
        return os.path.exists(os.path.join(self.root, "train"))

    def download(self):
        """Download the MUSDB Sample data"""
        if self._check_exists():
            return

        # download files
        try:
            os.makedirs(os.path.join(self.root))
        except OSError as e:
            if e.errno == errno.EEXIST:
                pass
            else:
                raise

        print('Downloading MUSDB 7s Sample Dataset to %s...' % self.root)
        data = urllib.request.urlopen(self.url)
        filename = 'MUSDB18-7-STEMS.zip'
        file_path = os.path.join(self.root, filename)
        with open(file_path, 'wb') as f:
            f.write(data.read())
        zip_ref = zipfile.ZipFile(file_path, 'r')
        zip_ref.extractall(os.path.join(self.root))
        zip_ref.close()
        os.unlink(file_path)

        print('Done!')
