
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import Ollama
import logging
import os
from backend.rag.vector_store import get_retriever

from dotenv import load_dotenv
from backend.utils.token_utils import count_tokens, is_prompt_safe, SAFE_MAX_INPUT_TOKENS
from backend.rag.vector_store import load_vector_store
import textwrap
   
    
load_dotenv()

TOP_K_DOCUMENTS = int(os.getenv("TOP_K_DOCUMENTS"))

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
)

file_handler = logging.FileHandler("rag.log")
file_handler.setFormatter(formatter)

if not logger.handlers:
    logger.addHandler(file_handler)


PROMPT_TEMPLATE =""" 
Act As a multilingual representative at , your role is to deliver exceptional chatbot support and also act as a quiz expert.
Understand the question Your objective is to provide the highest quality assistance, ensuring that your answers are
comprehensive and based on facts without any assumptions.Your goal is to strive to be the most friendly and helpful 
chat representative on your team. Craft a detailed and informative response in markdown to the user questions like actual person, addressing all aspects of their question.
Ensure your answer is thorough, while maintaining a friendly and supportive tone throughout. In any of your answer you must not generate any
example code of any programming language. while giving answer you must make your answer similar to the text of used documents.


Also ensure you can understand the language of question and provide response in same language tone, and provide response
in markdown format. Always use the information given in the content to look for answers, When asked a question outside
your provided context or knowledge, respectfully inform

-with this response, try to create interaction with auto generated question.Each response is an opportunity to deep dive further.


--------------------
CONTEXT:
{context}
--------------------

QUESTION:
{question}

ANSWER:
"""


prompt = PromptTemplate(
    template=PROMPT_TEMPLATE,
    input_variables=["context", "question"]
)

class RAGGenerator:

    def __init__(self):
        self.retriever = get_retriever(k=TOP_K_DOCUMENTS)
        self.vector_store = load_vector_store()

        self.llm = Ollama(
            model=os.getenv("MODEL"),
            base_url=os.getenv("BASE_URL")
        )

    def generate_answer(self, session_id=str, query=str, contextual_query=str):

        logger.info("-------RAG DEBUG START ------")
        logger.info(f"user query (LLM) : {query}")
        logger.info(f"retrived query : {contextual_query}")

        results = self.vector_store.similarity_search_with_score(
            contextual_query,
            k=6
        )

        logger.info(f'retrieved docs : {len(results)}')

        SIMILARITY_THRESOLD = 1.5

        documents = [] 

        for doc, score in results:

            if score <= SIMILARITY_THRESOLD:

                documents.append(doc)

        for i, (doc, score) in enumerate(results):

            preview = doc.page_content[:150].replace("\n", " ")

            logger.info(f"[{i+1}] score={score} | {preview}")

        logger.info(f'Docs after similarity search filter : {len(documents)}')

        context_parts = []
        current_tokens = 0
        used_documents = []

        for doc in documents:
            text = doc.page_content or ""

            if not text.strip():
                continue

            docs_tokens = count_tokens(text)

            if current_tokens + docs_tokens > SAFE_MAX_INPUT_TOKENS:
                logger.info("Token limit reached, Truncating text")
                break

            context_parts.append(text)
            used_documents.append(doc)
            current_tokens = current_tokens + docs_tokens

        context = "\n\n".join(context_parts)

        logger.info(f"context_tokens : {current_tokens}")
        logger.info(f"used_documents : {used_documents}")


        if len(context_parts) == 0:

            logger.info("Fallback triggered ")


            return {
                "answer": textwrap.dedent("""
                    I am a Klearcom chatbot assistant that can answer based upon the knowledge base of our company. 
                    Sorry for the inconvenience but I will not be able to answer the question which is out of our knowledge base.             

                    You can refer to the provided suggested questions to know our company better.

                    Suggested Questions:
                    1. what kind of innovative solutions does klearcom offers?
                    2. What is the IVR process?
                    3. what is klearcom's load testing solution regarding ivr improvement?
                    4. how klearcom can help discover Your IVR’s True In-Country Experience?
                    5. what is regression?
                    6. what our valuable partner eversana has to say about klearcom?
                    7. why klearcom should be chosen for my ivr solution?
                    """
                ),
                "sources": []
            }

        # -----------------------------------
        # BUILD FINAL PROMPT
        # -----------------------------------
        final_prompt = prompt.format(
            context=context,
            question=query   #  ONLY USER QUESTION
        )

        prompt_tokens = count_tokens(final_prompt)

        logger.info(f"Final prompt tokens: {prompt_tokens}")
        logger.info(f"Safe token limit: {SAFE_MAX_INPUT_TOKENS}")


        if not is_prompt_safe(prompt_tokens, include_margin=True):
            logger.warning("Prompt exceeded safe token limit")
            return {
                "answer": "Your query is too large to process safely. Please refine your question.",
                "sources": []
            }

        logger.info("FINAL PROMPT PREVIEW:")
        logger.info(final_prompt[:500])

        
        #-- LLM CALL--
        
        answer = self.llm.invoke(final_prompt)

        logger.info("LLM Raw Answer:")
        logger.info(answer)

        logger.info("========== RAG DEBUG END ==========")

        return{
            "answer" : answer,
            "sources": list({
                doc.metadata.get("url") for doc in used_documents
                if doc.metadata.get("url")
            }),           
        }






