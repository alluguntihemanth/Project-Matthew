# conv_agent.py
import streamlit as st
from langchain.chains import ConversationChain, LLMChain
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq

def load_conv_agent(groq_api_key):
    # Setup the customization in sidebar
    st.sidebar.title('Customization')
    system_prompt = st.sidebar.text_input("System prompt:")
    model = st.sidebar.selectbox(
        'Choose a model',
        ['llama3-8b-8192', 'mixtral-8x7b-32768', 'gemma-7b-it', 'gemma2-9b-it', 'llama-3.1-70b-versatile']
    )
    conversational_memory_length = st.sidebar.slider('Conversational memory length:', 1, 10, value=5)

    memory = ConversationBufferWindowMemory(k=conversational_memory_length, memory_key="chat_history", return_messages=True)
    
    # Initialize Groq Langchain chat object
    groq_chat = ChatGroq(groq_api_key=groq_api_key, model_name=model)

    return groq_chat, memory, system_prompt

def handle_chat(groq_chat, memory, system_prompt, current_heart_rate):
    # Get user input
    user_question = st.text_input("Ask a question:")

    # If the heart rate is present, add a condition to modify the system prompt
    if current_heart_rate:
        system_prompt += f" The user's current heart rate is {current_heart_rate} BPM. Adjust the tone of the conversation based on this data."
        
        if current_heart_rate > 100:
            system_prompt += " The heart rate is elevated. Respond with a calming and empathetic tone."
        elif current_heart_rate < 60:
            system_prompt += " The heart rate is low. Respond with a more energetic tone."
        else:
            system_prompt += " The heart rate is normal. Respond in a neutral tone."

    # Session state for chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    else:
        for message in st.session_state.chat_history:
            memory.save_context({'input': message['human']}, {'output': message['AI']})

    # If the user has asked a question,
    if user_question:
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{human_input}")
        ])
        
        conversation = LLMChain(
            llm=groq_chat,  
            prompt=prompt,  
            verbose=True,   
            memory=memory
        )
        
        response = conversation.predict(human_input=user_question)
        message = {'human': user_question, 'AI': response}
        st.session_state.chat_history.append(message)
        st.write("Chatbot:", response)
