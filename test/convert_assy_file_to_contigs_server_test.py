from __future__ import print_function

import unittest
import os
import requests
import time

from os import environ
import json
try:
    from ConfigParser import ConfigParser  # py2 @UnusedImport
except:
    from configparser import ConfigParser  # py3 @UnresolvedImport @Reimport

from pprint import pprint

from biokbase.AbstractHandle.Client import AbstractHandle as HandleService  # @UnresolvedImport @IgnorePep8
from workspace.client import Workspace
from gaprice_convert_assy_file_to_contigs.gaprice_convert_assy_file_to_contigsImpl import gaprice_convert_assy_file_to_contigs  # @IgnorePep8
from gaprice_convert_assy_file_to_contigs.gaprice_convert_assy_file_to_contigsServer import MethodContext  # @IgnorePep8

FILE_LOC = 'data'


class convert_assy_file_to_contigsTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.token = environ.get('KB_AUTH_TOKEN')
        cls.callbackURL = environ.get('SDK_CALLBACK_URL')
        print('CB URL: ' + cls.callbackURL)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': cls.token,
                        'provenance': [
                            {'service': 'gaprice_convert_assy_file_to_contigs',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        config_file = environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('gaprice_convert_assy_file_to_contigs'):
            cls.cfg[nameval[0]] = nameval[1]
        cls.wsURL = cls.cfg['workspace-url']
        cls.shockURL = cls.cfg['shock-url']
        cls.hs = HandleService(url=cls.cfg['handle-service-url'],
                               token=cls.token)
        cls.wsClient = Workspace(cls.wsURL, token=cls.token)
        wssuffix = int(time.time() * 1000)
        wsName = 'test_gaprice_convert_assy_file_to_contigs_' + str(wssuffix)
        cls.wsinfo = cls.wsClient.create_workspace({'workspace': wsName})
        print('created workspace ' + cls.getWsName())
        cls.serviceImpl = gaprice_convert_assy_file_to_contigs(cls.cfg)
        cls.staged = {}
        cls.nodes_to_delete = []
        cls.handles_to_delete = []
        cls.setupTestData()
        print('\n\n=============== Starting tests ==================')

    @classmethod
    def tearDownClass(cls):

        print('\n\n=============== Cleaning up ==================')

        if hasattr(cls, 'wsinfo'):
            cls.wsClient.delete_workspace({'workspace': cls.getWsName()})
            print('Test workspace was deleted: ' + cls.getWsName())
        if hasattr(cls, 'nodes_to_delete'):
            for node in cls.nodes_to_delete:
                cls.delete_shock_node(node)
        if hasattr(cls, 'handles_to_delete'):
            cls.hs.delete_handles(cls.hs.ids_to_handles(cls.handles_to_delete))
            print('Deleted handles ' + str(cls.handles_to_delete))

    @classmethod
    def getWsName(cls):
        return cls.wsinfo[1]

    def getImpl(self):
        return self.serviceImpl

    @classmethod
    def delete_shock_node(cls, node_id):
        header = {'Authorization': 'Oauth {0}'.format(cls.token)}
        requests.delete(cls.shockURL + '/node/' + node_id, headers=header,
                        allow_redirects=True)
        print('Deleted shock node ' + node_id)

    @classmethod
    def make_ref(self, object_info):
        return str(object_info[6]) + '/' + str(object_info[0]) + \
            '/' + str(object_info[4])

    # Helper script borrowed from the transform service, logger removed
    @classmethod
    def upload_file_to_shock(cls, file_path):
        """
        Use HTTP multi-part POST to save a file to a SHOCK instance.
        """

        header = dict()
        header["Authorization"] = "Oauth {0}".format(cls.token)

        if file_path is None:
            raise Exception("No file given for upload to SHOCK!")

        with open(os.path.abspath(file_path), 'rb') as dataFile:
            files = {'upload': dataFile}
            print('POSTing data')
            response = requests.post(
                cls.shockURL + '/node', headers=header, files=files,
                stream=True, allow_redirects=True)
            print('got response')

        if not response.ok:
            response.raise_for_status()

        result = response.json()

        if result['error']:
            raise Exception(result['error'][0])
        else:
            return result["data"]

    @classmethod
    def upload_file_to_shock_and_get_handle(cls, test_file):
        '''
        Uploads the file in test_file to shock and returns the node and a
        handle to the node.
        '''
        print('loading file to shock: ' + test_file)
        node = cls.upload_file_to_shock(test_file)
        pprint(node)
        cls.nodes_to_delete.append(node['id'])

        print('creating handle for shock id ' + node['id'])
        handle_id = cls.hs.persist_handle({'id': node['id'],
                                           'type': 'shock',
                                           'url': cls.shockURL
                                           })
        cls.handles_to_delete.append(handle_id)

        md5 = node['file']['checksum']['md5']
        return node['id'], handle_id, md5, node['file']['size']

    @classmethod
    def setupTestData(cls):
        cls.stage_assy_files()
        cls.stage_empty_data()

    @classmethod
    def stage_empty_data(cls):
        src_obj_name = 'empty'
        src_type = 'Empty.AType'

        objdata = cls.wsClient.save_objects(
            {'workspace': cls.getWsName(),
             'objects': [{'name': src_obj_name,
                          'type': src_type,
                          'data': {}}]
             })[0]
        cls.staged[src_obj_name] = {'obj_info': objdata,
                                    'ref': cls.make_ref(objdata)
                                    }

    @classmethod
    def stage_assy_files(cls):
        cls.load_assy_file_data(
            'sample.fa', 'AssemblyFile.json', 'test_assy_file', 'assy_file')
        cls.load_assy_file_data(
            'sample.fa', 'AssemblyFile.json',
            'test_assy_file_bad_node', 'assy_file_bad_node',
            with_bad_node_id=True)
        cls.load_assy_file_data(
            'sample_missing_data.fa',
            'AssemblyFile.json',
            'test_assy_file_missing_data', 'assy_file_missing_data')
        cls.load_assy_file_data(
            'sample_missing_data_last.fa',
            'AssemblyFile.json',
            'test_assy_file_missing_data_last', 'assy_file_missing_data_last')
        cls.load_assy_file_data(
            'sample_missing_data_ws.fa',
            'AssemblyFile.json',
            'test_assy_file_missing_data_ws', 'assy_file_missing_data_ws')
        cls.load_assy_file_data(
            'empty.fa',
            'AssemblyFile.json',
            'test_assy_file_empty', 'assy_file_empty')

    @classmethod
    def load_assy_file_data(cls, fa_file, ws_file, src_obj_name, key,
                            with_bad_node_id=False):
        src_type = 'KBaseFile.AssemblyFile'
        test_file = os.path.join(FILE_LOC, fa_file)
        node_id, handle, _, _ = cls.upload_file_to_shock_and_get_handle(
            test_file)
        if (with_bad_node_id):
            node_id += '1'

        test_json = os.path.join(FILE_LOC, ws_file)
        with open(test_json) as assyjsonfile:
            assyjson = json.loads(assyjsonfile.read())
        assyjson['assembly_file']['file']['url'] = cls.shockURL
        assyjson['assembly_file']['file']['id'] = node_id
        assyjson['assembly_file']['file']['hid'] = handle

        objdata = cls.wsClient.save_objects(
            {'workspace': cls.getWsName(),
             'objects': [{'name': src_obj_name,
                          'type': src_type,
                          'data': assyjson}]
             })[0]
        cls.staged[key] = {'obj_info': objdata,
                           'node': node_id,
                           'ref': cls.make_ref(objdata)}

    def test_assyfile_to_cs_basic_ops(self):
        staged = self.staged['assy_file']
        res = self.getImpl().convert(
            self.ctx,
            {'workspace_name': self.getWsName(),
             'assembly_file': staged['obj_info'][1],
             'output_name': 'foobarbaz'
             })
        pprint(res)
