from flask import Flask, render_template, request

app = Flask(__name__)

ALPHABET = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
N = len(ALPHABET)


def index_of(c):
    return ALPHABET.index(c)


def encrypt(message: str, key: str) -> str:
    if not key:
        return "❌ Ключевое слово не может быть пустым"

    result = []
    key = key.lower()
    key_index = 0

    for ch in message:
        if ch.lower() not in ALPHABET:
            result.append(ch)
            continue

        m = index_of(ch.lower())
        k = index_of(key[key_index % len(key)])
        key_index += 1

        c = (m + k) % N
        enc_char = ALPHABET[c]

        result.append(enc_char.upper() if ch.isupper() else enc_char)

    return "".join(result)


def decrypt(message: str, key: str) -> str:
    if not key:
        return "❌ Ключевое слово не может быть пустым"

    result = []
    key = key.lower()
    key_index = 0

    for ch in message:
        if ch.lower() not in ALPHABET:
            result.append(ch)
            continue

        c = index_of(ch.lower())
        k = index_of(key[key_index % len(key)])
        key_index += 1

        m = (c - k) % N
        dec_char = ALPHABET[m]

        result.append(dec_char.upper() if ch.isupper() else dec_char)

    return "".join(result)


@app.route("/", methods=["GET", "POST"])
def index():
    input_text = ""
    key = ""
    output_text = ""
    mode = ""

    if request.method == "POST":
        input_text = request.form.get("text", "")
        key = request.form.get("key", "")
        action = request.form.get("action")

        if action == "encrypt":
            output_text = encrypt(input_text, key)
            mode = "Зашифрованное сообщение"
        elif action == "decrypt":
            output_text = decrypt(input_text, key)
            mode = "Расшифрованное сообщение"

    return render_template(
        "index.html",
        input_text=input_text,
        key=key,
        output_text=output_text,
        mode=mode
    )


if __name__ == "__main__":
    app.run(debug=True)
