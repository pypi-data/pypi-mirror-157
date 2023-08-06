import os
import platform

PACKAGE_PATH = os.path.dirname(__file__)
PLATFORM = platform.system().lower()
BINS_DIR = os.path.join(PACKAGE_PATH, 'bins')
MODELS_DIR = os.path.join(PACKAGE_PATH, 'models')
MODEL_PATH = os.path.join(MODELS_DIR, 'pi.stan')
MODEL_NAME = 'pi'

RECOMMENDED_MEMORY = 16 * (1024**3)  # 16 GB

# Common arguments for all STAR runs
STAR_ARGUMENTS = {
    '--outSAMtype': ['BAM', 'SortedByCoordinate'],
    '--outSAMattributes': ['NH', 'HI', 'AS', 'NM', 'nM', 'MD', 'GX', 'GN'],
    # Defaults are 0.6, but we set a looser cutoff because we expect the
    # reads to have conversions.
    '--outFilterScoreMinOverLread': 0.3,
    '--outFilterMatchNminOverLread': 0.3,
}

# Additional arguments for STARsolo runs
STAR_SOLO_ARGUMENTS = {
    '--outSAMattributes': ['CR', 'CY', 'UR', 'UY', 'CB', 'UB', 'sS', 'sQ', 'sM'],
    '--soloFeatures': 'Gene',
    '--soloCBwhitelist': 'None',
}

NASC_ARGUMENTS = {
    '--outSAMmultNmax': 1,
    '--soloStrand': 'Forward',
    '--alignSJoverhangMin': 1000,
    '--alignSJDBoverhangMin': 1,
    '--outFilterMismatchNoverReadLmax': 1,
    '--outFilterMismatchNmax': 10,
    '--outFilterMismatchNoverLmax': 0.1,
    '--outFilterScoreMinOverLread': 0.66,
    '--outFilterMatchNminOverLread': 0.66,
    '--scoreDelOpen': -10000,
    '--scoreInsOpen': -10000,
}

BAM_PEEK_READS = 500000
BAM_REQUIRED_TAGS = ['MD']
BAM_READGROUP_TAG = 'RG'
BAM_BARCODE_TAG = 'CB'
BAM_UMI_TAG = 'UB'
BAM_GENE_TAG = 'GX'
BAM_CONSENSUS_READ_COUNT_TAG = 'RN'
COUNTS_SPLIT_THRESHOLD = 50000
VELOCITY_BLACKLIST = ['unassigned', 'ambiguous']
