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

from .indexer import CompressedIndexedText

from typing import Iterator, Sequence

class FunnyPassphraseGenerator(object):
    """
    This class takes as input a sequence of CompressedIndexedText
    instances, which can be considered groups of words.
    It generates a passphrase in the form of a random word from each
    group of words. If the number of words is larger than the number of
    groups, the generator loops over the groups of words.
    """
    def __init__(self, *args: Sequence[CompressedIndexedText]):
        self.cit = args
    
    def generate(self, num: int = 5) -> Iterator[str]:
        for cit_idx in range(num):
            real_cit_idx = cit_idx % len(self.cit)
            cI = self.cit[real_cit_idx]
            yield cI.get_random_line()
    
    def generate_passphrase(self, num: int = 5, sep: str = ' ') -> str:
        return sep.join(self.generate(num=num))