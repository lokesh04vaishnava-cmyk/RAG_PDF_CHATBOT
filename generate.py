import os
from groq import Groq


def generate_answer(query, context_chunks, client):
    context = "\n\n".join(context_chunks)

    system_prompt = (
        "You are a helpful assistant that answers questions based only on the "
        "provided context. If the answer is not in the context, say you don't know "
        "instead of guessing."
    )
    user_prompt = f"Context:\n{context}\n\nQuestion: {query}"

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content


def decompose_query(question, client):
    prompt = (
        "Split the following question into 1-3 separate, simple, self-contained "
        "sub-questions if it contains multiple distinct asks. If it's already a "
        "single simple question, just return it as-is. Return ONLY the sub-questions, "
        "one per line, with no numbering or extra text.\n\n"
        f"Question: {question}"
    )
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
    )
    lines = response.choices[0].message.content.strip().split("\n")
    return [line.strip("- ").strip() for line in lines if line.strip()]