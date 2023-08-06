# -*- coding: utf-8 -*-
"""
Created on Wed Jan 26 00:33:29 2022

@author: Andrew Freiburger
"""
from scipy.constants import hour
from Bio.Blast import NCBIWWW
from chemw import Proteins
#from pprint import pprint
from math import ceil
from glob import glob
import datetime
import json, os, re

# allows case insensitive dictionary searches
class CaseInsensitiveDict(dict):   # sourced from https://stackoverflow.com/questions/2082152/case-insensitive-dictionary
    @classmethod
    def _k(cls, key):
        return key.lower() if isinstance(key, str) else key

    def __init__(self, *args, **kwargs):
        super(CaseInsensitiveDict, self).__init__(*args, **kwargs)
        self._convert_keys()
        
    def __getitem__(self, key):
        return super(CaseInsensitiveDict, self).__getitem__(self.__class__._k(key))
    
    def __setitem__(self, key, value):
        super(CaseInsensitiveDict, self).__setitem__(self.__class__._k(key), value)
        
    def __delitem__(self, key):
        return super(CaseInsensitiveDict, self).__delitem__(self.__class__._k(key))
    
    def __contains__(self, key):
        return super(CaseInsensitiveDict, self).__contains__(self.__class__._k(key))
    
    def has_key(self, key):
        return super(CaseInsensitiveDict, self).has_key(self.__class__._k(key))
    
    def pop(self, key, *args, **kwargs):
        return super(CaseInsensitiveDict, self).pop(self.__class__._k(key), *args, **kwargs)
    
    def get(self, key, *args, **kwargs):
        return super(CaseInsensitiveDict, self).get(self.__class__._k(key), *args, **kwargs)
    
    def setdefault(self, key, *args, **kwargs):
        return super(CaseInsensitiveDict, self).setdefault(self.__class__._k(key), *args, **kwargs)
    
    def update(self, E=None, **F):
        super(CaseInsensitiveDict, self).update(self.__class__(E))
        super(CaseInsensitiveDict, self).update(self.__class__(**F))
        
    def _convert_keys(self):
        for k in list(self.keys()):
            v = super(CaseInsensitiveDict, self).pop(k)
            self.__setitem__(k, v)
            
            

class Codons():
    def __init__(self,
                 sequence: str = None,  # the genetic sequence can be optionally provided, for easy use in the other functions.
                 codons_table: str = 'standard', # the translation table for codons to amino acids
                 amino_acids_form: str = 'one_letter', # selects the scale of amino acid nomenclature
                 hyphenated: bool = None, # selects whether the printed protein will be hyphenated between the protein residues
                 verbose: bool = False,
                 printing: bool = True
                 ):
        self.verbose = verbose
        self.printing = printing
        self.proteins = {}
        self.transcribed_sequence = None
        self.protein_blast_results = None
        self.nucleotide_blast_results = None
        self.gene_fasta = None
        self.protein_fasta = None
        self.protein_mass = Proteins()
        
        # define the simulation paths
        self.paths = {}
        self.paths['changed_codons'] = os.path.join(os.path.dirname(__file__), 'rosetta_stone', 'changed_codons.json')
        self.paths['standard_table'] = os.path.join(os.path.dirname(__file__), 'rosetta_stone', 'standard_table.json')
        self.paths['amino_acid_synonyms'] = os.path.join(os.path.dirname(__file__), 'rosetta_stone', 'amino_acid_synonyms.json')
        
        self.parameters = {}
        self.parameters['residue_delimiter'] = '-' 
        
        # refine the sequence into the FASTA format
        self.sequence = sequence
        
        # define the proper codons table
        self.codons_table = json.load(open(self.paths['standard_table']))
        if codons_table != 'standard':
            self._convert_codon_tables(codons_table)    
        self.codons_table = CaseInsensitiveDict(self.codons_table)
        
        # define the amino acid nomenclature
        if amino_acids_form != 'full_name':
            self.amino_acid_synonyms = json.load(open(self.paths['amino_acid_synonyms']))
            for codon in self.codons_table:
                amino_acid = self.codons_table[codon] 
                if amino_acid not in ['stop', 'start']:
                    self.codons_table[codon] = self.amino_acid_synonyms[amino_acid][amino_acids_form]
            
            if amino_acids_form == 'one_letter' and not hyphenated:
                self.parameters['residue_delimiter'] = ''
                
    
    def _convert_codon_tables(self,codons_table):
        # convert the standard table into the desired table
        self.changed_codons = json.load(open(self.paths['changed_codons']))
        if codons_table not in self.changed_codons:
            raise IndexError(f'The {codons_table} parameter is not presently supported by the options: {list(self.changed_codons.keys())}. Edit the < changed_codons.json > file to offer the exchanges that you desire for your simulation.')
            
        self.changed_codons = self.changed_codons[codons_table]
        for cd in self.changed_codons:
            self.codons_table[cd] = self.changed_codons[cd]
    
    def _read_fasta(self,
                    fasta_path: str = None,  # the path to the fasta file
                    fasta_link: str = None,  # the path to the fasta file
                    ):
        # import and parse fasta-formatted files        
        if fasta_path is not None:
            with open(fasta_path) as input:
                self.fasta_lines = input.readlines()   
        elif fasta_link is not None:
            sequence = requests.get(fasta_link).content
            self.fasta_lines = io.StringIO(sequence.decode('utf-8')).readlines()
    
        sequence = ''
        for line in self.fasta_lines:
            if not re.search('^>', line):
                line = line.rstrip()
                sequence += line
            else:
                description = line
        return sequence, description
    
    def _paths(self, 
               export_name = None, 
               export_directory = None
               ):
        # define the simulation_path
        if export_directory is None:
            export_directory = os.getcwd()
        elif not os.path.exists(export_directory):
            raise ValueError('The provided directory does not exist')

        tag = ''
        if self.nucleotide_blast_results:
            tag = 'BLASTn'
        if self.protein_blast_results:
            if tag == 'BLASTn':
                tag = 'BLAST'
            else:
                tag = 'BLASTp'
        elif self.proteins != {}:
            tag = f'{len(self.proteins)}_proteins'
        elif self.transcribed_sequence:
            tag = f'{self.transcription}'
        if export_name is None:
            export_name = '-'.join([re.sub(' ', '_', str(x)) for x in ['codons', tag]])
            
        count = -1
        export_path = os.path.join(export_directory, export_name)
        file_extension = ''
        while os.path.exists(export_path):
            count += 1
            if re.search('(\.[a-zA-Z]+$)', export_path):
                file_extension = re.search('(\.[a-zA-Z]+$)', export_path).group()
                export_path = re.sub(file_extension, '', export_path)
                
            if not re.search('(-[0-9]+$)', export_path):
                export_path += f'-{count}'   
            else:
                export_path = re.sub('([0-9]+)$', str(count), export_path)
                
            export_path += file_extension
        
        # clean the export name
        export_path = re.sub('(--)', '-', export_path)
        export_path = re.sub('(-$)', '', export_path)
            
        return export_path
            
    def make_fasta(self,
                   sequence: str,  # the genetic nucleotide sequence
                   description: str = 'sequence', # the description of the genetic or protein sequence
                   export_path: str = None
                   ):
        if sequence is None:
            return None
        if not re.search('\*', sequence):
            sequence += '*'
            
        fasta_file = '\n'.join([f'>{description}',sequence])
        if export_path is not None:
            with open(export_path, 'w') as out:
                out.write(fasta_file)
        
        return fasta_file
            
    def transcribe(self,
                   sequence: str = None, # the genomic code as a string
                   description: str = '',  # a description of the sequence
                   fasta_path: str = None,  # the path to the fasta file
                   fasta_link: str = None,  # the path to the fasta file
                   ):
        if sequence:
            self.sequence = sequence
            self.gene_fasta = self.make_fasta(self.sequence, ' - '.join(['Genetic_sequence', f'{len(self.sequence)}_bps']))
        elif fasta_path:
            self.sequence, description = self._read_fasta(fasta_path)
        elif fasta_link:
            self.sequence, description = self._read_fasta(fasta_link = fasta_link)
            
        # determine the capitalization of the sequence
        for ch in sequence:
            if re.search('[a-zA-Z]',ch): 
                upper_case = ch.isupper()
                break
            
        # substitute the nucleotides with the appropriate capitalization
        self.transcription = 'DNA_to_RNA'
        if re.search('u|U', self.sequence):
            self.transcription = 'RNA_to_DNA'
            if upper_case:
                self.transcribed_sequence = re.sub('U', 'T', self.sequence)
            else:
                self.transcribed_sequence = re.sub('u', 't', self.sequence)
        if re.search('t|T', self.sequence):
            if upper_case:
                self.transcribed_sequence = re.sub('T', 'U', self.sequence)
            else:
                self.transcribed_sequence = re.sub('t', 'u', self.sequence)
                
        print('The sequence is transcribed.')
        if not description:
            description = f'>Transcribed sequence from {self.transcription}'
        self.transcribed_fasta = self.make_fasta(self.transcribed_sequence, description)
        return self.transcribed_sequence
        
        
    def translate(self,
                 sequence: str = None, # the genomic code as a string
                 description: str = None,  # a description of the sequence
                 fasta_path: str = None,  # the path to the fasta file
                 fasta_link: str = None,  # the path to the fasta file
                 ):
        if sequence:
            self.sequence = sequence
            self.gene_fasta = self.make_fasta(self.sequence, ' - '.join(['Genetic_sequence', f'{len(self.sequence)}_bps']))
        elif fasta_path:
            self.sequence, description = self._read_fasta(fasta_path)
        elif fasta_link:
            self.sequence, description = self._read_fasta(fasta_link = fasta_link)
            
        self.protein_fasta = []
        self.missed_codons = []
        codon = ''
        amino_acids = None
        for nuc in self.sequence:
            if re.search('[atucg]', nuc, flags = re.IGNORECASE):
                codon += nuc
                if len(codon) == 3:
                    if codon not in self.codons_table:
                        self.missed_codons.append(codon)
                    else:
                        amino_acid = self.codons_table[codon]
                        if amino_acid == 'start':
                            amino_acids = []
                        elif amino_acid == 'stop' and type(amino_acids) is list:
                            if len(amino_acids) >= 1:
                                protein = self.parameters['residue_delimiter'].join(amino_acids)
                                mass = self.protein_mass.mass(protein)
                                
                                self.proteins[protein] = mass
                                if not description:
                                    description = ' - '.join(['Protein', f'{len(protein)}_residues', f'{mass}_amu'])
                                fasta_file = self.make_fasta(protein, description)
                                self.protein_fasta.append(fasta_file)
                                amino_acids = None
                        else:
                            if type(amino_acids) is list and re.search('[a-z]+',amino_acid, flags = re.IGNORECASE):
                                amino_acids.append(amino_acid)
                                if self.verbose:
                                    print(codon, '\t', amino_acid)
                    
                    codon = ''
                    
        self.protein_fasta = '\n'.join(self.protein_fasta)
        if self.printing:
           print(self.protein_fasta)
           if self.missed_codons != []:
               print(f'The {self.missed_codons} codons were not captured by the employed codons table.')
            
        return self.proteins
    
    def blast_protein(self,  # https://blast.ncbi.nlm.nih.gov/Blast.cgi?PROGRAM=blastp&PAGE_TYPE=BlastSearch&LINK_LOC=blasthome
                      sequence: str = None,
                      database: str = 'nr', # the blastp database that will be searched with the collected FASTA sequences
                      description: str = '',  # a description of the sequence
                      fasta_path: str = None, # The path to a fasta file
                      fasta_link: str = None,  # the path to the fasta file
                      export_name = None, 
                      export_directory = None
                      ):
        if sequence:
            self.sequence = sequence 
            self.protein_fasta = self.make_fasta(sequence, description) 
        elif fasta_path:
            with open(fasta_path) as input:
                self.protein_fasta = input.read() 
        elif fasta_link:
            sequence = requests.get(fasta_link).content
            self.protein_fasta = io.StringIO(sequence.decode('utf-8')).read()
            
        # estimate the completion time
        estimated_time = datetime.datetime.now()+datetime.timedelta(seconds = len(self.protein_fasta)/2)    # approximately 1/2 second per amino acid   
        print(f'The database search for the parameterized protein(s) will complete circa {estimated_time}.')
        
        # acquire the BLAST results
        self.protein_blast_results = NCBIWWW.qblast('blastp', database, self.protein_fasta)
        
        # export the content
        self.export(export_name, export_directory) 
        self.paths['protein_blast_results'] = os.path.join(self.export_path, 'protein_blast_results.xml')
        with open(self.paths['protein_blast_results'], 'w') as protein_data:
            protein_data.write(self.protein_blast_results.read())
        
    def blast_nucleotide(self,
                         sequence: str = None,
                         database: str = 'nt',
                         description: str = '',  # a description of the sequence
                         fasta_path: str = None, # The path to a fasta file
                         fasta_link: str = None,  # the path to the fasta file
                         export_name = None, 
                         export_directory = None
                         ):
        self.nucleotide_blast_results = []
        if sequence:
            self.sequence = sequence 
            self.gene_fasta = self.make_fasta(sequence, description) 
        elif fasta_path:
            with open(fasta_path) as input:
                self.gene_fasta = input.read() 
        elif fasta_link:
            sequence = requests.get(fasta_link).content
            self.gene_fasta = io.StringIO(sequence.decode('utf-8')).read()
            
        # estimate the completion time
        estimated_length = len(self.gene_fasta)/2
        estimated_time = datetime.datetime.now()+datetime.timedelta(seconds = estimated_length)    # approximately 1 second per nucleic acid
        print(f'The database search for the parameterized genetic sequence will complete circa {estimated_time}, in {estimated_length/hour} hours.')
        
        # acquire the BLAST results
        if export_name is None:
            export_name = 'codons-BLASTn'
        self.export(export_name, export_directory)
        self.paths['nucleotide_blast_results'] = [os.path.join(self.export_path, 'nucleotide_blast_results.xml')]
        
        section_size = 2000
        sections = ceil(len(self.gene_fasta)/section_size)
        sequence_sections = [self.gene_fasta[i*section_size:(i+1)*section_size] for i in range(0, sections)]
        for sequence in sequence_sections:
            nucleotide_blast_result = NCBIWWW.qblast('blastn', database, self.gene_fasta)
            result = nucleotide_blast_result.read()
            self.nucleotide_blast_results.append(result)
            
            # export this modular portion
            export_path = self._paths('nucleotide_blast_results.xml', self.export_path)
            self.paths['nucleotide_blast_results'].append(export_path)
            with open(self.paths['nucleotide_blast_results'][-1], 'w') as nucleotide_data:
                nucleotide_data.write(result)
            
            print(f'Section {sequence_sections.index(sequence)+1}/{sections} is completed: {datetime.datetime.now()}')
            
        # remove the parceled information and export a new combined file
        self.nucleotide_blast_results = '\n\n'.join(self.nucleotide_blast_results)
        for xml in glob(os.path.join(self.export_path, '*.xml')):
            os.remove(xml)
            
        with open(self.paths['nucleotide_blast_results'][0], 'w') as nucleotide_data:
            nucleotide_data.write(self.nucleotide_blast_results)
                
    def export(self, export_name = None, export_directory = None):
        # define the simulation_path
        self.export_path = self._paths(export_name, export_directory)
        if not os.path.exists(self.export_path):
            os.mkdir(self.export_path)
        
        # export the genetic and protein sequences
        self.paths['genetic_sequence'] = os.path.join(self.export_path, 'genetic_sequence.fasta')
        with open(self.paths['genetic_sequence'], 'w') as genes:
            genes.write(self.gene_fasta)
            
        if self.proteins != {}:
            self.paths['protein_sequence'] = os.path.join(self.export_path, 'protein_sequence.fasta')
            with open(self.paths['protein_sequence'], 'w') as proteins:
                proteins.write(self.protein_fasta)
            
        if self.transcribed_sequence:
            self.paths['transcribed_sequence'] = os.path.join(self.export_path, 'transcribed_sequence.fasta')
            with open(self.paths['transcribed_sequence'], 'w') as genes:
                genes.write(self.transcribed_fasta)                 