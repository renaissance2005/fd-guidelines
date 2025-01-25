# Framework-Driven Guideline Generation for AI Adoption: A Risk-Based Perspective 

Studies have been conducted in the domain of responsible AI to espouse the ideals of accountability, fairness, privacy, safety, security, transparency, and respect for human autonomy. To keep track on the attainment of these objectives, online repositories of AI incidents and issues were established for evidence-based research. While interested readers can inspect the reported cases of AI incidents and issues, these repositories do not provide concrete solutions to prevent or mitigate the incidents or issues based upon the actual use cases. Hence, this study examined the incidents and issues reported by an online repository, considering the context with the potential risks, and provided countermeasures from literature. The cases of risks without any practical countermeasure from existing studies were highlighted and further segregated into recommendation for further research or regulatory actions. Incidentally, a system to store the repository of information regarding the context, risk, and countermeasure was developed such that guidelines can be generated based on the user selections. The guidelines can be used by acquisition team to foster the practices of responsible AI in the organization. 

## Background
Based on literature review, the framework should consists of the following 3 aspects:

![image](https://github.com/user-attachments/assets/433417df-c114-4b96-83f3-9775eef03c5a)

## Research Procedure
In this study, the AIAAIC repository was used due its ease of download as well as the availability of crucial information pertaining to sector and technology. The technology field served as a basis to examine the use cases and the associated issues reported.3 major stages are involved:
i)      Data Preparation
ii)     Data Population
iii)    Framework Application

Brief descriptions of activities associated with each stage is given in the following diagram:
![image](https://github.com/user-attachments/assets/c1665980-a40b-4232-9309-a68c93ac534e)

The excel file with the contents for the knowledge graph is kg-journal.xlxs
The code to create and populate the knowledge graph is given in import-excel.php 
The guidelines generator can be run with the file rmapp-guidelines.php with the command streamlit run {filename}

## Result
The result of executing the procedure is shown in the file Repository_used.xlxs. List of application covered include:

<img width="276" alt="image" src="https://github.com/user-attachments/assets/ac2e370d-0aea-46b2-8341-e0b00cdc3ef1">

## Conclusion
The contributions of this study include:
i.	  outlined the risk and countermeasure based on AI-application context for deliberation,
ii.	  highlighted the domain of application and risk that require further research, and
iii.	provided input for legislators and policy makers to devise appropriate regulations to manage the risks of AI adoption. 
