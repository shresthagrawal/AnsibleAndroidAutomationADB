#!/usr/bin/python
# to acticate developers enc . venv/bin/activate && . hacking/env-setup
ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}


DOCUMENTATION = '''
---
module: adb

short_description: Launch/Debug apps and Run shell commands on Andoid Device/Emulator on Ansible using ADB

version_added: "1.0"

description:
    - "ADB is a CLI tool in the Android SDK toolkit for running shell commands, launching
       debugging apps, and performing all android related task on a physical device
       or an emulator. This module uses the ADB tool to provide automation to all these functionality
       in Ansible"

options:
    adbLocation:
        description:
            - Enter the dir containing the Adb tool eg: /root/Android/Sdk/platform-tools/
        required: false
    task:
        description:
            - Should be one of configure/reboot/install/reinstall/uninstall/copy/fetch/shell/list/kill to perform a specific task         
        required: true
    src:
        description:
            - Source from where to copy/ fetch / install apk (required for copy , fetch or install)
        required: false    
    
    dest: 
        description:
            - Destination where to paste/ download (required for copy or fetch)
        required: false    

    target: 
        description: 
            - Host device to run the task. Eg: emulator-5554 . could also be all for all available device and input to take user input.
        required: true 

    pkgName: 
        description:
            - Package Name to uninstall       
        required: false 
    port:
        description:
            - Port for configuration if configure task is chosen
        required: false

    ip:
        description:
            - Ip address for configuration if configure task is choosen
        required: false

    command:
        description:
            - shell command to run if shell task is chosen    
                    

extends_documentation_fragment:
    - azure

author:
    - Shresth Agrawal (@shresthagrawal.31 | @arash)
'''

EXAMPLES = '''
# To reboot all conected devices
    - adb:
        task: 'reboot'
        target: 'all'

# To list all available devices
    - adb:
        task: 'list'
      register: output
    - name: dump output
        debug:
          var: output 

# To run arbitary shell command on device 'emulator-5554' 
    - adb:
        task: 'shell'
        command: 'whoami'
      register: output
    - name: dump output
        debug:
          var: output 
# To instll apk
    - adb:
        task: 'install'
        src: 'hello.apk'

#       
'''

RETURN = '''
original_message:
    description: The original name param that was passed in
    type: str
message:
    description: The output message that the sample module generates
'''

from ansible.module_utils.basic import AnsibleModule
import subprocess

defaultLocation = "/root/Android/Sdk/platform-tools/adb"

def convertResults(raw):
    return raw.decode('utf-8')


# results are alwats returned in an array with first value the output and second value the status
def getVersion(adbLocation):
    result =[]
    try:
        result.append(subprocess.check_output([adbLocation,"version"])) # result
        result.append(1) # status
    except OSError:
        result.append("")
        result.append(-1)
        print("Error: could not find ADB on the default/ specified location."+ 
              "Please Specify a location or recheck the existing solution")
    return result 

def listDevices(adbLocation):
    result =[]
    output=convertResults(subprocess.check_output([adbLocation,"devices","-l"]))
    result.append(output)
    result.append(1)
    raw = result[0][:]
    deviceList = []
    while(len(raw)!=0):
        if(raw.find("\nemulator")==-1):
            break
        raw = raw[raw.find("\nemulator")+1:]
        deviceList.append(raw[:raw.find(" ")])
        #print(raw[:raw.find(" ")])
    result.append(deviceList)   
    return result

def reboot(adbLocation,id):
    try:
        subprocess.check_output([adbLocation,'-s',id,'reboot'])
    except:
        print('Error: Could not reboot device, check if the server is running correctly')

def copy(adbLocation,id,src,dest):
    subprocess.check_output([adbLocation,'-s',id,'push',src,dest])

def fetch(adbLocation,id,src,dest):         
    subprocess.check_output([adbLocation,'-s',id,'pull',src,dest])

def install(adbLocation,id,src):    
    subprocess.check_output([adbLocation,'-s',id,'install','-t','-g',src])

def reinstall(adbLocation,id,src):  
    subprocess.check_output([adbLocation,'-s',id,'install','-t','-g','-r',src])

def uninstall(adbLocation,id,pkg):
    subprocess.check_output([adbLocation,'-s',id,'uninstall',pkg])

def killServer(adbLocation):
    subprocess.check_output([adbLocation,'kill-server'])

def shell(adbLocation,id,command):
    result =[]
    result.append(convertResults(subprocess.check_output([adbLocation,"-s",id,"shell",command])))
    result.append(1)
    return result

def configure(adbLocation,id,port):
    subprocess.check_output([adbLocation,"-s",id,'tcpip',port])
    

def run_module():
    # available arguments/parameters a user can pass to the module
    module_args = dict(
        adbLocation=dict(type='str', required=False, default=defaultLocation),
        target=dict(type='str', required=False,default="all"),
        task=dict(type='str', required=True),
        src=dict(type='str', required=False),
        dst=dict(type='str', required=False),
        port=dict(type='str', required=False),
        ip=dict(type='str', required=False),
        command=dict(type='str', required=False),
        pkgName=dict(type='str', required=False),

    )

    # seed the result dict in the object
    result = dict(
        status=1,
        output=''
    )

    # create an object for ansible module and pass the structure of input fields 
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        return result

    # get the list of all target devices
    targets = []
    if module.params['target']=="all":
        # if all is chosen get find all avilable targets
        targets=listDevices(module.params['adbLocation'])[2]
    elif module.params['target']=="input":
        # if input is choosen take input from user
        print(listDevices(module.params['adbLocation'])[0])
        targets.append(input("Enter the name of the Device:"))
    else :
        # if a specific host is choosen 
        targets.append(module.params['target'])

    # check if the adb location is correct 
    if(getVersion(module.params['adbLocation'])[1]==-1):
        module.fail_json(msg='error in adbLocation', **result)
        

    for target in targets:
        print(target)
        if(module.params['task']=="reboot"):
            reboot(module.params['adbLocation'],target)
        elif(module.params['task']=="install"):
            if(module.params['src']==""):
                module.fail_json(msg='no src found', **result)
            install(module.params['adbLocation'],target,module.params['src'])
        elif(module.params['task']=="reinstall"):
            if(module.params['src']==""):
                module.fail_json(msg='no src found', **result)
            reinstall(module.params['adbLocation'],target,module.params['src'])
        elif(module.params['task']=="uninstall"):
            if(module.params['pkgName']==""):
                module.fail_json(msg='no package to uninstall found', **result)
            reinstall(module.params['adbLocation'],target,module.params['pkgName'])
        elif(module.params['task']=="copy"):
            if(module.params['src']=="" or module.params['dst']==""):
                module.fail_json(msg='Source/Destination not found', **result)
            copy(module.params['adbLocation'],target,module.params['src'],module.params['dst'])
        elif(module.params['task']=="fetch"):
            if(module.params['src']=="" or module.params['dst']==""):
                module.fail_json(msg='Source/Destination not found', **result)
            fetch(module.params['adbLocation'],target,module.params['src'],module.params['dst'])
        elif(module.params['task']=="kill"):
            killServer(module.params['adbLocation'])
        elif(module.params['task']=="configure"):
            if(module.params['port']==""):
                module.fail_json(msg='Port not found', **result)
            configure(module.params['adbLocation'],target,module.params['port'])                
        elif(module.params['task']=="list"):
            result['output']=(listDevices(module.params['adbLocation'])[2])
        elif(module.params['task']=="shell"):
            if(module.params['command']==""):
                module.fail_json(msg='command not found' , **result)
            result['output']=shell(module.params['adbLocation'],target,module.params['command'])[0]

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
