from flask import Flask, request, jsonify, render_template
import utils
import concurrent.futures

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("dashboard.html")

@app.route("/api/post", methods=["POST"])
def api_post():
    data = request.json
    try:
        result = utils.gen_post(data["platform"], data["topic"])
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/hook", methods=["POST"])
def api_hook():
    data = request.json
    try:
        result = utils.gen_hook(data["topic"])
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/script", methods=["POST"])
def api_script():
    data = request.json
    try:
        result = utils.gen_script(data["topic"])
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/trendscore", methods=["POST"])
def api_trendscore():
    data = request.json
    try:
        result = utils.gen_trendscore(data["topic"])
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/hashtags", methods=["POST"])
def api_hashtags():
    data = request.json
    try:
        result = utils.gen_hashtags(data["platform"], data["topic"])
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/caption", methods=["POST"])
def api_caption():
    data = request.json
    try:
        result = utils.gen_caption(data["platform"], data["description"])
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/setvoice", methods=["POST"])
def api_setvoice():
    data = request.json
    try:
        utils.save_voice(int(data["user_id"]), data["description"])
        return jsonify({"result": f"Brand voice saved successfully."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/getvoice", methods=["POST"])
def api_getvoice():
    data = request.json
    try:
        voice = utils.get_voice(int(data["user_id"]))
        return jsonify({"result": voice or "No brand voice saved yet."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/create", methods=["POST"])
def api_create():
    data = request.json
    platform = data["platform"]
    topic = data["topic"]
    try:
        with concurrent.futures.ThreadPoolExecutor() as ex:
            f_trend = ex.submit(utils.gen_trendscore, topic)
            f_post = ex.submit(utils.gen_post, platform, topic)
            f_hash = ex.submit(utils.gen_hashtags, platform, topic)
            trend = f_trend.result()
            post = f_post.result()
            hashtags = f_hash.result()
            virality = utils.gen_virality(post, topic)
        return jsonify({"trendscore": trend, "post": post, "hashtags": hashtags, "virality": virality})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.json
    messages = data.get("messages", [])
    system_msg = {
        "role": "system",
        "content": (
            "You are Beru, an AI-powered social media content assistant. "
            "You help with content creation, social media strategy, hooks, scripts, captions, and hashtags. "
            "You are knowledgeable about YouTube, Instagram, LinkedIn, Twitter, and WhatsApp. "
            "Be concise, sharp, and genuinely helpful. Your Discord bot prefix is ','."
        )
    }
    try:
        result = utils.groq_complete([system_msg] + messages, max_tokens=500, temperature=0.8)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def run_dashboard(port=5000):
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
