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
from . import CompressedIndexedText

def main():
    ap = argparse.ArgumentParser(
        description="Funny passphrase indexer",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    # ap.add_argument('-e','--encoding', dest="encoding", help="Which encoding is expected in ")
    ap.add_argument('input', help="Input file. If the name is '-', standard input will be used")
    ap.add_argument('output', help="Output file")
    args = ap.parse_args()
    
    print(f"Compressing, indexing and writing all the text contents from {args.input} to {args.output}", file=sys.stderr)
    
    if args.input == "-":
        cit = CompressedIndexedText.IndexTextStream(sys.stdin, args.output)
    else:
        cit = CompressedIndexedText.IndexTextFile(args.input, args.output)
    
    print(f"Number of indexed lines in {args.output}: {cit.num_lines}")

if __name__ == "__main__":
    main()