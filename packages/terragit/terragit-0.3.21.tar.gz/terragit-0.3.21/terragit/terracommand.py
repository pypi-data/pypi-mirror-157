import json
import shutil
import subprocess
import threading
import time
import multiprocessing
from math import ceil
from multiprocessing.pool import ThreadPool
from os.path import exists


from tqdm import tqdm

from terragit.terragrunt import *
import terragit.terraConf as terra_conf

class terracommand(terragrunt, bcolors):
    def __init__(self, idProject, idCommit, idMr, gitlab_token, git_url, directory, verbose, ci_commit_title=""):
        super().__init__(verbose)
        self.idProject = idProject
        self.idCommit = idCommit
        self.idMr = idMr
        self.gitlab_token = gitlab_token
        self.git_url = git_url
        self.ci_commit_title = ci_commit_title
        self.directory = directory
        self.verbose = verbose
        self.terraconf = terra_conf.TerraConf()

    def terragruntCommand(self, command):
        mylist = []
        print("state", )
        if self.directory != None:
            mylist.append(self.directory)
        else:
            gl = gitlab.Gitlab(self.git_url, private_token=self.gitlab_token)
            project = gl.projects.get(self.idProject)
            if self.idCommit != None:
                commit = project.commits.get(self.idCommit)
                diff = commit.diff()
            if self.idMr != None:
                mr = project.mergerequests.get(self.idMr)
                diff = mr.changes()['changes']
            folderList = []
            if (len(diff) == 0):
                if not isdir(pathlib.Path(self.ci_commit_title).absolute().as_posix()):
                    print(bcolors.FAIL + self.ci_commit_title + " is not valid path" + bcolors.ENDC)
                else:
                    print("len(diff)==0 else ")
                    self.ci_commit_titlePath = pathlib.Path(self.ci_commit_title).absolute().as_posix()
                    self.pathList.append(self.ci_commit_titlePath)
                    self.printlog(command, self.pathList, self.logsFolder, self.verbose)
            else:
                for change in diff:
                    print("change ", change)
                    newPath = change['new_path']
                    if not ("live/") in newPath:
                        print(pathlib.Path(
                            newPath).absolute().as_posix() + bcolors.WARNING + " OUT of SCOPE" + bcolors.ENDC)
                    else:
                        pathh = pathlib.Path(newPath).parent.absolute().as_posix()
                        folderList.append(pathh)

            mylist = list(dict.fromkeys(folderList))
            print("mylist ", mylist)

        for path in mylist:
            print("mylist for ", mylist)
            if (isdir(path)):
                print("is dir ")
                self.getAllFolder(path)
                if command == "changes":
                    print(mylist)
                    return mylist
        self.printlog(command, self.pathList, self.logsFolder, self.verbose)
        if self.failedloglist:
            if self.verbose:
                for message in self.failedloglist:
                    logfileName = message.split("live/")[1].replace("/", "_")
                    os.chdir(self.failedlogsFolder)

                    shutil.move(self.logsFolder + "/" + logfileName + ".log", "failed_" + logfileName + ".log")
            sys.exit(1)

    def terragrunt_plan(self, group_name):

        token_ci_id = os.getenv("CI_JOB_TOKEN")
        path = os.getenv("my_path")
        list = []
        path_absolute = ""
        # if token_ci_id is None:
        #     path = self.terraconf.get_file_content()
        #     for root, dirs, files in os.walk(path[group_name]['path']):
        #         list.append(root)
        #     i = 0
        #     while str(group_name)+"-grp/infra" not in list[i]:
        #         i += 1
        #         if str(group_name)+"-grp/infra" in list[i]:
        #             path_absolute = list[i]
        #             break
        if token_ci_id is not None:
            path_absolute =path

        subdir = []
        for root, subdirs, files in os.walk(path_absolute):
            if os.path.lexists(os.path.join(root, "terragrunt.hcl")):
                subdir.append(root)

        cwd = ['/builds/clients-acp/202201/chosa-grp/infra/live/aws/global/iam/users/hiba',
               '/builds/clients-acp/202201/chosa-grp/infra/live/aws/global/iam/users/kacem.yedes']
        number_of_task = len(cwd)
        progress_bar = tqdm(total=number_of_task)
        process = 'terragrunt plan -out=tfplan && terragrunt show -json tfplan > tfplan.json'
        processes = []
        for c in cwd:
            proc = subprocess.Popen(["/bin/bash", "-c", process], bufsize=8192, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=c)
            lines = proc.stdout.readlines()
            processes.append(proc)
        for p in processes:
            p.wait()
            progress_bar.update()
        for c in cwd:
            exit = exists(os.path.expanduser(os.path.join(c+"/tfplan.json")))
            print(exit)
        files = []
        for i in range(len(cwd)):
            if exists(os.path.expanduser(os.path.join(cwd[i], "tfplan.json"))):
                file = open(os.path.expanduser(os.path.join(cwd[i], "tfplan.json")))
                data = file.readlines()
                json_object = json.loads(data[0])
                file.close()
                files.append(json_object['resource_changes'])

        added = 0
        changed = 0
        deleted = 0

        for i in range(len(files)):
            print(bcolors.ENDC, "You re working in folder" , bcolors.OKBLUE, cwd[i])
            for j in files[i]:
                if j['change']['actions'] == ['create']:
                    added += 1
                    print(bcolors.OKGREEN, "+", bcolors.ENDC, ' ressource', j['address'], 'will be added')
                if j['change']['actions'] == ['update']:
                    changed += 1
                    print(bcolors.WARNING,"~", bcolors.ENDC, ' ressource', j['address'], 'will be updated in-place')
                if j['change']['actions'] == ['delete']:
                    changed += 1
                    print(bcolors.FAIL ,"-", bcolors.ENDC, ' ressource', j['address'], 'will be destroyed')
        print("Plan:", bcolors.OKGREEN, added, bcolors.ENDC,"to add, ", bcolors.WARNING,changed, bcolors.ENDC," to change, ",bcolors.FAIL,deleted,bcolors.ENDC," to destroy.")

        # processes = []
        # processes1 = []
        # cwd = [path+'/live/aws/global/iam/users/hiba',
        #        path+'/live/aws/global/iam/users/hiba.jaouadi',
        #        path+'/live/aws/global/iam/users/kacem.yedes']
        # number_of_task = len(cwd)
        # progress_bar = tqdm(total=number_of_task)
        # # progress_bar2 = tqdm(total=number_of_task)
        # print(bcolors.OKGREEN, "collecting information ..")
        # process = 'source ~/my_profile && terragrunt plan -out=tfplan'
        # process1 = 'source ~/my_profile ; terragrunt show -json tfplan > tfplan.json'
        # process2 = 'source ~/my_profile && terragrunt plan -out=tfplan && terragrunt show -json tfplan > tfplan.json'
        # for c in cwd:
        #     if "webapp" not in c:
        #         proc = subprocess.Popen(["/bin/bash", "-c", process], bufsize=8192, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=c)
        #         processes.append(proc)
        # for p in processes:
        #     p.wait()
        #     progress_bar.update()
        # for c in cwd:
        #     if "webapp" not in c:
        #         proc1 = subprocess.Popen(["/bin/bash", "-c", process1], bufsize=8192, stdin=None, stdout=subprocess.PIPE ,stderr=subprocess.PIPE, cwd=c)
        #         processes1.append(proc1)
        # for p in processes1:
        #     p.wait()
        # for c in cwd:
        #     if "webapp" in c:
        #         proc = subprocess.run(["/bin/bash", "-c", process2],shell=False,bufsize=8192, stdout=subprocess.PIPE,stdin=None, stderr=subprocess.PIPE, cwd=c)
        #         progress_bar.update()
        #
        # files = []
        # for i in range(len(cwd)):
        #     if exists(os.path.expanduser(os.path.join(cwd[i], "tfplan.json"))):
        #         file = open(os.path.expanduser(os.path.join(cwd[i], "tfplan.json")))
        #         data = file.readlines()
        #         print("myyyy data",data)
        #         json_object = json.loads(data[2])
        #         file.close()
        #         files.append(json_object['resource_changes'])
        #
        # added = 0
        # changed = 0
        # deleted = 0
        #
        # for i in range(len(files)):
        #     print(bcolors.ENDC, "You re working in folder" , bcolors.OKBLUE, cwd[i])
        #     for j in files[i]:
        #         if j['change']['actions'] == ['create']:
        #             added += 1
        #             print(bcolors.OKGREEN, "+", bcolors.ENDC, ' ressource', j['address'], 'will be added')
        #         if j['change']['actions'] == ['update']:
        #             changed += 1
        #             print(bcolors.WARNING,"~", bcolors.ENDC, ' ressource', j['address'], 'will be updated in-place')
        #         if j['change']['actions'] == ['delete']:
        #             changed += 1
        #             print(bcolors.FAIL ,"-", bcolors.ENDC, ' ressource', j['address'], 'will be destroyed')
        # print("Plan:", bcolors.OKGREEN, added, bcolors.ENDC,"to add, ", bcolors.WARNING,changed, bcolors.ENDC," to change, ",bcolors.FAIL,deleted,bcolors.ENDC," to destroy.")

    def terragit_plan(self):
        # token_ci_id = os.getenv("CI_JOB_TOKEN")
        # path = os.getenv("my_path")
        path_absolute = "/home/hiba/Desktop/TERRAGIT/infra"
        # path_absolute = path
        # subdir = []
        # for root, subdirs, files in os.walk(path_absolute):
        #     if os.path.lexists(os.path.join(root, "terragrunt.hcl")):
        #         subdir.append(root)
        cwd = [
            # '/home/hiba/Desktop/TERRAGIT/infra/live/aws/1-dev/app-dev.chosa.allence.cloud/api-acm-validation',
               '/home/hiba/Desktop/TERRAGIT/infra/live/aws/global/iam/users/hiba',
               # '/home/hiba/Desktop/TERRAGIT/infra/live/aws/global/iam/users/hiba.jaouadi'
               ]
        number_of_task = len(cwd)
        progress_bar = tqdm(total=number_of_task)
        process1 = 'source ~/my_profile && terragrunt plan -out=tfplan'
        process2 = 'source ~/my_profile && terragrunt show -json tfplan > tfplan.json'
        processes = []
        lines = []
        lines2 = []

        if not os.path.exists("failedlogs"):
            os.makedirs("failedlogs")
        if not os.path.exists("logs"):
            os.makedirs("logs")

        for c in cwd:
            logs = open(os.path.expanduser(os.path.join("logs/log.txt")), mode='w+')
            failedlogs = open(os.path.expanduser(os.path.join("failedlogs/failed.txt")), mode='w+')
            proc = subprocess.Popen(["/bin/bash", "-c", process1], bufsize=8192, stdin=None,stdout=logs,stderr=failedlogs, cwd=c)
            processes.append(proc)

        for p in processes:
            p.wait()
            progress_bar.update()
        for c in cwd:
            proc = subprocess.Popen(["/bin/bash", "-c", process2], bufsize=8192, stdin=None,stdout=subprocess.PIPE,stderr=subprocess.PIPE, cwd=c)
        for c in cwd:
            exit = exists(os.path.expanduser(os.path.join(c+"/tfplan.json")))
        files = []
        for i in range(len(cwd)):
            if exists(os.path.expanduser(os.path.join(cwd[i], "tfplan.json"))):
                file = open(os.path.expanduser(os.path.join(cwd[i], "tfplan.json")))
                data = file.readlines()
                print(len(data))
                # json_object = json.loads(data[2])
                # file.close()
                # files.append(json_object['resource_changes'])

        # added = 0
        # changed = 0
        # deleted = 0
        #
        # for i in range(len(files)):
        #     print(bcolors.ENDC, "You re working in folder" , bcolors.OKBLUE, cwd[i])
        #     for j in files[i]:
        #         if j['change']['actions'] == ['create']:
        #             added += 1
        #             print(bcolors.OKGREEN, "+", bcolors.ENDC, ' ressource', j['address'], 'will be added')
        #         if j['change']['actions'] == ['update']:
        #             changed += 1
        #             print(bcolors.WARNING,"~", bcolors.ENDC, ' ressource', j['address'], 'will be updated in-place')
        #         if j['change']['actions'] == ['delete']:
        #             changed += 1
        #             print(bcolors.FAIL ,"-", bcolors.ENDC, ' ressource', j['address'], 'will be destroyed')
        # print("Plan:", bcolors.OKGREEN, added, bcolors.ENDC,"to add, ", bcolors.WARNING,changed, bcolors.ENDC," to change, ",bcolors.FAIL,deleted,bcolors.ENDC," to destroy.")
