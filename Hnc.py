from flask import Flask, render_template, request, redirect, url_for
import time

app = Flask(__name__)

# Kullanıcı verileri
users = {}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        if username and username not in users:
            users[username] = {
                'points': 0,
                'farming_active': False,
                'farming_start_time': None,
                'last_reward_day': None,
                'consecutive_days': 0
            }
            return redirect(url_for('main_page', username=username))
        elif username in users:
            return redirect(url_for('main_page', username=username))
    return render_template('index.html')

@app.route('/main/<username>')
def main_page(username):
    user_data = users.get(username)
    return render_template('main.html', username=username, points=user_data['points'])

@app.route('/tasks/<username>')
def tasks_page(username):
    user_data = users.get(username)
    return render_template('tasks.html', username=username)

@app.route('/leaderboard')
def leaderboard_page():
    sorted_users = sorted(users.items(), key=lambda x: x[1]['points'], reverse=True)
    return render_template('leaderboard.html', users=sorted_users)

@app.route('/start_farming/<username>')
def start_farming(username):
    user_data = users.get(username)
    if not user_data['farming_active']:
        user_data['farming_active'] = True
        user_data['farming_start_time'] = time.time()
    return redirect(url_for('main_page', username=username))

@app.route('/update/<username>')
def update(username):
    user_data = users.get(username)

    # Günlük ödül sistemi
    current_day = int(time.time() // (24 * 3600))  # Gün sayısını al
    if user_data['last_reward_day'] is None:
        user_data['last_reward_day'] = current_day
        user_data['consecutive_days'] = 1
        reward_user(user_data)
    elif current_day > user_data['last_reward_day']:
        if current_day - user_data['last_reward_day'] == 1:
            user_data['consecutive_days'] += 1
        else:
            user_data['consecutive_days'] = 1  # Gün kaçırıldıysa sıfırla
        user_data['last_reward_day'] = current_day
        reward_user(user_data)

    if user_data['farming_active']:
        elapsed_time = time.time() - user_data['farming_start_time']
        if elapsed_time >= 14400:  # 4 saat = 14400 saniye
            user_data['points'] += 44  # Farming ile kazanılan puan
            user_data['farming_active'] = False  # Farming süresi sona erdi
            user_data['farming_start_time'] = None  # Zamanı sıfırla

    return redirect(url_for('main_page', username=username))

def reward_user(user_data):
    # Günlük ödül miktarını belirle
    day = user_data['consecutive_days']
    if day in (1, 2):
        user_data['points'] += 10  # 1. ve 2. gün ödülü
    elif day in (3, 4):
        user_data['points'] += 30  # 3. ve 4. gün ödülü
    elif day in (5, 6):
        user_data['points'] += 60  # 5. ve 6. gün ödülü
    elif day == 7:
        user_data['points'] += 100  # 7. gün ödülü
        user_data['consecutive_days'] = 0  # 7. günden sonra sıfırla

if __name__ == '__main__':
    app.run(debug=True)
