from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_service.agent_prompt import PROMPT_TEMPLATE, EXAMPLE_FORMAT
import logging
import os
load_dotenv()

log = logging.getLogger()
log.setLevel(logging.INFO)

# from agent_prompt import prompt


class LangchainAgent:
    def __init__(self):
        self.llm = ChatGroq(
            model="llama-3.1-70b-versatile",
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        self.example_format = EXAMPLE_FORMAT
        # self.prompt = self.create_prompt(valid_names=valid_names, description=description)
        self.parser = StrOutputParser()
        self.descriptions = []
        self.valid_names = None
        self.chat_template = None
        self.prompt_chain_template = None
        self.llm_chain = None
        # self.get_custom_chain()

    def get_custom_chain(self):
        try:
            descriptions_count = len(self.descriptions)
            descriptions_string = "\n".join(self.descriptions)
        except Exception as e:
            log.error(f"Exception while generating description string: {e}")
            descriptions_string = ""
            descriptions_count = 0

        user_query = f"Extract exactly {descriptions_count} number of outputs from the input descriptions according to the provided instructions"
        messages = [
            ("system", PROMPT_TEMPLATE),
            ("user", user_query)
        ]

        self.chat_template = ChatPromptTemplate.from_messages(messages)
        self.prompt_chain_template = PromptTemplate(
            template="Following are the target description values. Remember the total no of descriptions provided here. You MUST always return the same number of outputs provided here: " + descriptions_string
        )
        self.llm_chain = RunnablePassthrough.assign(
            descriptions=self.prompt_chain_template
        ) | self.chat_template | self.llm | self.parser

    # def create_prompt(self, valid_names, description):
    #     valid_names_str = ", ".join(valid_names)
    #     description_str = "\n".join(description)
    #
    #     # Create a PromptTemplate object
    #     # template = PromptTemplate.from_template(prompt_template)
    #     # # Return a new PromptTemplate with formatted values
    #     # return template.format(valid_names=valid_names_str, descriptions=description_str)

    # def get_chain(self):
    #     print(self.prompt)
    #     chain = self.llm | self.parser
    #     return chain

    def get_response(self, valid_names, descriptions):
        try:
            self.valid_names = valid_names
            self.descriptions = descriptions

            valid_names_string = ", ".join(self.valid_names)

            self.get_custom_chain()
            # descriptions = "\n ".join(description)
            response = self.llm_chain.invoke(
                {
                    "valid_names": valid_names_string,
                    "example_format": self.example_format
                 }
            )
        except Exception as e:
            log.error(f"Exception in getting agent response: {e}")
            return "{}"
        return response
