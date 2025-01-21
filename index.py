from flask import Flask, render_template, request, redirect, url_for, g, jsonify
import os
import requests
from flask import send_from_directory

app = Flask(__name__)

@app.route('/')
def whats_your_name():
  if 'lang' not in globals():
    global lang
    lang = request.accept_languages.best_match(['ru', 'en'])
  return render_template(f'{lang}/wyn.html', lang=lang)

@app.route('/<lang>/login', methods = ['POST', 'GET'])
def get_username(lang):
  if request.method == 'POST':
    user = request.form['name'].strip()
    return redirect(url_for('itsyrnm', name=user, lang=lang))
  else:
    user = request.args.get('name')
    return redirect(url_for('itsyrnm', name=user, lang=lang))
  
@app.route('/<lang>/itsyrnm/<name>')
def itsyrnm(lang, name):
  return render_template(f'{lang}/itsyrnm/idle.html', name=name, lang=lang)

@app.route('/<lang>/itsyrnm/<name>/answer', methods = ['POST', 'GET'])
def itsyrnm_answer(lang, name):
  if request.method == 'POST':
    answer = request.form['answer'].strip().lower()
    print(answer)
    if answer == 'да!' or answer == 'yeah!':
      return render_template(f'{lang}/itsyrnm/yes.html', lang=lang, name=name)
    else:
      return render_template(f'{lang}/itsyrnm/no.html', lang=lang, name=name)
  else:
    return redirect(url_for('itsyrnm', name=name, lang=lang))
  
@app.route('/<lang>/time/<name>', methods = ['POST'])
def time_answer(lang, name):
  data = request.get_json()
  time = data.get('value')

  if time:
    return jsonify({'redirect_url': f'/{lang}/love/{name}/{time}'})
  return jsonify({'error': 'Некорректные данные'}), 400

@app.route('/<lang>/love/<name>/<time>')
def love(lang, name, time):
  time = int(time)
  hours = time // 3600
  minutes = (time - hours * 3600) // 60
  return render_template(f'{lang}/loveint.html', lang=lang, name=name, time=f'{hours:02d}:{minutes:02d}')

@app.route('/<lang>/love/<name>/<time>/select-int', methods=['POST'])
def select_int(lang, name, time):
  selint = request.form['love-int']
  if selint.isdigit():
    return render_template(f'{lang}/love_int/isdigit.html', lang=lang, name=name, time=time, selint=selint)
  return render_template(f'{lang}/love_int/isnotdigit.html', lang=lang, name=name, time=time, selint=selint)

@app.route('/<lang>/<name>/<time>/<selint>/success', methods=['POST'])
def success(lang, name, time, selint):
  get_ip = request.form['get-ip'].strip().lower()
  if get_ip == 'разрешить' or 'allow':
    user_ip = request.headers.get('X-Forwarded-For')
    if user_ip:
      user_ip = user_ip.split(',')[0]
    else:
      user_ip = request.remote_addr
    response = requests.get(f'http://ip-api.com/json/{user_ip}')
    data = response.json()
    country = data.get('country', 'unknown')
    del user_ip
    userdata = f'{name}, lang: {lang}, time: {time}, number: {selint}, country: {country}'
    file = open('./data/userdata.txt', 'r', encoding='utf-8')
    olddata = file.read()

    file = open('./data/userdata.txt', 'w', encoding='utf-8')
    newdata = olddata + f'{userdata}\n'
    file.write(newdata)

    return render_template(f'{lang}/success.html', lang=lang, name=name, time=time, selint=selint, country=country)
  else:
    userdata = f'{name}, lang: {lang}, time: {time}, number: {selint}, country: Unknown'
    file = open('./data/userdata.txt', 'r', encoding='utf-8')
    olddata = file.read()

    file = open('./data/userdata.txt', 'w', encoding='utf-8')
    newdata = olddata + f'{userdata}\n'
    file.write(newdata)
    return render_template(f'{lang}/go_out.html', lang=lang, name=name, time=time, selint=selint)

@app.errorhandler(Exception)
def page_not_found(e):
  if 'lang' not in globals():
    global lang
    lang = request.accept_languages.best_match(['ru', 'en'])
  try:
    return render_template(f'{lang}/errors/{e.code}.html', lang=lang), e.code
  except:
    return render_template(f'{lang}/errors/500.html', lang=lang), 500

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                          'favicon.ico',mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
  app.run(debug=True)