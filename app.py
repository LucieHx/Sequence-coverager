import pandas as pd
import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen
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

    st.write("FASTA file:\n\n", strips, "\n")

    strips_string = "".join(str(x) for x in strips) # converts from list to string

    strips_list = strips_string.rsplit("\n")[1:] # makes list again by separation with newline "\n"
                                                 # and removes header
        
    sequence = "".join(str(x) for x in strips_list)
    
    #sequence_for_display = ' '.join([sequence[i:i+60] for i in range(0, len(sequence), 60)]) # necessary to wrapp string
                                                                                             # so white space are added
    
    # Uncomment?
    
    #st.write("Original sequence:\n\n")#, sequence_for_display)
    #sequence_for_display =  "<span style='word-wrap:break-word;'>" + sequence +  "</span>"
    #st.markdown(sequence_for_display, unsafe_allow_html=True) 


    sequence = "".join(str(x) for x in strips_list)
    original_sequence = sequence
    empty = []
    empty_shouldnt_exist = []
    
    
    for peptide in peptides_sequnces: # check if peptide is in original sequence!!!
   
        
        if (peptide in sequence) and (peptide in original_sequence): 
  
            m = re.search(peptide, sequence)          
            sequence = sequence[:m.start()] + "<span style='color:blue'>" + peptide + "</span>" + sequence[m.end():]
            
        elif (peptide in original_sequence) and (peptide not in sequence): 

            omit = "(<span style='color:blue'>|</span>)*" # after each letter of peptide
            m = re.search(omit.join(x for x in peptide), sequence)
            peptide_newlocation = sequence[m.span()[0]:m.span()[1]]
            
            if ("<span style='color:blue'>" in peptide_newlocation) and ("</span>" in peptide_newlocation):
                peptide_newlocation = peptide_newlocation.replace("<span style='color:blue'>", "").replace("</span>", "") # remove formatting from peptide string
                sequence = sequence[:m.start()] + '<span style="color:blue">' + peptide_newlocation + '</span>' + sequence[m.end():]         
            elif "<span style='color:blue'>" in peptide_newlocation:
                peptide_newlocation = peptide_newlocation.replace("<span style='color:blue'>", "") # remove formatting from peptide string
                sequence = sequence[:m.start()] + "<span style='color:blue'>" + peptide_newlocation + sequence[m.end():]
            elif "</span>" in peptide_newlocation:
                peptide_newlocation = peptide_newlocation.replace("</span>", "") # remove formatting from peptide string
                sequence = sequence[:m.start()]  + peptide_newlocation + "</span>"  + sequence[m.end():]
            else:
                empty_shouldnt_exist.append(peptide_newlocation)
            
        
        else: empty.append(peptide)
        
 
    #st.markdown(sequence, unsafe_allow_html=True)   
    
    # adding text wrapping
    st.write("Mapped peptides:\n\n")
    sequence_for_display =  "<span style='word-wrap:break-word;'>" + sequence +  "</span>"
    st.markdown(sequence_for_display, unsafe_allow_html=True) 
    
    st.write("Not found peptides:\n\n", empty)
    st.write("Tady by nic byt nemělo!:\n\n", empty_shouldnt_exist)
 
 
    
    # scatter matrix plat
    #st.write(px.scatter_matrix(data, dimensions=dimensions, color=color, opacity=opacity))

    # výběr sloupce pro zobrazení rozdělení dat
    #interesting_column = st.selectbox("Interesting column", data.columns)
    # výběr funkce pro zobrazení rozdělovací funkce
    #dist_plot = st.selectbox("Plot type", [px.box, px.histogram, px.violin])

    #st.write(dist_plot(data, x=interesting_column, color=color))


if __name__ == "__main__":
    app()