from flask import Flask, render_template, url_for, session, logging, request, flash, redirect, flash, send_file
from random import randint 
from create import create_app
from qr_code import qrgen
import stripe
from authlib.integrations.flask_client import OAuth


app , stripe_keys = create_app()
#app.config['SERVER_NAME'] = 'rowida:5000'

stripe.api_key = stripe_keys['secret_key']
oauth = OAuth(app)

@app.route('/')
def home():
	return render_template("plans.html")


@app.route("/generate_qr_code")
def qr_code():
	tmp = str(randint(1,12))  # till now, later we'll make as a mix of username +id or rand num
	qrgen(tmp)
	filename = tmp +'.png'
	return send_file(filename,as_attachment=True)


@app.route('/google/')
def google():
    GOOGLE_CLIENT_ID = '555683154426-r0r89o5dr9l43iqskkbtl2aotstf1hkn.apps.googleusercontent.com'
    GOOGLE_CLIENT_SECRET = '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'

    CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
    oauth.register(
        name='google',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url=CONF_URL,
        client_kwargs={
            'scope': 'openid email profile'
        }
    )
    google = oauth.create_client('google')  # create the google oauth client
    redirect_uri = url_for('google_auth', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/google/auth/')
def google_auth():
    google = oauth.create_client('google')  
    token = oauth.google.authorize_access_token() 
    resp = token['userinfo'] 
    user_info = dict(resp)
    user = oauth.google.userinfo()  
    session['profile'] = user_info
    email = dict(session)['profile']['email']
    """Search for a user by email
    1- user found :: redirect to the main or whatever...
    2- redirect to the sign up 
    """
    ## if not session.logged_in :
    session.permanent = True 
    id = session.get("id")
    return redirect(f"/signup/{ id }")

@app.route("/signup/", defaults={'id': 1})
@app.route('/signup/<id>', methods = ['GET', 'POST'])
def register(id):
    session['id'] = id
    if 'profile' in dict(session):# outocompelete
        email = dict(session)['profile']['email']
        lst = dict(session)['profile']['name'].split()
        return render_template("signup.html", email = email , first =lst[0], last = lst[1])
    return render_template('signup.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    #db..
	return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    flash("You are loged out")
    return redirect(url_for('/'))

@app.route('/add_member', methods = ['GET', 'POST'])
def addmember():
    #db...
	return render_template("add_member.html")


@app.route("/payment_getaway")
def create_checkout_session(): #not yet
    checkout_session = stripe.checkout.Session.create(
        line_items=[
                {
                    "price": '250' ,
                    "quantity" : 1
                }
            ],
            payment_method_types = ['card'],
            mode = 'payment',
            success_url=request.host_url + 'payment_getaway/success',
            cancel_url=request.host_url + 'payment_getaway/cancel',
        )
        

if __name__ == '__main__':
	app.run()