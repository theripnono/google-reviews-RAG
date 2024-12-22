import os
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter,CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains.question_answering import load_qa_chain
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate

from reviews import export_reviews2_csv

# Todo search for multiple business

#setup
apikey = os.environ['OPENAI_API_KEY']
os.environ["TOKENIZERS_PARALLELISM"] = "false"

llm = ChatOpenAI(openai_api_key=apikey)

chain = load_qa_chain(llm, chain_type="stuff")


def csv_to_text(csv_file):
    """
    Funtion that it transforms the csv into a plain text
    """
    text = ''
    df = pd.read_csv(csv_file, sep=';')
    new_df = df[['comment', 'date']].copy()
    df_dict = new_df.to_dict(orient='records')
    for row in df_dict:
        text += row['comment'] + 'fecha del comentario ' + row['date'] + '\n\n'

    return text

def get_csv():
    
    """
    get csv from the path if does not exist it downloads and exports again
    """
    path = os.getcwd()
    dirs = os.listdir(path)

    csv_reviews = [file for file in dirs if file.endswith('_export.csv')]

    if len(csv_reviews) > 0:
        return csv_reviews[0]
    else:

        #export reviews
        export_reviews2_csv()

        path = os.getcwd()
        dirs = os.listdir(path)
        csv_reviews = [file for file in dirs if file.endswith('_export.csv')]

        return csv_reviews[0]


csv_reviews = get_csv()


#path = os.getcwd()
#dirs = os.listdir(path)
#csv_reviews =[file for file in dirs if file.endswith('_export.csv')][0]

text_content = csv_to_text(csv_reviews)

#text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100, length_function=len)

text_splitter = CharacterTextSplitter(
    separator="\n\n",
    chunk_size=2000,
    chunk_overlap=200,
    length_function=len,
    is_separator_regex=False,
)

docs = text_splitter.split_text(text_content)

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

#Vectorestore
vectorstore = FAISS.from_texts(docs, embeddings) # local dbstore
retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": 6})

def format_docs(docs):

    return "\n\n".join(doc.page_content for doc in docs)

template = """Se necesita averiguar información detallada sobre las opiniones de los usuarios, para analizar y mejorar la experiencia.
Si no sabes la respuesta, di simplemente que no la sabes, no intentes inventarte una respuesta.
Utiliza tres frases como máximo y procura que la respuesta sea lo más concreta posible.

{context}

Question: {question}

Respuestas útiles:"""
custom_rag_prompt = PromptTemplate.from_template(template)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | custom_rag_prompt
    | llm
    | StrOutputParser()
)

#todo add memory
q_a = True
while q_a:
    question = input("Ask me [write esc to end asking]: ")
    if q_a != "esc":
        print(rag_chain.invoke(question))
    else:
        q_a = False
        print("Ending")