import streamlit as st
import json
import os
from openai import OpenAI

st.set_page_config(page_title="Chatbot with Long-Term Memory")
st.title("Chatbot with Long-Term Memory")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
MEMORY_FILE = "memories.json"


def load_memories():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as file:
                return json.load(file)
        except:
            return []
    return []


def save_memories(memories):
    with open(MEMORY_FILE, "w") as file:
        json.dump(memories, file, indent=2)


def extract_new_memories(user_message, assistant_message, existing_memories):
    prompt = f"""
You are a memory extraction assistant.

Extract NEW facts about the user worth remembering.
Return ONLY a JSON list of strings.

Existing memories:
{json.dumps(existing_memories)}

User message:
{user_message}

Assistant response:
{assistant_message}
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[
                {"role": "system", "content": "Return JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        content = response.choices[0].message.content.strip()
        data = json.loads(content)
        if isinstance(data, list):
            return [str(x).strip() for x in data]
    except:
        return []
    return []


memories = load_memories()

st.sidebar.header("Saved Memories")
if memories:
    for m in memories:
        st.sidebar.write(f"- {m}")
else:
    st.sidebar.write("No memories yet. Start chatting!")

if st.sidebar.button("Clear All Memories"):
    save_memories([])
    st.rerun()


if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])


memory_text = ""
if memories:
    memory_text = "Here are things you remember about this user:\n" + "\n".join(f"- {m}" for m in memories)

system_prompt = f"""
You are a helpful chatbot.
{memory_text}
Use saved memories when relevant.
"""


user_input = st.chat_input("Say something...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    messages = [{"role": "system", "content": system_prompt}]
    messages += st.session_state.messages

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages,
        temperature=0.7
    )

    reply = response.choices[0].message.content

    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.write(reply)

    new_memories = extract_new_memories(user_input, reply, memories)
    updated = memories.copy()

    for m in new_memories:
        if m not in updated:
            updated.append(m)

    save_memories(updated)