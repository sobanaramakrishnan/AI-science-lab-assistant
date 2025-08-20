import streamlit as st
import os
import requests
from dotenv import load_dotenv
import google.generativeai as genai
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
FACTS_API_KEY = os.getenv("FACTS_API_KEY")  
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")
def get_science_fact():
    url = "https://api.api-ninjas.com/v1/facts"
    headers = {"X-Api-Key": FACTS_API_KEY} if FACTS_API_KEY else {}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return data[0].get("fact", "No fact found.")
        else:
            return f"API Error {r.status_code}: {r.text}"
    except Exception as e:
        return f"Request failed: {e}"
def get_chemical_property(smiles):
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/{smiles}/property/MolecularFormula,MolecularWeight,IUPACName,InChIKey/JSON"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            props = data["PropertyTable"]["Properties"][0]
            return {
                "Molecular Formula": props.get("MolecularFormula"),
                "Molecular Weight": props.get("MolecularWeight"),
                "IUPAC Name": props.get("IUPACName"),
                "InChIKey": props.get("InChIKey")
            }
        else:
            return {"error": f"API Error {r.status_code}: {r.text}"}
    except Exception as e:
        return {"error": str(e)}

st.set_page_config(page_title="AI Science Lab Assistant", page_icon="🧪", layout="centered")

st.title("AI Science Lab Assistant")
st.write("A virtual lab assistant for students. Ask science questions, run experiments, and see simulations!")

option = st.radio("Choose what you want to do:", 
                  ["Random Science Fact", "Chemical Property Lookup", "Step-by-Step Explanation"])

if option == "Random Science Fact":
    if st.button("Get Fact"):
        fact = get_science_fact()
        st.success(fact)

elif option == "Chemical Property Lookup":
    smiles = st.text_input("Enter SMILES string for molecule")
    if st.button("Lookup"):
        if smiles.strip():
            result = get_chemical_property(smiles.strip())
            st.json(result)
        else:
            st.warning("Please enter a SMILES string.")

elif option == "Step-by-Step Explanation":
    question = st.text_area("Ask your science question or describe an experiment:")
    if st.button("Explain"):
        if question.strip():
            with st.spinner("preparing a step-by-step explanation"):
                response = model.generate_content(
                    f"Explain this science experiment or concept for students in simple steps: {question}"
                )
                st.write(response.text)
        else:
            st.warning("Please enter a question or experiment description.")
