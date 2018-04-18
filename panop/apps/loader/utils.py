from __future__ import print_function
import os
import shutil

import pysftp
import requests


def batch_file_upload(local_file, destination_host, destination_directory, destination_filename, username, password):
    new_file_path = os.path.join(os.path.split(os.path.normpath(local_file._get_path()))[0], destination_filename)
    try:
        print("===UPLOAD===")
        print("Coping {0} to {1}".format(local_file._get_path(), new_file_path))
        shutil.copyfile(local_file._get_path(), new_file_path)
    except shutil.SameFileError:
        pass
    with pysftp.Connection(destination_host, username=username, password=password) as sftp:
        with sftp.cd(destination_directory):
            sftp.put(new_file_path)
    os.remove(new_file_path)


def real_time_bulk_insert(filename, url, soapaction, format_table, authscheme, auth=None):
    for data_row in csv_to_kvp(filename):
        response = real_time_insert(data_row, url, soapaction, format_table, authscheme, auth)
        print(response.status_code, response.text)
        print(response.request)


def real_time_insert(data, url, soapaction, format_table, authscheme, auth=None):
    """Real-time insert into Campaign Central format table

    data: dict with SOAP KVPRecord key-value pairs

    url: fully qualified URL to campaign central API
      ex. http://linux7316.wic.west.com:8080/campcentral/realtimeInsert

    soapaction: sets SOAPAction HTTP header
     ex. "http://campaigncentral.west.com/soap-api/rtinsert/NewOperation" (note quotes)

    format_table: Campaign Central format table

    authscheme: authentication scheme used inside the SOAP request. Currently, only 'basic' and 'none' are supported

    auth: dict with authentication values. For basic auth, this would be {'name': name, 'password': password}"""
    # build SOAP header
    if authscheme == 'basic':
        header = soap_basic_auth_header(auth)
    else:
        header = ''

    # build SOAP body
    body_start = "<soapenv:Body><rtin:InsertRequest><Format>{0}</Format><Records><rtin:KVPRecord>".format(format_table)
    body_end = "</rtin:KVPRecord></Records></rtin:InsertRequest></soapenv:Body>"
    params = "".join(['<param key="{key}" value="{value}"/>'.format(key=k, value=v) for k, v in data.items()])
    body = body_start + params + body_end

    soap_envelope = '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:rtin="http://campaigncentral.west.com/soap-api/rtinsert">'
    soap_envelope += header
    soap_envelope += body
    soap_envelope += '</soapenv:Envelope>'

    soap_envelope = soap_envelope.encode('utf-8')

    # build HTTP headers
    headers = {'Host': extract_host_from_url(url),
               'Content-Type': 'text/xml; charset=UTF-8',
               'Content-Length': str(len(soap_envelope)),
               'SOAPAction': soapaction}

    # send request
    return requests.post(url=url, headers=headers, data=soap_envelope, verify=False)


def csv_to_kvp(filename):
    """Returns a list of dicts mapping rows 1+ as values to headers/keys found in row 0"""
    f = open(filename, 'rt', encoding='utf=8')
    byte_lines = f.readlines()
    f.close()
    lines = byte_lines  # [l.decode("utf-8") for l in byte_lines]
    headers = lines[0].split(',')
    rows = lines[1:]
    rows = [row.split(',') for row in rows]
    return [{header.strip(): row[i] for i, header in enumerate(headers)} for row in rows]


def soap_basic_auth_header(auth):
    return """<soapenv:Header>
    <BasicAuth>
    <Name>{name}</Name>
    <Password>{password}</Password>
    </BasicAuth>
    </soapenv:Header>""".format(name=auth['name'], password=auth['password'])


def extract_host_from_url(url):
    if url.startswith('http://'):
        return url[7:].split('/')[0]
    elif url.startswith('https://'):
        return url[8:].split('/')[0]
    else:
        return url.split('/')[0]