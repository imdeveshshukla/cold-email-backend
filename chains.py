import getpass
from dotenv import load_dotenv
import os
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_groq import ChatGroq
from utils import clean_text
load_dotenv()

class Chain:
    def __init__(self) -> None:
        if not os.environ.get("GROQ_API_KEY"):
            os.environ["GROQ_API_KEY"] = getpass.getpass("Enter API key for Groq: ")
        self.model = ChatGroq(model="llama3-8b-8192")
    
    def write_mail(self,file,jd):
        loader = PyPDFLoader(
            file,
        )
        docs = loader.load()
        data = docs[0]
        resume = data.page_content
        prompt_template2 = ChatPromptTemplate.from_messages(
            [("system", 
            """
            ### This is My Resume : 
            {resume}  
            ### INSTRUCTIONS:
            
            ### Only return valid json
            
            Generate an email for job description how i am well fit for job
            according to resume
            Only print json which should contain subject,content
            Score should be out of 100
            And Json shoud in this format:
            {{
                subject:__,
                content:___
            }}
            Also don't explain
            If Job description is not found only generate resume template for cold email to any job according to my resume
            Don't print anything other then Email JSON
            ### If Job description is empty then generate email general purpose for all company
            ### Don't write anything other then email
            ### (NO PREAMBLE)
            """), ("user", """
            JOB_DESCRIPTION:{jd}
            """)]
        )
        try:
            prompt = prompt_template2.invoke({"resume": resume,"jd":jd})
            res = self.model.invoke(prompt)
            json_parser = JsonOutputParser()
            resJson = json_parser.parse(res.content)
            return resJson
        except:
            print("Some Error Found In LLM")
            return { "subject":"LLM Issue","content":"" }