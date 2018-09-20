import os
import os.path
import errno
import numpy as np
import sklearn.preprocessing
from PIL import Image


eps = np.finfo(np.float32).eps


class MAG(object):
    """`MUSMAG Dataset.
    Args:
        root (string): Root directory of dataset where musmag is stored
        train (bool, optional)
        download (bool, optional): If true, downloads the dataset from the internet and puts it in root directory. If dataset is already downloaded, it is not downloaded again.
    """

    def __init__(
        self,
        root_dir=None,
        subsets='train',
        valid=False,
        valid_tracks=[],
        target='vocals',
        data_type='.jpg',
        download=False,
        scale=False,
        in_memory=False,
    ):

        self.data_type = data_type
        if data_type == '.jpg':
            self.url = 'https://s3.eu-west-3.amazonaws.com/sisec18.unmix.app/dataset/MUSMAG.zip'
        # add raw musdb18 reader here

        if root_dir is None:
            if download:
                self.root_dir = os.path.expanduser("~/MUSDB18/MUSMAG")
            else:
                if "MUSMAG_PATH" in os.environ:
                    self.root_dir = os.environ["MUSMAG_PATH"]
                else:
                    raise RuntimeError("Variable `MUSMAG_PATH` has not been set.")
        else:
            self.root_dir = os.path.expanduser(root_dir)

        self.subsets = subsets  # training set or test set
        self.target = target
        self.scale = scale

        if download:
            if data_type == '.jpg':
                self.download()
            else:
                print("Dataset download not supported.")

        if not self._check_exists():
            raise RuntimeError('Dataset not found.' +
                               ' You can use `download=True`')

        self.tracks = self.load_tracks(
            self.subsets,
            valid=valid,
            tracknames=valid_tracks
        )

        self.in_memory = in_memory

        if self.in_memory:
            self.X, self.Y = self._get_tensors()
            self.X = np.array(self.X)
            self.Y = np.array(self.Y)

        if scale:
            self.input_scaler = sklearn.preprocessing.StandardScaler()
            self.output_scaler = sklearn.preprocessing.StandardScaler()

            for idx in range(len(self)):
                X, Y = self[idx]
                if self.data_type == '.jpg':
                    X = dequantize(X)
                    Y = dequantize(Y)
                self.input_scaler.partial_fit(np.squeeze(X))
                self.output_scaler.partial_fit(np.squeeze(Y))

    def __len__(self):
        return len(self.tracks)

    def __getitem__(self, idx):
        if self.in_memory:
            X = self.X[idx]
            Y = self.Y[idx]
        else:
            X, Y = self.load_track_path(self.tracks[idx])

        return X, Y

    def __repr__(self):
        s = "X: %s\n" % str(((len(self.tracks),)))
        s += "Y: %s" % str(((len(self.tracks),)))
        return s

    def read_path(self, path):
        """
        returns:
            (nb_frames, nb_bins, nb_channels)
        """
        if self.data_type == '.jpg':
            img = Image.open(path)
            img = np.array(img).astype(np.uint8)
            # inverse flipped image
            img = img[::-1, ...]
            if img.ndim <= 2:
                M = np.atleast_3d(img).swapaxes(0, 1)
            else:
                img = img.swapaxes(0, 1)
                # select only red and blue channels
                M = img[:, :, [0, 1]]
        else:
            M = np.load(path, mmap_mode='c')
        return M

    def load_track_path(self, track_folder):
        mix_path = os.path.join(
            track_folder,
            'mix' + self.data_type
        )

        mix = self.read_path(mix_path)

        # add track to list of tracks
        trg_path = os.path.join(
            track_folder,
            self.target + self.data_type
        )
        target = self.read_path(trg_path)
        return mix, target

    def load_tracks(self, subsets="train", valid=False, tracknames=[]):
        if subsets is not None:
            if isinstance(subsets, str):
                subsets = [subsets]
            else:
                subsets = subsets
        else:
            subsets = ['train', 'test']

        tracks = []
        for subset in subsets:
            subset_folder = os.path.join(self.root_dir, subset)
            _, folders, files = next(os.walk(subset_folder))

            if subset == 'train' and not valid:
                track_list = [x for x in sorted(folders) if x not in tracknames]
            if subset == 'train' and valid:
                track_list = [x for x in sorted(folders) if x in tracknames]
            else:
                track_list = sorted(folders)

            for track_name in track_list:
                track_folder = os.path.join(subset_folder, track_name)
                tracks.append(track_folder)

        return tracks

    def _get_tensors(self):
        X = []
        Y = []
        for track_path in self.tracks:
            cur_X, cur_Y = self.load_track_path(track_path)
            X.append(cur_X)
            Y.append(cur_Y)

        return X, Y

    def _check_exists(self):
        return os.path.exists(
            os.path.join(self.root_dir, 'train')
        )

    def download(self):
        """Download the MUSMAG data if it doesn't exist in processed_folder."""
        from six.moves import urllib
        import zipfile

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

        print('Downloading MUSMAG...')
        data = urllib.request.urlopen(self.url)
        filename = 'MUSMAG.zip'
        file_path = os.path.join(self.root_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(data.read())
        zip_ref = zipfile.ZipFile(file_path, 'r')
        zip_ref.extractall(os.path.join(self.root_dir))
        zip_ref.close()
        os.unlink(file_path)

        print('Done!')


def dequantize(X):
    return np.exp(X.astype(np.float) / (2 ** 8 - 1))-1
