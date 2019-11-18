import random
import string
from flask import Flask

app = Flask(__name__)

def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    return randomString()


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
