from typing import List
from flask import Flask, Response, Request, jsonify

import os
import json
import html
import random
import requests

quiz_url = "https://opentdb.com/api.php?amount=3&type=multiple"

emoji_numbers = {
    "0": "0️⃣",
    "1": "1️⃣",
    "2": "2️⃣",
    "3": "3️⃣",
    "4": "4️⃣",
}

emoji_categories = {
    "General Knowledge": "General Knowledge 🎓",
    "Entertainment: Books": "Books 📚",
    "Entertainment: Film": "Film 🍿",
    "Entertainment: Music": "Music 🎹",
    "Entertainment: Musicals & Theatres": "Musicals & Theatres 🎭",
    "Entertainment: Television": "Television 📺",
    "Entertainment: Video Games": "Video Games 🎮",
    "Entertainment: Board Games": "Board Games 🎲",
    "Science & Nature": "Science & Nature 🧬",
    "Science: Computers": "Computers 💻",
    "Science: Mathematics": "Mathematics 🧮",
    "Mythology": "Mythology 🔱",
    "Sports": "Sports ⚽",
    "Geography": "Geography 🗺️",
    "History": "History 📜",
    "Politics": "Politics 👨‍⚖️",
    "Art": "Art 🎨",
    "Celebrities": "Celebrities 👩‍🎤",
    "Animals": "Animals 🐅",
    "Vehicles": "Vehicles 🏎️",
    "Entertainment: Comics": "Comics 💬",
    "Science: Gadgets": "Gadgets ⚙️",
    "Entertainment: Japanese Anime & Manga": "Japanese Anime & Manga 🇯🇵",
    "Entertainment: Cartoon & Animations": "Cartoon & Animations 📺",
}


WELCOME_MESSAGE = "Hello and welcome to the trivia bot! ✨\n\nYou'll be asked 3 different trivia questions from any difficulty and category."
QUESTION_TEMPLATE = "*Category: {category}* \n👉 {question_text} \n{options}"

def make_text_answers(*messages) -> List[dict]:
    return [{"text": msg} for msg in messages]

def get_quiz() -> list:
    r = requests.get(quiz_url)
    quiz_data = r.json().get("results")

    quiz_data_new = {}
    for idx, q in enumerate(quiz_data):
        options = q.get("incorrect_answers", [])
        correct = q.get("correct_answer")

        correct_index = random.randint(0, 3)
        options.insert(correct_index, correct)

        options_text = "\n".join([f"{emoji_numbers.get(str(i+1))} {html.unescape(o)}"
            for i, o in enumerate(options)])
        
        quiz_data_new.update({
            f"{idx+1}_category": q.get("category"),
            f"{idx+1}_question": html.unescape(q.get("question")),
            f"{idx+1}_options_text": options_text,
            f"{idx+1}_correct": str(correct_index + 1),
            f"{idx+1}_correct_text": html.unescape(correct),
        })

    return quiz_data_new

def format_question(slots: dict, number: str) -> str:
    return QUESTION_TEMPLATE.format(
        # number=f"{emoji_numbers.get(number)}",
        category=emoji_categories.get(slots.get(f"{number}_category")),
        question_text=slots.get(f"{number}_question"),
        options=slots.get(f"{number}_options_text"),
    )

def wrong_option(data: dict, number: str) -> dict:
    return {
        "fsm": {
            "state": data.get("domain").get("state_table").get(f"question_{number}"),
            "slots": data.get("fsm").get("slots"),
        },
        "answers": [{"text": "Select one of the options."}],
    }

def init_quiz(data: dict) -> dict:
    slots = data.get("fsm").get("slots")
    slots.update(get_quiz())

    return jsonify({
        "fsm": {
            "state": data.get("fsm").get("state"),
            "slots": slots
        },
        "answers": make_text_answers(
            WELCOME_MESSAGE,
            format_question(slots, "1")
        ),
    })

def validate_ans_1(data: dict) -> dict:
    if data.get("question").get("text") not in ["1", "2", "3", "4"]:
        return jsonify(wrong_option(data, "1"))

    slots = data.get("fsm").get("slots")
    return jsonify({
        "fsm": {
            "state": data.get("fsm").get("state"),
            "slots": slots
        },
        "answers": make_text_answers(format_question(slots, "2")),
    })
    

def validate_ans_2(data: dict) -> dict:
    if data.get("question").get("text") not in ["1", "2", "3", "4"]:
        return jsonify(wrong_option(data, "2"))

    slots = data.get("fsm").get("slots")
    return jsonify({
        "fsm": {
            "state": data.get("fsm").get("state"),
            "slots": slots
        },
        "answers": make_text_answers(format_question(slots, "3")),
    })

def score(data: dict) -> dict:
    if data.get("question").get("text") not in ["1", "2", "3", "4"]:
        return jsonify(wrong_option(data, "3"))

    slots = data.get("fsm").get("slots")
    
    answer_1 = slots.get("answer_1")
    answer_2 = slots.get("answer_2")
    answer_3 = slots.get("answer_3")
    
    correct_1 = slots.get("1_correct")
    correct_2 = slots.get("2_correct")
    correct_3 = slots.get("3_correct")

    score = 0
    score = score + 1 if answer_1 == correct_1 else score
    score = score + 1 if answer_2 == correct_2 else score
    score = score + 1 if answer_3 == correct_3 else score

    message = f"You got {score}/3 answers right."
    if score == 0:
        message += "\nBetter luck next time! 😔"
    elif score == 1:
        message += "\nKeep trying! 😟"
    elif score == 2:
        message += "\nPretty good! 🤩"
    elif score == 3:
        message += "\nYou are good! Congrats! 🤯"

    return jsonify({
        "fsm": data.get("fsm"),
        "answers": make_text_answers(
            message,
            "Do you want to see the correct answers?",
        ),
    })

def score_review(data: dict) -> dict:
    slots = data.get("fsm").get("slots")

    correct_1 = slots.get("1_correct_text")
    correct_2 = slots.get("2_correct_text")
    correct_3 = slots.get("3_correct_text")

    message = []
    for i in range(1,4):
        question = slots.get(f"{i}_question")
        corr_text = slots.get(f"{i}_correct_text")
        message.append(f"{emoji_numbers.get(str(i))} {question} \n👉 *{corr_text}*")
    message_final = "\n\n".join(message)

    return jsonify({
        "fsm": data.get("fsm"),
        "answers": make_text_answers(message_final),
    })

registered_extensions = {
    "init": init_quiz,
    "val_ans_1": validate_ans_1,
    "val_ans_2": validate_ans_2,
    "score": score,
    "score_review": score_review,
}

def get_all_extensions():
    return jsonify(list(registered_extensions.keys()))

def get_extension(request: Request):
    data = request.get_json()
    f = registered_extensions.get(data.get("extension", ""))
    if not f:
        return Response(status=400)
    return f(data)

def entrypoint(request: Request):
    if request.path == "/extensions" and request.method == "GET":
        return get_all_extensions()
    elif request.path == "/extension" and request.method == "POST":
        return get_extension(request)
    else:
        return Response(status=400)


if __name__ == "__main__":
    from flask import request

    app = Flask(__name__)
    debug = True if os.getenv("DEBUG", "false") == "true" else False

    @app.route("/extensions", methods=["GET"])
    def get_all_extensions_flask():
        return jsonify(list(registered_extensions.keys()))
    
    @app.route("/extension", methods=["POST"])
    def get_extension_flask():
        data = request.get_json()
        app.logger.debug(data)
        req = data.get("extension")
        f = registered_extensions.get(req)
        if not f:
            return Response(status=400)
        r = f(data)
        app.logger.debug(r)
        return r

    app.run(host="0.0.0.0", port=8770, debug=debug)
