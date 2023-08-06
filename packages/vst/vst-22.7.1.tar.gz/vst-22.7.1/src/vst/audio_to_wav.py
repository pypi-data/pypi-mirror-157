import argparse
from pathlib import Path

import ffmpeg  # type: ignore
from vst.classes.shell import Shell  # type: ignore


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-i', '--input', action='store', required=True, type=Path,
        help='Path to folder with audio files (ogg/mp3/wav)',
    )

    parser.add_argument(
        '-o', '--output', action='store', required=True, type=Path,
        help='Set destination path to folder where to save WAV files',
    )
    parser.add_argument(
        '-t', '--truncate', action='store_true', required=False,
        help='Truncate silence',
    )
    parser.add_argument(
        '-r', '--recursive', action='store_true', required=False,
        help='Find files also in subdirectories of input path',
    )
    parser.add_argument(
        '-v', '--verbose', action='store_true', required=False,
        help='Show information while the script is running',
    )
    return parser.parse_args()


def audio_to_wav():
    arguments = parse_arguments()
    shell = Shell()

    supported_audio_formats = [
        'aac', 'ac3', 'aiff', 'ape', 'flac', 'm4a', 'mp2', 'mp3', 'mp4', 'ogg', 'ogx', 'opus', 'ts', 'wav', 'wma', 'wv',
    ]

    audio_files_paths = shell.get_files_by_extensions(arguments.input, supported_audio_formats, arguments.recursive)
    number_of_all_files = len(audio_files_paths)

    if arguments.verbose:
        message = f'''
        \r  Number of audio files: {number_of_all_files}
        \r             Input path: {arguments.input}
        \r            Output path: {arguments.output}
        \r              Recursive: {'Yes' if arguments.recursive else 'No'}
        \r               Truncate: {'Yes' if arguments.truncate else 'No'}
        '''
        print(message)

    if not Path(arguments.output).exists():
        shell.mkdir(arguments.output, parent=True)

    for index, path in enumerate(audio_files_paths, start=1):
        relative_path_to_file = Path(str(path).replace(str(arguments.input), '').strip('/')).with_suffix('.wav')
        full_path_to_file = arguments.output / relative_path_to_file
        folder_to_create = full_path_to_file.parent

        if not folder_to_create.exists():
            shell.mkdir(folder_to_create, parent=True)

        if arguments.verbose:
            print(f'Converting file: {index}/{number_of_all_files} ({path})')

        audio_stream = ffmpeg.output(
            ffmpeg.input(path),
            str(full_path_to_file),
            format='wav',
            acodec='pcm_s16le',
            ac=1,
            ar='22050',
        )
        ffmpeg.run(audio_stream, overwrite_output=True, capture_stderr=True, capture_stdout=True)

        if arguments.truncate:
            audio_stream = ffmpeg.output(
                ffmpeg.input(full_path_to_file),
                str(full_path_to_file.with_suffix('.TS.wav')),
                af='silenceremove'
                   '=start_periods=1'
                   ':stop_duration=0.4'
                   ':start_threshold=-50dB'
                   ':stop_periods=-1'
                   ':stop_duration=0.4'
                   ':stop_threshold=-50dB',
            )
            ffmpeg.run(audio_stream, overwrite_output=True, capture_stderr=True, capture_stdout=True)


def main() -> None:
    try:
        audio_to_wav()
    except KeyboardInterrupt:
        print(' <= Application terminated by the user\n')
        exit(0)


if __name__ == '__main__':
    main()
