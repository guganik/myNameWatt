from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def idle():
  return render_template('idle.html')

@app.route('/success/<name>')
def success(name):
  return render_template('success.html', name=name)

@app.route('/login', methods = ['POST', 'GET'])
def get_username():
  if request.method == 'POST':
    with open('./data/usernames.txt', 'r+', encoding='utf-8') as file:
      data = file.read()
      user = request.form['name']
      if user not in data.split('\n'):
        file.write(user + '\n')
    return redirect(url_for('success', name=user))
  else:
    user = request.args.get('name')
    return redirect(url_for('success', name=user))

if __name__ == '__main__':
  app.run(debug=True)