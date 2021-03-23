import os
import json
import html
import random
import requests

from typing import List
from flask import Flask, Response, Request, jsonify

quiz_url = "https://opentdb.com/api.php?amount=3&type=multiple&category="

emoji_numbers = {
    "0": "0️⃣",
    "1": "1️⃣",
    "2": "2️⃣",
    "3": "3️⃣",
    "4": "4️⃣",
}

trivia_categories = [
    {
        "id": 9,
        "name": "General Knowledge",
        "pretty_name": "General Knowledge 🎓"
    },
    {
        "id": 10,
        "name": "Entertainment: Books",
        "pretty_name": "Books 📚"
    },
    {
        "id": 11,
        "name": "Entertainment: Film",
        "pretty_name": "Film 🍿"
    },
    {
        "id": 12,
        "name": "Entertainment: Music",
        "pretty_name": "Music 🎹"
    },
    {
        "id": 13,
        "name": "Entertainment: Musicals & Theatres",
        "pretty_name": "Musicals & Theatres 🎭"
    },
    {
        "id": 14,
        "name": "Entertainment: Television",
        "pretty_name": "Television 📺"
    },
    {
        "id": 15,
        "name": "Entertainment: Video Games",
        "pretty_name": "Video Games 🎮"
    },
    {
        "id": 16,
        "name": "Entertainment: Board Games",
        "pretty_name": "Board Games 🎲"
    },
    {
        "id": 17,
        "name": "Science & Nature",
        "pretty_name": "Science & Nature 🧬"
    },
    {
        "id": 18,
        "name": "Science: Computers",
        "pretty_name": "Computers 💻"
    },
    {
        "id": 19,
        "name": "Science: Mathematics",
        "pretty_name": "Mathematics 🧮"
    },
    {
        "id": 20,
        "name": "Mythology",
        "pretty_name": "Mythology 🔱"
    },
    {
        "id": 21,
        "name": "Sports",
        "pretty_name": "Sports ⚽"
    },
    {
        "id": 22,
        "name": "Geography",
        "pretty_name": "Geography 🗺️"
    },
    {
        "id": 23,
        "name": "History",
        "pretty_name": "History 📜"
    },
    {
        "id": 24,
        "name": "Politics",
        "pretty_name": "Politics 👨‍⚖️"
    },
    {
        "id": 25,
        "name": "Art",
        "pretty_name": "Art 🎨"
    },
    {
        "id": 26,
        "name": "Celebrities",
        "pretty_name": "Celebrities 👩‍🎤"
    },
    {
        "id": 27,
        "name": "Animals",
        "pretty_name": "Animals 🐅"
    },
    {
        "id": 28,
        "name": "Vehicles",
        "pretty_name": "Vehicles 🏎️"
    },
    {
        "id": 29,
        "name": "Entertainment: Comics",
        "pretty_name": "Comics 💬"
    },
    {
        "id": 30,
        "name": "Science: Gadgets",
        "pretty_name": "Gadgets ⚙️"
    },
    {
        "id": 31,
        "name": "Entertainment: Japanese Anime & Manga",
        "pretty_name": "Japanese Anime & Manga 🇯🇵"
    },
    {
        "id": 32,
        "name": "Entertainment: Cartoon & Animations",
        "pretty_name": "Cartoon & Animations 📺"
    }
]

def get_category_pretty_name(name: str) -> str:
    pretty_names = [cat.get("pretty_name")
                    for cat in trivia_categories if cat.get("name") == name]
    if len(pretty_names) == 0:
        return name
    return pretty_names[0]

WELCOME_MESSAGE = "Hello and welcome to the trivia bot! ✨\n\nYou'll be asked 3 different trivia questions from any difficulty and category."
QUESTION_TEMPLATE = "*Category: {category}* \n👉 {question_text} \n{options}"


def make_text_answers(*messages) -> List[dict]:
    return [{"text": msg} for msg in messages]


def get_quiz(category: str = "") -> list:
    if category:
        r = requests.get(quiz_url + str(trivia_categories[int(category)-1].get("id")))
    else:
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
        category=get_category_pretty_name(slots.get(f"{number}_category")),
        question_text=slots.get(f"{number}_question"),
        options=slots.get(f"{number}_options_text"),
    )


def wrong_option(data: dict, state: str) -> dict:
    return {
        "fsm": {
            "state": data.get("domain").get("state_table").get(state),
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


def init_category(data: dict) -> dict:
    if data.get("question").get("text") not in [str(i+1) for i in range(len(trivia_categories))]:
        return jsonify(wrong_option(data, "select_category"))
    
    slots = data.get("fsm").get("slots")
    slots.update(get_quiz(category=data.get("question").get("text")))

    return jsonify({
        "fsm": {
            "state": data.get("fsm").get("state"),
            "slots": slots
        },
        "answers": make_text_answers(
            format_question(slots, "1")
        ),
    })


def validate_ans_1(data: dict) -> dict:
    if data.get("question").get("text") not in ["1", "2", "3", "4"]:
        return jsonify(wrong_option(data, "question_1"))

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
        return jsonify(wrong_option(data, "question_2"))

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
        return jsonify(wrong_option(data, "question_3"))

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
    for i in range(1, 4):
        question = slots.get(f"{i}_question")
        corr_text = slots.get(f"{i}_correct_text")
        message.append(
            f"{emoji_numbers.get(str(i))} {question} \n👉 *{corr_text}*")
    message_final = "\n\n".join(message)

    return jsonify({
        "fsm": data.get("fsm"),
        "answers": make_text_answers(message_final),
    })
