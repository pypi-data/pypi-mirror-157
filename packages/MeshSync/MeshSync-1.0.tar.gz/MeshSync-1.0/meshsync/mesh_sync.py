# -*- coding: utf-8 -*-

"""mesh_sync provides entry point main()."""

__version__ = "1.0"

import base64
import re
import sys
import os
import requests


def check_if_dot_git_exists() -> bool:
    # Scan the root directory for .git
    for root, dirs, files in os.walk(os.getcwd()):
        if '.git' in dirs:
            return True
    return False


def find_git_url() -> str or None:
    """
    Scan the .git folder for the repository url and name
    :return:
    """
    for root, dirs, files in os.walk(os.getcwd()):
        if '.git' in dirs or '.git' in files or '.git' in root:
            for file in files:
                if file == 'config':
                    with open(os.path.join(root, file), 'r') as f:
                        contents = f.read()
                        url = re.search(r'url\s*=\s*(.*)', contents).group(1)
                        path_and_project_name = url.replace("https://github.com/", "").replace(".git", "")
                        return path_and_project_name
    return None


def fetch_latest_commit_hash() -> str or None:
    """
    Scan the .git folder for the latest commit hash
    :return:
    """

    url = "https://api.github.com/repos/MeshMonitors-Remote-1/ShopifyMonitor/commits"

    payload = {}
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': 'Bearer -',
        'Cookie': '_octo=GH1.1.613847517.1655532567; logged_in=no'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)


def download_and_replace_file(session, url, file_path: str, auth_token: str):
    """
    Download a file from a url and replace the file at the given path
    :param auth_token:
    :param session:
    :param url:
    :param file_path:
    :return:
    """
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'Bearer {auth_token}',
        'Cookie': '_octo=GH1.1.613847517.1655532567; logged_in=no'
    }
    response = session.request("GET", url, headers=headers)

    if response.status_code != 200:
        print("File_Get Error: %s" % response.text)
        return None

    # Make folder if it doesn't exist
    if '/' in file_path:
        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))

    with open(file_path, 'wb') as f:
        file_content = base64.b64decode(response.json()['content'])
        f.write(file_content)


def get_update_file(auth_token: str, repo_url) -> str or None:
    """
    Scan the .git folder for the latest commit hash
    :param auth_token:
    :param repo_url:
    :return:
    """

    url = f"https://api.github.com/repos/{repo_url}/contents/UPDATE_FILE"
    session = requests.Session()

    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'Bearer {auth_token}',
        'Cookie': '_octo=GH1.1.613847517.1655532567; logged_in=no'
    }

    response = session.request("GET", url, headers=headers)

    if response.status_code == 200:
        # Get the file content and since it's a base64 encoded string, decode it
        content = base64.b64decode(response.json()['content'])

        # Convert the content to a string
        content = content.decode('utf-8')

        ask_for_confirmation = input("Do you want to replace the update/download files with the latest version? [y/n] ")
        if ask_for_confirmation.lower() == 'y':
            if len(content) > 0:
                change_list = content.split('\n')
                for change in change_list:
                    change_wanted = change.split(':')
                    if len(change_wanted) > 1:
                        change_action = change_wanted[0]
                        change_file = change_wanted[1]
                        if change_action == 'overwrite':
                            print("Overwrite/Download file: %s" % change_file)
                            link = f"https://api.github.com/repos/" \
                                   f"{repo_url}/contents/{change_file}"
                            download_and_replace_file(session, link, change_file, auth_token)
        else:
            print("Aborting...")
            sys.exit(0)
    else:
        print("Auth Error: %s" % response.text)
        return None


def get_all_files(auth_token: str, repo_url):
    session = requests.Session()

    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'Bearer {auth_token}',
        'Cookie': '_octo=GH1.1.613847517.1655532567; logged_in=no'
    }

    response = session.request("GET", repo_url, headers=headers)

    if response.status_code == 200:
        response_json = response.json()
        for file in response_json['tree']:
            if file['type'] == 'blob':
                print(">> Downloading file: %s" % file['path'])
                url = f"https://api.github.com/repos/{repo_url}/contents/" + file['path']
                download_and_replace_file(session, url, file['path'], auth_token)
    else:
        print("Auth Error: %s" % response.text)
        return None


def main():
    # Check if config.txt exists
    if not os.path.exists('config.txt'):
        token = input("Token not found, please enter your github token: ")
        with open('config.txt', 'w') as f:
            f.write(token)
    else:
        # read the token from config.txt
        with open('config.txt', 'r') as f:
            token = f.read()

    print(">> Executing mesh_sync version %s." % __version__)
    if check_if_dot_git_exists():
        print(">> Found .git folder, checking for updates...")
        git_url = find_git_url()
        if git_url is not None:
            print(">> Found git url: %s" % git_url)
            get_update_file(auth_token=token, repo_url=git_url)
        else:
            print(">> Could not find .git url")
            git_url_input = input("Please enter the git url: ")
            if git_url_input is not None:
                is_empty = os.listdir(os.getcwd()) == []
                if is_empty:
                    print(">> No files found in the current directory, downloading latest version...")
                    get_all_files(token, f"https://api.github.com/repos/{git_url}/git/trees/master?recursive=1")
                else:
                    print(">> Found files in the current directory, updating latest version...")
                    get_update_file(auth_token=token, repo_url=git_url)
            else:
                print("Please enter a valid git url. Aborting...")
                sys.exit(0)
