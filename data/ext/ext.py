from flask import Flask, Response, request, jsonify

import json
import html
import random
import requests

app = Flask(__name__)

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
            f"{idx+1}_correct_text": correct,
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
            "state": data.get("dom").get("state_table").get(f"question_{number}"),
            "slots": data.get("fsm").get("slots"),
        },
        "res": "Select one of the options."
    }

def init_quiz(data: dict) -> dict:
    slots = data.get("fsm").get("slots")
    slots.update(get_quiz())

    return jsonify({
        "fsm": {
            "state": data.get("fsm").get("state"),
            "slots": slots
        },
        "res": [
            WELCOME_MESSAGE,
            format_question(slots, "1"),
        ],
    })

def validate_ans_1(data: dict) -> dict:
    if data.get("txt") not in ["1", "2", "3", "4"]:
        return jsonify(wrong_option(data, "1"))

    slots = data.get("fsm").get("slots")
    return jsonify({
        "fsm": {
            "state": data.get("fsm").get("state"),
            "slots": slots
        },
        "res": format_question(slots, "2"),
    })
    

def validate_ans_2(data: dict) -> dict:
    if data.get("txt") not in ["1", "2", "3", "4"]:
        return jsonify(wrong_option(data, "2"))

    slots = data.get("fsm").get("slots")
    return jsonify({
        "fsm": {
            "state": data.get("fsm").get("state"),
            "slots": slots
        },
        "res":format_question(slots, "3"),
    })

def score(data: dict) -> dict:
    if data.get("txt") not in ["1", "2", "3", "4"]:
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
        "res": [
            message,
            "Do you want to see the correct answers?",
        ],
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
        "res": message_final,
    })

func_map = {
    "ext_init": init_quiz,
    "ext_val_ans_1": validate_ans_1,
    "ext_val_ans_2": validate_ans_2,
    "ext_score": score,
    "ext_score_review": score_review,
}


@app.route("/ext/get_all_funcs", methods=["GET"])
def get_all_funcs():
    return jsonify(list(func_map.keys()))

@app.route("/ext/get_func", methods=["POST"])
def get_func():
    data = request.get_json()
    req = data.get("req")
    f = func_map.get(req)
    if not f:
        return Response(status=400)
    return f(data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8770)
