import traceback

try:
    import urllib.request
    import urllib.error
    from pathlib import Path
    import argparse
    import sys
    import re
except ImportError as e:
    print('Error: {}'.format(e))
    print('This script works with Python 3.5+. Please use a more recent version of Python')
    exit(-1)

try:
    from tqdm.auto import tqdm
    tqdm_available = True
except ImportError:
    tqdm_available = False
    print("tqdm module not available. This script will work anyway, but it is recommended to install \n"
          "tqdm to display download progress bars and estimate download time. \n"
          "Check https://tqdm.github.io/ to see how to install it.")

_BASE_URL_ = "https://data.bris.ac.uk/datasets/3cqb5b81wk2dc2379fx1mrxh47/"


def sizeof_fmt(num, suffix="B"):
    # copied from https://stackoverflow.com/a/1094933
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"

        num /= 1024.0

    return f"{num:.1f}Yi{suffix}"


def download_file(url, output_path, block_size=8192000, dry_run=False):
    filename = output_path.name
    path = output_path.expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    progress_bar = None
    base_str = f"Downloading {filename}"

    with open(path, "wb") as output_file:
        with urllib.request.urlopen(url) as response:
            file_size = response.getheader('content-length')

            if file_size:
                file_size = int(file_size)

                if tqdm_available:
                    progress_bar = tqdm(desc=base_str, total=file_size, unit="B", file=sys.stdout, unit_scale=True,
                                        position=1, leave=False)

            progress = 0

            while True:
                if dry_run:
                    if tqdm_available:
                        tqdm.write('Skipping the actual download (dry run)')
                    else:
                        print('Skipping the actual download (dry run)')

                    break

                buffer = response.read(block_size)

                if not buffer:
                    if not tqdm_available:
                        print()
                    break

                output_file.write(buffer)
                buffer_size = len(buffer)
                progress += buffer_size

                if file_size:
                    if tqdm_available:
                        progress_bar.update(buffer_size)
                    else:
                        print(f"{base_str} {sizeof_fmt(progress)}/{sizeof_fmt(file_size)} "
                              f"{progress/file_size*100:0.2f}%\r", end='')
                        sys.stdout.flush()

        if progress_bar is not None:
            progress_bar.close()


def create_parser():
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("output-path", type=Path, help="Path where you want to download the dataset")
    parser.add_argument('--videos', dest='what', action='append_const', const='videos',
                        help='Download video files')
    parser.add_argument('--digital-twin', dest='what', action='append_const', const='digital-twin',
                        help='Download digital twin files')
    parser.add_argument('--slam-gaze', dest='what', action='append_const', const='slam-and-gaze',
                        help='Download slam and gaze files')
    parser.add_argument('--audio', dest='what', action='append_const', const='audio-hdf5',
                        help='Download audio files')
    parser.add_argument('--hands', dest='what', action='append_const', const='hands-masks',
                        help='Download hand mask files')
    parser.add_argument('--consent-forms', dest='what', action='append_const', const='consent form',
                        help='Download consent forms')
    parser.add_argument('--acquisition-guidelines', dest='what', action='append_const',
                        const='acquisitionguidelines', help='Download acquisition guidelines')
    parser.add_argument('--vrs', dest='what', action='append_const', const='vrs',
                        help='Download vrs files')
    parser.add_argument('--participants', nargs='?', type=str, default='all',
                        help='Specify participants IDs. You can specify a single participant, e.g. `--participants 1` '
                             'or a comma-separated list of them, e.g. `--participants 1,2,3`. '
                             'Participants range between 1 and 9')
    parser.add_argument('--dry-run', action='store_true', help='Runs the script without actually '
                                                               'downloading any files. This will create '
                                                               'folders and empty files')

    return parser


def load_files():
    parts = {}

    with open(Path('data/files.txt').resolve(), 'r') as f:
        for line in f:
            p = Path(line.strip())

            if len(p.suffixes) == 0:
                continue

            parents = p.parents
            what = parents[-2].name.lower()

            if what not in parts:
                parts[what] = {}

            if len(parents) == 2:
                if 'no_participant' in parts[what]:
                    parts[what]['no_participant'].append(p)
                else:
                    parts[what]['no_participant'] = [p]
            else:
                participant = parents[-3].name
                assert bool(re.match('P0[0-9]', participant))

                if participant in parts[what]:
                    parts[what][participant].append(p)
                else:
                    parts[what][participant] = [p]


    return parts


def main(args):
    if args.what is None:
        args.what = ('videos', 'digital-twin', 'slam-and-gaze', 'audio-hdf5', 'hands-masks', 'consent form',
                     'acquisitionguidelines', 'vrs')
    if args.participants != 'all':
        args.participants = [p.strip() for p in args.participants.split(',')]
        string_check = len(args.participants[0]) == 3 and args.participants[0][0] == 'P'
        int_check = len(args.participants[0]) == 1
        assert int_check or string_check, 'Invalid participant format. ' \
                                          'Please enter the participants in numerical (1), ' \
                                          'or string format (P01).'
        args.participants = list(map(int, args.participants)) if int_check else args.participants

    parts = load_files()
    to_download = []

    for what in args.what:
        if 'no_participant' in parts[what]:
            to_download.extend(parts[what]['no_participant'])

        if args.participants == 'all':
            participants = (f'P0{i}' for i in range(1, 10))
        else:
            participants = args.participants

        for p in participants:
            if p in parts[what]:
                to_download.extend(parts[what][p])

    download(args, to_download)


def download(args, to_download):
    output_path = (Path(getattr(args, 'output-path')) / 'HD-EPIC').expanduser().resolve()
    n_files = len(to_download)
    print_header(f'Thanks for using the HD-EPIC downloader!\n'
                 f'Going to download {n_files} files to {output_path}\n'
                 f'Please bear in mind that download speed may be very slow depending on your region')

    if tqdm_available:
        progress_bar = tqdm(total=n_files, unit='files', desc=f'Downloading {n_files} files', file=sys.stdout,
                            leave=True, position=0)
    else:
        progress_bar = None

    errors = 0

    for i, f in enumerate(to_download):
        url = _BASE_URL_ + str(f)

        try:
            download_file(url, output_path / f, dry_run=args.dry_run)  # TODO check file exists with MD5 and skip if it does
        except Exception:
            print(f'An error occurred: while trying to download {url}. Skipping this file. The error was:\n\n')
            print(traceback.format_exc(), file=sys.stderr)
            errors += 1

        if progress_bar is None:
            print(f'Downloaded {i + 1}/{n_files} files')
        else:
            progress_bar.update()

    print_header(f"All files downloaded! Errors: {errors}")

    if progress_bar is not None:
        progress_bar.close()


def print_header(str_):
    print('-' * 80)
    print(str_)
    print('-' * 80)


if __name__ == "__main__":
    # test_url = "https://data.bris.ac.uk/datasets/3cqb5b81wk2dc2379fx1mrxh47/Videos/P03/P03-20240216-084005.mp4"
    # download_file(test_url, '~/Desktop')
    parser = create_parser()
    args = parser.parse_args()
    main(args)