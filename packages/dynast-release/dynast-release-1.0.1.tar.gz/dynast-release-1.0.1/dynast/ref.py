import math
import os
import tempfile
from typing import Dict, Optional

from . import utils
from .logging import logger


def STAR_genomeGenerate(
    fasta_path: str,
    gtf_path: str,
    index_dir: str,
    n_threads: int = 8,
    memory: int = 16 * 1024**3,
    temp_dir: Optional[str] = None,
) -> Dict[str, str]:
    """Generate a STAR index from a reference.

    Args:
        fasta_path: Path to genome fasta
        gtf_path: Path to GTF annotation
        index_dir: Path to output STAR index
        n_threads: Number of threads, defaults to `8`
        memory: *Suggested* memory to use (this is not guaranteed), in bytes
        temp_dir: Temporary directory

    Retuurns:
        Dictionary of generated index
    """
    if fasta_path.endswith('.gz'):
        plaintext_path = utils.mkstemp(dir=temp_dir)
        logger.warning(f'Decompressing {fasta_path} to {plaintext_path} because STAR requires a plaintext FASTA')
        utils.decompress_gzip(fasta_path, plaintext_path)
        fasta_path = plaintext_path
    if gtf_path.endswith('.gz'):
        plaintext_path = utils.mkstemp(dir=temp_dir)
        logger.warning(f'Decompressing {gtf_path} to {plaintext_path} because STAR requires a plaintext GTF')
        utils.decompress_gzip(gtf_path, plaintext_path)
        gtf_path = plaintext_path

    logger.debug(f'Calculating optimal STAR index parameters for {memory} bytes of memory')
    # Calculate genome length and number of FASTA entries
    genome_length = 0
    n_entries = 0
    with utils.open_as_text(fasta_path, 'r') as f:
        for line in f:
            if line.startswith('>'):
                n_entries += 1
            else:
                genome_length += len(line.strip())

    # Taken from STAR manual (https://github.com/alexdobin/STAR/blob/master/doc/STARmanual.pdf)
    # genomeSAindexNbases = min(14, log2(GenomeLength)/2 - 1)
    sa_index_n_bases = min(14, int(math.log2(genome_length) / 2 - 1))
    # genomeChrBinNbits = min(18, log2[max(GenomeLength/NumberOfReferences,ReadLength)])
    chr_bin_n_bits = min(18, int(math.log2(genome_length / n_entries)))

    # Adapted from Cellranger
    sa_index_memory = (4**sa_index_n_bases) * 8
    sa_sparse_d = max(
        1, math.ceil((8 * genome_length) / (max(1, memory - 2 * 1024**3) - genome_length - sa_index_memory))
    )
    min_memory = genome_length + sa_index_memory + 3 * 1024**3
    if memory < min_memory:
        raise Exception(f'STAR requires at least {min_memory} to index this reference.')

    logger.debug(
        'Calculated parameters: '
        f'genome_length={genome_length} '
        f'n_entries={n_entries} '
        f'sa_index_n_bases={sa_index_n_bases} '
        f'chr_bin_n_bits={chr_bin_n_bits} '
        f'sa_sparse_d={sa_sparse_d}'
    )

    logger.debug(f'Generating STAR index to {index_dir}')
    command = [utils.get_STAR_binary_path(), '--runMode', 'genomeGenerate']
    command += ['--genomeDir', index_dir]
    command += ['--genomeFastaFiles', fasta_path]
    command += ['--sjdbGTFfile', gtf_path]
    command += ['--runThreadN', n_threads]
    command += ['--limitGenomeGenerateRAM', memory]
    command += ['--genomeSAsparseD', sa_sparse_d]
    command += ['--genomeSAindexNbases', sa_index_n_bases]
    command += ['--genomeChrBinNbits', chr_bin_n_bits]
    command += [
        '--outTmpDir',
        os.path.join(temp_dir, f'{tempfile.gettempprefix()}{next(tempfile._get_candidate_names())}')
    ]

    utils.run_executable(command)

    return {'index': index_dir}


@logger.namespaced('ref')
def ref(
    fasta_path: str,
    gtf_path: str,
    index_dir: str,
    n_threads: int = 8,
    memory: int = 16 * 1024**3,
    temp_dir: Optional[str] = None
):
    """Main interface for the `ref command.

    Args:
        fasta_path: Path to genome fasta
        gtf_path: Path to GTF annotation
        index_dir: Path to output STAR index
        n_threads: Number of threads, defaults to `8`
        memory: *Suggested* memory to use (this is not guaranteed), in bytes
        temp_dir: Temporary directory
    """
    logger.info(f'Indexing FASTA {fasta_path} and GTF {gtf_path} with STAR')
    index_dir = STAR_genomeGenerate(
        fasta_path, gtf_path, index_dir, n_threads=n_threads, memory=memory, temp_dir=temp_dir
    )
