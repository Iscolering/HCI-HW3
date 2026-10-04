from nicegui import ui
import requests

API_URL = "http://localhost:8005"

questions = []

# Part 5 (change 1): light grey page background so the white cards stand out as figures against the ground
ui.query("body").classes("bg-slate-100")
# Part 5 (change 2): a single centered, width-limited column so every element shares one left/right edge
page_body = ui.column().classes("w-full max-w-2xl mx-auto px-4 py-8 gap-4")

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

def render_question(question, number):
    # Part 5 (change 3): every card is full width, so the cards line up into one continuous list
    with ui.card().classes("w-full p-4 shadow-sm hover:shadow-md transition-shadow"):
        with ui.row().classes("w-full items-start no-wrap gap-3"):
            # Part 5 (change 4): a number badge gives each question a clear starting point and a scannable order
            ui.label(str(number)).classes(
                "shrink-0 w-8 h-8 rounded-full bg-indigo-100 text-indigo-700 font-semibold "
                "flex items-center justify-center text-sm")

            # Only the question/answer area toggles the answer, so that clicking the
            # edit/delete buttons does not also show/hide the answer.
            with ui.column().classes("flex-grow gap-2 cursor-pointer select-none") \
                    .on("click", lambda: toggle_answer(question)):
                ui.label(question["q"]).classes("text-base font-medium text-slate-800 leading-snug")

                # Part 5 (change 5): a "Show answer" signifier with a chevron tells users the card is clickable
                with ui.row().classes("items-center gap-1 text-sm text-indigo-600"):
                    ui.icon("expand_more").bind_name_from(
                        question["state"], "show_answer",
                        backward=lambda shown: "expand_less" if shown else "expand_more")
                    ui.label().bind_text_from(
                        question["state"], "show_answer",
                        backward=lambda shown: "Hide answer" if shown else "Show answer")

                # Part 5 (change 6): the answer sits in its own tinted, bordered region connected to its question
                with ui.column().classes("w-full gap-0 bg-green-50 border-l-4 border-green-600 rounded px-3 py-2") \
                        .bind_visibility_from(question["state"], "show_answer"):
                    ui.label("Answer").classes("text-xs uppercase tracking-wide text-green-700 font-semibold")
                    ui.label(question["a"]).classes("text-sm text-green-900")

            # Part 5 (change 7): low-emphasis icon buttons grouped together on the right, with a red delete
            # Each button captures this card's question, so it only affects this question
            with ui.row().classes("shrink-0 gap-0 no-wrap"):
                ui.button(icon="edit", on_click=lambda: open_edit_dialog(question)) \
                    .props("flat round dense color=grey-7").tooltip("Edit question")
                ui.button(icon="delete", on_click=lambda: delete_question(question["id"])) \
                    .props("flat round dense color=negative").tooltip("Delete question")

def toggle_answer(question):
    # Toggle the question's own state (indexing questions by id breaks once questions are deleted)
    question["state"]["show_answer"] = not question["state"]["show_answer"]

def delete_question(id):
    if api_delete("/delete", id):
        ui.notify("Question deleted", type="info")
    render_page()

def open_edit_dialog(question):
    with ui.dialog() as dialog, ui.card().classes("w-[32rem] max-w-full p-6 gap-4"):
        ui.label("Edit question").classes("text-lg font-semibold text-slate-800")
        new_q = ui.textarea(label="Question", value=question["q"]).props("outlined autogrow").classes("w-full")
        new_a = ui.textarea(label="Answer", value=question["a"]).props("outlined autogrow").classes("w-full")
        with ui.row().classes("w-full justify-end gap-2"):
            ui.button("Cancel", on_click=dialog.close).props("flat color=grey-8")
            ui.button('Update question', on_click=lambda: [
                dialog.close(),
                api_put("/update", question["id"], {
                    "question": new_q.value,
                    "answer": new_a.value
                }),
                render_page()
            ]).props("unelevated color=indigo")
    dialog.open()

def add_new_question(question, answer):
    if not question or not answer:
        ui.notify("Please enter both a question and an answer", type="warning")
        return
    api_post("/add", {"question": question, "answer": answer})
    render_page()

def render_text_inputs():
    # Part 5 (change 8): the add-question form is grouped inside its own titled card, visually separate
    # from the list of existing questions
    with ui.card().classes("w-full p-4 gap-3 mt-4 border-t-4 border-indigo-500"):
        ui.label("Add a new question").classes("text-lg font-semibold text-slate-800")
        new_question_input = ui.input(label="New question").props("clearable outlined dense").classes("w-full")
        new_answer_input = ui.input(label="New answer").props("clearable outlined dense").classes("w-full")
        with ui.row().classes("w-full justify-end"):
            add_question_btn = ui.button(text="Add question", icon="add", on_click=lambda: add_new_question(
                question=new_question_input.value,
                answer=new_answer_input.value
            )).props("unelevated color=indigo")

def render_header():
    # Part 5 (change 9): a page title and short instructions establish a clear visual hierarchy
    with ui.column().classes("w-full gap-1 mb-2"):
        ui.label("HCI Review").classes("text-3xl font-bold text-slate-900")
        ui.label(f"{len(questions)} question{'' if len(questions) == 1 else 's'} \u00b7 click a question to reveal its answer") \
            .classes("text-sm text-slate-500")

def init_page():
    render_page()

def render_page():
    global questions
    questions = api_get("/questions")
    page_body.clear()
    with page_body:
        render_header()
        for number, question in enumerate(questions, start=1):
            question["state"] = {"show_answer": False}
            render_question(question, number)
        if not questions:
            ui.label("No questions yet. Add one below!").classes("w-full text-center text-slate-500 py-6")
        render_text_inputs()
    

init_page()
ui.run(port=8084, title="HCI Review Application")
