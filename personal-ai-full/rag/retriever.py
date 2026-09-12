# ============================================================
# JARVIS RAG RETRIEVER v5.2
# BEASTMODE COPILOT ENGINE
# FUNCTION + FILE + CALL GRAPH AWARE
# ============================================================


import re
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

from config import CHROMA_DIR



# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent


MODEL_PATH = (
    BASE_DIR
    /
    "models"
    /
    "all-MiniLM-L6-v2"
)



# ============================================================
# LOAD EMBEDDING MODEL
# ============================================================

print("[RAG] Loading embedding model...")


model = SentenceTransformer(
    str(MODEL_PATH),
    local_files_only=True
)


print("[RAG] Embedding model ready.")





# ============================================================
# CHROMA
# ============================================================


CHROMA_DIR = Path(CHROMA_DIR)


client = chromadb.PersistentClient(
    path=str(CHROMA_DIR)
)


collection = client.get_or_create_collection(
    name="local_docs"
)





# ============================================================
# TEXT UTILITIES
# ============================================================


def normalize(text):

    if not text:
        return ""

    return str(text).lower().strip()





def extract_symbols(query):

    return re.findall(

        r"[a-zA-Z_][a-zA-Z0-9_]*",

        normalize(query)

    )





def extract_terms(query):

    words = re.findall(

        r"[a-zA-Z0-9_./\\-]+",

        normalize(query)

    )


    stop_words = {

        "how",
        "does",
        "the",
        "a",
        "an",
        "is",
        "are",
        "what",
        "why",
        "using",
        "use",
        "with",
        "from",
        "for",
        "explain",
        "show",
        "tell"

    }


    return [

        x

        for x in words

        if len(x) > 1
        and x not in stop_words

    ]





# ============================================================
# SCORE ENGINE
# ============================================================


def calculate_score(

        query,
        doc,
        meta,
        distance=None

):


    score = 0


    query = normalize(query)
    doc = normalize(doc)


    meta = meta or {}


    filename = normalize(
        meta.get("file","")
    )


    source = normalize(
        meta.get("source","")
    )


    symbol = normalize(
        meta.get("symbol","")
    )


    unit = normalize(
        meta.get("unit_type","")
    )



    # ----------------------------
    # Semantic
    # ----------------------------


    try:

        score += max(

            0,

            20 - float(distance)*10

        )

    except:

        pass




    # ----------------------------
    # File matching
    # ----------------------------


    for term in extract_terms(query):


        if term in filename:

            score += 25


        if term in source:

            score += 15





    # ----------------------------
    # API file priority
    # ----------------------------


    if "api_server.py" in query:


        if "api_server.py" in filename:

            score += 200





    # ----------------------------
    # Symbol matching
    # ----------------------------


    for q_symbol in extract_symbols(query):


        q_symbol = q_symbol.lower()



        if q_symbol == symbol:

            score += 450



        elif q_symbol in symbol:

            score += 150



        if q_symbol in doc:

            score += 40

    # ----------------------------
    # Unit priority
    # ----------------------------


    if unit == "function":

        score += 100


    elif unit == "class":

        score += 30


    elif unit == "module_header":

        score -= 500





    # ----------------------------
    # Relationship intelligence
    # ----------------------------


    relationships = {


        "speak_async":

        [

            "speak_async",

            "from voice.tts import",

            "result = speak_async"

        ],


        "handle_user_input":

        [

            "handle_user_input"

        ],


        "voice":

        [

            "voice.tts",

            "tts",

            "speak"

        ]

    }




    for key, patterns in relationships.items():


        if key in query:


            for pattern in patterns:


                if pattern in doc:

                    score += 100





    # ----------------------------
    # Caller graph boost
    # ----------------------------


    if "speak_async(" in doc:

        score += 250



    if "request.get_json" in doc:

        score += 100



    if "@app.route" in doc:

        score += 50




    # ----------------------------
    # Reduce unrelated voice loop
    # ----------------------------


    if "voice_loop" in symbol:

        score -= 100




    return score







# ============================================================
# SEARCH ENGINE
# ============================================================


def search(

        query,

        n=8,

        candidates=60,

        max_chars=12000

):


    if not query:

        return ""



    try:


        total = collection.count()


        if total == 0:

            return ""





        embedding = model.encode(

            [query],

            show_progress_bar=False

        ).tolist()





        result = collection.query(

            query_embeddings=embedding,

            n_results=min(

                candidates,

                total

            ),

            include=[

                "documents",

                "metadatas",

                "distances"

            ]

        )




        docs = result["documents"][0]

        metas = result["metadatas"][0]

        distances = result["distances"][0]





        ranked = []

        seen = set()





        for i, doc in enumerate(docs):


            meta = metas[i] or {}



            key = (

                meta.get(

                    "source",

                    ""

                ),

                meta.get(

                    "symbol",

                    ""

                )

            )



            if key in seen:

                continue



            seen.add(key)




            score = calculate_score(

                query,

                doc,

                meta,

                distances[i]

            )



            ranked.append(

                {

                    "score": score,

                    "doc": doc,

                    "meta": meta

                }

            )





        ranked.sort(

            key=lambda x: x["score"],

            reverse=True

        )




        ranked = ranked[:n]





        output = []

        size = 0





        for index,item in enumerate(

            ranked,

            start=1

        ):


            meta = item["meta"]



            block = f"""

==================================================
RESULT {index}
==================================================

FILE:

{meta.get("file","")}


SYMBOL:

{meta.get("symbol","")}


TYPE:

{meta.get("unit_type","")}


LINES:

{meta.get("start_line","")}
-
{meta.get("end_line","")}


SOURCE:

{meta.get("source","")}


SCORE:

{item["score"]:.2f}


CODE:

{item["doc"]}

"""



            if size + len(block) > max_chars:

                break



            output.append(block)

            size += len(block)





        print()

        print(

            "[RAG] Query:",

            query

        )


        print(

            "[RAG] Selected:",

            len(output)

        )


        print()

        print(

            "[RAG] Top matches:"

        )




        for item in ranked[:5]:


            print(

                f"{item['score']:.2f} -> "

                f"{item['meta'].get('source','')} | "

                f"{item['meta'].get('symbol','')}"

            )





        return "\n".join(output)





    except Exception as e:


        print(

            "[RAG ERROR]",

            e

        )


        return ""



# ============================================================
# TEST
# ============================================================


if __name__ == "__main__":


    result = search(

        "How does api_server.py use speak_async from voice.tts?"

    )


    print(result)