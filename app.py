import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from functools import lru_cache
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceInstructEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from htmlTemplates import css, bot_template, user_template
from login_page import login_page
from langchain.llms import HuggingFaceHub


def login_page():
    st.title("Login Page")

    # Add some instructions for users
    st.write("Please enter your DXC email address to log in.")

    # Email and password input fields
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    # Check if the login button is clicked
    if st.button("Login"):
        # Extract the domain from the email address
        domain = email.split('@')[-1].lower()

        # Replace this with your own authentication logic
        if domain == "dxc.com" and password == "meryem1234567891":
            st.success("Logged in as {}".format(email))
            # Hide the login page and show the main app page bn
            main_app = st.empty()
            main_app.title("Your Streamlit App")
            main_app.write("Welcome to the main app page!")
            # Add your app's main functionality here
        else:
            st.error("Invalid email or password")
    return True

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text


def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks


def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    #embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-xl")
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore


def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()
    #llm = HuggingFaceHub(repo_id="google/flan-t5-xxl", model_kwargs={"temperature":0.5, "max_length":512})

    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain


def handle_userinput(user_question):
    response = st.session_state.conversation({'question': user_question})
    st.session_state.chat_history = response['chat_history']

    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            st.write(user_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)




def app_page():
    st.header("Chat with multiple PDFs :books:")
    user_question = st.text_input("Ask a question about your documents:")
    if user_question:
        handle_userinput(user_question)

    with st.sidebar:
        st.subheader("Your documents")
        pdf_docs = st.file_uploader(
            "Upload your PDFs here and click on 'Process'", accept_multiple_files=True)
        if st.button("Process"):
            with st.spinner("Processing"):
                # get pdf text
                raw_text = get_pdf_text(pdf_docs)

                # get the text chunks
                text_chunks = get_text_chunks(raw_text)

                # create vector store
                vectorstore = get_vectorstore(text_chunks)

                # create conversation chain
                st.session_state.conversation = get_conversation_chain(
                    vectorstore)

def main():
    load_dotenv()
    st.set_page_config(page_title="Ask your questions here ", page_icon=":books:")
    st.write(css, unsafe_allow_html=True)

    if not st.session_state.get('logged_in'):
        # Show the login page if the user is not logged in
        if login_page():
            st.session_state.logged_in = True
        else:
            st.write("Login failed. Please try again.")
    else:
        # If the user is logged in, show the main app page
        app_page()

if __name__ == '__main__':
    main()