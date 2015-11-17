import argparse
from os import path as op
import os

subsets_names = ['Dev', 'Test']
sources_names = ['bass', 'drums', 'other', 'vocals']

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Parse SISEC dataset')

    parser.add_argument('mds_folder', type=str, help='MDS 100 Folder')

    args = parser.parse_args()
    mixtures_folder = op.join(args.mds_folder, "Mixtures")
    sources_folder = op.join(args.mds_folder, "Sources")

    # build a dict
    tracks = {}
    # parse all the mixtures
    if op.isdir(mixtures_folder):
        for subset in subsets_names:
            subset_folder = op.join(mixtures_folder, subset)
            print subset_folder
            for _, track_folders, _ in os.walk(subset_folder):
                for track_name in track_folders:
                    print track_name
                    track_path = op.join(subset_folder, track_name)
                    print track_path
                    track_mixture_path = op.join(track_path, 'mixture.wav')
                    print track_mixture_path
                    track_sources_paths = []
                    for source in sources_names:
                        track_sources_paths.append(
                            op.join(
                                sources_folder, subset, track_name, source
                            ) + '.wav'
                        )
                    print track_sources_paths

    else:
        print "%s not exists." % op.join("Estimates", args.mds_folder)
