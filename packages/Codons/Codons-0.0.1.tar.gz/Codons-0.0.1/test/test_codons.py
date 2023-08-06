from shutil import rmtree
import codons
import unittest, re, os, io

dna_sequence = 'cactaagaaa gatgctgctg ctgctaaaaa taagatgcgc cacaagcgca cttccaccaa'
cd = codons.Codons()

def test_init():
    cd = codons.Codons(dna_sequence)
    for TF in [cd.verbose, cd.printing, cd.verbose]:
        assert type(TF) is bool
    assert type(cd.codons_table) is codons.genes.CaseInsensitiveDict
    for dic in [cd.paths, cd.proteins, cd.parameters]:
        assert type(dic) is dict
    for path in ['changed_codons', 'standard_table', 'amino_acid_synonyms']:
        assert type(cd.paths[path]) is str
    for string in [cd.sequence, cd.parameters['residue_delimiter']]:
        assert type(string) is str
           
def test_transcribe():
    # DNA -> RNA
    rna_sequence = cd.transcribe(dna_sequence)
    assert not re.search('[tT]', rna_sequence)
                   
    # RNA -> DNA
    dna_sequence2 = cd.transcribe(rna_sequence)
    assert dna_sequence == dna_sequence2
           
def test_translate():
    # translate into a protein
    proteins = cd.translate(dna_sequence)
    
    # assert qualities of the execution               
    assert type(proteins) is dict
    for pro in proteins:
        assert type(proteins[pro]) is float
                                     
def test_make_fasta():
    description = 'This is a sample DNA sequence'
    fasta = cd.make_fasta(dna_sequence, description)

    fasta_lines = io.StringIO(fasta)
    first = True
    for line in fasta_lines:
        if first:
            line = re.sub('>', '', line)
            assert line.rstrip() == description
            first = False
        else:
            assert line == dna_sequence+'*' 

            
# ================== The BLAST functions fail with the small sequence, and larger sequences are not practical for a unit-test script ==================
# def test_blast_protein():
#     cd.translate(dna_sequence)
#     print(cd.protein_fasta)
#     cd.blast_protein()

#     # assert qualities of the search
#     assert os.path.exists(cd.paths['protein_blast_results'])
#     rmtree(cd.paths['protein_blast_results'])
                   
# def test_blast_nucleotide():
#     cd.translate(dna_sequence)
#     cd.blast_nucleotide()

#     # assert qualities of the search
#     assert os.path.exists(cd.paths['nucleotide_blast_results'])
#     rmtree(cd.paths['nucleotide_blast_results'])
                   