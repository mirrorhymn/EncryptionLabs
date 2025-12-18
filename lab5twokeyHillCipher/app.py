from flask import Flask, render_template, request

app = Flask(__name__)

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZАБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
MOD = len(ALPHABET)


def text_to_numbers(text):
    return [ALPHABET.index(c.upper()) for c in text if c.upper() in ALPHABET]


def numbers_to_text(numbers):
    return ''.join(ALPHABET[n % MOD] for n in numbers)


def mod_inverse(a, m):
    for i in range(1, m):
        if (a * i) % m == 1:
            return i
    return None


def matrix_mod_inv(matrix, modulus):
    a, b, c, d = matrix[0][0], matrix[0][1], matrix[1][0], matrix[1][1]
    det = (a * d - b * c) % modulus
    det_inv = mod_inverse(det, modulus)
    if det_inv is None:
        return None
    return [[d * det_inv % modulus, -b * det_inv % modulus],
            [-c * det_inv % modulus, a * det_inv % modulus]]


def hill_encrypt(text, key):
    nums = text_to_numbers(text)
    if len(nums) % 2 != 0:
        nums.append(0)
    result = []
    for i in range(0, len(nums), 2):
        x, y = nums[i], nums[i + 1]
        x_new = (key[0][0] * x + key[0][1] * y) % MOD
        y_new = (key[1][0] * x + key[1][1] * y) % MOD
        result.extend([x_new, y_new])
    return numbers_to_text(result)


def hill_decrypt(text, key):
    inv_key = matrix_mod_inv(key, MOD)
    if not inv_key:
        return "Ключ не обратим!"
    nums = text_to_numbers(text)
    result = []
    for i in range(0, len(nums), 2):
        x, y = nums[i], nums[i + 1]
        x_new = (inv_key[0][0] * x + inv_key[0][1] * y) % MOD
        y_new = (inv_key[1][0] * x + inv_key[1][1] * y) % MOD
        result.extend([x_new, y_new])
    return numbers_to_text(result)


@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    if request.method == "POST":
        text = request.form.get("text", "")
        try:
            a = int(request.form.get("a"))
            b = int(request.form.get("b"))
            c = int(request.form.get("c"))
            d = int(request.form.get("d"))
        except ValueError:
            return render_template("index.html", result="Ключи должны быть числами")
        key = [[a, b], [c, d]]
        action = request.form.get("action")
        if action == "encrypt":
            result = hill_encrypt(text, key)
        else:
            result = hill_decrypt(text, key)
    return render_template("index.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)
