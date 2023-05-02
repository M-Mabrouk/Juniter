import asyncio
import os
import re
import zipfile
import rarfile
import subprocess
import pandas as pd
from typing import Callable

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'my_app')
TEMPLATE_DIR = os.path.abspath(TEMPLATE_DIR)

TEMPLATE_SRC_DIR = os.path.join(TEMPLATE_DIR, 'src','main','java')
TEMPLATE_TEST_DIR = os.path.join(TEMPLATE_DIR, 'src','test','java','com','example','my_app')

PROJECTS_DIR = os.path.join(os.path.dirname(__file__), 'projects')
PROJECTS_DIR = os.path.abspath(PROJECTS_DIR)
TESTS_DIR = os.path.join(os.path.dirname(__file__), 'tests')
TESTS_DIR = os.path.abspath(TESTS_DIR)

RESULTS_DIR = os.path.join(os.path.dirname(__file__), 'results')
RESULTS_DIR = os.path.abspath(RESULTS_DIR)

if not os.path.exists(PROJECTS_DIR):
    os.mkdir(PROJECTS_DIR)
if not os.path.exists(TESTS_DIR):
    os.mkdir(TESTS_DIR)
if not os.path.exists(RESULTS_DIR):
    os.mkdir(RESULTS_DIR)


def clear_files():
    clear_project()
    clear_test()
    for project in os.listdir(PROJECTS_DIR):
        subprocess.call(['rm', '-rf', os.path.join(PROJECTS_DIR, project)])
    for test in os.listdir(TESTS_DIR):
        subprocess.call(['rm', '-rf', os.path.join(TESTS_DIR, test)])


def clear_project():
    for package in os.listdir(TEMPLATE_SRC_DIR):
        subprocess.call(['rm', '-rf', os.path.join(TEMPLATE_SRC_DIR, package)])

def clear_test():
    for test in os.listdir(TEMPLATE_TEST_DIR):
        subprocess.call(['rm', '-rf', os.path.join(TEMPLATE_TEST_DIR, test)])

def bootstrap(projects_file:str, tests_file:str):
    # Clear the project and test directories
    clear_project()
    clear_test()
    
    # Extract the template project
    if projects_file.endswith('.zip'):
        # Extract the project
        with zipfile.ZipFile(projects_file, 'r') as zip_ref:
            zip_ref.extractall(PROJECTS_DIR)
    elif projects_file.endswith('.rar'):
        # Extract the project
        with rarfile.RarFile(projects_file, 'r') as rar_ref:
            rar_ref.extractall(PROJECTS_DIR)
    else:
        return False
    if tests_file.endswith('.zip'):
        # Extract the tests
        with zipfile.ZipFile(tests_file, 'r') as zip_ref:
            zip_ref.extractall(TESTS_DIR)
    elif tests_file.endswith('.rar'):
        # Extract the tests
        with rarfile.RarFile(tests_file, 'r') as rar_ref:
            rar_ref.extractall(TESTS_DIR)
    else:
        return False

    return True

def prepare_project(project_file:str):
    clear_project()
    project_dir = None
    if project_file.endswith('.zip'):
        # Extract the project
        project_path = os.path.join(PROJECTS_DIR, project_file)
        with zipfile.ZipFile(project_path, 'r') as zip_ref:
            # Get the name of the extracted project directory
            project_dir = os.path.join(PROJECTS_DIR, project_file[:-4])
            zip_ref.extractall(project_dir)
    if project_file.endswith('.rar'):
        # Extract the project
        project_path = os.path.join(PROJECTS_DIR, project_file)
        with rarfile.RarFile(project_path, 'r') as rar_ref:
            # Get the name of the extracted project directory
            project_dir = os.path.join(PROJECTS_DIR, project_file[:-4])
            rar_ref.extractall(project_dir)
        
    # If the project was't a zip or rar file, skip it
    if project_dir is None:
        return False
    
    target = None
    # Recursively find the src directory in the extracted project directory
    for root, dirs, files in os.walk(project_dir):
        if 'src' == root.split('/')[-1]:
            target = root
            break
    if target is None:
        return False
    for package in os.listdir(target):
        if package == 'tests' or package == 'module-info.java':
            continue
        subprocess.call(['cp', '-r', os.path.join(target, package), TEMPLATE_SRC_DIR])
    return True

def prepare_test(test_file:str):
    clear_test()
    subprocess.call(['cp', '-r', os.path.join(TESTS_DIR, test_file), TEMPLATE_TEST_DIR])

def create_dataframes():
    labels = ['filename', 'tests', 'failures', 'errors', 'skipped']
    eval_results = {test_file[:-5]:pd.DataFrame(columns=labels) for test_file in os.listdir(TESTS_DIR)}
    eval_results['Total'] = pd.DataFrame(columns=labels)
    return eval_results

async def run(mapping:dict = None , progress:Callable = None):
    print('Running Juniter')
    done = 0
    out_of = len(list(os.listdir(TESTS_DIR))) * len(list(os.listdir(PROJECTS_DIR)))
    if progress is not None:
                progress({'current': done, 'total': out_of})
    await asyncio.sleep(0.1)
    eval_results = create_dataframes()
    for project in os.listdir(PROJECTS_DIR):
        if not prepare_project(project):
            continue
        total_results = [0, 0, 0, 0]
        for test in os.listdir(TESTS_DIR):
            prepare_test(test)
            comp = subprocess.run(["mvn", "compile"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, cwd=TEMPLATE_DIR)
            result = subprocess.run(["mvn", "test"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, cwd=TEMPLATE_DIR)
            await asyncio.sleep(0.1)
            test_name = test[:-5]
            output = result.stdout
            test_results = re.search(r'Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+)', output.decode('utf-8'))
            if test_results is None:
                continue
            done += 1
            if progress is not None:
                progress({'current': done, 'total': out_of})
            test_results = test_results.groups()
            filename = project[:-4]
            if mapping is not None and project in mapping:
                filename = mapping[project]
            test_results = [int(x) for x in test_results]
            eval_results[test_name].loc[len(eval_results[test_name])] = [filename] + test_results
            total_results = [sum(x) for x in zip(total_results, test_results)]
        eval_results['Total'].loc[len(eval_results['Total'])] = [filename] + total_results
    return eval_results



def save_results(eval_results:dict, save_dir:str=RESULTS_DIR):
    for file_name, results in eval_results.items():
        results.to_csv(os.path.join(save_dir, file_name + '.csv'), index=False)
    

            

    
