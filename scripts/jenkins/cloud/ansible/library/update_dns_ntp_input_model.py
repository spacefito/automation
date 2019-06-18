#!/usr/bin/python
# (c) Copyright 2019 SUSE LLC
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
DOCUMENTATION = '''
---
module: dns-update
short_description: 
options:
  dns-servers:
    description:
      - list of dns servers
    required: true
  ntp-servers:
      - list of ntp servers
    required: true
author:
'''

EXAMPLES = '''
- dns-update:
        dns-servers: dns1 dns2
        ntp-servers: ntp1 ntp2
'''


import yaml

from ansible.module_utils.basic import AnsibleModule

def main():
    argument_spec = dict(
        dns_servers=dict(type='list', default=[]),
        ntp_servers=dict(type='list', default=[]),
        file_path=dict(type='str', default='cloudConfig.yml')
    )
    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=False)

    dns_servers = module.params.get('dns_servers')
    ntp_servers = module.params.get('ntp_servers')
    file_path = module.params.get('file_path')

    with open(file_path) as f:
        data = yaml.load(f.read(), Loader=yaml.SafeLoader)

    data['cloud']['dns-settings'] = dict(nameservers=dns_servers)
    data['cloud']['ntp-servers'] = ntp_servers

    with open(file_path, 'w') as f:
        f.write(yaml.safe_dump(data, default_flow_style=False))

    module.exit_json(changed=True)


if __name__ == '__main__':
    main()