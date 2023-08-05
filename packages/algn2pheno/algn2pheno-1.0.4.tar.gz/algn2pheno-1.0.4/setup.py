# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['algn2pheno']

package_data = \
{'': ['*']}

install_requires = \
['biopython>=1.79,<2.0',
 'numpy>=1.3,<2.0',
 'pandas>=1.3.5,<2.0.0',
 'sqlalchemy>=1.4.4,<2.0.0']

entry_points = \
{'console_scripts': ['algn2pheno = algn2pheno.__main__:main']}

setup_kwargs = {
    'name': 'algn2pheno',
    'version': '1.0.4',
    'description': 'A bioinformatics tool for rapid screening of genetic features (nt or aa changes) potentially linked to specific phenotypes',
    'long_description': '# aln2pheno\n\n**A bioinformatics tool for rapid screening of genetic features (nt or aa changes) potentially linked to specific phenotypes**\n\n\nINTRODUCTION\n------------------\n\nThe **aln2pheno** module screens a amino acid/nucleotide alignment against a "genotype-phenotype" database and reports the repertoire of mutations of interest per sequences and their potential impact on phenotype.\n\n\nINPUT FILES\n----------------\n\nTable database in .tsv or .xlsx format \n\n**AND**        \n\nAlignment (nucleotide or amino acid)   \n\n\n(Mutation numbering will refer to the user-defined reference sequence included in the alignment).\n\n\nUSAGE\n----------------\n\n```bash\n\nusage: algn2pheno.py [-h] [--db DB] [--sheet SHEET] [--table TABLE]\n                     [--gencol GENCOL] [--phencol PHENCOL] -g GENE --algn ALGN\n                     -r REFERENCE [--nucl] [--odir ODIR] [--output OUTPUT]\n                     [--log LOG] [-f]\n\nparse arguments\n\noptional arguments:\n  -h, --help            show this help message and exit\n  --db DB               phenotype db. if excel, provide sheet name and columns\n                        numbers for genotype and phenotype data. if not excel,\n                        provide path to db, ensure 3 columns \'Mutation\',\n                        \'Phenotype category\' & \'Flag\'\n  --sheet SHEET, -s SHEET\n                        Give sheet name (gene name or \'Lineages\'). excel\n                        input.\n  --table TABLE, -t TABLE\n                        table name in db. default: pokay. sqlite input.\n  --gencol GENCOL       nr of column with genotype data. excel input.\n  --phencol PHENCOL     nr of column with phenotype data. excel input.\n  -g GENE, --gene GENE  Set gene or protein prefix\n  --algn ALGN           Input alignment file\n  -r REFERENCE, --reference REFERENCE\n                        Give full reference sequence as in alignment file (use\n                        quotation marks if this contains a space)\n  --nucl                provide if nucleotide alignment instead of amino acid.\n  --odir ODIR, -o ODIR  output directory\n  --output OUTPUT       Set output file prefix\n  --log LOG             logfile\n  -f, --force           overwrite existing files\n\n\n```\n\n\nHow to run (examples)\n----------------------\n\n1. database (.tsv) + amino acid alignment (SARS-CoV-2 Spike)\n\n```bash\npython algn2pheno.py --db database.tsv --algn alignment_aa_Spike.fasta -g S -r reference_header --odir output_folder --output output_prefix\n```\n\n2. database (.xlsx) + amino acid alignment (SARS-CoV-2 Spike)\n\n```bash\npython algn2pheno.py --db database.xlsx --algn alignment_aa_Spike.fasta --sheet S --gencol ["Mutation" column number] --phencol ["Phenotype category" column number] -g S -r reference_header --odir output_folder --output output_prefix\n```\n\nREQUIREMENTS\n-----------------\n\nThe input database must contain mutations and associated phenotypes, listed in columns named `Mutation` and `Phenotype category` respectively. An additional column `Flag` may be provided for the ".tsv" input format.\n\nIn the case of using an excel file as input, an intermediary .tsv database will be created. A "Flag" column will be generated automatically with Flags "D" and "P" to differentiate mutation(s) Directly associated with the phenotype ("D") and mutation(s) Partially associated with the phenotype (i.e., the mutation is Part of a constellation associated with that phenotype) ("P"). Constellation of mutations should be included in the same row separated by commas (e.g., H69del,H70del,L452R,N501Y). \n\nUndefined amino acids should be included as "X" in the protein alignment.\nUndefined nucleotides should be included as "N" in the gene alignment.\n\n**Modules:**\n\n> Main alignment to phenotype.\n  - python=3.7\n  - biopython\n  - numpy \n  - pandas\n\n> Further modules required to scrape Pokay database.\n  - openpyxl\n  - requests\n  - pygithub\n  - sqlalchemy\n  - beautifulsoup4\n  - lxml\n\n\nINSTALLATION\n-----------------\n\n- git clone this repository.\n- install and activate environment with required modules (see _pyenv.yml_).\n\nCONFIGURATION\n-----------------\n\nThis module does not require configuration.   \n\n\n\nMAIN OUTPUTS\n------------------------\n\n> **_full_mutation_report.tsv**: provides the repertoire of "Flagged mutations" (i.e., database mutations detected in the alignment), the list of "phenotypes" supported by those mutations of interest and the list of "All mutations" detected in alignment for each sequence.\n\n> **_flagged_mutation_report.tsv**: "Flagged mutation" binary matrix for all sequences and the "associated" phenotypes.\n\n\nOther intermediate outputs:\n\n> _all_mutation_matrix:  matrix of all mutations found in the alignment [mutations coded as 1 (presence), 0 (absence)]. At this stage, undefined amino acids ("X") or undefined nucleotides ("n") are not yet handled as no coverage positions.\n\n> _all_mutation_report: matrix of all mutations found in the alignment [mutations coded as 1 (presence), 0 (absence) or nc (no coverage) positions] and associated phenotypes for the mutations in the database.\n\n> _all_db_mutations_report: matrix of mutations in the database [mutations coded as 1 (presence), 0 (absence) or nc (no coverage) positions] and associated phenotypes, regardless if they were found or not in the alignment\n\n> database.CLEAN.tsv: conversion of the ".xlsx" database into a clean ".tsv" format adding the gene "prefix" (-g argument) to each mutation (similar to when providing a .tsv database with the three headers \'Mutation\', \'Phenotype category\' and \'Flag\')\n\nMAINTAINERS\n----------------\n\nCurrent maintainers:\n\n- Joao Santos (santosjgnd) \n\n- Bioinformatics Unit of the Portuguese National Institute of Health Dr. Ricardo Jorge (INSA) (insapathogenomics)\n\n\n\nCITATION\n----------\n\nIf you run algn2pheno, please cite:\n\nJoão D. Santos,  Carlijn Bogaardt, Joana Isidro, João P. Gomes, Daniel Horton, Vítor Borges (2022). Algn2pheno: A bioinformatics tool for rapid screening of genetic features (nt or aa changes) potentially linked to specific phenotypes.\n\n\nFUNDING\n----------------\n\nThis work was supported by funding from the European Union’s Horizon 2020 Research and Innovation programme under grant agreement No 773830: One Health European Joint Programme.\n\n',
    'author': 'SantosJGND',
    'author_email': 'dourado.jns@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/SantosJGND/algn2pheno',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
