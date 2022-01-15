from biobb_disgenet.disgenet.da_disgenet import da_disgenet

prop = {
        'disease_id':'C0002395',
        'limit': '10',
        'format': 'json'
        }

da_disgenet(output_file_path='output_genes', retrieve_by="similarity", properties=prop)
