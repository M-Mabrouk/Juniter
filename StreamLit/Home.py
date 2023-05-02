import asyncio
import time
import streamlit as st
import pandas as pd
import sys
import os
import zipfile

sys.path.append(os.path.dirname(__file__)[:-9])

import Juniter

import numpy as np
import os

st.set_page_config(page_title='Juniter', page_icon=':robot_face:', layout='wide')


def save_files(projects, tests, mapping=None):
    Juniter.clear_files()
    # Save the projects
    for project in projects:
        with open(os.path.join(Juniter.PROJECTS_DIR, project.name), 'wb') as f:
            f.write(project.getbuffer())
    # Save the tests
    for test in tests:
        with open(os.path.join(Juniter.TESTS_DIR, test.name), 'wb') as f:
            f.write(test.getbuffer())
    # Save the mapping
    if mapping:
        st.session_state['map'] = dict()
        df = pd.read_csv(mapping)
        for i in range(len(df)):
            st.session_state['map'][str(df.iloc[i, 0])] = str(df.iloc[i, 1])

def clean():
    Juniter.clear_files()
    st.session_state['map'] = None

def update_progress(info):
    st.session_state['progress'] = info['current'] / info['total']
    st.session_state['prg_bar'].progress(st.session_state['progress'])
    st.session_state['prg_info'].write(f'step {info["current"]} out of {info["total"]}')


def convert_zip(dfs:dict):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    # Convert the dataframes to csv files
    for test in dfs:
        dfs[test].to_csv(os.path.join(Juniter.RESULTS_DIR, test + '.csv'), index=False)
    # Convert the csv files to zip
    with zipfile.ZipFile(os.path.join(Juniter.RESULTS_DIR, 'results.zip'), 'w') as zip:
        for file_name in os.listdir(Juniter.RESULTS_DIR):
            if file_name.endswith('.csv'):
                zip.write(os.path.join(Juniter.RESULTS_DIR, file_name), arcname=file_name)
        # Remove the csv files
        for file_name in os.listdir(Juniter.RESULTS_DIR):
            if file_name.endswith('.csv'):
                os.remove(os.path.join(Juniter.RESULTS_DIR, file_name))
    return open(os.path.join(Juniter.RESULTS_DIR, 'results.zip'), 'rb')
    
    
    

    

with st.columns([1,3,1])[1]:
    st.write('# Juniter')
    st.write('---')

if 'processing' not in st.session_state:
    st.session_state['processing'] = True

if 'progress' not in st.session_state:
    st.session_state['progress'] = 0

if 'results' not in st.session_state:
    st.session_state['results'] = None

if 'map' not in st.session_state:
    st.session_state['map'] = None

if st.session_state['processing']:
    clean()
    _, col2, _ = st.columns([1,3,1])
    with col2:
        st.subheader('Upload your projects')
        project_files = st.file_uploader('projects', type=['zip', 'rar'], accept_multiple_files=True, label_visibility='hidden', key='projects')
        st.write('\n')
        st.subheader('Upload your tests')
        test_files = st.file_uploader('tests', type=['java'], accept_multiple_files=True, label_visibility='hidden', key='tests')
        st.write('\n')
        st.subheader('Upload your mapping file (Optional)')
        mapping_file = st.file_uploader('mapping', type=['csv'], accept_multiple_files=False, label_visibility='hidden', key='mapping')
        st.write('---')
    
    col1, col2, col3 = st.columns(3)
    with col2:
        if st.button('Evaluate', use_container_width=True, type='primary'):
            if project_files == [] or test_files == []:
                st.error('Please upload both your projects and tests')
            else:
                save_files(project_files, test_files, mapping_file)
                st.session_state['processing'] = False
                st.experimental_rerun()
else:
    pre = st.empty()
    _, col2, col3 = st.columns([1,3,1])
    if st.session_state['progress'] < 1 or st.session_state['results'] is None:
        with col2:
            st.subheader('Progress')
            if 'prg_bar' not in st.session_state:
                st.session_state['prg_bar'] = st.progress(0)
            st.session_state['prg_bar'].progress(st.session_state['progress'])
        with col2.columns([4,1])[1]:
            if 'prg_info' not in st.session_state:
                st.session_state['prg_info'] = st.empty()
        with col2:
            st.write('---')
        st.session_state['results'] =  asyncio.run(Juniter.run(progress=update_progress, mapping=st.session_state['map']))
        st.experimental_rerun()
    else:
        Juniter.clear_files()
        with col2:
            st.success('Evaluation done')
            downloadable = convert_zip(st.session_state['results'])
            tabs = st.tabs(st.session_state['results'].keys())
            for key, value in st.session_state['results'].items():
                with tabs[list(st.session_state['results'].keys()).index(key)]:
                    st.dataframe(value,use_container_width=True)
        with col2:
            st.download_button('Download results', data=downloadable, file_name='results.zip', mime='application/zip')
        
    
