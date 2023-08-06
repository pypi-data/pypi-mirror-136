# Shortcuts for interacting with Azure resources
## Usage
### Print a VM IP after fuzzy searching
```
$ azure-interactive-shortcuts public-vm-ip
⠙ Collecting IP addresses from all VMs using Azure CLI
```
```
$ azure-interactive-shortcuts public-vm-ip
azis public-vm-ip
[19:12:24] Found 180 virtual machines, and 96 public ip   _public_vm_ip.py:76
           addresses                                                         
           4 ip addresses have the same name, and have    _public_vm_ip.py:85
           been discarded                                                    
Select an IP address:
 aatifs-cool-vm1-ip1   Resource group: my-rg1, VMs: aatifs-cool-VM1... 
 aatifs-cool-vm1-ip2   Resource group: my-rg1, VMs: aatifs-cool-VM1... 
 aatifs-cool-vm2-ip3   Resource group: my-rg2, VMs: aatifs-cool-VM2... 
 aatifs-cool-vm2-ip4   Resource group: my-rg2, VMs: aatifs-cool-VM2... 
```

This allows you to have quick one-liners:
```bash
ssh azureuser@"$(azis public-vm-ip)"
```

## Installation
Recommended installation is with [pipx](https://github.com/pypa/pipx):
```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
python3 -m pipx install azure-interactive-shortcuts
```

### Autocompletion
Autocompletion is done with [argcomplete](https://github.com/kislyuk/argcomplete)
```bash
pipx install --force argcomplete

# ~/.bashrc
eval "$(register-python-argcomplete azis)"
eval "$(register-python-argcomplete azure-interactive-shortcuts)"
```