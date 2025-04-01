import hashlib
import traceback

try:
    import urllib.request
    import urllib.error
    import urllib.parse
    from pathlib import Path
    import argparse
    import sys
    import re
except ImportError as e:
    print('This script works with Python 3.6+. Please use a more recent version of Python')
    print(traceback.format_exc(), file=sys.stderr)
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


def md5_checksum(path):
    hash_md5 = hashlib.md5()

    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)

    return hash_md5.hexdigest()


def download_file(url, output_path, block_size=8192000, dry_run=False, md5=None):
    filename = output_path.name
    path = output_path.expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    progress_bar = None
    base_str = f"Downloading {filename}"

    if not dry_run and md5 is not None and path.exists():
        local_md5 = md5_checksum(path)

        if local_md5 == md5:
            msg = f"File {filename} already downloaded, skipping this file"

            if tqdm_available:
                tqdm.write(msg)
            else:
                print(msg)

            return
        else:
            msg = (f"File {filename} exists locally but md5 checksums don't match\n"
                   f"This is likely due to a partial download or a corrupted file\n"
                   f"Will download the file now")

            if tqdm_available:
                tqdm.write(msg)
            else:
                print(msg)

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
    parser.add_argument('--vrs', dest='what', action='append_const', const='vrs',
                        help='Download vrs files')
    parser.add_argument('--digital-twin', dest='what', action='append_const', const='digital-twin',
                        help='Download digital twin files')
    parser.add_argument('--slam-gaze', dest='what', action='append_const', const='slam-and-gaze',
                        help='Download slam and gaze files')
    parser.add_argument('--audio', dest='what', action='append_const', const='audio-hdf5',
                        help='Download audio files')
    parser.add_argument('--hands', dest='what', action='append_const', const='hands-masks',
                        help='Download hand mask files')
    parser.add_argument('--consent-form', dest='what', action='append_const', const='consent form',
                        help='Download consent form')
    parser.add_argument('--acquisition-guidelines', dest='what', action='append_const',
                        const='acquisitionguidelines', help='Download acquisition guidelines')
    parser.add_argument('--participants', nargs='?', type=str, default='all',
                        help='Specify participants IDs. You can specify a single participant, e.g. `--participants 1` '
                             'or a comma-separated list of them, e.g. `--participants 1,2,3`. '
                             'Participants numbers must range between 1 and 9')
    parser.add_argument('--dry-run', action='store_true', help='Runs the script without actually '
                                                               'downloading any files. This will connect to the server '
                                                               'but will not download any files. The script will '
                                                               'create folders and empty files')

    return parser


def load_files():
    parts = {}
    pattern = re.compile('P0[0-9]')

    with open(Path('data/md5.txt').resolve(), 'r') as f:
        for line in f:
            splits = line.split()
            md5 = splits[0]
            p = Path(' '.join(splits[1:]).strip())

            if len(p.suffixes) == 0:
                continue

            what = p
            participant = 'no_participant'

            while str(what.parent) != '.':
                what = what.parent

                if bool(pattern.match(what.name)):
                    participant = what.name

            if what == p:
                what = 'root'
            else:
                what = what.name.lower()

            if what not in parts:
                parts[what] = {}

            if participant in parts[what]:
                parts[what][participant].append((p, md5))
            else:
                parts[what][participant] = [(p, md5)]

    return parts


def main(args):
    if args.what is None:
        args.what = ['videos', 'vrs', 'digital-twin', 'slam-and-gaze', 'audio-hdf5', 'hands-masks', 'consent form',
                     'acquisitionguidelines']
    if args.participants != 'all':
        try:
            args.participants = [p.strip() for p in args.participants.split(',')]
            p_check = all(int(p) in range(1, 10) for p in args.participants)

            if not p_check:
                sys.exit('Invalid participants number. Participants numbers must be between 1 and 9')
        except (ValueError, AttributeError):
            sys.exit(('Invalid participants format. Please specify participants with comma-separated '
                      'integer numbers in [1, 9]. For example, `--participants 1,2,3`'))

    parts = load_files()
    to_download = []

    args.what.append('root')

    for what in args.what:
        if 'no_participant' in parts[what]:
            to_download.extend(parts[what]['no_participant'])

        if args.participants == 'all':
            r = range(1, 10)
        else:
            r = list(set(args.participants))

        participants = (f'P0{i}' for i in r)

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

    for i, t in enumerate(to_download):
        f, md5 = t
        url = _BASE_URL_ + urllib.parse.quote(str(f))

        try:
            download_file(url, output_path / f, dry_run=args.dry_run, md5=md5)
        except Exception:
            print(f'An error occurred: while trying to download {url}. Skipping this file. The error was:\n\n')
            print(traceback.format_exc(), file=sys.stderr)
            errors += 1

        if progress_bar is None:
            print(f'Downloaded {i + 1}/{n_files} files')
        else:
            progress_bar.update()

    if errors == 0:
        print_header(f"All files downloaded without errors!")
    else:
        print_header(f"All done, but one or more files were not downloaded! N. of errors: {errors}/{n_files}")

    if progress_bar is not None:
        progress_bar.close()


def print_header(str_):
    print('-' * 80)
    print(str_)
    print('-' * 80)


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()
    main(args)