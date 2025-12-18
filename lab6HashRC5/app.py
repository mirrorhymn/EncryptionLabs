from flask import Flask, render_template, request

app = Flask(__name__)

#реализвция RC5
def RC5_encrypt(block, key, w=32, r=12):


    def to_words(b):
        return [int.from_bytes(b[i:i+4], 'little') for i in range(0, 8, 4)]

    def to_bytes(words):
        return b''.join([w.to_bytes(4, 'little') for w in words])

    P = 0xB7E15163
    Q = 0x9E3779B9

    L = [int.from_bytes(key[i:i+4], 'little') for i in range(0, 16, 4)]
    S = [0] * (2*r + 2)
    S[0] = P
    for i in range(1, 2*r+2):
        S[i] = (S[i-1] + Q) & 0xFFFFFFFF

    A = B = i = j = 0
    n = max(len(L), len(S))
    for k in range(3*n):
        A = S[i] = ((S[i] + A + B) << 3 | (S[i] + A + B) >> (32-3)) & 0xFFFFFFFF
        B = L[j] = ((L[j] + A + B) << (A+B & 31) | (L[j] + A + B) >> (32-(A+B & 31))) & 0xFFFFFFFF
        i = (i+1) % len(S)
        j = (j+1) % len(L)

    A_word, B_word = to_words(block)
    A_word = (A_word + S[0]) & 0xFFFFFFFF
    B_word = (B_word + S[1]) & 0xFFFFFFFF

    for i in range(1, r+1):
        A_word = ((A_word ^ B_word) << (B_word & 31) | (A_word ^ B_word) >> (32-(B_word & 31))) & 0xFFFFFFFF
        A_word = (A_word + S[2*i]) & 0xFFFFFFFF
        B_word = ((B_word ^ A_word) << (A_word & 31) | (B_word ^ A_word) >> (32-(A_word & 31))) & 0xFFFFFFFF
        B_word = (B_word + S[2*i+1]) & 0xFFFFFFFF

    return to_bytes([A_word, B_word])

#функция хэширования
def rc5_hash(text):
    data = text.encode('utf-8')
    pad_len = (8 - len(data) % 8) % 8
    data += bytes([0]*pad_len)

    H = bytes([0]*8)

    for i in range(0, len(data), 8):
        block = data[i:i+8]
        key = H + H  # 16 байт
        encoded = RC5_encrypt(block, key)
        H = bytes([encoded[j] ^ block[j] for j in range(8)])

    return H.hex()

@app.route('/', methods=['GET', 'POST'])
def index():
    result = ''
    if request.method == 'POST':
        text = request.form['text']
        result = rc5_hash(text)
    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
