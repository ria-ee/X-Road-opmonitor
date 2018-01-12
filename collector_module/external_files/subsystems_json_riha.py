#!/usr/bin/python

import argparse
import json
import re
import six
import sys
import xrdinfo


DEFAULT_TIMEOUT=5.0


def print_error(content):
    """Thread safe and unicode safe error printer."""
    content = u"ERROR: {}\n".format(content)
    if six.PY2:
        sys.stderr.write(content.encode('utf-8'))
    else:
        sys.stderr.write(content)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='List Subsystems info based on RIHA and X-Road global configuration.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='You need to provide either Security Server or Central Server address.\n\n'
            'NB! Global configuration signature is not validated when using Central Server.\n'
            'Use local Security Server whenever possible.'
    )
    parser.add_argument('-s', metavar='SECURITY_SERVER', help='DNS name/IP/URL of local Security Server')
    parser.add_argument('-c', metavar='CENTRAL_SERVER', help='DNS name/IP/URL of Central Server/Configuration Proxy')
    parser.add_argument('-t', metavar='TIMEOUT', help='timeout for HTTP query', type=float)
    parser.add_argument('--riha', metavar='RIHA_JSON', help='RIHA data file in json format.')
    args = parser.parse_args()

    timeout = DEFAULT_TIMEOUT
    if args.t:
        timeout = args.t

    if args.s:
        try:
            sharedParams = xrdinfo.sharedParamsSS(addr=args.s, timeout=timeout)
        except (xrdinfo.XrdInfoError) as e:
            print_error(e)
            exit(1)
    elif args.c:
        try:
            sharedParams = xrdinfo.sharedParamsCS(addr=args.c, timeout=timeout)
        except (xrdinfo.XrdInfoError) as e:
            print_error(e)
            exit(1)
    else:
        parser.print_help()
        exit(1)

    if six.PY2:
        # Convert to unicode
        args.riha = args.riha.decode('utf-8')

    jsonData = ''
    if args.riha:
        try:
            with open(args.riha, 'r') as f:
                if six.PY2:
                    jsonData = json.loads(f.read().decode('utf-8'))
                else:
                    jsonData = json.load(f)
        except Exception:
            print_error('Cannot load file ' + args.riha)

    rihaSystems = {}
    if jsonData:
        for item in jsonData['content']:
            systemCode = ''
            systemName = ''
            ownerCode = ''
            ownerName = ''
            contacts = []
            if 'details' in item:
                if 'short_name' in item['details']:
                    systemCode = item['details']['short_name']
                if 'name' in item['details']:
                    systemName = item['details']['name']
                if 'owner' in item['details']:
                    if 'code' in item['details']['owner']:
                        ownerCode = item['details']['owner']['code']
                    if 'name' in item['details']['owner']:
                        ownerName = item['details']['owner']['name']
                if 'contacts' in item['details'] and item['details']['contacts'] is not None:
                    for contact in item['details']['contacts']:
                        email = ''
                        name = ''
                        if 'email' in contact:
                            email = contact['email']
                        if 'name' in contact:
                            name = contact['name']
                        contacts.append({'email': email, 'name': name})

            val = {'systemName': systemName, 'ownerName': ownerName, 'contacts': contacts}
            # TODO: (2017-11-30) the .lower() here and later should considered as temporary hack to find contacts by matching data in RIHA and in X-Road
            # Instead, data about systemCode (subSystemCode) should keep with exact match between two systems with other methods
            id1 = '{}/{}'.format(ownerCode, systemCode.lower())
            rihaSystems[id1] = val
            # print(id1, rihaSystems[id1])

            # Fix for RIHA
            # TODO: (2017-11-30) the matches of RIHA "memberCode/memberCode-subSystemCode" and/or "another_memberCode/memberCode-subSystemCode"
            # should considered as temporary hack to find contacts by matching data in RIHA and in X-Road
            # Instead, data about systemCode (subSystemCode) should keep with exact match between two systems with other methods
            m = re.match("^(\d{8})-(.+)$", systemCode)
            if m:
                # RIHA "memberCode/memberCode-subSystemCode" subsystem might be X-Road "memberCode/subSystemCode" subsystem
                id2='{}/{}'.format(ownerCode, m.group(2).lower())
                rihaSystems[id2] = val
                # print(id2, rihaSystems[id2])

                # RIHA "another_memberCode/memberCode-subSystemCode" might be X-Road "memberCode/subSystemCode"
                # id3='{}/{}'.format(m.group(1), m.group(2).lower())
                # rihaSystems[id3] = val
                # print(id3, rihaSystems[id3])

    try:
        registered = list(xrdinfo.registeredSubsystems(sharedParams))
    except (xrdinfo.XrdInfoError) as e:
        print_error(e)
        exit(1)

    jsonDataArr = []
    try:
        for subsystem in xrdinfo.subsystemsWithMembername(sharedParams):
            # Example: ('ee-dev', 'GOV', '70006317', 'testservice', u'Riigi Infos\xfcsteemi Amet')

            if subsystem[0:4] not in registered:
                # print('Not registered: {}'.format(subsystem))
                continue

            # TODO: (2017-11-30) the .lower() here and before should considered as temporary hack to find contacts by matching data in RIHA and in X-Road
            # Instead, data about systemCode (subSystemCode) should keep with exact match between two systems with other methods
            id = '{}/{}'.format(subsystem[2], subsystem[3].lower())
            if id in rihaSystems:
                jsonData = {
                    'x_road_instance': subsystem[0],
                    'member_class': subsystem[1],
                    'member_code': subsystem[2],
                    'member_name': rihaSystems[id]['ownerName'] if rihaSystems[id]['ownerName'] else subsystem[4],
                    'subsystem_code': subsystem[3],
                    'subsystem_name': {'et': rihaSystems[id]['systemName'], 'en': ''},
                    'email': rihaSystems[id]['contacts']
                }
            else:
                jsonData = {
                    'x_road_instance': subsystem[0],
                    'member_class': subsystem[1],
                    'member_code': subsystem[2],
                    'member_name': subsystem[4],
                    'subsystem_code': subsystem[3],
                    'subsystem_name': {'et': '', 'en': ''},
                    'email': []
                }
            # print(json.dumps(jsonData, indent=2, ensure_ascii=False))
            jsonDataArr.append(jsonData)
    except (xrdinfo.XrdInfoError) as e:
        print_error(e)
        exit(1)

    with open('riha.json', 'w') as f:
        if six.PY2:
            f.write(json.dumps(jsonDataArr, indent=2, ensure_ascii=False).encode('utf-8'))
        else:
            json.dump(jsonDataArr, f, indent=2, ensure_ascii=False)
