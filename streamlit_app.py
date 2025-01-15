import streamlit as st
from pathlib import Path
import time
import base64
import os
import random

# App title
st.set_page_config(page_title="🦙💬 Llama 2 Chatbot")

image_path = Path(__file__).parent  / "poc_gantt.png"
pptx_gantt_path = Path(__file__).parent  / "poc_gantt.pptx"

# Store LLM generated responses
INTRO_PROMPT = (
    "Hi, I'm a workflow automation tool. To begin, let's gather some key details about your case to get started. "
    "If you don't know something, you can leave it blank. To start with, could you provide a one-line summary of the project?"
)

INFERRED_CONTEXT_RESPONSE = (
    "Great, this is what I've identified so far:\n\n"
    "- **Case Industry**: Automotive & Mobility\n"
    "- **Problem to Solve**: Strategy\n\n"
    "To help improve the quality of my response, I would like you to provide some more information about the case.\n"
    "Firstly, what is the expected case length?"
)

GEOGRAPHY_PROMPT = "Thank you, and what is the expected geography of the case? (**Global**, **Regional**, **National**)"

RESOURCES_PROMPT = "Thank you, and how many resources are you expecting to be working on this case? (**M+1**, **M+2**, **M+3**, **M+4**, Other)"

SUMMARY_PROMPT = (
    "Let me summarise all the information you've provided so far:\n\n"
    "- **Case Industry**: Automotive & Mobility\n"
    "- **Problem to Solve**: Strategy\n"
    "- **Case length**: 6 weeks\n"
    "- **Geography**: Global\n"
    "- **Case team resources**: M+4\n\n"
    "Is this correct?"
)

ADDITIONAL_NOTES_PROMPT = (
    "Great - a few extra notes before we kick off:\n"
    "- I re-read the notes from your client kickoff call on Tuesday, and it seems like Pricing and Product are key priorities for the client. **Would you like me to reflect this in our workplan?**\n"
    "- It seems from news reports and forum chatter that the Client is receiving pressure from an activist investor in Singapore — a key concern is the company’s recent EPS. **Would you like me to include EPS impact analysis in the modelling workstream?**\n"
    "- It seems as though Laura, the Analyst on your case, has a key development priority to work on a client-facing workstream — **are you happy for me to allocate her time to the survey workstream?**\n"
)

NEXT_STEPS_PROMPT = (
    "How would you like me to proceed?\n"
    "1. Generate a full project workplan\n"
    "2. Generate a workplan for a specific week (e.g., Week 1)\n"
    "3. Generate key meetings to schedule."
)

WORKPLAN_PROMPT = (
    "Based on the information you've provided, here's a proposed workplan with detailed workstreams and timelines:\n\n"
    "### **Proposed Workplan for Automotive Software Growth Strategy**\n\n"
    "#### **Suggested Workstreams:**\n\n"
    "---\n\n"
    "#### **1. Market Model (Weeks 1-5): Sylvia, Tom**\n"
    "**Objective:** Build a robust market sizing model to estimate market growth in automotive software cut by geography, module, customer archetype. Show growth over time and forecast to 2050.\n"
    "- **Data and Assumption Gathering (Weeks 1-2):**\n"
    "    - Collect relevant data and define modeling assumptions\n"
    "    - **Sources:** S&P Capital IQ, competitor reports, analyst data\n"
    "- **Model Setup + Driver Tree (Weeks 1-3):**\n"
    "    - Structure a market sizing framework with key drivers\n"
    "    - Pricing sensitivity analysis and impact on company EPS\n"
    "- **Driver Testing and Iteration (Weeks 4-5):**\n"
    "    - Validate assumptions and refine growth projections\n"
    "    - Pricing recommendations + impact on company EPS"
    "- **Output:** Market sizing model by geography, module, and customer archetype with forecasts to 2050 and accompanying slide [click to see example slides] + pricing recommendations\n\n"
    "---\n\n"
    "#### **2. Competitive Landscape (Weeks 2-4): Chelsea, Brian**\n"
    "**Objective:** Identify and analyze Automotive SoftwareCo's competitors to inform positioning and strategy.\n"
    "- **Global Archetypes and Key Players (Weeks 2-3):**\n"
    "    - Identify key competitor archetypes and players within each EPS comparison.\n"
    "    - **Sources:** Custom searches, industry associations, analyst reports.\n"
    "- **Zoom on Automotive SoftwareCo's Key Markets (Weeks 2-3):**\n"
    "    - Deep dive into Automotive SoftwareCo's specific geographic and product markets. -- zoom on pricing\n"
    "    - **Sources:** Client annual reports, financial reports, and regional data.\n"
    "- **Competitor Roadmaps (Weeks 3-4):**\n"
    "    - Analyze competitor offerings, strengths, and weaknesses relative to Automotive SoftwareCo.\n"
    "    - **Sources:** Competitor annual reports, industry white papers, thought leadership.\n\n"
    "---\n\n"
    "#### **3. Survey / Qualitative Data Gathering (Weeks 1-5): Laura, Diego**\n"
    "**Objective:** Gather insights from key Automotive SoftwareCo stakeholders and industry experts to inform strategic recommendations.\n"
    "- **Executive Survey Set-Up (Week 1):**\n"
    "    - Define question list.\n"
    "    - Define interviewee/recipient list.\n"
    "    - Schedule calls / code survey.\n"
    "- **Survey Execution (Weeks 2-3):**\n"
    "    - Conduct interviews.\n"
    "    - Distribute and manage survey responses.\n"
    "- **Survey Analysis (Weeks 4-5):**\n"
    "    - Consolidate findings.\n"
    "    - Develop visual outputs and insights.\n"
    "    - **Example Output:** Heatmap of priority focus areas.\n\n"
    "---\n\n"
    "#### **4. Product (Weeks 3-5): Chelsea, Tom**\n"
    "**Objective:** Understand product positioning and customer archetypes for Automotive SoftwareCo and competitors.\n"
    "- **DMS Product Overview (Weeks 3-5):**\n"
    "    - Analyze key modules, functionality, and market penetration.\n"
    "    - **Sources:** Competitor and industry reports, product specifications.\n"
    "- **Customer Archetypes (Weeks 3-5):**\n"
    "    - Define customer segments and personas based on survey and market data.\n"
    "- **Automotive SoftwareCo Product Suite Overview (Weeks 3-5):**\n"
    "    - Deep dive into Automotive SoftwareCo's products and customer segmentation.\n"
    "    - **Sources:** Internal client reports, industry benchmarks.\n\n"
    "---\n\n"
    "#### **5. Synthesis and Recommendation (Weeks 4-6): All**\n"
    "**Objective:** Deliver actionable strategic initiatives and a roadmap for implementation for Automotive SoftwareCo.\n"
    "- **Strategic Initiative Development (Weeks 4-5):**\n"
    "    - Prioritize based on geographies, customer archetypes, and competitive positioning.\n"
    "    - Incorporate survey findings, market model outputs, and product recommendations.\n"
    "- **High-Level Costing and 'Size of the Prize' (Week 5):**\n"
    "    - Estimate financial impact and resource requirements.\n"
    "- **Implementation Plan / Roadmap (Week 6):**\n"
    "    - Provide a phased roadmap for execution.\n"
)

WEEK_1_PROMPT = (
    "Sure, see below the team’s suggested priorities for Week 1:\n"
    "#### **1. Market Model: Sylvia, Tom**\n"
    "**Data and Assumption Gathering:**\n"
    "- Collect relevant data and define modeling assumptions\n"
    "- **Sources:** S&P Capital IQ, competitor reports, analyst data\n"
    "**Model Setup + Driver Tree:**\n"
    "- Structure a market sizing framework with key drivers\n"
    "#### **2. Competitive Landscape: Chelsea, Brian**\n"
    "- Identify key competitor archetypes and players within each, EPS comparison\n"
    "- **Sources:** Custom searches, industry associations, analyst reports\n"
    "#### **3. Survey / Qualitative Data Gathering: Laura, Diego**\n"
    "- **Executive Survey Set-Up:**\n"
    "    - Define question list\n"
    "    - Define interviewee/recipient list\n"
    "    - Schedule calls / code survey\n"
    "---\n"
    "Does this workflow align with your vision for the engagement? Let me know if adjustments or additional details are needed!"
)

SCHEDULE_PROMPT = (
    "Sure, see below a set of suggested meetings you can schedule to get started:\n\n"
    "**Key Meetings to Schedule:**\n"
    "- **Internal**\n"
    "    - Stand-ups and check-outs (daily)\n"
    "    - Partner 'content'/ problem-solving sessions (daily)\n"
    "    - Team check-ins (weekly)\n"
    "- **External**\n"
    "    - Check-in meetings with client counterparts (daily)\n"
    "    - Data gathering calls with relevant client stakeholders (Weeks 1 and 2)\n"
    "    - **Senior leadership Steering Committees for Weeks 3 and 6**\n"
    "\nWould you like me to check your team and client stakeholder availabilities and get these calls scheduled?"
)


# Predefined GPT responses
gpt_responses = [
    INTRO_PROMPT,
    INFERRED_CONTEXT_RESPONSE,
    GEOGRAPHY_PROMPT,
    RESOURCES_PROMPT,
    SUMMARY_PROMPT,
    ADDITIONAL_NOTES_PROMPT,
    NEXT_STEPS_PROMPT,
    WORKPLAN_PROMPT,
    WEEK_1_PROMPT,
    SCHEDULE_PROMPT
]


# Initialize session state
if 'response_index' not in st.session_state:
    st.session_state['response_index'] = 0

if 'messages' not in st.session_state:
    st.session_state['messages'] = [
        # {"role": "assistant", "content": INTRO_PROMPT}
    ]

# Define text streamer
def text_streamer(text, chunk_size=5, delay=0.05):
    """
    Generator function to simulate streaming by yielding chunks of text.

    Args:
        text (str): The input text to be streamed.
        chunk_size (int): The size of each text chunk to yield. Defaults to 5 characters.
        delay (float): Delay in seconds between yielding chunks. Defaults to 0.1.

    Yields:
        str: A chunk of the text.
    """
    for i in range(0, len(text), chunk_size):
        yield text[i:i + chunk_size]
        time.sleep(delay)

def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'You can download the Gantt chart <a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">here</a>'
    return href

# Display chat messages
for message in st.session_state['messages']:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

# Function to clear chat history
def clear_chat_history():
    st.session_state['messages'] = []
    st.session_state['response_index'] = 0

st.sidebar.button('Clear Chat History', on_click=clear_chat_history)
streaming = False

# Handle user input
if prompt := st.chat_input(disabled=streaming):
    st.session_state['messages'].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state['response_index'] += 1

# Generate assistant response
if st.session_state['response_index'] == 0:
    response_text = gpt_responses[st.session_state['response_index']]
    
    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown(response_text)

    st.session_state['messages'].append({"role": "assistant", "content": response_text})

elif st.session_state['response_index'] < len(gpt_responses) and st.session_state['response_index'] > 0:
    streaming = True
    response_text = gpt_responses[st.session_state['response_index']]
    full_response = ""
    
    with st.chat_message("assistant"):
        # if st.session_state['response_index'] == 6:
        #     st.button("Generate Full Project Workplan")
        #     st.button("Generate Workplan for Week 1")
        #     st.button("Generate Key Meetings to Schedule")

        if st.session_state['response_index'] > 6:
            with st.spinner('Thinking...'):
                time.sleep(3)
        placeholder = st.empty()
        for chunk in text_streamer(response_text):
            full_response += chunk
            placeholder.markdown(full_response)

        if st.session_state['response_index'] == 7:
            for chunk in text_streamer("\n\nI've also generated a Gantt chart for you to see the timeline of the project."):
                full_response += chunk
            image_bytes = open(image_path, "rb").read()
            st.image(image_path)
            st.write(get_binary_file_downloader_html(pptx_gantt_path, "Gantt Chart"), unsafe_allow_html=True)
            st.write("I hope this helps! Let me know if you have any questions.")
            placeholder.markdown(full_response)
        
    streaming = False
    st.session_state['messages'].append({"role": "assistant", "content": full_response})


