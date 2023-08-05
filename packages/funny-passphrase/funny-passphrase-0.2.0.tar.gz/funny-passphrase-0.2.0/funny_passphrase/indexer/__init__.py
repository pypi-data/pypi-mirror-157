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

import io
import random
import shutil
import tempfile

from typing import (
    Optional,
    Sequence,
)

from typing_extensions import Final
import xz

class CompressedIndexedText(object):
    """
    Compress textual files, generating also a compressed index
    of the starting lines Index textual files
    """
    
    INT_BIN_SIZE: Final[int] = 8
    
    def __init__(self, cfiles: Sequence[str], encoding: str = "utf-8"):
        self.encoding = encoding
        self.cf_l = []
        self._max_lines_l = []
        num_lines = 0
        for cfile in cfiles:
            cF = xz.open(cfile, mode="rb")
            
            # Now, get the number of members
            if len(cF.stream_boundaries) != 2:
                raise ValueError(f"Unexpected number of members in {cfile}")
            
            f_length = cF.seek(0, io.SEEK_END)
            if (f_length - cF.stream_boundaries[1]) % self.INT_BIN_SIZE:
                raise ValueError(f"Unexpected mismatch in elements from {cfile}")
            _num_lines = (f_length - cF.stream_boundaries[1]) // self.INT_BIN_SIZE
            
            self.cf_l.append(cF)
            num_lines += _num_lines
            # Limits in number of lines
            self._max_lines_l.append(num_lines)
        
        self._num_lines = num_lines
    
    def get_line(self, lineno) -> str:
        if lineno < 0 or lineno >= self._num_lines:
            raise ValueError(f"Requested line {lineno} is out of range [0, {self._num_lines})")
        
        cF = None
        prev_max = 0
        lineno_effective = lineno
        for the_cF, linemax in zip(self.cf_l, self._max_lines_l):
            if lineno < linemax:
                cF = the_cF
                lineno_effective = lineno - prev_max
                break
            prev_max = linemax
        
        if cF is None:
            raise ValueError(f"Corrupted code?")
        
        cF.seek(cF.stream_boundaries[1] + lineno_effective*self.INT_BIN_SIZE, io.SEEK_SET)
        boffset = cF.read(self.INT_BIN_SIZE)
        offset = int.from_bytes(boffset, byteorder='big', signed=False)
        if offset >= cF.stream_boundaries[1]:
            raise ValueError(f"Corrupted index")
        
        # Seek the pos
        cF.seek(offset, io.SEEK_SET)
        
        # And return the line, translated to the encoding
        line = cF.readline().decode(self.encoding).rstrip()
        return line
    
    @property
    def num_lines(self) -> int:
        return self._num_lines
    
    def get_random_line(self) -> str:
        rand_line = random.randint(0, self._num_lines - 1)
        return self.get_line(rand_line)
    
    @classmethod
    def IndexTextStream(cls, instream, outfile: str, encoding: str ="utf-8") -> "CompressedIndexedText":
        """
        It is assumed instream is a file-like object
        opened in binary mode
        or something which implements readline method
        returning bytes and tell method
        in order to read line by line
        """
        
        with xz.open(outfile, mode="wb") as output, tempfile.SpooledTemporaryFile(max_size=1024*1024) as output_idx:
            #posarr = []
            pos = instream.tell()
            bline = instream.readline()
            # First, write the lines taking note of the offsets
            lastb = b''
            while len(bline) > 0:
                lastb = bline[-1]
                output.write(bline)
                #posarr.append(pos)
                output_idx.write((pos).to_bytes(cls.INT_BIN_SIZE, byteorder='big', signed=False))
                pos = instream.tell()
                bline = instream.readline()
            
            # This is needed to avoid corner cases
            if lastb != b'\n':
                output.write(b'\n')
            
            # Now, write the index in a separate stream
            output.change_stream()
            output_idx.seek(0, io.SEEK_SET)
            shutil.copyfileobj(output_idx, output)
            #for pos in posarr:
            #    output.write((pos).to_bytes(cls.INT_BIN_SIZE, byteorder='big', signed=False))
        
        return cls(cfiles=[outfile],encoding=encoding)
    
    @classmethod
    def IndexTextFile(cls, infile: str, outfile: str, encoding: str = "utf-8") -> "CompressedIndexedText":
        with open(infile, mode="rb") as inpF:
            return cls.IndexTextStream(inpF, outfile, encoding=encoding)
