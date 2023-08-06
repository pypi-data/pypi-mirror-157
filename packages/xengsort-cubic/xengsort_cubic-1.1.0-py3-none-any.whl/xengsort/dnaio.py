import sys
import io
import gzip
from collections import Counter
from subprocess import check_output
from os import path as ospath

import numpy as np
from numba import njit, uint8, uint32, int32, uint64, int64


# FASTA/FASTQ/TEXT/gz handling ######################################

class FormatError(RuntimeError):
    pass


def fastq_reads(files, sequences_only=False, dirty=False):
    """
    For the given 
    - list or tuple of FASTQ paths,
    - single FASTQ path (string; "-" for stdin)
    - open binary FASTQ file-like object f,
    yield a triple of bytes (header, sequence, qualities) for each read.
    If sequences_only=True, yield only the sequence of each read.

    This function operatates at the bytes (not string) level.
    The header contains the initial b'@' character.

    Automatic gzip decompression is provided
    if a file is a string and ends with .gz or .gzip.
    """
    func = _fastq_reads_from_filelike
    if sequences_only:
        func = _fastq_seqs_from_filelike
        if dirty:
            func = _fastq_seqs_dirty_from_filelike
    if isinstance(files, (list, tuple)):
        # multiple files
        for f in files:
            yield from _universal_reads(f, func)
    else:
        # single file
        yield from _universal_reads(files, func)


def fasta_reads(files, sequences_only=False):
    """
    For the given
    - list or tuple of FASTA paths,
    - single FASTA path (string),
    - open binary FASTA file-like object f,
    yield a pair of bytes (header, sequence) for each entry (of each file).
    If sequences_only=True, yield only the sequence of each entry.
    This function operatates at the bytes (not string) level.
    The header DOES NOT contain the initial b'>' character.
    If f == "-", the stdin buffer is used.
    Automatic gzip decompression is provided,
    if f is a string and ends with .gz or .gzip.
    """
    func = _fasta_reads_from_filelike if not sequences_only else _fasta_seqs_from_filelike
    if isinstance(files, (list, tuple)):
        # multiple files
        for f in files:
            yield from _universal_reads(f, func)
    else:
        # single file
        yield from _universal_reads(files, func)


def text_reads(f):
    """
    For the given text file path or open binary file-like object f,
    yield a each line as a bytes object, without the newline.
    If f == "-", the stdin buffer is used.
    Automatic gzip decompression is provided
    if f is a string and ends with .gz or .gzip.
    """
    yield from _universal_reads(f, _text_reads_from_filelike)


####################################

def _universal_reads(f, func):
    """
    yield each read from file f, where
    f is a filename (string), possibly ending with .gz/.gzip,
      or a file-like object,
    func describes the logic of obtaining reads from the file,
    and can be one of
      _fastq_reads_from_filelike: yields triples (header, sequence, qualities)
      _fastq_seqs_from_filelike: yields sequences only
      _fasta_reads_from_filelike: yields pairs (header, sequence)
      _fasta_seqs_from_filelike: yields sequences only
      _text_reads_from_filelike: yields each line as a read
    All objects are bytes/bytearray objects (can be decoded using ASCII encoding).
    Headers are yielded WITHOUT the initial character (> for FASTA, @ for FASTQ).
    """
    if not isinstance(f, (str, bytes)):
        yield from func(f)
    elif f == "-" or f == b"-":
        yield from func(sys.stdin.buffer)
    elif f.endswith((".gz", ".gzip")):
        with gzip.open(f, "rb") as file:
            reader = io.BufferedReader(file, 4*1024*1024)
            yield from func(reader)
    else:
        with open(f, "rb", buffering=-1) as file:
            yield from func(file)


def _fastq_reads_from_filelike(f, HEADER=b'@'[0], PLUS=b'+'[0]):
    strip = bytes.strip
    entry = 0
    while f:
        header = strip(next(f))
        if not header: continue
        entry += 1
        seq = strip(next(f))
        plus = strip(next(f))
        qual = strip(next(f))
        if header[0] != HEADER:
            raise FormatError(f"ERROR: Illegal FASTQ header: '{header.decode()}', entry {entry}")
        if plus[0] != PLUS:
            raise FormatError(f"ERROR: Illegal FASTQ plus line: '{plus.decode()}',\nheader '{header.decode()}',\nsequence '{seq.decode()}',\nentry {entry}")
        if len(plus) > 1 and plus[1:] != header[1:]:
            raise FormatError(f"ERROR: FASTQ Header/plus mismatch: '{header.decode()}' vs. '{plus.decode()}', entry {entry}")
        yield (header[1:], seq, qual)


def _fastq_seqs_from_filelike(f, HEADER=b'@'[0], PLUS=b'+'[0]):
    strip = bytes.strip
    while f:
        header = strip(next(f))
        if not header: continue
        seq = strip(next(f))
        plus = next(f)
        next(f)  # ignore quality value
        if header[0] != HEADER:
            raise FormatError(f"ERROR: Illegal FASTQ header: '{header.decode()}'")
        if plus[0] != PLUS:
            raise FormatError(f"ERROR: Illegal FASTQ plus line: {plus.decode()}'")
        yield seq


def _fastq_seqs_dirty_from_filelike(f):
    strip = bytes.strip
    while f:
        next(f)
        seq = strip(next(f))
        next(f)
        next(f)  # ignore quality value
        yield seq


def _fasta_reads_from_filelike(f, COMMENT=b';'[0], HEADER=b'>'[0]):
    strip = bytes.strip
    header = seq = None
    for line in f:
        line = strip(line)
        if len(line) == 0:
            continue
        if line[0] == COMMENT:
            continue
        if line[0] == HEADER:
            if header is not None:
                yield (header, seq)
            header = line[1:]
            seq = bytearray()
            continue
        seq.extend(line)
    if header is not None:
        yield (header, seq)


def _fasta_seqs_from_filelike(f, COMMENT=b';'[0], HEADER=b'>'[0]):
    strip = bytes.strip
    header = seq = False
    for line in f:
        line = strip(line)
        if len(line) == 0:
            continue
        if line[0] == COMMENT:
            continue
        if line[0] == HEADER:
            if header:
                yield seq
            header = True
            seq = bytearray()
            continue
        seq.extend(line)
    yield seq


def _text_reads_from_filelike(f):
    strip = bytes.strip
    while f:
        yield strip(next(f))


@njit(nogil=True, locals=dict(
        n=uint64, M=int64, i=int32, m=int64, nxt=uint64, line=uint32))
def _find_fastq_seqmarks(buf, linemarks):
    """
    Find start and end positions of lines in byte buffer 'buf'.
    Store the information in 'linemarks', such that
    linemarks[i, 0:4] has information about record number i.

    Return pair (m, nxt), where:
        m: number of sequences processed (-1 indicates error)
        nxt: position at which to continue processing 
             in the next iteration (start of new entry, '@')
    linemarks[i,0] = start of sequence
    linemarks[i,1] = end of sequence
    linemarks[i,2] = start of read
    linemarks[i,3] = end of read
    """
    n = buf.size
    if n == 0: return (int64(0), uint64(0))
    M = linemarks.shape[0]
    i = 0
    m = -1  # number of current record we're in
    nxt = 0  # byte of beginning of last record
    line = 0  # current line in FASTQ record (0,1,2,3)
    # find start of current line
    while True:
        if buf[i] == 10:
            i += 1
            if line == 0:
                linemarks[m, 3] = i
            if i >= n:
                # we did not find valid record start
                if line == 0:
                    m += 1
                    nxt = n
                return (m, nxt)
        if line == 0:
            m += 1
            nxt = i
            if buf[i] != ord('@'):
                return (int64(-(m+1)), nxt)  # format ERROR
            linemarks[m, 2] = i
            if m >= M: return (M, nxt)
        elif line == 1:
            linemarks[m, 0] = i
        # find end of current line
        while buf[i] != 10:
            i += 1
            if i >= n:
                # we did not find the end of the line before the buffer was exhausted
                # we cannot set linemarks[m, 1].
                return (m, nxt)
        if line == 1:
            linemarks[m, 1] = i
        line = (line + 1) & 3
    # unreachable
    return (int64(-1), uint64(0))


def fastq_chunks(files, bufsize=2**23, maxreads=(2**23)//200):
    """
    Yield all chunks from a list or tuple of FASTQ files.
    A chunk is a pair (buffer, linemarks), where
    - buffer is readable/writable byte buffer
    - buffer[linemarks[i,0]:linemarks[i,1]] contains the i-th sequence 
      of the chunk; other line marks are not stored.
    - The part of linemarks that is returned is such that
      linemarks.shape[0] is at most maxreads and equals the number of reads.
    CAUTION: If bufsize is very small, such that not even a single FASTQ entry
      fits into the buffer, it will appear that the buffer is empty.
    """
    # defaults are good for single-threaded runs; multiply by #threads.
    if not isinstance(files, (list, tuple)):
        files = (files,)  # single file? make it a singleton tuple
    if bufsize > 2**30:
        raise ValueError("require bufsize <= 1 GiB (2**30)")
    linemarks = np.empty((maxreads, 4), dtype=np.int32)
    buf = np.empty(bufsize, dtype=np.uint8)
    for filename in files:
        with io.BufferedReader(io.FileIO(filename, 'r'), buffer_size=bufsize) as f:
            prev = 0
            while True:
                read = f.readinto(buf[prev:])
                if read == 0: break
                available = prev + read  # number of bytes available
                m, cont = _find_fastq_seqmarks(buf[:available], linemarks)
                if m <= 0: 
                    raise RuntimeError(f"FASTQ Format error (buffer size {bufsize}). "
                        "Ensure that you are using UNCOMPRESSED files (no .gz!), "
                        "or uncompress on-the-fly via <(zcat sample.fq.gz); see README.")
                chunk = (buf, linemarks[:m])
                yield chunk
                #cont = linemarks[m-1,1] + 1
                prev = available - cont
                if prev > 0:
                    buf[:prev] = buf[cont:available]
                    #print(f"  moving buf[{cont}:{available}] to buf[0:{prev}]")
                assert prev < cont


def fastq_chunks_paired(pair, bufsize=2**23, maxreads=2**23//200):
    """
    Yield all chunks from a list or tuple of FASTQ files.
    A chunk is a pair (buffer, linemarks), where
    - buffer is readable/writable byte buffer
    - buffer[linemarks[i,0]:linemarks[i,1]] contains the i-th sequence 
      of the chunk; other line marks are not stored.
    - The part of linemarks that is returned is such that
      linemarks.shape[0] is at most maxreads and equals the number of reads.
    CAUTION: If bufsize is very small, such that not even a single FASTQ entry
      fits into the buffer, it will appear that  the buffer is empty.
    """
    # defaults are good for single-threaded runs; multiply by #threads.
    (files1, files2) = pair
    if not isinstance(files1, (list, tuple)):
        files1 = (files1,)
    if not isinstance(files2, (list, tuple)):
        files2 = (files2,)
    linemarks1 = np.empty((maxreads, 4), dtype=np.int32)
    linemarks2 = np.empty((maxreads, 4), dtype=np.int32)
    buf1 = np.empty(bufsize, dtype=np.uint8)
    buf2 = np.empty(bufsize, dtype=np.uint8)
    if len(files1) != len(files2):
        raise RuntimeError(f"different numbers of fastq files")
    for i in range(len(files1)):
        with io.BufferedReader(io.FileIO(files1[i], 'r'), buffer_size=bufsize) as f1, \
             io.BufferedReader(io.FileIO(files2[i], 'r'), buffer_size=bufsize) as f2:
            prev1 = prev2 = 0
            while True:
                read1 = f1.readinto(buf1[prev1:])
                read2 = f2.readinto(buf2[prev2:])
                if read1 == 0 and read2 == 0: break
                # TODO: shouldn't the check be on available ??!
                available1 = prev1 + read1
                available2 = prev2 + read2
                ###print(type(buf1[:available1]), buf1[:available1].shape, type(linemarks1))
                m1, cont1 = _find_fastq_seqmarks(buf1[:available1], linemarks1)
                m2, cont2 = _find_fastq_seqmarks(buf2[:available2], linemarks2)
                if m1 <= 0 or m2 <= 0: 
                    raise RuntimeError(f"FASTQ Format error (buffer size {bufsize}). "
                        "Ensure that you are using UNCOMPRESSED files (no .gz!), "
                        "or uncompress on-the-fly via <(zcat sample.fq.gz); see README.")
                if m1 == m2:
                    chunk = (buf1, linemarks1[:m1], buf2, linemarks2[:m2])
                elif m1 < m2:
                    chunk = (buf1, linemarks1[:m1], buf2, linemarks2[:m1])
                    cont2 = linemarks2[m1][2]
                else:
                    chunk = (buf1, linemarks1[:m2], buf2, linemarks2[:m2])  
                    cont1 = linemarks1[m2][2]
                yield chunk
                prev1 = available1 - cont1
                prev2 = available2 - cont2
                if prev1 > 0:
                    buf1[:prev1] = buf1[cont1:available1]
                    buf1[prev1:] = 0
                if prev2 > 0:
                    buf2[:prev2] = buf2[cont2:available2]
                    buf2[prev2:] = 0
                #assert prev1 < cont1
                #assert prev2 < cont2

####################################################################

# Grouping
#
# A groupby function is a function that returns a group name, given
# - a filename (full absolute path or relative path)
# - a sequence name (header string)


def groupby_all(path, header):
    return "all"


def groupby_basename(path, header):
    fname = ospath.basename(ospath.abspath(path))
    while True:
        fname, ext = ospath.splitext(fname)
        if not ext:
            break
    return fname


def groupby_seqname(path, header):
    fields = header[1:].split()
    if not fields:
        return "default"
    return fields[0]


def groupby_seqname_strict(path, header):
    return header[1:].split()[0]  # raises IndexError if header is empty


def groupby_dict_factory(d, default="default"):
    """
    return a groupby function that looks up group in given dict,
    using the first word of the sequence header
    """
    def groupby_d(path, header):
        fields = header[1:].split()
        name = fields[0] if fields else ''
        if default:
            return d.get(name, default)
        return d[name]
    return groupby_d


def get_grouper(groupspec):
    """
    groupspec is singleton list or pair list:
    (method[, specifier]) with the following possibilities:
    ('const', constant): a constant group name for all sequences
    """
    method = groupspec[0]
    spec = groupspec[1] if len(groupspec) > 1 else None
    if method == 'const':
        if spec is None:
            raise ValueError('groupby "const" needs an argument (the constant)')
        return lambda path, header: spec
    if method == 'all':
        return None
    raise NotImplementedError('this groupby functionality is not yet implemented: {groupspec}')


def get_group_sizes(files, groupmap, offset=0, override=None):
    lengths = Counter()
    if files is None:
        return lengths
    if override is not None:
        if groupmap is None:
            lengths["all"] = override
            return lengths
        for (_, _, group) in grouped_sequences(files, groupmap):
            lengths[group] = override
        return lengths
    # count total lengths of sequences
    for (_, seq, group) in grouped_sequences(files, groupmap):
        lengths[group] += len(seq) + offset
    return lengths


def grouped_sequences(files, groupby=None, format=None):
    """
    For each sequence in the given list/tuple of files or (single) file path,
    yield a triple (header, sequence, group),
    according to the given groupby function.

    The file format (.fast[aq][.gz]) is recognized automatically,
    but can be explicitly given by format="fasta" or format="fastq".
    """
    if isinstance(files, (list, tuple)):
        for f in files:
            yield from _grouped_sequences_from_a_file(f, groupby, format=format)
    else:
        yield from _grouped_sequences_from_a_file(files, groupby, format=format)


def _grouped_sequences_from_a_file(fname, groupby=None, format=None):
    few = fname.lower().endswith
    if format is not None:
        format = format.lower()
    if format == "fasta" or few((".fa", ".fna", ".fasta", ".fa.gz", ".fna.gz", ".fasta.gz")):
        if groupby is not None:
            reads = _fasta_reads_from_filelike
            for (h, s) in _universal_reads(fname, reads):
                g = groupby(fname, h)
                yield (h, s, g)
        else:
            reads = _fasta_seqs_from_filelike
            for s in _universal_reads(fname, reads):
                yield (True, s, "all")
    elif format == "fastq" or few((".fq", ".fastq", ".fq.gz", ".fastq.gz")):
        if groupby is not None:
            reads = _fastq_reads_from_filelike
            for (h, s, q) in _universal_reads(fname, reads):
                g = groupby(fname, h)
                yield (h, s, g)
        else:
            reads = _fastq_seqs_from_filelike
            for s in _universal_reads(fname, reads):
                yield (True, s, "all")
    else:
        raise FormatError("format of file '{fname}' not recognized")


####################################################################

def get_sizebounds(files):
    """
    return a pair (sumbound, maxbound), where
    sumbound is an upper bound on the sum of the number of q-grams in the given 'files',
    maxbound is an upper bound on the maximum of the number of q-grams in one entry in 'files'.
    """
    if files is None:
        return (0, 0)
    sb = mb = 0
    for (_, seq, _) in grouped_sequences(files):
        ls = len(seq)
        sb += ls
        if ls > mb:  mb = ls
    return (sb, mb)


def number_of_sequences_in(fname):
    # TODO: this only works with Linux / Mac
    few = fname.lower().endswith  # few = "filename ends with"
    if few((".fa", ".fasta")):
        x = check_output(["grep", "-c", "'^>'", fname])
        return int(x)
    if few((".fa.gz", ".fasta.gz")):
        x = check_output(["gzcat", fname, "|", "grep", "-c", "'^>'"])
        return int(x)
    if few((".fq", ".fastq")):
        x = check_output(["wc", "-l", fname])
        n = int(x.strip().split()[0])
        return n//4
    if few((".fq.gz", ".fastq.gz")):
        x = check_output(["gzcat", fname, "|", "wc", "-l"])
        n = int(x.strip().split()[0])
        return n//4


# FASTQ checking ####################################################

def fastqcheck(args):
    files = args.sequences
    if args.paired:
        success = fastqcheck_paired(list(zip(*[iter(files)]*2)), args)
    else:
        success = fastqcheck_single(files, args)
    exitcode = 0 if success else 1
    sys.exit(exitcode)


def fastqcheck_paired(filepairs, args):
    success = True
    for (f1, f2) in filepairs:
        print(f"Checking {f1}, {f2}...")
        msg = "OK"
        try:
            for entry1, entry2 in zip(fastq_reads(f1), fastq_reads(f2)):
                c1 = entry1[0].split()[0]
                c2 = entry2[0].split()[0]
                if c1 != c2:
                    raise FormatError(f"headers {c1.decode()} and {c2.decode()} do not match")
        except FormatError as err:
            success = False
            msg = "FAILED: " + str(err)
        print(f"{f1}, {f2}: {msg}")
    return success


def fastqcheck_single(files, args):
    success = True
    for f in files:
        print(f"Checking {f}...")
        msg = "OK"
        try:
            for entry in fastq_reads(f):
                pass
        except FormatError as err:
            success = False
            msg = "FAILED: " + str(err)
        print(f"{f}: {msg}")
    return success


# FASTA header extraction ###########################################

_SEPARATORS = {'TAB': '\t', 'SPACE': ' '}

def fastaextract(args):
    """extract information from FASTA headers and write in tabular form to stdout"""
    files = args.files
    items = args.items
    seps = args.separators
    sfx = [args.suffix] if args.suffix else []
    seps = [_SEPARATORS.get(sep.upper(), sep) for sep in seps]
    if items is None: 
        items = list()
        seps = list()
    if len(seps) == 1:
        seps = seps * len(items)
    seps = [""] + seps
    head = ['transcript_id'] + items

    first = [x for t in zip(seps, head) for x in t] + sfx
    print("".join(first))
    for f in files:
        for (header, _) in fasta_reads(f):
            infolist = get_header_info(header, items, ":", seps) + sfx
            print("".join(infolist))


def get_header_info(header, items, assigner, seps):
    fields = header.decode("ascii").split()
    assigners = [i for (i,field) in enumerate(fields) if assigner in field]
    if 0 in assigners: 
        assigners.remove(0)
    D = dict()
    if items is None: items = list()
    for j, i in enumerate(assigners):
        field = fields[i]
        pos = field.find(assigner)
        assert pos >= 0
        name = field[:pos]
        nexti = assigners[j+1] if j+1 < len(assigners) else len(fields)
        suffix = "_".join(fields[i+1:nexti])
        if len(suffix)==0:
            D[name] = field[pos+1:]
        else:
            D[name] = field[pos+1:] + '_' + suffix
    # dictionary D now has values for all fields
    L = [seps[0], fields[0]]
    for i, item in enumerate(items):
        if item in D:
            L.append(seps[i+1])
            L.append(D[item])
    return L


# FASTQ name guessing and argument parsing   ##########################

def guess_pairs(fastq, replace):
    if replace != 1 and replace != 2:
        raise ValueError("ERROR: guess_pairs: Parameter 'replace' must be 1 or 2")
    # replace=1: Replace rightmost occurrence of '_R2' by '_R1'
    # replace=2: Replace rightmost occurrence of '_R1' by '_R2'
    orig = str(3 - replace)
    o = "_R" + orig
    r = "_R" + str(replace)
    pairnames = list()
    for name in fastq:
        start = name.rfind(o)
        if start < 0:
            raise ValueError(f"ERROR: guess_pairs: FASTQ file name '{name}' does not contain '{o}'")
        pairnames.append(name[:start] + r + name[start+len(o):])
    return pairnames


def parse_fastq_args(args):
    # parses args.{first, second, single, guess_pairs}
    argerror = ArgumentParser.error
    paired = False
    if args.first or args.second:
        paired = True
        if args.guess_pairs and args.first:
            if args.second:
                argerror("ERROR: With given --first, cannot specify --second together with --guess-pairs")
            args.second = guess_pairs(args.first, 2)
        elif args.guess_pairs and args.second:
            args.first = guess_pairs(args.second, 1)
        if len(args.first) != len(args.second):
            argerror(f"ERROR: --first and --second must specify the same number of files ({len(args.first)} vs {len(args.second)})")
        if args.first is None or args.second is None:
            argerror(f"ERROR: not enough information given for paired reads")
    if args.single:
        if paired:
            argerror(f"ERROR: cannot use --single together with --first/--second")
    fastq = (args.single,) if single else (args.first, args.second)
    return paired, fastq


