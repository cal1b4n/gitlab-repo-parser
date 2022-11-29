import requests
import json
import argparse
from datetime import datetime
import os

# Define Lists to be used
group_ids = []
group_names = []
project_id = []
excluded_formats = ['.exe', '.dll', '.jpeg', '.jpg', '.png', '.svg', '.gif', '.ico']

# Arguments
parser = argparse.ArgumentParser(description='Search for keyword in GitLab projects')
parser.add_argument('-g', '--group', help='Group name to search in', required=False)
parser.add_argument('-p', '--project', help='Project name to search in', required=False)
parser.add_argument('-k', '--keyword', help='Keyword to search in', required=True)
args = parser.parse_args()

# Keyword to search for
project = args.project
group = args.group
keyword = args.keyword

# Create timestamp for log file
now = datetime.now()
start_time = now.strftime("%H:%M:%S")
print("Start time: ", start_time)

# Define URL & Access Token
access_token = os.getenv('GITLAB_TOKEN')
gitlab_url = os.getenv('GITLAB_URL')

# Clear output file
open(f"found_keywords-{start_time}.txt", "w").close()


# Loop through groups and add group_id and group_name to lists
def get_all_groups():
    parse_groups = requests.get(gitlab_url + f'api/v4/groups?access_token={access_token}&per_page=100',
                                verify='./star.ele.local.crt')

    for group in parse_groups.json():

        print("====================")
        print("Group ID:", group['id'], "Group name: ", group['name'], "\n")

        group_ids.append(group['id'])
        group_names.append(group['name'])

        # Get all projects in group
        page = 1
        id_answer = True
        while (id_answer == True):
            parse_projects = requests.get(gitlab_url + 'api/v4/groups/' + str(
                group['id']) + '/projects' + f"?access_token={access_token}&per_page=100&page={page}",
                                          verify='./star.ele.local.crt')
            for project in parse_projects.json():
                project_id.append(project['id'])
                print("Project ID:", project['id'], "Project name: ", project['name'])

            pretty_json = json.dumps(parse_projects.json(), indent=4, sort_keys=True)
            answer = json.loads(pretty_json)
            id_answer = "id" in answer

            page += 1
            print("====================")
            print("PAGE: ", page)

        print("====================")


# Loop through projects and get project tree and print out project name and file names
def get_all_projects():
    for project in project_id:
        page = 1
        id_answer = True
        while (id_answer == True):
            parse_projects_tree = requests.get(
                gitlab_url + f'api/v4/projects/{project}/repository/tree?access_token={access_token}&recursive=true&per_page=100&page={page}',
                verify='./star.ele.local.crt')
            page += 1
            pretty_json = json.dumps(parse_projects_tree.json(), indent=4, sort_keys=True)
            answer = json.loads(pretty_json)
            id_answer = "id" in answer
            for file in parse_projects_tree.json():
                try:
                    file_path = file['path']
                    file_path_edited = file_path.replace("/", "%2F")
                    if file['type'] == "blob" and not file['name'].endswith(tuple(excluded_formats)):

                        parse_file_content = requests.get(
                            gitlab_url + f'api/v4/projects/{project}/repository/files/{file_path_edited}/raw?&access_token={access_token}',
                            verify='./star.ele.local.crt')

                        print("\n\n\n")
                        print("====================")
                        print("Project #:  ", int(project_id.index(project)) + 1, "/", len(project_id) + 1)
                        print("Project ID: ", project)
                        print("File Name:  ", file['name'])
                        print("File Path:  ", file['path'])
                        print("File ID:    ", file['id'])
                        print("====================")

                        if parse_file_content.status_code == 404:
                            print("path is not correct +")
                        else:
                            print("Status Code --- ", parse_file_content.status_code)
                            print("====================")

                        # Search for keyword in file content and print out line number and line content ignore empty lines and case sensitive
                        for line in parse_file_content.text.splitlines():
                            if keyword.lower() in line.lower():
                                print("Line Content: ", line)
                                print("====================")
                                with open(f"found_keywords-{start_time}.txt", 'a') as f:
                                    f.write(
                                        f"Project ID: {str(project)}\n File Name: {str(file['name'])}\n File Path: {str(file['path'])}\n File ID: {str(file['id'])}\n Line Content: {str(line)}\n")

                    elif file['type'] == "tree":
                        print("Found tree type, Skipping")
                    elif file['name'].endswith(tuple(excluded_formats)) == True:
                        print("Found excluded format, Skipping")
                    else:
                        print("Error problem")
                        exit()
                except TypeError:
                    print(f"Can not find Repository tree of project {project}. Skipping...")
                    continue

    print("\n\n\n====================")
    print("Done!")
    print("====================")
    print("Number of groups in the list = ", len(group_ids))
    print("Number of projects in the list = ", len(project_id))


# Loop through single group
def get_single_group():
    # Get all projects in group
    page = 1
    id_answer = True
    while (id_answer == True):
        parse_projects = requests.get(
            gitlab_url + f'api/v4/groups/{group}/projects?access_token={access_token}&per_page=100&page={page}',
            verify='./star.ele.local.crt')

        for project in parse_projects.json():
            project_id.append(project['id'])
            print("Project ID:", project['id'], "Project name: ", project['name'])

        pretty_json = json.dumps(parse_projects.json(), indent=4, sort_keys=True)
        answer = json.loads(pretty_json)
        id_answer = "id" in answer

        page += 1
        print("====================")
        print("PAGE: ", page)

    print("====================")


# Loop through projects of a single group
def get_single_project():
    page = 1
    id_answer = True
    while id_answer:
        parse_projects_tree = requests.get(
            gitlab_url + f'api/v4/projects/{project}/repository/tree?access_token={access_token}&recursive=true&per_page=100&page={page}',
            verify='./star.ele.local.crt')
        page += 1
        pretty_json = json.dumps(parse_projects_tree.json(), indent=4, sort_keys=True)
        answer = json.loads(pretty_json)
        id_answer = "id" in answer
        for file in parse_projects_tree.json():
            try:
                file_path = file['path']
                file_path_edited = file_path.replace("/", "%2F")
                if file['type'] == "blob" and not file['name'].endswith(tuple(excluded_formats)):

                    parse_file_content = requests.get(
                        gitlab_url + f'api/v4/projects/{project}/repository/files/{file_path_edited}/raw?&access_token={access_token}',
                        verify='./star.ele.local.crt')

                    print("\n\n\n")
                    print("====================")
                    print("Project ID: ", project)
                    print("File Name:  ", file['name'])
                    print("File Path:  ", file['path'])
                    print("File ID:    ", file['id'])
                    print("====================")

                    if parse_file_content.status_code == 404:
                        print("path is not correct +")
                    else:
                        print("Status Code --- ", parse_file_content.status_code)
                        print("====================")
                        # Search for keyword in file content and print out line number and line content ignore empty lines and case sensitive
                        for line in parse_file_content.text.splitlines():
                            if keyword.lower() in line.lower():
                                print("Line Content: ", line)
                                print("====================")
                                with open(f"found_keywords-{start_time}.txt", 'a') as f:
                                    f.write(
                                        f"Project ID: {str(project)}\n File Name: {str(file['name'])}\n File Path: {str(file['path'])}\n File ID: {str(file['id'])}\n Line Content: {str(line)}\n")

                elif file['type'] == "tree":
                    print("Found tree type, Skipping")
                elif file['name'].endswith(tuple(excluded_formats)):
                    print("Found excluded format, Skipping")
                else:
                    print("Error problem")
                    exit()

            except TypeError:
                print(f"Can not find Repository tree of project {project}. Skipping...")
                continue


if group is not None:
    get_single_group()

if group is None and project is not None:
    get_single_project()

elif group is None and project is None:
    get_all_groups()
    get_all_projects()
