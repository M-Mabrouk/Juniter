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
    st.session_state['map'] = None
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

if 'phase' not in st.session_state:
    st.session_state['phase'] = 'upload'

print(st.session_state['phase'])
center = st.columns([1, 3, 1])[1]

with center:
    st.write('# Juniter')
    st.write('---')

    if st.session_state.phase == 'upload':
        # Upload the projects
        st.subheader('Upload your projects')
        project_files = st.file_uploader('projects', type=['zip', 'rar'], accept_multiple_files=True, label_visibility='hidden', key='projects')
        st.write('\n')
        st.subheader('Upload your tests')
        test_files = st.file_uploader('tests', type=['java'], accept_multiple_files=True, label_visibility='hidden', key='tests')
        st.write('\n')
        st.subheader('Upload your mapping file (Optional)')
        mapping_file = st.file_uploader('mapping', type=['csv'], accept_multiple_files=False, label_visibility='hidden', key='mapping')
        st.write('---')
        if st.button('Evaluate', use_container_width=True, type='primary'):
            if project_files and test_files:
                save_files(project_files, test_files, mapping_file)
                st.session_state.phase = 'inbetween'
                st.experimental_rerun()
            else:
                st.error('Please upload at least one project and one test')
    if st.session_state.phase == 'inbetween':
        st.write('---')
        st.write('---')
        st.write('---')
        st.write('---')
        st.write('---')
        st.write('---')
        st.session_state.phase = 'evaluate'
    if st.session_state.phase == 'evaluate':
        # Evaluate the projects
        st.subheader('Evaluation in progress')
        prg = st.empty()
        with center.columns([1, 1, 1])[2]:
                prg.progress(0)
                step = st.empty()
                step.text('Step 0 out of ?')
        st.write('---')
        for snapshot in Juniter.run_generator(mapping=st.session_state['map']):
            prg.progress(snapshot['current'] / snapshot['total'])
            with center.columns([1, 1, 1])[2]:
                step.text(f'Step {snapshot["current"]} out of {snapshot["total"]}')
            st.session_state['results'] = snapshot['results']
        
        st.session_state.phase = 'results'
        st.experimental_rerun()
    if st.session_state.phase == 'results':
        Juniter.clear_files()
        with center:
            st.success('Evaluation done')
            downloadable = convert_zip(st.session_state['results'])
            tabs = st.tabs(st.session_state['results'].keys())
            for key, value in st.session_state['results'].items():
                with tabs[list(st.session_state['results'].keys()).index(key)]:
                    st.dataframe(value,use_container_width=True)
        with center:
            st.download_button('Download results', data=downloadable, file_name='results.zip', mime='application/zip')

        