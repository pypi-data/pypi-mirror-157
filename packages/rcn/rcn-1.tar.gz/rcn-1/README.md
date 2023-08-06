# rcn-cli

RControlNet CLI for setting up client for both IOR and RCN

### Install

    pip install git+https://github.com/mayank31313/rcn-cli

### Usage

#### Configure profile

    python -m rcn configure --profile default
    
#### List Profiles

    python -m rcn profile ls
    
#### Set Profile as default

    python -m rcn profile set-default [profile-name]