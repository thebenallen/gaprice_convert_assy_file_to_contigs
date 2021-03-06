############################################################
#
# Autogenerated by the KBase type compiler -
# any changes made here will be overwritten
#
############################################################

try:
    import json as _json
except ImportError:
    import sys
    sys.path.append('simplejson-2.3.3')
    import simplejson as _json

import requests as _requests
import urlparse as _urlparse
import random as _random
import base64 as _base64
from ConfigParser import ConfigParser as _ConfigParser
import os as _os

_CT = 'content-type'
_AJ = 'application/json'
_URL_SCHEME = frozenset(['http', 'https'])


def _get_token(user_id, password,
               auth_svc='https://nexus.api.globusonline.org/goauth/token?' +
                        'grant_type=client_credentials'):
    # This is bandaid helper function until we get a full
    # KBase python auth client released
    auth = _base64.b64encode(user_id + ':' + password)
    headers = {'Authorization': 'Basic ' + auth}
    ret = _requests.get(auth_svc, headers=headers, allow_redirects=True)
    status = ret.status_code
    if status >= 200 and status <= 299:
        tok = _json.loads(ret.text)
    elif status == 403:
        raise Exception('Authentication failed: Bad user_id/password ' +
                        'combination for user %s' % (user_id))
    else:
        raise Exception(ret.text)
    return tok['access_token']


def _read_rcfile(file=_os.environ['HOME'] + '/.authrc'):  # @ReservedAssignment
    # Another bandaid to read in the ~/.authrc file if one is present
    authdata = None
    if _os.path.exists(file):
        try:
            with open(file) as authrc:
                rawdata = _json.load(authrc)
                # strip down whatever we read to only what is legit
                authdata = {x: rawdata.get(x) for x in (
                    'user_id', 'token', 'client_secret', 'keyfile',
                    'keyfile_passphrase', 'password')}
        except Exception, e:
            print "Error while reading authrc file %s: %s" % (file, e)
    return authdata


def _read_inifile(file=_os.environ.get(  # @ReservedAssignment
                  'KB_DEPLOYMENT_CONFIG', _os.environ['HOME'] +
                  '/.kbase_config')):
    # Another bandaid to read in the ~/.kbase_config file if one is present
    authdata = None
    if _os.path.exists(file):
        try:
            config = _ConfigParser()
            config.read(file)
            # strip down whatever we read to only what is legit
            authdata = {x: config.get('authentication', x)
                        if config.has_option('authentication', x)
                        else None for x in ('user_id', 'token',
                                            'client_secret', 'keyfile',
                                            'keyfile_passphrase', 'password')}
        except Exception, e:
            print "Error while reading INI file %s: %s" % (file, e)
    return authdata


class ServerError(Exception):

    def __init__(self, name, code, message, data=None, error=None):
        self.name = name
        self.code = code
        self.message = '' if message is None else message
        self.data = data or error or ''
        # data = JSON RPC 2.0, error = 1.1

    def __str__(self):
        return self.name + ': ' + str(self.code) + '. ' + self.message + \
            '\n' + self.data


class _JSONObjectEncoder(_json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, frozenset):
            return list(obj)
        return _json.JSONEncoder.default(self, obj)


class Workspace(object):

    def __init__(self, url=None, timeout=30 * 60, user_id=None,
                 password=None, token=None, ignore_authrc=False,
                 trust_all_ssl_certificates=False):
        if url is None:
            url = 'https://kbase.us/services/ws/'
        scheme, _, _, _, _, _ = _urlparse.urlparse(url)
        if scheme not in _URL_SCHEME:
            raise ValueError(url + " isn't a valid http url")
        self.url = url
        self.timeout = int(timeout)
        self._headers = dict()
        self.trust_all_ssl_certificates = trust_all_ssl_certificates
        # token overrides user_id and password
        if token is not None:
            self._headers['AUTHORIZATION'] = token
        elif user_id is not None and password is not None:
            self._headers['AUTHORIZATION'] = _get_token(user_id, password)
        elif 'KB_AUTH_TOKEN' in _os.environ:
            self._headers['AUTHORIZATION'] = _os.environ.get('KB_AUTH_TOKEN')
        elif not ignore_authrc:
            authdata = _read_inifile()
            if authdata is None:
                authdata = _read_rcfile()
            if authdata is not None:
                if authdata.get('token') is not None:
                    self._headers['AUTHORIZATION'] = authdata['token']
                elif(authdata.get('user_id') is not None
                     and authdata.get('password') is not None):
                    self._headers['AUTHORIZATION'] = _get_token(
                        authdata['user_id'], authdata['password'])
        if self.timeout < 1:
            raise ValueError('Timeout value must be at least 1 second')

    def _call(self, method, params, json_rpc_context = None):
        arg_hash = {'method': method,
                    'params': params,
                    'version': '1.1',
                    'id': str(_random.random())[2:]
                    }
        if json_rpc_context:
            arg_hash['context'] = json_rpc_context

        body = _json.dumps(arg_hash, cls=_JSONObjectEncoder)
        ret = _requests.post(self.url, data=body, headers=self._headers,
                             timeout=self.timeout,
                             verify=not self.trust_all_ssl_certificates)
        if ret.status_code == _requests.codes.server_error:
            json_header = None
            if _CT in ret.headers:
                json_header = ret.headers[_CT]
            if _CT in ret.headers and ret.headers[_CT] == _AJ:
                err = _json.loads(ret.text)
                if 'error' in err:
                    raise ServerError(**err['error'])
                else:
                    raise ServerError('Unknown', 0, ret.text)
            else:
                raise ServerError('Unknown', 0, ret.text)
        if ret.status_code != _requests.codes.OK:
            ret.raise_for_status()
        ret.encoding = 'utf-8'
        resp = _json.loads(ret.text)
        if 'result' not in resp:
            raise ServerError('Unknown', 0, 'An unknown server error occurred')
        return resp['result']
 
    def ver(self, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method ver: argument json_rpc_context is not type dict as required.')
        resp = self._call('Workspace.ver',
                          [], json_rpc_context)
        return resp[0]
  
    def create_workspace(self, params, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method create_workspace: argument json_rpc_context is not type dict as required.')
        resp = self._call('Workspace.create_workspace',
                          [params], json_rpc_context)
        return resp[0]
  
    def alter_workspace_metadata(self, params, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method alter_workspace_metadata: argument json_rpc_context is not type dict as required.')
        self._call('Workspace.alter_workspace_metadata',
                   [params], json_rpc_context)
  
    def clone_workspace(self, params, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method clone_workspace: argument json_rpc_context is not type dict as required.')
        resp = self._call('Workspace.clone_workspace',
                          [params], json_rpc_context)
        return resp[0]
  
    def lock_workspace(self, wsi, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method lock_workspace: argument json_rpc_context is not type dict as required.')
        resp = self._call('Workspace.lock_workspace',
                          [wsi], json_rpc_context)
        return resp[0]
  
    def get_workspacemeta(self, params, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method get_workspacemeta: argument json_rpc_context is not type dict as required.')
        resp = self._call('Workspace.get_workspacemeta',
                          [params], json_rpc_context)
        return resp[0]
  
    def get_workspace_info(self, wsi, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method get_workspace_info: argument json_rpc_context is not type dict as required.')
        resp = self._call('Workspace.get_workspace_info',
                          [wsi], json_rpc_context)
        return resp[0]
  
    def get_workspace_description(self, wsi, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method get_workspace_description: argument json_rpc_context is not type dict as required.')
        resp = self._call('Workspace.get_workspace_description',
                          [wsi], json_rpc_context)
        return resp[0]
  
    def set_permissions(self, params, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method set_permissions: argument json_rpc_context is not type dict as required.')
        self._call('Workspace.set_permissions',
                   [params], json_rpc_context)
  
    def set_global_permission(self, params, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method set_global_permission: argument json_rpc_context is not type dict as required.')
        self._call('Workspace.set_global_permission',
                   [params], json_rpc_context)
  
    def set_workspace_description(self, params, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method set_workspace_description: argument json_rpc_context is not type dict as required.')
        self._call('Workspace.set_workspace_description',
                   [params], json_rpc_context)
  
    def get_permissions_mass(self, mass, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method get_permissions_mass: argument json_rpc_context is not type dict as required.')
        resp = self._call('Workspace.get_permissions_mass',
                          [mass], json_rpc_context)
        return resp[0]
  
    def get_permissions(self, wsi, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method get_permissions: argument json_rpc_context is not type dict as required.')
        resp = self._call('Workspace.get_permissions',
                          [wsi], json_rpc_context)
        return resp[0]
  
    def save_object(self, params, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method save_object: argument json_rpc_context is not type dict as required.')
        resp = self._call('Workspace.save_object',
                          [params], json_rpc_context)
        return resp[0]
  
    def save_objects(self, params, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method save_objects: argument json_rpc_context is not type dict as required.')
        resp = self._call('Workspace.save_objects',
                          [params], json_rpc_context)
        return resp[0]
  
    def get_object(self, params, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method get_object: argument json_rpc_context is not type dict as required.')
        resp = self._call('Workspace.get_object',
                          [params], json_rpc_context)
        return resp[0]
  
    def get_object_provenance(self, object_ids, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method get_object_provenance: argument json_rpc_context is not type dict as required.')
        resp = self._call('Workspace.get_object_provenance',
                          [object_ids], json_rpc_context)
        return resp[0]
  
    def get_objects(self, object_ids, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method get_objects: argument json_rpc_context is not type dict as required.')
        resp = self._call('Workspace.get_objects',
                          [object_ids], json_rpc_context)
        return resp[0]
  
    def get_objects2(self, params, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method get_objects2: argument json_rpc_context is not type dict as required.')
        resp = self._call('Workspace.get_objects2',
                          [params], json_rpc_context)
        return resp[0]
  
    def get_object_subset(self, sub_object_ids, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method get_object_subset: argument json_rpc_context is not type dict as required.')
        resp = self._call('Workspace.get_object_subset',
                          [sub_object_ids], json_rpc_context)
        return resp[0]
  
    def get_object_history(self, object, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method get_object_history: argument json_rpc_context is not type dict as required.')
        resp = self._call('Workspace.get_object_history',
                          [object], json_rpc_context)
        return resp[0]
  
    def list_referencing_objects(self, object_ids, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method list_referencing_objects: argument json_rpc_context is not type dict as required.')
        resp = self._call('Workspace.list_referencing_objects',
                          [object_ids], json_rpc_context)
        return resp[0]
  
    def list_referencing_object_counts(self, object_ids, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method list_referencing_object_counts: argument json_rpc_context is not type dict as required.')
        resp = self._call('Workspace.list_referencing_object_counts',
                          [object_ids], json_rpc_context)
        return resp[0]
  
    def get_referenced_objects(self, ref_chains, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method get_referenced_objects: argument json_rpc_context is not type dict as required.')
        resp = self._call('Workspace.get_referenced_objects',
                          [ref_chains], json_rpc_context)
        return resp[0]
  
    def list_workspaces(self, params, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method list_workspaces: argument json_rpc_context is not type dict as required.')
        resp = self._call('Workspace.list_workspaces',
                          [params], json_rpc_context)
        return resp[0]
  
    def list_workspace_info(self, params, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method list_workspace_info: argument json_rpc_context is not type dict as required.')
        resp = self._call('Workspace.list_workspace_info',
                          [params], json_rpc_context)
        return resp[0]
  
    def list_workspace_objects(self, params, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method list_workspace_objects: argument json_rpc_context is not type dict as required.')
        resp = self._call('Workspace.list_workspace_objects',
                          [params], json_rpc_context)
        return resp[0]
  
    def list_objects(self, params, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method list_objects: argument json_rpc_context is not type dict as required.')
        resp = self._call('Workspace.list_objects',
                          [params], json_rpc_context)
        return resp[0]
  
    def get_objectmeta(self, params, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method get_objectmeta: argument json_rpc_context is not type dict as required.')
        resp = self._call('Workspace.get_objectmeta',
                          [params], json_rpc_context)
        return resp[0]
  
    def get_object_info(self, object_ids, includeMetadata, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method get_object_info: argument json_rpc_context is not type dict as required.')
        resp = self._call('Workspace.get_object_info',
                          [object_ids, includeMetadata], json_rpc_context)
        return resp[0]
  
    def get_object_info_new(self, params, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method get_object_info_new: argument json_rpc_context is not type dict as required.')
        resp = self._call('Workspace.get_object_info_new',
                          [params], json_rpc_context)
        return resp[0]
  
    def rename_workspace(self, params, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method rename_workspace: argument json_rpc_context is not type dict as required.')
        resp = self._call('Workspace.rename_workspace',
                          [params], json_rpc_context)
        return resp[0]
  
    def rename_object(self, params, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method rename_object: argument json_rpc_context is not type dict as required.')
        resp = self._call('Workspace.rename_object',
                          [params], json_rpc_context)
        return resp[0]
  
    def copy_object(self, params, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method copy_object: argument json_rpc_context is not type dict as required.')
        resp = self._call('Workspace.copy_object',
                          [params], json_rpc_context)
        return resp[0]
  
    def revert_object(self, object, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method revert_object: argument json_rpc_context is not type dict as required.')
        resp = self._call('Workspace.revert_object',
                          [object], json_rpc_context)
        return resp[0]
  
    def get_names_by_prefix(self, params, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method get_names_by_prefix: argument json_rpc_context is not type dict as required.')
        resp = self._call('Workspace.get_names_by_prefix',
                          [params], json_rpc_context)
        return resp[0]
  
    def hide_objects(self, object_ids, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method hide_objects: argument json_rpc_context is not type dict as required.')
        self._call('Workspace.hide_objects',
                   [object_ids], json_rpc_context)
  
    def unhide_objects(self, object_ids, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method unhide_objects: argument json_rpc_context is not type dict as required.')
        self._call('Workspace.unhide_objects',
                   [object_ids], json_rpc_context)
  
    def delete_objects(self, object_ids, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method delete_objects: argument json_rpc_context is not type dict as required.')
        self._call('Workspace.delete_objects',
                   [object_ids], json_rpc_context)
  
    def undelete_objects(self, object_ids, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method undelete_objects: argument json_rpc_context is not type dict as required.')
        self._call('Workspace.undelete_objects',
                   [object_ids], json_rpc_context)
  
    def delete_workspace(self, wsi, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method delete_workspace: argument json_rpc_context is not type dict as required.')
        self._call('Workspace.delete_workspace',
                   [wsi], json_rpc_context)
  
    def undelete_workspace(self, wsi, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method undelete_workspace: argument json_rpc_context is not type dict as required.')
        self._call('Workspace.undelete_workspace',
                   [wsi], json_rpc_context)
  
    def request_module_ownership(self, mod, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method request_module_ownership: argument json_rpc_context is not type dict as required.')
        self._call('Workspace.request_module_ownership',
                   [mod], json_rpc_context)
  
    def register_typespec(self, params, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method register_typespec: argument json_rpc_context is not type dict as required.')
        resp = self._call('Workspace.register_typespec',
                          [params], json_rpc_context)
        return resp[0]
  
    def register_typespec_copy(self, params, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method register_typespec_copy: argument json_rpc_context is not type dict as required.')
        resp = self._call('Workspace.register_typespec_copy',
                          [params], json_rpc_context)
        return resp[0]
  
    def release_module(self, mod, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method release_module: argument json_rpc_context is not type dict as required.')
        resp = self._call('Workspace.release_module',
                          [mod], json_rpc_context)
        return resp[0]
  
    def list_modules(self, params, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method list_modules: argument json_rpc_context is not type dict as required.')
        resp = self._call('Workspace.list_modules',
                          [params], json_rpc_context)
        return resp[0]
  
    def list_module_versions(self, params, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method list_module_versions: argument json_rpc_context is not type dict as required.')
        resp = self._call('Workspace.list_module_versions',
                          [params], json_rpc_context)
        return resp[0]
  
    def get_module_info(self, params, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method get_module_info: argument json_rpc_context is not type dict as required.')
        resp = self._call('Workspace.get_module_info',
                          [params], json_rpc_context)
        return resp[0]
  
    def get_jsonschema(self, type, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method get_jsonschema: argument json_rpc_context is not type dict as required.')
        resp = self._call('Workspace.get_jsonschema',
                          [type], json_rpc_context)
        return resp[0]
  
    def translate_from_MD5_types(self, md5_types, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method translate_from_MD5_types: argument json_rpc_context is not type dict as required.')
        resp = self._call('Workspace.translate_from_MD5_types',
                          [md5_types], json_rpc_context)
        return resp[0]
  
    def translate_to_MD5_types(self, sem_types, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method translate_to_MD5_types: argument json_rpc_context is not type dict as required.')
        resp = self._call('Workspace.translate_to_MD5_types',
                          [sem_types], json_rpc_context)
        return resp[0]
  
    def get_type_info(self, type, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method get_type_info: argument json_rpc_context is not type dict as required.')
        resp = self._call('Workspace.get_type_info',
                          [type], json_rpc_context)
        return resp[0]
  
    def get_all_type_info(self, mod, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method get_all_type_info: argument json_rpc_context is not type dict as required.')
        resp = self._call('Workspace.get_all_type_info',
                          [mod], json_rpc_context)
        return resp[0]
  
    def get_func_info(self, func, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method get_func_info: argument json_rpc_context is not type dict as required.')
        resp = self._call('Workspace.get_func_info',
                          [func], json_rpc_context)
        return resp[0]
  
    def get_all_func_info(self, mod, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method get_all_func_info: argument json_rpc_context is not type dict as required.')
        resp = self._call('Workspace.get_all_func_info',
                          [mod], json_rpc_context)
        return resp[0]
  
    def grant_module_ownership(self, params, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method grant_module_ownership: argument json_rpc_context is not type dict as required.')
        self._call('Workspace.grant_module_ownership',
                   [params], json_rpc_context)
  
    def remove_module_ownership(self, params, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method remove_module_ownership: argument json_rpc_context is not type dict as required.')
        self._call('Workspace.remove_module_ownership',
                   [params], json_rpc_context)
  
    def list_all_types(self, params, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method list_all_types: argument json_rpc_context is not type dict as required.')
        resp = self._call('Workspace.list_all_types',
                          [params], json_rpc_context)
        return resp[0]
  
    def administer(self, command, json_rpc_context = None):
        if json_rpc_context and type(json_rpc_context) is not dict:
            raise ValueError('Method administer: argument json_rpc_context is not type dict as required.')
        resp = self._call('Workspace.administer',
                          [command], json_rpc_context)
        return resp[0]
 