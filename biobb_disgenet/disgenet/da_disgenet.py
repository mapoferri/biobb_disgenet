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


class DADisgenet(BiobbObject):
    """
    | biobb_disgenet Disease Attribute Disgenet
    | This class is for downloading a Disease Attribute request from DisGeNET database.
    | Wrapper for the DisGeNET database `https://www.disgenet.org` and the  DisGeNET REST API ´https://www.disgenet.org/api/´ for downloading available collections of genes and variants associated data to human diseases.

    Args:
        retrieve_by (str) (Optional): Configuration params to pass for the retrieval of the association on the REST API, not mandatory, in default is obtained by gene ID (uniprot_entry, source)
        output_file_path (str): Path to the output file, that can be in format TSV, JSON or XML. 
        properties (dict - Python dict containing the properties for the API interrogation, considering also the credentials of the user to the database):
            * **diseaseName** (*str*) - (None) Disease name recognized by the database.
            * **disease_id** (*str*) - (None) Disease id or a list of disease ids separated by commas.
            * **source** (*str*) - ("ALL") Source of the associations (CURATED, INFERRED, ANIMAL_MODELS, ALL, BEFREE, CGI, CLINGEN, CLINVAR, CTD_human, CTD_mouse, CTD_rat, GENOMICS_ENGLAND, GWASCAT, GWASDB, HPO, LHGDN, MGD, ORPHANET, PSYGENET, RGD, UNIPROT).
            * **max_dsi** (*str*) - (None) Max value of DSI range for the gene.
            * **min_dsi** (*str*)  - (None) Min value of DSI range for the gene.
            * **min_dpi** (*str*) - (None) Min value of DPI range for the gene.
            * **max_dpi** (*str*) - (None) Max value of DPI range for the gene.
            * **max_pli** (*str*) -  (None) Max value of pLI range for the gene.
            * **min_pli** (*str*) -  (None) Min value of pLI range for the gene.
            * **format** (*str*) - ("json") Format output file.
            * **limit** (*str*) - (None) Number of disease to retrieve.
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

            from biobb_disgenet.disgenet.DADisgenet import DADisgenet

            prop = {
                'disease_id':'disease_id',
                'source': 'source', 
                'min_dsi': 'min_dsi',
                'max_dsi': 'max_dsi',
                'min_dpi': 'min_dpi',
                'max_dpi': 'max_dpi',
                'min_pli': 'min_pli',
                'max_pli':'max_pli', 
                'format': 'format',
                'limit': 'limit'
            }
            DADisgenet(
                    retrieve_by='source',
                    output_file_path='/path/to/associationsFile',
                    properties=prop)

    Info:
            retrieve_by can be:
                disease, diseaseName, source, mappings, similarity

    """

    def __init__(self, output_file_path, retrieve_by=None, properties=None, **kwargs) -> None:
        properties = properties or {}

        super().__init__(properties)

        # Input/Output files
        self.io_dict = { 
                'in': {'retrieve_by': retrieve_by}, 
                'out': {'output_file_path': output_file_path} 
        }

        # Properties specific for BB
        self.source = properties.get('source', "ALL")
        self.vocabulary = properties.get('vocabulary', None)
        self.disease_id = properties.get('disease_id', None)
        self.diseaseName = properties.get('diseaseName', None)
        self.min_dsi = properties.get('min_dsi', None)
        self.max_dsi = properties.get('max_dsi', None)
        self.max_dpi = properties.get('max_dpi', None)
        self.min_dpi = properties.get('min_dpi', None)
        self.max_pli = properties.get('max_pli', None)
        self.min_pli = properties.get('min_pli', None)
        self.format = properties.get('format', "json")
        self.limit = properties.get('limit', None)
        self.properties = properties

        # Check the properties
        self.check_properties(properties)

    @launchlogger
    def launch(self) -> int:
        """Execute the :class:`DADisgenet <disgenet.da_disgenet.DADisgenet>` object."""

        # Setup Biobb
        if self.check_restart(): return 0
        self.stage_files()
        
        # Check mandatory params that is gene_id
        output_path = check_output_path(self.io_dict["out"]["output_file_path"], False, "output", self.properties["format"], self.out_log, self.__class__.__name__)
        response = da_session("disease", self.io_dict["in"]["retrieve_by"], self.properties, self.out_log, self.global_log)
        new_keys, request = extension_request(response, self.io_dict["in"]["retrieve_by"], self.properties)
        auth_session(request, new_keys, output_path, self.out_log, self.global_log)

        return 0


def da_disgenet(output_file_path: str, retrieve_by: str = None, properties: dict = None, **kwargs) -> int:
    """Create :class:`DADisgenet <disgenet.da_disgenet.DADisgenet>` class and
    execute the :meth:`launch() <disgenet.da_disgenet.DADisgenet.launch>` method."""

    return DADisgenet(output_file_path=output_file_path,
                      retrieve_by=retrieve_by,
                      properties=properties, **kwargs).launch()


def main():
    """Command line execution of this building block. Please check the command line documentation."""
    parser = argparse.ArgumentParser(description='This class is a wrapper for an associations call of teh DisGeNET database REST API.', formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999))
    parser.add_argument('--config', required=False, help='This file can be a YAML file, JSON file or JSON string')

    # Specific args of each building block
    required_args = parser.add_argument_group('required arguments')
    parser.add_argument('--retrieve_by', required=False, help='Retrieval factor necessary to define the search of the associations; gene, uniprot entry, disease, source, evidence by disease, evidence by gene available choices.')
    required_args.add_argument('--output_file_path', required=True, help='Description for the output file path. Accepted formats: json, csv or html.')

    args = parser.parse_args()
    config = args.config if args.config else None
    properties = settings.ConfReader(config=config).get_prop_dic()

    # Specific call of each building block
    da_disgenet(output_file_path=args.output_file_path,
                retrieve_by=args.retrieve_by,
                properties=properties)


if __name__ == '__main__':
    main()
