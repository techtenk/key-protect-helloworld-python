# Copyright 2015 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function
import copy
import base64
import sys
import os
import requests
from flask import Flask, jsonify, abort, render_template
from flask import request
from Crypto.Cipher import AES
import json

app = Flask(__name__)
route_secrets = '/api/v2/secrets'
authorization_header_field = 'Authorization'
space_header_field = 'Bluemix-Space'
org_header_field = 'Bluemix-Org'
secret_mime_type = 'application/vnd.ibm.kms.secret+json'
aes_algorithm_type = 'AES'


@app.route('/')
def Welcome():
    cred = json.load(open('auth.json'))
    welcome_file = 'index.html'

    # check to make sure values in the auth.json file are updated
    if (cred['token'] == '') or (cred['space'] == ''):
        welcome_file = 'update_auth_file.html'
    return app.send_static_file(welcome_file)


@app.route('/unauthorized')
def Unauthorized_Page():
    return app.send_static_file('unauthorized.html')

def getKeyAndIV():

        # Use the IV and Key used to encrypt the secret message.  Instead of transferring through a file, like in this
        # sample, the sender of the IV and KEY should have directly placed it into Key Protect and then only sent the
        # secret references to the IV and KEY to the person that they want to decrypt the message.  Because we do not
        # have a common space to share, we're going to load the IV and KEY into this user's space

        key_info = json.load(open('encryption_keys.json'))
        key = key_info['key']

        with open('iv.txt', 'r') as ff:
            iv = ff.read()
            return key, iv




def setup():
    cred = json.load(open('auth.json'))
    url = 'https://' + cred['host'] + route_secrets
    token = cred['token'].strip()
    space = cred['space'].strip()
    org = cred['org'].strip()
    headers = {
        'Content-Type': 'application/json',
        authorization_header_field: token.encode('UTF-8'),
        space_header_field: space.encode('UTF-8'),
        org_header_field: org.encode('UTF-8')
    }

    return url, headers


@app.route('/messages', methods=['POST'])
def decrypt_message():

    data = request.get_json(force=True)
    iv_id = data['iv']
    key_id = data['key']

    url, headers = setup()
    iv_url = '/'.join([url, iv_id])
    key_url = '/'.join([url, key_id])

    print('\n\nGet Secrets ', file=sys.stderr)
    print('\nIV_Url: '+iv_url, file=sys.stderr)
    print('\nKey_Url: '+key_url, file=sys.stderr)

    # get keys from Key Protect
    try:
        print('\n\nGet IV Secret', file=sys.stderr)
        get_iv_request = requests.get(iv_url, headers=headers)

        get_iv_status = get_iv_request.status_code
        get_iv_headers = get_iv_request.headers

        print('\nResponse Status Code: '+str(get_iv_status), file=sys.stderr)
        response_iv = get_iv_request.json()
        print('\nRespones Body: '+str(response_iv), file=sys.stderr)
        print('\nCorrelation-Id: '+get_iv_headers['Correlation-Id'],
              file=sys.stderr)

        if get_iv_status >= 400:
            raise Exception(get_iv_status, response_iv)

        payload_iv = base64.b16decode(response_iv['resources'][0]['payload'])
    except requests.exceptions.RequestException as e:
        print('\n\n'+str(e), file=sys.stderr)
        err_msg = 'cannot create IV. Check auth.json file'
        response = jsonify(message=err_msg)
        response.status_code = 400
        return response
    except Exception as e:
        print('\n\n'+str(e), file=sys.stderr)
        response = jsonify(message=e.message, iv_id=iv_id)
        response.status_code = 400
        return response

    try:
        print('\n\nGet Key Secret', file=sys.stderr)
        get_key_request = requests.get(key_url, headers=headers)

        get_key_status = get_key_request.status_code
        get_key_headers = get_key_request.headers

        print('\nResponse Status Code: '+str(get_key_status), file=sys.stderr)
        response_key = get_key_request.json()
        print('\nRespones Body: '+str(response_key), file=sys.stderr)
        print('\nCorrelation-Id: '+get_key_headers['Correlation-Id'],
              file=sys.stderr)

        if get_key_status >= 400:
            raise Exception(get_key_status, response_key)

        payload_key = response_key['resources'][0]['payload'].encode('UTF-8')
    except requests.exceptions.RequestException as e:
        print('\n\n'+str(e), file=sys.stderr)
        err_msg = 'cannot create key. Check auth.json file'
        response = jsonify(message=err_msg)
        response.status_code = 400
        return response
    except Exception as e:
        print('\n\n'+str(e), file=sys.stderr)
        response = jsonify(message=e.message, key_id=key_id)
        response.status_code = 400
        return response

    try:
        print('\n\nCipher', file=sys.stderr)
        cipher2 = AES.new(payload_key, AES.MODE_CFB, payload_iv)
        decrypted_msg = []

        print('\n\nDecrypt Message', file=sys.stderr)

        with open('secret message.txt', 'r') as f1:
            decrypted_msg.append(cipher2.decrypt(f1.read()))

        print('\n\nWrite Decrypted file', file=sys.stderr)

        revealed_file_name = 'revealed_msg.txt'
        with open(revealed_file_name, 'w') as f2:
            for block in decrypted_msg:
                f2.write(block)
    except Exception as e:
        print('\n\nError: '+str(e), file=sys.stderr)
        response = jsonify(description='Decrypt failed',
                           key_id=key_id,
                           iv_id=iv_id)
        response.status_code = 500
        return response

    print('\n\nDelete Secrets ', file=sys.stderr)

    # now delete the keys from Key Protect
    try:
        print('\n\nDelete IV Secret', file=sys.stderr)
        delete_iv_request = requests.delete(iv_url, headers=headers)

        delete_iv_status = delete_iv_request.status_code
        delete_iv_headers = delete_iv_request.headers

        print('\nResponse Status Code: '+str(delete_iv_status),
              file=sys.stderr)
        print('\nCorrelation-Id: '+delete_iv_headers['Correlation-Id'],
              file=sys.stderr)

        if delete_iv_status >= 400:
            raise Exception(delete_iv_status, delete_iv_request.json())

        print('\n\nDelete Key Secret', file=sys.stderr)
        delete_key_request = requests.delete(key_url, headers=headers)

        delete_key_status = delete_key_request.status_code
        delete_key_headers = delete_key_request.headers

        print('\nResponse Status Code: '+str(delete_key_status),
              file=sys.stderr)
        print('\nCorrelation-Id: '+delete_key_headers['Correlation-Id'],
              file=sys.stderr)

        if delete_key_status >= 400:
            raise Exception(delete_key_status, delete_key_request.json())
    except requests.exceptions.RequestException as e:
        print('\n\n'+str(e), file=sys.stderr)
        err_msg = 'cannot delete key. Check auth.json file'
        response = jsonify(message=err_msg)
        response.status_code = 500
        return response
    except Exception as e:
        print('\n\n'+str(e), file=sys.stderr)
        response = jsonify(description='delete failed',
                           key_id=key_id,
                           iv_id=iv_id)
        response.status_code = 500
        return response

    return json.dumps({
        'message': decrypted_msg[0],
        'file_name': revealed_file_name
    })


@app.route('/keys', methods=['GET'])
def get_key_ids():
    '''Get the secret references for the IV and KEY we'll need

    This gets the shared IV ad KEY from the encryption_keys.json file and uses that to generate the secrets in
    Key Protect.

    :return:  Reference for IV and KEY that we generate
    '''

    url, headers = setup()
    print('\n\nPost Secrets', file=sys.stderr)
    print('\nUrl: '+url, file=sys.stderr)

    key, iv = getKeyAndIV()

    post_request_body_template = {
        'metadata': {
            'collectionType': 'application/vnd.ibm.kms.secret+json',
            'collectionTotal': 1
        },
        'resources': []
    }

    try:
        encoded_iv = base64.b16encode(iv)
        print('\n\nPost IV Secret', file=sys.stderr)
        iv_secret = {
            'name': 'IV for sample message',
            'type': secret_mime_type,
            'algorithmType': aes_algorithm_type,
            'payload': encoded_iv
        }

        iv_post_request_body = copy.deepcopy(post_request_body_template)
        iv_post_request_body['resources'].append(iv_secret)
        print('\nRequest Body: '+str(iv_post_request_body), file=sys.stderr)

        post_iv_request = requests.post(url, headers=headers,
                                        json=iv_post_request_body)

        post_iv_status = post_iv_request.status_code
        post_iv_headers = post_iv_request.headers

        print('\nResponse Status Code: '+str(post_iv_status), file=sys.stderr)
        response_iv = post_iv_request.json()
        print('\nResponse Body: '+str(response_iv), file=sys.stderr)
        print('\nCorrelation-Id: '+post_iv_headers["Correlation-Id"],
              file=sys.stderr)

        if post_iv_status >= 400:
            raise Exception(post_iv_status, response_iv)

        iv_id = response_iv['resources'][0]['id']
        print('\nIv Id: '+iv_id, file=sys.stderr)
    except requests.exceptions.RequestException as e:
        print('\n\nError: '+str(e), file=sys.stderr)
        err_msg = 'cannot post iv. Check auth.json file'
        response = jsonify(message=err_msg)
        response.status_code = 500
        return response
    except Exception as e:
        print('\n\nError: '+str(e), file=sys.stderr)
        response = jsonify(message=e.message)
        response.status_code = 500
        return response

    try:
        print('\n\nPost Key Secret', file=sys.stderr)
        key_secret = {
            'name': 'Key for sample message',
            'type': secret_mime_type,
            'algorithmType': aes_algorithm_type,
            'payload': key
        }
        key_post_request_body = copy.deepcopy(post_request_body_template)
        key_post_request_body['resources'].append(key_secret)
        print('\nRequest Body: '+str(key_post_request_body), file=sys.stderr)

        post_key_request = requests.post(url, headers=headers,
                                         json=key_post_request_body)

        post_key_status = post_key_request.status_code
        post_key_headers = post_key_request.headers

        print('\nResponse Status Code: '+str(post_key_status), file=sys.stderr)
        response_key = post_key_request.json()
        print('\nResponse Body: '+str(response_key), file=sys.stderr)
        print('\nCorrelation-Id: '+post_key_headers['Correlation-Id'],
              file=sys.stderr)

        if post_key_status >= 400:
            raise Exception(post_key_status, response_key)

        key_id = response_key['resources'][0]['id']
        print('\nKey Id: '+key_id, file=sys.stderr)
    except requests.exceptions.RequestException as e:
        print('\n\nError: '+str(e), file=sys.stderr)
        err_msg = 'cannot post key. Check auth.json file'
        response = jsonify(message=err_msg)
        response.status_code = 500
        return response
    except Exception as e:
        print('\n\nError: '+str(e), file=sys.stderr)
        response = jsonify(message=e.message)
        response.status_code = 500
        return response

    return json.dumps({
        'message': 'POST the key_info object to /messages',
        'key_info': {'iv': iv_id, 'key': key_id}
    })


@app.errorhandler(401)
def unauthorized(error):
    print(error, file=sys.stderr)
    return render_template('unauthorized.html'), 401


def main():
    port = os.getenv('PORT', '5001')
    app.run(host='0.0.0.0', port=int(port), debug=True)

if __name__ == '__main__':
    main()
