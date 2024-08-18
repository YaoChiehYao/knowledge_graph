
import os
from dotenv import load_dotenv
import streamlit as st
from streamlit.runtime.scriptrunner.script_run_context import get_script_run_ctx

# Load environment variables from .env file
load_dotenv()


from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.graphs import Neo4jGraph


# Initialize OpenAI and Neo4j components with environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")

# Check if environment variables are set
if not all([OPENAI_API_KEY, OPENAI_MODEL, NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD]):
    st.error("Missing environment variables. Please set OPENAI_API_KEY, NEO4J_URI, NEO4J_USERNAME, and NEO4J_PASSWORD.")


llm = ChatOpenAI(
    openai_api_key=OPENAI_API_KEY,
    model=OPENAI_MODEL,
)

embeddings = OpenAIEmbeddings(
    openai_api_key=OPENAI_API_KEY
)

graph = Neo4jGraph(
    url=NEO4J_URI,
    username=NEO4J_USERNAME,
    password=NEO4J_PASSWORD,
)

import streamlit as st
from streamlit.runtime.scriptrunner.script_run_context import get_script_run_ctx

# tag::write_message[]
def write_message(role, content, save = True):
    """
    This is a helper function that saves a message to the
     session state and then writes a message to the UI
    """
    # Append to session state
    if save:
        st.session_state.messages.append({"role": role, "content": content})

    # Write to UI
    with st.chat_message(role):
        st.markdown(content)
# end::write_message[]

# tag::get_session_id[]
def get_session_id():
    return get_script_run_ctx().session_id
# end::get_session_id[]

import streamlit as st
# Create a movie chat chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser

chat_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a drugs expert providing associated drug information from the target gene user provided."),
        ("human", "{input}"),
    ]
)

movie_chat = chat_prompt | llm | StrOutputParser()

# Create a set of tools
from langchain.tools import Tool

tools = [
    Tool.from_function(
        name="General Chat",
        description="For general medical database chat",
        func=movie_chat.invoke,
    )
]

# Create chat history callback
from langchain_community.chat_message_histories import Neo4jChatMessageHistory

def get_memory(session_id):
    return Neo4jChatMessageHistory(session_id=session_id, graph=graph)

# Create the agent
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain import hub


from langchain_core.prompts import PromptTemplate

agent_prompt = hub.pull("hwchase17/react-chat", api_key=LANGCHAIN_API_KEY)

agent = create_react_agent(llm, tools, agent_prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True
    )

chat_agent = RunnableWithMessageHistory(
    agent_executor,
    get_memory,
    input_messages_key="input",
    history_messages_key="chat_history",
)

# Create a handler to call the agent
# from utils import get_session_id

def generate_response(user_input):
    """
    Create a handler that calls the Conversational agent
    and returns a response to be rendered in the UI
    """

    response = chat_agent.invoke(
        {"input": user_input},
        {"configurable": {"session_id": get_session_id()}},)

    return response['output']

# Page Config
st.set_page_config(
    page_title="Medical Database Chatbot",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'About': 'This app provides drug information based on gene input.'
    }
)

# Set up Session State
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi, I'm Meda, a general medical database Chatbot!  How can I help you?"},
    ]

# Submit handler
def handle_submit(message):
    """
    Submit handler:

    context using data from Neo4j.
    """

    # Handle the response
    with st.spinner('Thinking...'):
        # Call the agent
        response = generate_response(message)
        write_message('assistant', response)


# Display messages in Session State
for message in st.session_state.messages:
    write_message(message['role'], message['content'], save=False)

# Handle any user input
if question := st.chat_input("What is up?"):
    # Display user message in chat message container
    write_message('user', question)

    # Generate a response
    handle_submit(question)
