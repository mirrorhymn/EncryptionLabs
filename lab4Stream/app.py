from flask import Flask, render_template, request

app = Flask(__name__)

def xor_cipher(message: str, key: str) -> str:
    if not key:
        return "Ключ не может быть пустым"
    message_bytes = message.encode('utf-8')
    key_bytes = key.encode('utf-8')
    result = bytes([b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(message_bytes)])
    return result.hex()  # возвращаем в виде hex

def xor_decipher(hex_message: str, key: str) -> str:
    if not key:
        return "Ключ не может быть пустым"
    try:
        message_bytes = bytes.fromhex(hex_message)
    except ValueError:
        return "неверный формат сообщения (должен быть HEX)"
    key_bytes = key.encode('utf-8')
    result = bytes([b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(message_bytes)])
    return result.decode('utf-8', errors='replace')


@app.route("/", methods=["GET", "POST"])
def index():
    output = ""
    message = ""
    key = ""
    if request.method == "POST":
        message = request.form.get("message", "")
        key = request.form.get("key", "")
        action = request.form.get("action")

        if action == "encrypt":
            output = xor_cipher(message, key)
        elif action == "decrypt":
            output = xor_decipher(message, key)

    # Передаём обратно все значения, чтобы они оставались в форме
    return render_template("index.html", output=output, message=message, key=key)

if __name__ == "__main__":
    app.run(debug=True)
