#!/usr/bin/env python3

"""Module containing the BioBBs DisGeNET class and the command line interface."""
import argparse
import shutil
from pathlib import PurePath
from biobb_common.generic.biobb_object import BiobbObject
from biobb_common.configuration import  settings
from biobb_common.tools import file_utils as fu
from biobb_common.tools.file_utils import launchlogger
from biobb_disgenet.disgenet.common import *


class DDADisgenet(BiobbObject):
    """
    | biobb_disgenet Disease Association Disgenet
    | This class is for downloading a Disease Disease Associations file from DisGeNET database.
    | Wrapper for the DisGeNET database `https://www.disgenet.org` and the  DisGeNET REST API ´https://www.disgenet.org/api/´ for downloading available collections of genes and variants associated data to human diseases.

    Args:
        shared_by (str): Configuration params to pass for the retrieval of the association on the REST API (gene, uniprot_entry, disease, source, evidences_gene, evidences_disease)
        output_file_path (str): Path to the output file, that can be in format TSV, JSON or XML. 
        properties (dict - Python dict containing the properties for the API interrogation, considering also the credentials of the user to the database):
            * **source** (*str*) - ("ALL") Source of the associations (CURATED, INFERRED, ANIMAL_MODELS, ALL, BEFREE, CGI, CLINGEN, CLINVAR, CTD_human, CTD_mouse, CTD_rat, GENOMICS_ENGLAND, GWASCAT, GWASDB, HPO, LHGDN, MGD, ORPHANET, PSYGENET, RGD, UNIPROT).
            * **disease_vocabulary** (*str*) - Disease vocabulary (icd9cm, icd10, mesh, omim, do, efo, nci, hpo, mondo, ordo).
            * **pvalue** (*str*) - (None) Pvalue of the disease-disease score range.
            * **format** (*str*) - ("json") Format output file.
            * **limit** (*str*) - ("10") Number of disease to retrieve.
            * **remove_tmp** (*bool*) - (True) [WF property] Remove temporal files.
            * **restart** (*bool*) - (False) [WF property] Do not execute if output files exist.
            * **container_path** (*str*) - (None)  Path to the binary executable of your container.
            * **container_image** (*str*) - (None) Container Image identifier.
            * **container_volume_path** (*str*) - ("/data") Path to an internal directory in the container.
            * **container_working_dir** (*str*) - (None) Path to the internal CWD in the container.
            * **container_user_id** (*str*) - (None) User number id to be mapped inside the container.
            * **container_shell_path** (*str*) - ("/bin/bash") Path to the binary executable of the container shell.


    Examples:
        This is a use example of how to use the building block from Python:

            from biobb_disgenet.disgenet.dda_disgenet import dda_disgenet

            prop = { 
                'disease_id': 'C0002395',
                'source': 'source', 
                'pvalue':'pvalue',
                'vocabulary':'vocabulary',
                'format': 'format',
                'limit': 'limit'
            }
            dda_disgenet(shared_by='genes',
                    output_file_path='/path/to/associationsFile',
                    properties=prop)

    Info:

    """

    def __init__(self, retrieve_by, output_file_path, properties = None, **kwargs) -> None:
        properties = properties or {}

        # 2.0 Call parent class constructor
        super().__init__(properties)

        # Input/Output files
        self.io_dict = { 
                'in': {'retrieve_by': retrieve_by}, 
            'out': {'output_file_path': output_file_path }
        }

        # Properties specific for BB
        self.source = properties.get('source', "ALL")
        self.pvalue = properties.get('pvalue', None)
        self.format = properties.get('format', "json")
        self.limit = properties.get('limit', '10')
        self.properties = properties

        # Check the properties
        self.check_properties(properties)

    @launchlogger
    def launch(self) -> int:
        """Execute the :class:`DDADisgenet <disgenet.dda_disgenet.DDADisgenet>` object."""
        
        # Setup Biobb
        if self.check_restart(): return 0
        self.stage_files()
        
        # Check mandatory params that is gene_id
        check_mandatory_property(self.properties, 'limit', self.out_log, self.__class__.__name__)
        output_path = check_output_path(self.io_dict["out"]["output_file_path"], False, "output", self.properties["format"], self.out_log, self.__class__.__name__)

        # Try1 function
        response = dda_session(self.io_dict["in"]["retrieve_by"], self.properties, self.out_log, self.global_log)
        new_keys, request = extension_request(response, self.io_dict["in"]["retrieve_by"], self.properties)
        auth_session(request, new_keys, output_path, self.out_log, self.global_log)

        return 0


def dda_disgenet(retrieve_by: str , output_file_path: str, properties: dict = None, **kwargs) -> int:
    """Create :class:`DDADisgenet <disgenet.dda_disgenet.DDADisgenet>` class and
    execute the :meth:`launch() <disgenet.dda_disgenet.DDADisgenet.launch>` method."""

    return DDADisgenet(retrieve_by=retrieve_by,
                       output_file_path=output_file_path,
                       properties=properties, **kwargs).launch()


def main():
    """Command line execution of this building block. Please check the command line documentation."""
    parser = argparse.ArgumentParser(description='This class is a wrapper for an associations call of teh DisGeNET database REST API.', formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999))
    parser.add_argument('--config', required=False, help='Configuration file')

    # Specific args of each building block
    required_args = parser.add_argument_group('required arguments')
    required_args.add_argument('--shared_by', required=False, help='Retrieval factor necessary to define the search of the associations; gene, uniprot entry, disease, source, evidence by disease, evidence by gene available choices.')
    required_args.add_argument('--output_file_path', required=True, help='Description for the output file path. Accepted formats: json, csv or html.')

    args = parser.parse_args()
    config = args.config if args.config else None
    properties = settings.ConfReader(config=config).get_prop_dic()

    # Specific call of each building block
    dda_disgenet(shared_by=args.shared_by,
                 output_file_path=args.output_file_path,
                 properties=properties)


if __name__ == '__main__':
    main()

