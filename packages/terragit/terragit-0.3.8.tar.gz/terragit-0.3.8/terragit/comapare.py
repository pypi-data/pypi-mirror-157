import subprocess

import requests # token : gitlab_token
import os

class Compare:
    def __init__(self):

        #,tf_state1, tf_state2
        def list_state(self, infra):
            cmd = " cd " + infra + " && terragrunt state list < tf"
            popen = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True,
                                     encoding='utf8')
            lines = popen.communicate(input='\n')[0].split("\n")