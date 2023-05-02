import streamlit as st

with st.columns([1, 7, 1])[1]:
    st.write("# Juniter")

    st.write("---")

    st.write("This tool was built to serve as an evaluation tool for an **OOP** University-level course, taught in Java.")

    st.write("It uses a maven template project and the maven command-line tool through python to run tests on multiple projects and outputs the results to CSV files.")

    st.write("**Juniter supports both Junit 4 and 5.**")

    st.write("The tool was intended to be used to evaluate \"vanilla\" java projects built without the use of any package-manager, so it won't work with gradle nor ant,")
    st.write("but it can be repurposed to evaluate maven projects by changing the template project. ")

    st.write("For more information, please refer to the [GitHub repository](https://github.com/M-Mabrouk/Juniter).")
