# This code contains the program to generate guidelines for AI acquisition
# it will produce 4 tabs as user interface for interaction with the users
# in addition, the code will extract data from knowledge graph database
# and output coherent guidelines for the user.
# Author: David Lau Keat Jin, Date: 10 August, 2024
from dotenv import load_dotenv
import os
import streamlit as st
import ollama
import time
from langchain_community.graphs import Neo4jGraph

# Load authentication information from environment
load_dotenv('.env', override=True)
NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USERNAME = os.getenv('NEO4J_USERNAME')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')
NEO4J_DATABASE = os.getenv('NEO4J_DATABASE') or 'neo4j'

kg = Neo4jGraph(
    url=NEO4J_URI, username=NEO4J_USERNAME, password=NEO4J_PASSWORD, database=NEO4J_DATABASE
)

system_content = """You are a expert writer for procurement specification.
Based on the risk treatment selected by the user, explain in no more than three sentences, 
the meaning of the treatment, the phase in which the treatment should be applied and 
the task required to be implemented by the stakeholder. If there are more than one treatment given, 
separate the treatments into different paragraphs with numbering as sequence.

# Example: 
"To prevent the risk of inaccurate information, the development team should
incorporate reranking strategy in the deployment phase. This involve calculating the semantic
similarity of the information with the query and prioritize the information retrieved. The most similar
information should be presented if lower-ranked information has low similarity to the query." 
"""

# Initialize session state variables
if 'context_selected' not in st.session_state:
    st.session_state['context_selected'] = False

if 'risk_selected' not in st.session_state:
    st.session_state['risk_selected'] = False

if 'treatment_selected' not in st.session_state:
    st.session_state['treatment_selected'] = {}

# Function to get applications from Context nodes
def get_applications():
    query = "MATCH (c:Context) RETURN DISTINCT c.Application AS application ORDER BY application"
    results = kg.query(query)
    return [record['application'] for record in results]

# Function to get risks associated with a specific context
def get_risks(application):
    query = f"""
    MATCH (c:Context {{Application: '{application}'}})<-[:AFFECTS]-(r:Risk)
    RETURN DISTINCT r.Name AS risk ORDER BY risk
    """
    results = kg.query(query)
    return [record['risk'] for record in results]

# Function to get treatments associated with specific risks
def get_treatments(risk, application):
    query = f"""
    MATCH (r:Risk {{Name: '{risk}'}})<-[:MODIFIES]-(t:Treatment)-[:RELATES_TO]->(Context {{Application: '{application}'}})
    RETURN DISTINCT t.Name AS treatment
    """
    results = kg.query(query)
    return [record['treatment'] for record in results]

# Function to get the effects for a treatment modifying a specific risk
# this is superceded by the requirement to get the phase only
def get_treatment_effects(risk, treatment):
    query = f"""
    MATCH (t:Treatment {{Name: '{treatment}'}})-[m:MODIFIES]->(r:Risk {{Name: '{risk}'}})
    RETURN t.LC_Phase AS LC_Phase
    """
    results = kg.query(query)
    return results[0] if results else None

# Function to get the stakeholder responsible for a specific treatment
def get_stakeholder(treatment):
    query = f"""
    MATCH (s:Stakeholder)-[:RESPONSIBLE_FOR]->(t:Treatment {{Name: '{treatment}'}})
    RETURN DISTINCT s.Name AS Stakeholder
    """
    results = kg.query(query)
    return results[0]['Stakeholder'] if results else None

def genenerate_guidelines(riskinfo):
    import ollama

    context = riskinfo

    rag_template = """You are a procurement expert that takes the results
    from a Neo4j Cypher query and forms a human-readable response. The
    query results is a list with risk and the associated treatment. 
    generated based on a user's natural language question. You are required
    to generate a guideline for implementation of treatment for each risk.
    The guideline will describe the treatment, the stakeholder responsible for 
    implementation of the treatment and the life cycle phase involved as obtained
    from the context. If there are more than one treatment for a risk, then separate
    the treatments in numbered paragraphs under the risk. 
    
    Query Results:
    {context}

    If the provided information is empty, say you don't know the answer.
    Empty information looks like this: []

    Never say you don't have the right information if there is data in
    the query results. Always use the data in the query results.

    # Example: 
    Risk: Inaccurate information
    1. Treatment: Reranking strategy
    Reranking strategy should be used in Deployment phase by the Development team. 
    This involves determining the semantic similarities of information retrieved 
    with the given query. 

    2. Treatment: Exploit external knowledge
    Exploiting external knowledge involves referring to external and usually updated
    information related to the query. The Development team should incorporate this 
    function during the Deployment phase of the system. 
    """

    question = f"What is the treatment for the risks in {riskinfo}?"

    ollama_response = ollama.chat(model='llama3.1:8b', messages=[
        {
            'role':'system',
            'content': rag_template,        
        },
        {
            'role':'user', 
            'content': question
        },
    ])
    response = ollama_response['message']['content']

    return(response)

# Function to reset session state
def reset_selections():
    st.session_state['context_selected'] = False
    st.session_state['risk_selected'] = False
    st.session_state['treatment_selected'] = {}
    st.session_state['treatment_details'] = {}

# Streamlit app with tabs
st.title("AI Acquisition Guidelines Generator")

tab1, tab2, tab3, tab4 = st.tabs(["Context", "Risk", "Countermeasure", "Guidelines"])

# Tab 1: Context
with tab1:
    st.header("Select Context")
    applications = get_applications()
    application = st.selectbox("Choose an application", applications)

    if st.button("Submit Context"):
        st.session_state['context_selected'] = True
        st.session_state['selected_application'] = application
        st.success(f"Context '{application}' selected. You can now proceed to the Risk tab.")

# Tab 2: Risk
with tab2:
    if not st.session_state['context_selected']:
        st.warning("Please select a context in the Context tab first.")
    else:
        st.header("Select Risk")
        risks = get_risks(st.session_state['selected_application'])
        selected_risks = st.multiselect("Choose risks", risks)

        if st.button("Submit Risk"):
            st.session_state['risk_selected'] = True
            st.session_state['selected_risks'] = selected_risks
            st.success(f"Risks '{', '.join(selected_risks)}' selected. You can now proceed to the Treatment tab.")

# Tab 3: Treatment
with tab3:
    if not st.session_state['risk_selected']:
        st.warning("Please select risks in the Risk tab first.")
    else:
        st.header("Select Countermeasure")
        selected_treatments = {}
        for risk in st.session_state['selected_risks']:
            st.subheader(f"Countermeasure for Risk: {risk}")
            treatments = get_treatments(risk, application)
            selected_treatments[risk] = st.multiselect(f"Choose countermeasure for {risk}", treatments, key=risk)

        if st.button("Submit Countermeasure"):
            if all(selected_treatments[risk] for risk in selected_treatments):
                st.session_state['treatment_selected'] = selected_treatments
                st.success("Treatments selected. You can now proceed to the Summary tab.")
            else:
                st.warning("Please select at least one treatment for each risk before proceeding.")

# Tab 4: Summary and Guidelines
with tab4:
    if not st.session_state['treatment_selected']:
        st.warning("Please select countermeasure in the Countermeasure tab first.")
    else:
        st.header("Guidelines for Risk Mitigation")
        st.write("The selected risk(s) is/are:")
        
        query_result = []
        
        # Collect all risks into a list
        risks = [risk for risk in st.session_state['treatment_selected'].keys()]

        # Display risks in a single line separated by commas
        st.write(f"Risk: {', '.join(risks)}")

        for risk, treatments in st.session_state['treatment_selected'].items():
           
            for treatment in treatments:
                effects = get_treatment_effects(risk, treatment)
                stakeholder = get_stakeholder(treatment)
                if effects:
                    entry = {
                        'Risk': risk,
                        'Treatment': treatment,
                        'LC_Phase': effects['LC_Phase'],
                        'Stakeholder': stakeholder
                    }
                    query_result.append(entry)
                else:
                    st.write(f"There are no countermeasure registered for the risk: {risk})")
        
        start_time = time.time() 

        # Generate the guidelines using local LLM
        result = genenerate_guidelines(query_result)
        
        # Display or use query_result as needed
        st.write(result)
        
     # Add a reset button to clear all selections and memory
    if st.button("Reset Selections"):
        reset_selections()
        st.experimental_rerun()

# End of the code        



