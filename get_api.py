from fastapi import FastAPI, Query
from index import classifier , OutScope_Response

app = FastAPI()

@app.get("/get_answers/")
async def get_answers(query: str = Query(None, min_length=2)):
    answer = classifier(query)

    return answer

