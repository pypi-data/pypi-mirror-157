import json
import os
from typing import Union
import requests
import random

from kachery_cloud.mutable_local import get_mutable_local, set_mutable_local
from .get_kachery_cloud_dir import get_kachery_cloud_dir
from ._kacherycloud_request import _kacherycloud_request
from .store_file_local import _compute_file_hash
from ._fs_operations import _makedirs, _chmod_file
from ._access_group_encrypt import _access_group_decrypt


def load_file(uri: str, *, verbose: bool=False, local_only: bool=False) -> Union[str, None]:
    if uri.startswith('sha1-enc://'):
        query = _get_query_from_uri(uri)
        ag = query['ag']
        sha1_enc = uri.split('?')[0].split('/')[2]
        sha1 = _access_group_decrypt(sha1_enc, access_group=ag)
        uri2 = f'sha1://{sha1}?{uri.split("?")[1]}'
        return load_file(uri2, verbose=verbose, local_only=local_only)

    if local_only:
        return load_file_local(uri)
    if uri.startswith('/'):
        if os.path.exists(uri):
            return uri
        else:
            return None
    if uri.startswith('sha1://'):
        x = load_file_local(uri)
        if x is not None:
            return x
        sha1 = uri.split('?')[0].split('/')[2]
        return _load_sha1_file_from_cloud(sha1, verbose=verbose)
        
    assert uri.startswith('ipfs://'), f'Invalid or unsupported URI: {uri}'
    a = uri.split('?')[0].split('/')
    assert len(a) >= 3, f'Invalid or unsupported URI: {uri}'
    cid = a[2]

    kachery_cloud_dir = get_kachery_cloud_dir()
    e = cid[-6:]
    parent_dir = f'{kachery_cloud_dir}/ipfs/{e[0]}{e[1]}/{e[2]}{e[3]}/{e[4]}{e[5]}'
    filename = f'{parent_dir}/{cid}'
    if os.path.exists(filename):
        return filename

    payload = {
        'type': 'findIpfsFile',
        'cid': cid
    }
    response= _kacherycloud_request(payload)
    found = response['found']
    if found:
        url = response['url']
    else:
        return None
        # url = f'https://{cid}.ipfs.dweb.link'
        # url = f'https://cloudflare-ipfs.com/ipfs/{cid}'
        # url = f'https://ipfs.filebase.io/ipfs/{cid}'

    if verbose:
        print(f'Loading file from kachery cloud: {uri}')    
    if not os.path.exists(parent_dir):
        _makedirs(parent_dir)
    tmp_filename = f'{filename}.tmp.{_random_string(8)}'
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(tmp_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    try:
        os.rename(tmp_filename, filename)
        _chmod_file(filename)
    except:
        if not os.path.exists(filename): # maybe some other process beat us to it
            raise Exception(f'Unexpected problem moving file {tmp_filename}')
    return filename

def _load_sha1_file_from_cloud(sha1: str, *, verbose: bool) -> Union[str, None]:
    payload = {
        'type': 'findFile',
        'hashAlg': 'sha1',
        'hash': sha1
    }
    response= _kacherycloud_request(payload)
    found = response['found']
    uri = f'sha1://{sha1}'
    if found:
        url = response['url']
    else:
        return None

    kachery_cloud_dir = get_kachery_cloud_dir()
    e = sha1
    parent_dir = f'{kachery_cloud_dir}/sha1/{e[0]}{e[1]}/{e[2]}{e[3]}/{e[4]}{e[5]}'
    filename = f'{parent_dir}/{sha1}'
    if verbose:
        print(f'Loading file from kachery cloud: {uri}') 
    if not os.path.exists(parent_dir):
        _makedirs(parent_dir)
    tmp_filename = f'{filename}.tmp.{_random_string(8)}'
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(tmp_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    try:
        os.rename(tmp_filename, filename)
        _chmod_file(filename)
    except:
        if not os.path.exists(filename): # maybe some other process beat us to it
            raise Exception(f'Unexpected problem moving file {tmp_filename}')
    return filename

def load_file_local(uri: str) -> Union[str, None]:
    query = _get_query_from_uri(uri)
    assert uri.startswith('sha1://'), f'Invalid local URI: {uri}'
    a = uri.split('?')[0].split('/')
    assert len(a) >= 3, f'Invalid or unsupported URI: {uri}'
    sha1 = a[2]

    kachery_cloud_dir = get_kachery_cloud_dir()

    s = sha1
    parent_dir = f'{kachery_cloud_dir}/sha1/{s[0]}{s[1]}/{s[2]}{s[3]}/{s[4]}{s[5]}'
    filename = f'{parent_dir}/{sha1}'
    if os.path.exists(filename):
        return filename
    
    if 'location' in query:
        location = query['location']
        if os.path.isabs(location) and os.path.exists(location):
            sha1_2 = _compute_file_hash(location, 'sha1')
            if sha1_2 == sha1:
                return location
    
    # check for linked file
    a_txt = get_mutable_local(f'linked_files/sha1/{sha1}')
    if a_txt is not None:
        a = json.loads(a_txt)
        path0 = a['path']
        size0 = a['size']
        mtime0 = a['mtime']
        if os.path.exists(path0):
            if os.path.getsize(path0) == size0 and os.stat(path0).st_mtime == mtime0:
                return path0
            sha1_0 = _compute_file_hash(path0, algorithm='sha1')
            if sha1_0 == sha1:
                set_mutable_local(f'linked_files/sha1/{sha1}', json.dumps({
                    'path': path0,
                    'size': os.path.getsize(path0),
                    'mtime': os.stat(path0).st_mtime,
                    'sha1': sha1
                }))
                return path0
            else:
                print(f'Warning: sha1 of linked file has changed: {path0} {uri}')
    
    return None

def _get_query_from_uri(uri: str):
    a = uri.split('?')
    ret = {}
    if len(a) < 2: return ret
    b = a[1].split('&')
    for c in b:
        d = c.split('=')
        if len(d) == 2:
            ret[d[0]] = d[1]
    return ret

def _random_string(num_chars: int) -> str:
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(random.choice(chars) for _ in range(num_chars))