import tqdm
import stempeg
import argparse
from pathlib import Path
from musdb import DB
import sys


def musdb_convert(inargs=None):
    """
    cli application to conver audio files to spectrogram images
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'musdb_root',
        type=str,
    )

    parser.add_argument(
        'output_root',
        type=str
    )

    parser.add_argument(
        '--download', action='store_true', default=False,
        help='use the downloaded 7s musdb stems',
    )

    parser.add_argument(
        '--extension', type=str, default='.wav'
    )

    args = parser.parse_args(inargs)

    mus = DB(root=args.musdb_root, download=args.download)

    for track in tqdm.tqdm(mus):

        track_estimate_dir = Path(
            args.output_root, track.subset, track.name
        )
        track_estimate_dir.mkdir(exist_ok=True, parents=True)
        # write out tracks to disk

        stempeg.write_audio(
            path=str(track_estimate_dir / Path('mixture').with_suffix(args.extension)),
            data=track.audio,
            sample_rate=track.rate
        )
        for name, track in track.targets.items():
            stempeg.write_audio(
                path=str(track_estimate_dir / Path(name).with_suffix(args.extension)),
                data=track.audio,
                sample_rate=track.rate
            )


if __name__ == '__main__':
    musdb_convert(sys.argv[1:])
