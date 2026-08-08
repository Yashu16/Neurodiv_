from flask import Flask, render_template, request
from generator import generate_representations

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    concept = ""

    if request.method == "POST":
        concept = request.form.get("concept", "").strip()
        if concept:
            try:
                result = generate_representations(concept)
            except Exception as e:
                error = str(e)

    return render_template("index.html", result=result, error=error, concept=concept)


if __name__ == "__main__":
    app.run(debug=True, port=5000)