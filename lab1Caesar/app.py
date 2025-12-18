from flask import Flask, request, render_template

app = Flask(__name__)


def caesar_cipher(text, shift):
    ru_low = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
    ru_up = ru_low.upper()
    en_low = "abcdefghijklmnopqrstuvwxyz"
    en_up = en_low.upper()

    result = ""

    for ch in text:
        if ch in ru_low:
            result += ru_low[(ru_low.index(ch) + shift) % len(ru_low)]
        elif ch in ru_up:
            result += ru_up[(ru_up.index(ch) + shift) % len(ru_up)]
        elif ch in en_low:
            result += en_low[(en_low.index(ch) + shift) % len(en_low)]
        elif ch in en_up:
            result += en_up[(en_up.index(ch) + shift) % len(en_up)]
        else:
            result += ch

    return result


@app.route("/", methods=["GET", "POST"])
def index():
    text = ""
    result = ""
    shift = 1

    if request.method == "POST":
        text = request.form.get("text", "")
        shift = int(request.form.get("shift", 1))
        action = request.form.get("action", "encrypt")
        prev_result = request.form.get("result", "")

        if action == "encrypt":
            result = caesar_cipher(text, shift)

        elif action == "decrypt":
            source = prev_result if prev_result else text
            result = caesar_cipher(source, -shift)

    return render_template(
        "index.html",
        text=text,
        result=result,
        shift=shift
    )


if __name__ == "__main__":
    app.run(debug=True)
