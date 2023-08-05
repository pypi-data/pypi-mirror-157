#!/usr/bin/env python
# -*- coding: utf-8 -*-

# funny_passphrase, a library to index text files, and generate
# passphrases from them.
# Copyright (C) 2022 Barcelona Supercomputing Center, José M. Fernández
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

import argparse
import sys
from .generator import FunnyPassphraseGenerator
from .indexer import CompressedIndexedText

def main():
    ap = argparse.ArgumentParser(
        description="Funny passphrase generator",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    # ap.add_argument('-e','--encoding', dest="encoding", help="Which encoding is expected in ")
    ap.add_argument("--wg", dest="wgs", action="append", required=True, nargs="+", type=str, help="The indexed files which integrate this group")
    ap.add_argument("-w","--words", action="store", required=True, type=int, help="Number of words to generate in each passphrase")
    ap.add_argument("-n","--num", action="store", default=1, type=int, help="Number of passphrases to generate")
    ap.add_argument("-o","--output", action="store", default="-", type=str, help="Output file (default stdout)")
    args = ap.parse_args()
    
    ws_list = []
    if args.wgs is None:
        sys.exit(1)
    for i_ws, ws in enumerate(args.wgs):
        print(f"* Group {i_ws} with {len(ws)} word sets", file=sys.stderr)
        ws_list.append(CompressedIndexedText(ws))
    
    fpg = FunnyPassphraseGenerator(*ws_list)
    print(f"Writing the {args.num} passphrases to {args.output}", file=sys.stderr)
    if args.output == "-":
        out = sys.stdout
    else:
        out = open(args.output, mode="w", encoding="utf-8")
    try:
        for _ in range(args.num):
            print(fpg.generate_passphrase(sep=' ', num=args.words), file=out)
    finally:
        if out != sys.stdout:
            out.close()

if __name__ == "__main__":
    main()