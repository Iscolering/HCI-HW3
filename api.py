import uvicorn
 
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="HCI Mini Review App API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

questions = [{
                "id": 0,
                "q": "Is Fitts' Law an example of a predictive model or a descriptive model?",
                "a": "Predictive model"
                },
             {
                "id": 1,
                "q": "Does this course focus more on genius design, systems design, or user-centered design?",
                "a": "User-centered design"
                },
             {
                "id": 2,
                "q": "What is the main goal of the ideation phase of iterative design?",
                "a": "Generating as many possible design solutions as possible"
                }
            ]

class QuestionRequest(BaseModel):
    question: str
    answer: str

@app.get("/questions")
def get_questions():
    return questions

@app.post("/add")
def add_question(req: QuestionRequest):
    # Use one more than the largest existing id (rather than len(questions)) so that
    # ids stay unique even after questions have been deleted.
    new_id = max((q["id"] for q in questions), default=-1) + 1
    questions.append({ 
        "id": new_id,
        "q": req.question,
        "a": req.answer
    })

def find_question(id: int):
    # Return the question dictionary with the given id, or raise a 404 if it does not exist
    for question in questions:
        if question["id"] == id:
            return question
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Question with ID {id} not found")

# Route that can be used to delete a question/answer from the dataset.
@app.delete("/delete/{id}")
def delete_question(id: int):
    question = find_question(id)
    questions.remove(question)
    return {"detail": f"Question with ID {id} deleted"}

# Route that can be used to update a question/answer within the dataset.
@app.put("/update/{id}")
def update_question(id: int, req: QuestionRequest):
    question = find_question(id)
    question["q"] = req.question
    question["a"] = req.answer
    return question

if __name__=="__main__":
    uvicorn.run(app, port=8005)