import argparse
from pathlib import Path

import requests
from phonemizer.phonemize import phonemize

from vst.classes.shell import Shell  # type: ignore

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
# Code used from ForwardTacotron because ForwardTacotron is not a library :(
# https://github.com/as-ideas/ForwardTacotron/blob/master/utils/text/cleaners.py
# https://github.com/as-ideas/ForwardTacotron/blob/master/utils/text/symbols.py

_pad = '_'
_punctuation = '!\'(),.:;? '
_special = '-'

# Phonemes
_vowels = 'iyɨʉɯuɪʏʊeøɘəɵɤoɛœɜɞʌɔæɐaɶɑɒᵻ'
_non_pulmonic_consonants = 'ʘɓǀɗǃʄǂɠǁʛ'
_pulmonic_consonants = 'pbtdʈɖcɟkɡqɢʔɴŋɲɳnɱmʙrʀⱱɾɽɸβfvθðszʃʒʂʐçʝxɣχʁħʕhɦɬɮʋɹɻjɰlɭʎʟ'
_suprasegmentals = 'ˈˌːˑ'
_other_symbols = 'ʍwɥʜʢʡɕʑɺɧ'
_diacrilics = 'ɚ˞ɫ'
# some extra symbols that I found in from wiktionary ipa annotations
_extra_phons = ['g', 'ɝ', '̃', '̍', '̥', '̩', '̯', '͡']

phonemes = list(
    _pad + _punctuation + _special + _vowels + _non_pulmonic_consonants
    + _pulmonic_consonants + _suprasegmentals + _other_symbols + _diacrilics) + _extra_phons

phonemes_set = set(phonemes)


def to_phonemes(text: str, lang: str) -> str:
    phonemes = phonemize(text,
                         language=lang,
                         backend='espeak',
                         strip=True,
                         preserve_punctuation=True,
                         with_stress=False,
                         njobs=1,
                         punctuation_marks=';:,.!?¡¿—…"«»“”()',
                         language_switch='remove-flags')
    phonemes = ''.join([p for p in phonemes if p in phonemes_set])
    return phonemes
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =


def translator(translation, sentence: str, accent: str) -> str:
    new_sentence = sentence
    for key, value in translation.items():
        new_sentence = new_sentence.replace(key, value.get(accent, value.get('general', key)))
    return new_sentence


def download_translation(download_path: Path, url_path: str = 'default'):
    package_name = 'vst'
    url = url_path

    if url_path == 'default':
        url = f'https://raw.githubusercontent.com/8tm/{package_name}/master/src/{package_name}/translation/en_to_pl.py'

    r = requests.get(url, allow_redirects=True)

    shell = Shell()
    shell.rmtree(str(download_path))
    shell.mkdir(path=str(download_path))

    with open(f'{download_path}/downloaded_en_to_pl.py', 'w') as translation_file:
        translation_file.write(r.content.decode())


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-i', '--input', action='store', required=True, type=Path,
        help='Path to english training/validation file',
    )
    parser.add_argument(
        '-o', '--output', action='store', required=True, type=Path,
        help='Path to the folder where new translated training/validation files will be saved',
    )
    parser.add_argument(
        '-d', '--dialect', action='store', required=False, type=str, default='en-us',
        help='Select dialect. Default: en-us',
    )
    parser.add_argument(
        '-t', '--translation', action='store', required=False, type=str, default='default',
        help='URL to translation file en_to_pl.py or use default one if parametr is empty or not set.',
    )
    parser.add_argument(
        '-v', '--verbose', action='store_true', required=False,
        help='Show information while the script is running',
    )
    return parser.parse_args()


def eng_to_pl():
    arguments = parse_arguments()

    if not Path(arguments.input).exists():
        print(f'File not found: {arguments.input}')
        exit(1)

    if arguments.translation != 'default':
        print(f'Downloading translation from: {arguments.translation}')
        download_path = Path('/tmp/vst/')
        download_translation(download_path, arguments.translation)
        import sys
        sys.path.append(str(download_path))
        from downloaded_en_to_pl import translation
    else:
        from vst.translation.en_to_pl import translation

    with open(arguments.input, 'r') as transcode_file:
        lines = transcode_file.readlines()

    translated_lines = []

    for index, line in enumerate(lines):
        elements = line.split('|')
        ipa_text = to_phonemes(elements[1], arguments.dialect)
        elements[1] = translator(translation, ipa_text, arguments.dialect)
        new_line = '|'.join(element.replace('\n', '') for element in elements) + '\n'
        translated_lines.append(new_line)

        if arguments.verbose:
            print(new_line)

    with open(arguments.output, 'w') as new_transcode_file:
        new_transcode_file.writelines(translated_lines)


def main():
    try:
        eng_to_pl()
    except KeyboardInterrupt:
        print(' <= Application terminated by the user\n')
        exit(0)


if __name__ == '__main__':
    main()
