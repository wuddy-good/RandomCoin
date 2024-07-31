from datetime import datetime, date
from flask import Flask, request, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from random import randint


def format_coins(coins):
    return "{:,}".format(coins)


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:artatrq123@localhost/random_coin"

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    username = db.Column(db.String(50), unique=True)
    photo_url = db.Column(db.String(255))
    is_premium = db.Column(db.Boolean, default=False)
    coins = db.Column(db.Integer, default=0)
    already_invited_someone = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class Referral(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.id'))
    code = db.Column(db.BigInteger)
    reward_given = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class Transactions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.id'))
    amount = db.Column(db.BigInteger)
    type = db.Column(db.String(50), default="Daily Reward")  # NOTE: Invited Friends as second option
    created_at = db.Column(db.DateTime, server_default=db.func.now())


@app.route('/')
def index():
    return "Telegram mini app is running."


@app.route('/user')
def user_profile():
    try:
        user_id = int(request.args.get('id'))
    except (ValueError, TypeError):
        return "Invalid user ID", 400

    photo_url = request.args.get('photo_url')

    data = {
        'id': user_id,
        'first_name': request.args.get('first_name'),
        'last_name': request.args.get('last_name'),
        'username': request.args.get('username'),
        'photo_url': photo_url,
        'is_premium': request.args.get('is_premium') == 'True',
        'referral_code': request.args.get('referral_code')
    }

    user = User.query.filter_by(id=data['id']).first()

    if user is None:
        user = User(id=data['id'], first_name=data['first_name'], last_name=data['last_name'],
                    username=data['username'], photo_url=data['photo_url'], is_premium=data['is_premium'])
        db.session.add(user)
        db.session.commit()
    else:
        if data['photo_url'] is not None and data['photo_url'] != user.photo_url:
            user.photo_url = data['photo_url']
            db.session.commit()
        if data['is_premium'] is not None and data['is_premium'] != user.is_premium:
            user.is_premium = data['is_premium']
            db.session.commit()

    if data['referral_code'] and data['referral_code'] != 'None':
        existing_referral = Referral.query.filter_by(user_id=user.id, code=data['referral_code']).first()

        if not existing_referral:
            referrer_user = User.query.filter_by(id=data['referral_code']).first()
            if referrer_user:
                referral = Referral(user_id=user.id, code=data['referral_code'])
                db.session.add(referral)
                db.session.commit()

    data['id'] = user.id
    data['first_name'] = user.first_name
    data['last_name'] = user.last_name
    data['username'] = user.username
    data['referral_code'] = Referral.query.filter_by(user_id=user.id).first().code if Referral.query.filter_by(
        user_id=user.id).first() else 'Not found'
    data['is_premium'] = user.is_premium
    data['photo_url'] = user.photo_url
    data['coins'] = format_coins(user.coins)

    transactions = Transactions.query.filter_by(user_id=user.id).order_by(Transactions.created_at.desc())

    return render_template('profile.html', user=data, active_tab='home', transactions=transactions)


@app.route('/leaderboard')
def leaderboard():
    leaderboard = User.query.order_by(User.coins.desc()).all()
    user = User.query.filter_by(id=request.args.get('id')).first()
    user_place_in_leaderboard = leaderboard.index(user) + 1 if user in leaderboard else None
    holders_count = len(leaderboard)
    return render_template('leaderboard.html', user=user, active_tab='leaderboard', leaderboard=leaderboard,
                           user_place_in_leaderboard=user_place_in_leaderboard, holders_count=holders_count)


@app.route('/friends')
def friends():
    try:
        user_id = int(request.args.get('id'))
    except (ValueError, TypeError):
        return "Invalid user ID", 400

    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return "User not found", 404

    # Get referrals where the user is the referrer (i.e., user is the inviter)
    referrals = Referral.query.filter_by(code=user_id).all()

    referrers_raw = Referral.query.filter_by(user_id=user_id).first()
    referrer = User.query.filter_by(id=referrers_raw.code).first() if referrers_raw else None

    friends = []
    for referral in referrals:
        friend = User.query.filter_by(id=referral.user_id).first()
        if friend and friend != user and friend.coins is not None:
            friends.append(friend)
        else:
            print(f"User with ID {referral.user_id} not found or has no coins")

    if referrer and referrer != user:
        friends.append(referrer)

    for i in friends:
        print(i)
        print(i.username)
        print(i.coins)

    friends_count = len(friends)

    return render_template('friends.html', user=user, friends_count=friends_count, friends=friends,
                           active_tab='friends')


@app.route('/claim_daily_reward')
def claim_daily_reward():
    user_id = request.args.get('user_id')

    # Вызываем функцию для выдачи ежедневной награды
    result = give_daily_reward(user_id)

    user = User.query.filter_by(id=user_id).first()
    if user is None or result is False:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    return jsonify({'success': result, 'coins': format_coins(user.coins), 'new_amount': format_coins(result)}), 200


def give_daily_reward(user_id):
    # Get the start and end of the current day
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_end = datetime.combine(date.today(), datetime.max.time())

    # Check if there are any transactions for the user today
    existing_transaction = Transactions.query.filter(
        Transactions.user_id == user_id,
        Transactions.created_at >= today_start,
        Transactions.created_at <= today_end
    ).first()

    if existing_transaction:
        return False

    # If no transaction exists, proceed to give coins
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return "User not found", 404

    amount = randint(1000, 20000)
    user.coins += amount
    db.session.commit()

    # Record the transaction
    transaction = Transactions(user_id=user_id, amount=amount)
    db.session.add(transaction)
    db.session.commit()

    # Process referral rewards
    process_referral_rewards(user_id, amount)

    return amount


def process_referral_rewards(user_id, amount):
    # Find the referral of the user
    referral = Referral.query.filter_by(user_id=user_id).first()

    if referral:
        referrer = User.query.filter_by(id=referral.code).first()
        if referrer:
            # Check if reward has been given before
            if not referral.reward_given:
                referrer.coins += amount
                referrer.already_invited_someone = True
                referral.reward_given = True
                db.session.commit()

                # Record the transaction for referrer
                transaction = Transactions(user_id=referrer.id, amount=amount, type="Referral Reward")
                db.session.add(transaction)
                db.session.commit()
            elif referral.reward_given:
                # Reward referrer with 10% of the new daily reward
                reward = int(amount * 0.1)
                referrer.already_invited_someone = True
                referrer.coins += reward
                referral.reward_given = True
                db.session.commit()

                print(referrer.coins)
                print(referrer.already_invited_someone)

                # Record the transaction for referrer
                transaction = Transactions(user_id=referrer.id, amount=reward, type="Referral Reward")
                db.session.add(transaction)
                db.session.commit()


if __name__ == '__main__':
    app.run(port=5000)
