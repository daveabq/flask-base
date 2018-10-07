"""
Copyright 2005-2018 QuantumRocket. All rights reserved.
Use of this source code is governed by a BSD-style
license that can be found in the LICENSE file.

Simple parsing of key/value pairs from configuration files.

The file format is 'key = value', where blank lines and lines
starting with '#' are regarded as comments.
"""

import os


def get_config_filename():
    return os.environ['QUANTUMROCKET_CONFIG']


def load(filename):

    pairs = {}

    if filename is None or filename == '':
        return pairs

    with open(filename) as f:

        for line in f:

            line = line.strip()

            if line.startswith('#') or len(line) == 0:
                continue

            try:
                tokens = line.split()
                
                if len(tokens) is 2:
                    pairs[tokens[0].strip()] = ''
                else:
                    pairs[tokens[0].strip()] = tokens[2].strip()
                    
            except Exception:
                raise Exception('ERROR: invalid key/value pairs file, line [' + line + ']')

    return pairs
