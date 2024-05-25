import os
import datetime
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.vectorstores import Milvus
from sentence_transformers import SentenceTransformer
from langchain_community.embeddings.sentence_transformer import (SentenceTransformerEmbeddings)
from pymilvus import MilvusClient, DataType
from langchain_core.documents import Document as docx
import pandas as pd
from docx import Document

os.environ["TOKENIZERS_PARALLELISM"] = "true"

client = MilvusClient(
   uri="http://localhost:19530"
)

# create the open-source embedding function
embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

model = SentenceTransformer("all-MiniLM-L6-v2")

#-------------------------------------------------------------------------------------------------------------------#

def createTimestampCollection():
   schema = MilvusClient.create_schema(
       auto_id=False
   )
   
   #create schema
   schema.add_field(field_name="id" , datatype=DataType.VARCHAR, max_length=100, is_primary=True)
   schema.add_field(field_name="last_modified_timestamp", max_length=50, datatype=DataType.VARCHAR)
   schema.add_field(field_name="partition", max_length=50, datatype=DataType.VARCHAR)

   index_params = client.prepare_index_params()

   # Add indexe to field "id"
   index_params.add_index(
       field_name="id",
       index_type="INVERTED"
   )

   #add index to field "last_modified_timestamp"
   index_params.add_index(
       field_name="last_modified_timestamp",
       index_type="INVERTED"
   )

   # Add index to field "partition"
   index_params.add_index(
      field_name="partition",
      index_type="INVERTED"
   )

   
   #create a collection for storing timestamp and partition name
   client.create_collection(
       collection_name="Timestamp",
       schema=schema,
       index_params=index_params
   )
   
   #now load the collecion into database
   client.load_collection(
       collection_name="Timestamp"
   )
   
   print("Timestamp collection is created successfully")
#-------------------------------------------------------------------------------------------------------------------#


def read_docx(file_path):
    """
    Read the contents of a .docx file.

    Args:
    - file_path (str): The path to the .docx file.

    Returns:
    - str: The text content of the .docx file.
    """
    doc = Document(file_path)
    full_text = []
    for paragraph in doc.paragraphs:
        full_text.append(paragraph.text)
    return '\n'.join(full_text)

#-------------------------------------------------------------------------------------------------------------------#

# preprocess data to insert in milvus
def preprocess_docs(text_content, file_path):
   data = []
   content = text_content.split('\n')


   for i in range(0, len(content), 2):
       if i+1 < len(content):
         data.append({"question": content[i], "answer": content[i+1]})

   dataframe = pd.DataFrame(data)

   documents = []
   for i in range(0 , len(dataframe)):
     embedding= model.encode(f"Question: {dataframe['question'][i]}\nAnswer: {dataframe['answer'][i]}").tolist()
     docs = {
        "source": file_path,
        "text": f"Question: {dataframe['question'][i]}\nAnswer: {dataframe['answer'][i]}",
        "vector": embedding
     }
      
     documents.append(docs)

   return documents   


#-------------------------------------------------------------------------------------------------------------------#


# Get the paths of each file in the directory
def get_file_paths(directory):
  """Gets file paths in a directory (doesn't recurse into subdirectories)."""
  file_paths = []
  for filename in os.listdir(directory):
    # Combine directory and filename to create absolute path
    file_path = os.path.join(directory, filename)
    file_path = file_path.replace("\\" , "/")
    # Check if it's a file (optional)
    if os.path.isfile(file_path):
      file_paths.append(file_path)
  return file_paths


#--------------------------------------------------------------------------------------------------------------------#

# Index the documents in Milvus
def index_document(filepath, partition):
    try:
        if os.path.exists(filepath):
            print("file exist")
    except Exception as error:
        print(error)
        return None
    
    text_content = read_docx(filepath)
    data = preprocess_docs(text_content, filepath)
    
    client.create_partition(
      collection_name= "burnerKB",
      partition_name= partition)

    client.load_partitions(
      collection_name="burnerKB",
      partition_names=[partition])

    res = client.insert(
     collection_name="burnerKB",
     data=data,
     partition_name=partition)
    
    print("File is loaded successfully")

#-------------------------------------------------------------------------------------------------------------------#

def updateFile(partition):
    
    client.release_partitions(
      collection_name="burnerKB",
      partition_names=[partition])   
    
    client.drop_partition(
       collection_name="burnerKB",
       partition_name=partition)

#-----------------------------------------------------------------------------------------------------------------#

# Insert the modified timestamp if file
def insert_Timestamp_in_DB(filepath , timestamp, partition):
   data = [{"id": filepath, "last_modified_timestamp": timestamp, "partition": partition}]

   res = client.insert(
      collection_name="Timestamp",
      data=data
   )

#------------------------------------------------------------------------------------------------------------------#

# Update the modified timestamp of the file 
def update_Timestamp_in_DB(filepath, last_modfied_time, partition):
   data = [{"id": filepath, "last_modified_timestamp": last_modfied_time, "partition": partition}]
   
   res = client.upsert(
      collection_name="Timestamp",
      data=data
   )

#-------------------------------------------------------------------------------------------------------------------#

docs = [
   docx(
   page_content="This is knowledge base",
   metadata={"source": "burnerplatform"},
)]

def createCloudburnerKB():
   Milvus.from_documents(
      docs,
      embeddings,
      collection_name="burnerKB",
      connection_args={"host": "localhost", "port": "19530"},
   )
   print("burnerKB is created successfully")   


#-------------------------------------------------------------------------------------------------------------------#

# Detect the modification in files and update it in Milvus
def check_modification():
    FilePaths = get_file_paths("C:/Users/avisaini/Desktop/langchain_Burner/Files")
    print(len(FilePaths))
    

    #check if the Timestamp collection is exist or not
    if client.has_collection("Timestamp") == False:
       createTimestampCollection()
    else:
       print("Timestamp collection already exist")  


    # check if cloudburner collection exist or not
    if client.has_collection("burnerKB") == False:
       createCloudburnerKB()
    else:
       print("burnerKB collection already exist")   
         

    # Traversing each file in directory
    for filepath in FilePaths:
      try: 
         print(filepath)
         modified_time = os.path.getmtime(filepath)  #get the modified timestamp of file
         modified_time_str = datetime.datetime.fromtimestamp(modified_time).strftime('%Y-%m-%d %H:%M:%S') #convert time into iso format
         print("latest modified timestamp", modified_time_str)

         # Get the timestamp and partition of a file
         doc = client.get(
            collection_name="Timestamp",
            ids=[filepath]
            )   

         doc_length = len(doc)
         
         # New file is detected 
         if doc_length == 0:
            print("New file is detected")
            partition = "File_" + f"{len(FilePaths)}"
            insert_Timestamp_in_DB(filepath, modified_time_str, partition)
            index_document(filepath, partition) 
         
         # File is already inserted, now check modifications in it
         elif doc_length > 0:
            last_modified_timestamp = doc[0]['last_modified_timestamp']
            FilePartition = doc[0]["partition"]           
            print("last time", last_modified_timestamp)
            
            # Modification detected in the file
            if last_modified_timestamp != modified_time_str: 
               print("Modification is detected in file")
               update_Timestamp_in_DB(filepath, modified_time_str, FilePartition)
               updateFile(FilePartition)
               index_document(filepath, FilePartition) 
                     
               # No modifications in the file
            else:
               print("No modification is detected in file")
      
      except Exception as e:
            print("Error occurred in file:", filepath, e) 
                    
              























