from flask import Flask, render_template, request
import base64
import os  # для генерации случайного ключа

app = Flask(__name__)


class RC5:
    def __init__(self):
        self.r = 12
        self.w = 32
        self.b = 16
        self.u = self.w // 8
        self.t = 2 * (self.r + 1)
        self.P32 = 0xB7E15163
        self.Q32 = 0x9E3779B9

    def rotl(self, x, y):
        y %= 32
        return ((x << y) | (x >> (32 - y))) & 0xFFFFFFFF

    def rotr(self, x, y):
        y %= 32
        return ((x >> y) | (x << (32 - y))) & 0xFFFFFFFF

    def expand_key(self, key: bytes):
        L = [0] * (len(key) // 4)
        for i in range(len(key)):
            L[i // 4] |= key[i] << (8 * (i % 4))

        S = [0] * self.t
        S[0] = self.P32
        for i in range(1, self.t):
            S[i] = (S[i - 1] + self.Q32) & 0xFFFFFFFF

        i = j = 0
        A = B = 0
        v = 3 * max(self.t, len(L))

        for _ in range(v):
            A = S[i] = self.rotl((S[i] + A + B) & 0xFFFFFFFF, 3)
            B = L[j] = self.rotl((L[j] + A + B) & 0xFFFFFFFF, A + B)
            i = (i + 1) % self.t
            j = (j + 1) % len(L)

        return S

    def encrypt_block(self, A, B, S):
        A = (A + S[0]) & 0xFFFFFFFF
        B = (B + S[1]) & 0xFFFFFFFF
        for i in range(1, self.r + 1):
            A = (self.rotl(A ^ B, B) + S[2 * i]) & 0xFFFFFFFF
            B = (self.rotl(B ^ A, A) + S[2 * i + 1]) & 0xFFFFFFFF
        return A, B

    def decrypt_block(self, A, B, S):
        for i in range(self.r, 0, -1):
            B = self.rotr((B - S[2 * i + 1]) & 0xFFFFFFFF, A) ^ A
            A = self.rotr((A - S[2 * i]) & 0xFFFFFFFF, B) ^ B
        B = (B - S[1]) & 0xFFFFFFFF
        A = (A - S[0]) & 0xFFFFFFFF
        return A, B

    def pad(self, data):
        pad_len = 8 - (len(data) % 8)
        return data + bytes([pad_len] * pad_len)

    def unpad(self, data):
        pad_len = data[-1]
        return data[:-pad_len]

    def encrypt(self, text, key):
        data = self.pad(text.encode())
        S = self.expand_key(key.encode())
        out = bytearray()
        for i in range(0, len(data), 8):
            A = int.from_bytes(data[i:i + 4], 'little')
            B = int.from_bytes(data[i + 4:i + 8], 'little')
            A, B = self.encrypt_block(A, B, S)
            out += A.to_bytes(4, 'little') + B.to_bytes(4, 'little')
        return base64.b64encode(out).decode()

    def decrypt(self, text, key):
        data = base64.b64decode(text)
        S = self.expand_key(key.encode())
        out = bytearray()
        for i in range(0, len(data), 8):
            A = int.from_bytes(data[i:i + 4], 'little')
            B = int.from_bytes(data[i + 4:i + 8], 'little')
            A, B = self.decrypt_block(A, B, S)
            out += A.to_bytes(4, 'little') + B.to_bytes(4, 'little')
        return self.unpad(out).decode(errors="ignore")


@app.route("/", methods=["GET", "POST"])
def index():
    result = ""
    generated_key = ""
    if request.method == "POST":
        text = request.form.get("text", "")
        key = request.form.get("key", "")
        action = request.form.get("action", "")

        rc5 = RC5()

        if "generate_key" in request.form:
            key_bytes = os.urandom(16)
            generated_key = key_bytes.hex()
        else:
            if action == "encrypt":
                result = rc5.encrypt(text, key)
            elif action == "decrypt":
                result = rc5.decrypt(text, key)

    return render_template("index.html", result=result, generated_key=generated_key)


if __name__ == "__main__":
    app.run(debug=True)
