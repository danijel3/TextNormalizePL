import argparse
import json
from pathlib import Path

from tqdm import tqdm

from process import normalize


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ids', action='store_true', help='Input files have IDs as the first token.')
    parser.add_argument('--force', action='store_true', help='Overwrite existing files.')
    parser.add_argument('text', nargs='+', type=Path)

    args = parser.parse_args()

    for input_file in tqdm(args.text):
        output_file = input_file.with_suffix('.norm')
        offset_file = input_file.with_suffix('.normoff')
        if output_file.exists() and not args.force:
            print(f'Skipping {input_file}...')
            continue
        with open(input_file) as f, open(output_file, 'w') as g, open(offset_file, 'w') as h:
            for l in f:
                tok = l.strip().split()

                if args.ids:
                    tid = tok[0]
                    tok = tok[1:]

                n, off = normalize(' '.join(tok))
                assert (len(n.split()) == len(off)), f'Assertion error in {input_file}: ' \
                                                     f'word count doesn\'t match offset count'
                if args.ids:
                    g.write(f'{tid}\t')
                    h.write(f'{tid}\t')

                g.write(f'{n}\n')
                h.write(f'{json.dumps(off)}\n')


if __name__ == '__main__':
    main()
