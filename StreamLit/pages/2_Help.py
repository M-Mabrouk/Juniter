import streamlit as st
from PIL import Image
import os

with st.columns([1,3,1])[1]:
    st.write('# Juniter')
    st.write('---')
    img1 = Image.open(os.path.join(os.path.dirname(__file__)[:-6],'Images/Home_1.png'))
    img2 = Image.open(os.path.join(os.path.dirname(__file__)[:-6],'Images/Home_2.png'))
    img3 = Image.open(os.path.join(os.path.dirname(__file__)[:-6],'Images/Home_3.png'))

    st.subheader('Step 1: Upload your java projects and tests (and mapping file)')
    st.image(img1, use_column_width=True)
    st.write('The mapping file, if uploaded, needs to be a CSV file with the following format (Any headers can be used):')
    st.dataframe({'project_filename': ['Team 1.rar', 'team_02.zip', 'team 3.zip'], 'Alias': ['Team 1', 'Team 2', 'Team 3']}, use_container_width=True)
    st.write('---')
    st.subheader('Step 2: Click on Evaluate and Wait for the results to be generated')
    st.image(img2, use_column_width=True)
    st.write('---')
    st.subheader('Step 3: View and Download the results')
    st.image(img3, use_column_width=True)