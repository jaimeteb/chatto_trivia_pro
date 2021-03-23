from flask import Request, Response, jsonify
from trivia import trivia

registered_extensions = {
    "init": trivia.init_quiz,
    "init_category": trivia.init_category,
    "val_ans_1": trivia.validate_ans_1,
    "val_ans_2": trivia.validate_ans_2,
    "score": trivia.score,
    "score_review": trivia.score_review,
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
    import os
    from flask import Flask, request

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
