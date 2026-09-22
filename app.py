import streamlit as st

from query import ask

st.set_page_config(page_title="The Unofficial Guide", page_icon="🏠")

st.title("The Unofficial Guide")
st.caption(
    "Ask a question about off-campus housing near Howard University. Answers are grounded "
    "in tenant reviews, shuttle schedules, and official Howard housing guidance — nothing else."
)

question = st.text_input("Your question", placeholder="e.g. What do tenants say about Clover at the Parks?")

if st.button("Ask") and question:
    with st.spinner("Retrieving and generating..."):
        result = ask(question)

    st.subheader("Answer")
    st.write(result["answer"])

    st.subheader("Retrieved from")
    if result["sources"]:
        for s in result["sources"]:
            st.write(f"- {s}")
    else:
        st.write("No sources — the answer above was not drawn from the document collection.")
