import argparse
from os import path as op
import os


def get_sds_track(root_dir=None, subsets=['Dev', 'Test']):

    mixtures_folder = op.join(root_dir, "Mixtures")
    sources_folder = op.join(root_dir, "Sources")

    sources_names = ['bass', 'drums', 'other', 'vocals']

    # parse all the mixtures
    if op.isdir(mixtures_folder):
        for subset in subsets:
            subset_folder = op.join(mixtures_folder, subset)
            for _, track_folders, _ in os.walk(subset_folder):
                for track_name in track_folders:
                    track = {}
                    track['name'] = track_name
                    track['base_path'] = op.join(subset_folder, track_name)
                    track['path'] = op.join(
                        track['base_path'], 'mixture.wav'
                    )
                    track['sources'] = []
                    for source in sources_names:
                        track['sources'].append(
                            {
                                'name': source,
                                'path': op.join(
                                    sources_folder,
                                    subset,
                                    track_name,
                                    source
                                ) + '.wav'
                            }
                        )
                    yield track
    else:
        print "%s not exists." % op.join("Estimates", args.mds_folder)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Parse SISEC dataset')

    parser.add_argument('sds_folder', type=str, help='SDS 100 Folder')

    args = parser.parse_args()

    print len(list(get_sds_track(args.sds_folder, subsets=['Test'])))
