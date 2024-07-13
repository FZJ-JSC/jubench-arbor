#!/usr/bin/env python3

import json
from argparse import ArgumentParser as CLI
from pathlib import Path

cli = CLI(description='Generate inputs files for benchmark.')
cli.add_argument('--default',  action='store_true', help='Generate default inputs; ignores most arguments except input template.')
cli.add_argument('--depth',   '-d', type=int, choices=range(5, 16),                 default=10,                   help='Depth between 5 and 15')
cli.add_argument('--nodes',   '-n', type=int,                                       default=8,                    help='Number of nodes')
cli.add_argument('--variant', '-v', type=str, choices=['small', 'medium', 'large'], default='large',              help='Variant name')
cli.add_argument('--output',  '-o', type=str,                                       default='input.json',         help='Output path')
cli.add_argument('--input',   '-i', type=str,                                       default='jube/input.json.in', help='Input path')

args = cli.parse_args()

cwd = Path(__file__).parent
inp = cwd / Path(args.input)
out = cwd / Path(args.output)

if not inp.exists() or not inp.is_file():
    print(f"Input file {inp} unreadable.")
    exit(-42)

def write_input_json(raw, depth, nodes, variant, out):
    if out.exists():
        print(f"Output file {out} exists; refusing to overwrite.")
        exit(-42)

    cells_per_node = {
        'large': 192000,
        'medium': 144000,
        'small': 96000,
    }

    cells = cells_per_node[variant]*nodes

    tmp = raw.replace("#cells#", str(cells)).replace("#depth#", str(depth))

    with open(out, 'w') as fd:
        print(tmp, file=fd)

with open(inp) as fd:
    raw = fd.read()

if args.default:
    for v in ['large', 'medium', 'small']:
        # baseline is 8 nodes x 4 A100 GPUs
        write_input_json(raw, 10,     8, v, cwd / f'baseline_{v}.json')
        # highscaling is 20 x 50PF = 20 x 642 nodes x 4 A100 GPUs
        write_input_json(raw, 10, 12840, v, cwd / f'highscaling_{v}.json')
else:
    write_input_json(raw, args.depth, args.nodes, args.variant, out)
