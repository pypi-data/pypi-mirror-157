# funny-passphrase

This is the repository of a library and command line tools to index text files, and generate
passphrases from sets of them.

## Passphrase generator

The passphrase generator takes one or more sets of indexed text files,
and it generates one or more passphrases composed by the number of
specified words. The program keeps rotating on the sets, choosing 
a word from all the words in the indexed files composing the set.
being specified

```bash
usage: funny-passphrase [-h] --wg WGS [WGS ...] -w WORDS [-n NUM] [-o OUTPUT]

Funny passphrase generator

optional arguments:
  -h, --help            show this help message and exit
  --wg WGS [WGS ...]    The indexed files which integrate this group (default: None)
  -w WORDS, --words WORDS
                        Number of words to generate in each passphrase (default: None)
  -n NUM, --num NUM     Number of passphrases to generate (default: 1)
  -o OUTPUT, --output OUTPUT
                        Output file (default stdout) (default: -)
```

## Text indexer

The indexed text files consumed by the passphrase generator are generated
through the text indexer. A indexed text file is a seekable xz file with
two streams: the first one is the text itself; and the
second stream contains the offsets to the different lines in the text.

```bash
usage: fp-indexer [-h] input output

Funny passphrase indexer

positional arguments:
  input       Input file. If the name is '-', standard input will be used
  output      Output file

optional arguments:
  -h, --help  show this help message and exit
```

## Command line usage

Usual pattern is indexing at least one text file (for instance, the list
English adjectives and nouns and Spanish adjectives from Wiktionary),
and then use the passphrase generator as many times as needed:

```bash
wiktionary-fetcher --lang en --terms nouns en-nouns.txt
wiktionary-fetcher --lang en --terms adjectives en-adjectives.txt
wiktionary-fetcher --lang es --terms adjectives es-adjectives.txt

fp-indexer en-nouns.txt en_nouns.txt.xz_idx
fp-indexer en-adjectives.txt en_adjectives.txt.xz_idx
fp-indexer es-adjectives.txt es_adjectives.txt.xz_idx

# Generate 10 passphrases of 6 words each,
# rotating between adjectives and nouns
funny-passphrase --wg en_adjectives.txt.xz_idx es_adjectives.txt.xz_idx --wg en_nouns.txt.xz_idx -w 6 -n 10
```
