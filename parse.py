import argparse
from os import path as op

subsets_names = ['Dev', 'Test']
sources_names = ['bass', 'drums', 'other', 'vocals', 'accompaniment']

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Parse SISEC dataset')

    parser.add_argument('mds_folder', type=str, help='MDS 100 Folder')

    args = parser.parse_args()

    if op.isdir(args.mdsfolder):
        for subset in subsets_names:
            mixtures_folder = op.join(args.mdsfolder, subset)
            print mixtures_folder

    else:
        print "Directory not exists."
