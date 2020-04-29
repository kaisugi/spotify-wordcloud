from flask import Flask, request, send_file, Response
from wordcloud import WordCloud
import hashlib


app = Flask(__name__)

@app.route('/generate')
def generate():
    try:
        text = request.args.get('text', '')
        ha = hashlib.md5(text.encode('utf-8')).hexdigest()

        wc = WordCloud(font_path='/app/.fonts/ipaexg.ttf', width=1024, height=576, colormap='summer').generate(text)
        image = wc.to_image()
        image.save(f"{ha}.png", format='png', optimize=True)

        return send_file(f"{ha}.png", mimetype='image/png')

    except Exception as e:
        print(e)
        return Response(status=400)


if __name__ == '__main__':
    app.run()