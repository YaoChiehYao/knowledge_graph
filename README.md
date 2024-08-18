
## BioMedical graph database iBKH + LLM chatbot for biomedical discovery 

### Summary
This project builds a neo4j graph based on multiple medical databases from iBKH and deploys it to the llm chatbot using Streamlit.

### Workflow
1. Creat data and import file in the same folder
mkdir data import  

2. Download dump file to import folder
[Dunmp file](https://drive.google.com/file/d/11mHAlsWn-hFODjt3qKkS3rro1t1ceGtK/view?usp=drive_link) 

3. Use Docker file to install Neo4j and check if the import folder connect to container 
```bash 
Docker compose up -d
docker exec -it your_container_id /bin/bash
ls import/
```

4. Create a new database in neo4j browser to import the dump file
```Neo4j Cypher
CREATE DATABASE ibkh;
SHOW DATABASES;
```

6. Import Dump file to Neo4j database
```bash
docker exec -it your_container_id neo4j-admin database load ibkh --from-path=/var/lib/neo4j/import/dump --overwrite-destination=true --verbose```
```

After the database is built, you can use iBKH.ipynb to chat with the biomedical data and chatbot, which will respond natively by llm 
if your question is not inside the graph database.


### Reference
Su, C., Hou, Y., Zhou, M., Rajendran, S., Maasch, J. R. M. A., Abedi, Z., Zhang, H., Bai, Z., Cuturrufo, A., Guo, W., Chaudhry, F. F., Ghahramani, G., Tang, J., Cheng, F., Li, Y., Zhang, R., DeKosky, S. T., Bian, J., & Wang, F. (2023). Biomedical discovery through the integrative biomedical knowledge hub (iBKH). iScience, 26(4), 106460. https://doi.org/10.1016/j.isci.2023.106460
