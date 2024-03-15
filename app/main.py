from fastapi import FastAPI,Form,Request,Depends,HTTPException,status,websockets
from typing import Optional,Annotated
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import models
from database import engine,Sessionlocal,DATABASE_URL
import os
from openai import OpenAI
from sqlalchemy import create_engine
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.vectorstores import Chroma
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_openai import OpenAIEmbeddings
from langchain.memory import ChatMessageHistory

client = OpenAI(api_key="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") 
# client = OpenAI()
# openai_api_key = f"{os.getenv(OPENAI_API_KEY)}"
# openai_api_key = os.getenv("OPENAI_API_KEY")
app = FastAPI()
models.Base.metadata.create_all(bind=engine)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates_path = os.path.join(BASE_DIR, "frontend", "templates")
templates = Jinja2Templates(directory=templates_path)
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "frontend", "static")), name="static")




def get_db():
    db=Sessionlocal()
    try:
        yield db
        
    finally:
        db.close()

db_dependency = Annotated[Session,Depends(get_db)]




@app.get('/',response_class=HTMLResponse)
async def read_root(request:Request):
    return templates.TemplateResponse('index.html',{"request":request})


# New endpoint for classifying prompts as "ChatGPT" or "Database"
class PromptInput(BaseModel):
    prompt: str

@app.post("/classify/")
async def classify(prompt_input: PromptInput):
    try:
        database_keywords=["timezone","airports","iata_code","airlines",'cost','travel packages','travel']
        keyword_count = sum(keyword in prompt_input.prompt.lower() for keyword in database_keywords)
        if keyword_count > 1:
            result = "database"
        else:
            classification_prompt = [{
                "role": "system",
                "content": "Determine if the following question should be answered by ChatGPT or requires a specific database query."
            }, {
                "role": "user",
                "content": prompt_input.prompt
            }]
            response = client.chat.completions.create(model="gpt-4",  # Update to the appropriate engine
            messages=classification_prompt,
            temperature=0.5,
            max_tokens=60)
            if response.choices and len(response.choices)>0:
                result=response.choices[0].message.content.strip()
                print(prompt_input.prompt)
                print("********")
            # print(result)
                if 'database' in result:
                    result ="database"
                else:
                    print(result[50:])
                    result='chatgpt'
            else:
                result='Give me more details'
        
        # result = response['choices'][0]['message']['content'].strip()
        print(result)
        if result == 'chatgpt':
            answer_response = client.chat.completions.create(
                model='gpt-4',
                messages=[{
                    'role':'user',
                    'content':prompt_input.prompt
                }],
                temperature=0.5,
                max_tokens=60
            ).choices[0].message.content.strip()
        else:
            answer_response = nlp_prompt_to_sql(prompt_input.prompt)
            # if "query" in answer_response.lower():
            #     answer_response = client.chat.completions.create(
            #         model='gpt-4',
            #         messages=[{
            #             'role': 'user',
            #             'content': prompt_input.prompt
            #         }],
            #         temperature=0.5,
            #         max_tokens=60
            #     ).choices[0].message.content.strip()
            # print(answer_response)
        return {"classification": answer_response}
    
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


def nlp_prompt_to_sql(prompt_input_sql):
    nlpdb = SQLDatabase.from_uri(DATABASE_URL)
    history = ChatMessageHistory()
    # print(nlpdb.dialect)
    # print(nlpdb.get_usable_table_names())
    # print(nlpdb.table_info)
    
    # natural language to sql thing
    answer_prompt = PromptTemplate.from_template(
    """Given the following user question, corresponding SQL query, and SQL result, answer the user question.
    
    Question : {question}
    SQL Query :{query}
    SQL Result : {result}
    Answer: """
    )
    llm = ChatOpenAI(model='gpt-3.5-turbo',temperature=0)
    rephrase_answer = answer_prompt | llm | StrOutputParser()
    execute_query = QuerySQLDataBaseTool(db=nlpdb)
    generate_query = create_sql_query_chain(llm,nlpdb)
    # print(generate_query)
    chain=(
        RunnablePassthrough.assign(query=generate_query).assign(
            result=itemgetter("query")|execute_query
        )| rephrase_answer
    )
    examples = [
    {
        "input": "Show me all travel packages available for New York City.",
        "query": "SELECT `packagename`, `description`, `cost` FROM travel_packages JOIN cities ON travel_packages.destination_city_id = cities.id WHERE cities.name = 'New York City';"
    },
    {
        "input": "Find all luxury travel packages with a minimum cost of 5,000.",
        "query": "SELECT `packagename`, `description`, `cost` FROM travel_packages WHERE cost >= 5000 AND packageType = 'Luxury';"
    },
    {
        "input": "List all travel packages to European countries.",
        "query": "SELECT `packagename`, `description`, `cost` FROM travel_packages JOIN cities ON travel_packages.destination_city_id = cities.id JOIN countries ON cities.country_id = countries.id WHERE countries.continent = 'Europe';"
    },
    {
        "input": "I want to see travel packages that include hiking activities.",
        "query": "SELECT `packagename`, `description`, `cost` FROM travel_packages WHERE activities LIKE '%hiking%';"
    },
    {
        "input": "What are the budget travel packages to Japan under 1500?",
        "query": "SELECT `packagename`, `description`, `cost` FROM travel_packages JOIN cities ON travel_packages.destination_city_id = cities.id WHERE cities.country = 'Japan' AND cost < 1500;"
    }
]

    # dynamic few-shot example selection
    vectorstore = Chroma()
    vectorstore.delete_collection()
    example_selector = SemanticSimilarityExampleSelector.from_examples(
        examples,
        OpenAIEmbeddings(),
        vectorstore,
        k=2,
        input_keys=['input'],
        
    )
    # example_selector.select_examples({"input": f"{prompt_input_sql}"})
    # print(example_selector.select_examples({"input":f"{prompt_input_sql}"}))
    response = chain.invoke({"question":f"{prompt_input_sql}","messages":history.messages})
    history.add_user_message(prompt_input_sql)
    history.add_ai_message(response)
    # response = chain.invoke({"question":"number of airports in europe","messages":history.messages})
    print(response)
    # print(history.messages)
    if not response or 'no data found' in response.lower():
        return response.capitalize()
    else:
        return response
# print(nlp_prompt_to_sql("number of airports in usa"))