from nicegui import ui
import requests

API_URL = "http://localhost:8005"

questions = []
page_body = ui.column()

def api_get(path):
    try:
        # Attempt to send GET request to API
        response = requests.get(f"{API_URL}{path}", timeout=5)
        # If we get an error code back, raise an exception
        response.raise_for_status()
        # Otherwise, GET was successful so return response data
        return response.json()
    except requests.RequestException as e:
        # GET request was unsuccessful
        # Send an alert with error details to the UI and return empty list
        ui.notify(f"Could not reach API: {e}", type="negative")
        return []

def api_post(path, data):
    try:
        # Attempt to send POST request to API with data payload
        response = requests.post(f"{API_URL}{path}", json=data, timeout=5)
        # If we get an error code back, raise an exception
        response.raise_for_status()
        # Otherwise, POST was successful so return True
        return True
    except requests.RequestException as e:
        # POST request was unsuccessful
        # Send an alert with error details to the UI and return False
        ui.notify(f"Could not reach API: {e}", type="negative")
        return False

def api_delete(path, id):
    try:
        # Attempt to send DELETE request to API for the question with the given id
        response = requests.delete(f"{API_URL}{path}/{id}", timeout=5)
        # If we get an error code back (e.g., 404 for an unknown id), raise an exception
        response.raise_for_status()
        # Otherwise, DELETE was successful so return True
        return True
    except requests.RequestException as e:
        # DELETE request was unsuccessful
        # Send an alert with error details to the UI and return False
        ui.notify(f"Could not delete question: {e}", type="negative")
        return False

def api_put(path, id, data):
    try:
        # Attempt to send PUT request to API with the updated question/answer as the data payload
        response = requests.put(f"{API_URL}{path}/{id}", json=data, timeout=5)
        # If we get an error code back (e.g., 404 for an unknown id), raise an exception
        response.raise_for_status()
        # Otherwise, PUT was successful so return True
        return True
    except requests.RequestException as e:
        # PUT request was unsuccessful
        # Send an alert with error details to the UI and return False
        ui.notify(f"Could not update question: {e}", type="negative")
        return False

def render_question(question):
    with ui.card():
        # Only the question/answer text toggles the answer, so that clicking the
        # edit/delete buttons does not also show/hide the answer.
        with ui.column().on("click", lambda: toggle_answer(question)):
            ui.label(question["q"])
            ui.label(question["a"]).classes("text-s text-green font-bold").bind_visibility_from(question["state"], "show_answer")
        with ui.row():
            # Each button captures this card's question, so it only affects this question
            ui.button("Edit", on_click=lambda: open_edit_dialog(question))
            ui.button("Delete", on_click=lambda: delete_question(question["id"]))

def toggle_answer(question):
    # Toggle the question's own state (indexing questions by id breaks once questions are deleted)
    question["state"]["show_answer"] = not question["state"]["show_answer"]

def delete_question(id):
    api_delete("/delete", id)
    render_page()

def open_edit_dialog(question):
    with ui.dialog() as dialog, ui.card():
        new_q = ui.textarea(label="Question", value=question["q"])
        new_a = ui.textarea(label="Answer", value=question["a"])
        ui.button('Update question', on_click=lambda: [
            dialog.close(),
            api_put("/update", question["id"], {
                "question": new_q.value,
                "answer": new_a.value
            }),
            render_page()
        ])
    dialog.open()

def add_new_question(question, answer):
    api_post("/add", {"question": question, "answer": answer})
    render_page()

def render_text_inputs():
    new_question_input = ui.input(label="New question").props("clearable")
    new_answer_input = ui.input(label="New answer").props("clearable")
    add_question_btn = ui.button(text="Add question", on_click=lambda: add_new_question(
        question=new_question_input.value,
        answer=new_answer_input.value
    ))

def init_page():
    render_page()

def render_page():
    global questions
    questions = api_get("/questions")
    page_body.clear()
    with page_body:
        for question in questions:
            question["state"] = {"show_answer": False}
            render_question(question)
        render_text_inputs()
    

init_page()
ui.run(port=8084, title="HCI Review Application")