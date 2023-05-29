#!/usr/bin/python

# Copyright: (c) 2023, Ludovic Maître <rastaman@github.com>
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: freeboxvm

short_description: Manage Freebox virtual machines.

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "1.0.0"

description: Use the Freebox API to manage virtual machines.

options:
    action:
        description: This is the action to perform.
        required: true
        type: str
    vm_id:
        description:
            - The identifier of the VM
            - Only used on operation who target one VM.
        required: false
        type: str
    token_file:
        description: Token file, default ./.fbx_auth
        required: false
        type: str
    api_version:
        description: API version, default 'v8'
        required: false
        type: str
# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
extends_documentation_fragment:
    - ansible.modules.freeboxvm

author:
    - Ludovic Maître (@rastaman)
'''

EXAMPLES = r'''
# Pass in a message
- name: List VMs
  ansible.modules.freeboxvm:
    action: get_config_all

# pass in a message and have changed true
- name: Test with a message and changed output
  expansible.home.freeboxvm:
    name: hello world
    new: true

# fail the module
- name: Test failure of the module
  expansible.home.freeboxvm:
    name: fail me
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
original_message:
    description: The original name param that was passed in.
    type: str
    returned: always
    sample: 'hello world'
message:
    description: The output message that the test module generates.
    type: str
    returned: always
    sample: 'goodbye'
'''

import asyncio
import json
from freebox_api import Freepybox
from ansible.module_utils.basic import AnsibleModule

def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        action=dict(type='str', required=True),
        vm_id=dict(type='str', required=False),
        vm_config=dict(type='raw', required=False),
        token_file=dict(type='str', required=False, default='./.fbx_auth'),
        api_version=dict(type='str', required=False, default='v8'),
        freebox_host=dict(type='str', required=False, default='mafreebox.freebox.fr'),
        freebox_port=dict(type='int', required=False, default=443)
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        message=''
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    action = module.params['action']
    vm_id = module.params['vm_id']
    vm_config = module.params['vm_config']
    token_file = module.params['token_file']
    api_version = module.params['api_version']
    host = module.params['freebox_host']
    port = module.params['freebox_port']
  
    # during the execution of the module, if there is an exception or a
    # conditional state that effectively causes a failure, run
    # AnsibleModule.fail_json() to pass in the message and the result
    if action == 'fail me':
        module.fail_json(msg='You requested this to fail', **result)

    fbx = Freepybox(
        token_file = token_file,
        api_version = api_version
    )

    result = asyncio.run(executeAction(fbx, host, port, action, vm_id, vm_config))

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)

async def executeAction(fbx, host, port, action, vm_id, vm_config):
    payload = dict()
    await fbx.open(host=host, port=port)
    if action == 'list':
        payload['changed'] = True
        payload['message'] = await fbx.vm.get_config_all()
    elif action == 'stop':
        payload['changed'] = True
        payload['message'] = await fbx.vm.stop(vm_id)        
    elif action == 'start':
        payload['changed'] = True
        payload['message'] = await fbx.vm.start(vm_id)
    elif action == 'get_system_info':
        payload['changed'] = True
        payload['message'] = await fbx.vm.get_system_info()
    elif action == 'get_config_vm':
        payload['changed'] = True
        payload['message'] = await fbx.vm.get_config_vm(vm_id)
    elif action == 'get_config_all':
        payload['changed'] = True
        payload['message'] = await fbx.vm.get_config_all()
    elif action == 'delete':
        payload['changed'] = True
        payload['message'] = await fbx.vm.delete(vm_id)
    elif action == 'create':
        payload['changed'] = True
        payload['message'] = await fbx.vm.create(vm_config)
    elif action == 'resize':
        payload['changed'] = True
        payload['message'] = await fbx.vm.resize(vm_config['disk_path'], vm_config['disk_size'])
    await fbx.close()
    return payload

def main():
    run_module()


if __name__ == '__main__':
    main()
