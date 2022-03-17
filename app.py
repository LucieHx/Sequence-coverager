import pandas as pd
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen
from termcolor import colored
import re

from contextlib import contextmanager, redirect_stdout
from io import StringIO
from time import sleep
import streamlit as st

@contextmanager
def st_capture(output_func):
    with StringIO() as stdout, redirect_stdout(stdout):
        old_write = stdout.write

        def new_write(string):
            ret = old_write(string)
            output_func(stdout.getvalue())
            return ret
        
        stdout.write = new_write
        yield

output = st.empty()

def app():
    st.title("Sequence coverage")
    
    # vstup 1: výběr datové sady
    data_file_path = st.file_uploader("Data file")
    data = None
    
    columns = ['Leading razor protein', 'Sequence']
    
    if data_file_path is not None:
        # read data if user uploads a file
        data = pd.read_csv(data_file_path, sep='\t', usecols = columns)
        # seek back to position 0 after reading
        data_file_path.seek(0)
    if data is None:
        st.warning("No data loaded")
        return
    
    # vstup 2: výběr uniprotid
    uniprot_id = st.text_input("Enter uniprot ID")
    
    st.write(uniprot_id)
    
    if uniprot_id is None:
        st.warning("No uniprot id loaded")
        
    
    # Getting sequences for selected uniprot id (protein)
    peptides_sequnces = data[data["Leading razor protein"] == uniprot_id]["Sequence"]
    
    # Create url from uniprot id and access sequence
    url = 'https://www.uniprot.org/uniprot/' + uniprot_id + '.fasta'

    html = urlopen(url).read()

    soup = BeautifulSoup(html)

    strips = []

    for script in soup(["script", "style"]):
        script.decompose() 
        
    strips = list(soup.stripped_strings) # pure fasta file

    st.write("Your FASTA file:\n\n", strips, "\n")

    strips_string = "".join(str(x) for x in strips) # converts from list to string

    strips_list = strips_string.rsplit("\n")[1:] # makes list again by separation with newline "\n"
                                                 # and removes header
        
    sequence = "".join(str(x) for x in strips_list)
    st.write("Your sequence:\n\n", sequence)
    
    empty = []

    for peptide in peptides_sequnces:
        if peptide in sequence:
            m = re.search(peptide, sequence)
            sequence = sequence[:m.start()] + "\x1b[44;33m" + peptide + "\x1b[m" + sequence[m.end():]
        else: empty.append(peptide)

    #st.write(sequence)
    
    with st_capture(output.code):
        print(sequence)
        sleep(1)
    # sleep(1)
    # print("World")
    
    #st.markdown(f'<span style="color:blue">some *blue* text</span>)
    #st.write(f'blabla{#1aa3ff}')
    
    colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple']
    for color in colors:
        st.write('<span style="color:%s">%s</span>' % (color, "blb"), unsafe_allow_html=True)
    #color=["blue"]
    #st.write('<span style="color:%s">%s</span>' % (color, color), unsafe_allow_html=True)


    # scatter matrix plat
    #st.write(px.scatter_matrix(data, dimensions=dimensions, color=color, opacity=opacity))

    # výběr sloupce pro zobrazení rozdělení dat
    #interesting_column = st.selectbox("Interesting column", data.columns)
    # výběr funkce pro zobrazení rozdělovací funkce
    #dist_plot = st.selectbox("Plot type", [px.box, px.histogram, px.violin])

    #st.write(dist_plot(data, x=interesting_column, color=color))


if __name__ == "__main__":
    app()