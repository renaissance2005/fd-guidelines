# Importing the relevant libraries
from dotenv import load_dotenv
import os

# Warning control
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
from neo4j import GraphDatabase
import textwrap

# Load authentication information from environment
load_dotenv('.env', override=True)
NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USERNAME = os.getenv('NEO4J_USERNAME')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')
NEO4J_DATABASE = os.getenv('NEO4J_DATABASE') or 'neo4j'

# Read the Excel file
excel_file = 'kg-journal.xlsx'
df = pd.read_excel(excel_file)

# Connect to Neo4j Desktop database
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

# Create nodes and relationships in Neo4j
with driver.session() as session:
    for _, row in df.iterrows():
        query = (
            f"MERGE (c:Context {{Application: '{row['application']}', "
            f"Purpose: '{row['purpose']}', Sector: '{row['sector']}'}})"
            
            f"MERGE (r:Risk {{Name:'{row['risk_name']}', LC_Phase:'{row['risk_phase']}'}})"
            f"MERGE (r)-[:AFFECTS]->(c)"            
            
            f"MERGE (t:Treatment {{Name:'{row['ctms_name']}', LC_Phase:'{row['ctms_phase']}'}})"
            f"MERGE (t)-[:MODIFIES]->(r)"
            f"MERGE (t)-[:RELATES_TO]->(c)"         
                        
            f"MERGE (s:Stakeholder {{Name:'{row['stakeholder']}'}})"
            f"MERGE (s)-[:RESPONSIBLE_FOR]->(t)"
        )
        session.run(query)

driver.close()