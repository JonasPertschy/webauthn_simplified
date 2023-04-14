### Settings ################################
registration_possible       = False # Set to True to allow registration
require_user_verification   = True # Set to True to require strong user verification
rp_id                       = "localhost" # Set to your domain name
rp_name                     = "WebAuthn Demo" # Set to your domain name
user_name                   = "Jonas" # Set to your name
user_id                     = "1" # Set to your user id
expected_origin             = "http://localhost:8085" # Set to your domain name
#############################################

from flask import Flask, send_from_directory, request, jsonify, session
import json
from flask_session import Session
from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
    options_to_json,
    base64url_to_bytes,
)
from webauthn.helpers import bytes_to_base64url
from webauthn.helpers.cose import COSEAlgorithmIdentifier
from webauthn.helpers.structs import (
    RegistrationCredential,
    AuthenticationCredential,
)

app = Flask(__name__)
SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)

@app.route("/")
def hello():
    return send_from_directory('.', 'index.html')

@app.route("/simplewebauthn.js")
def simplewebauthn():
    return send_from_directory('.', 'simplewebauthn.js')
@app.route("/style.css")
def css():
    return send_from_directory('.', 'style.css')

@app.route("/get-config")
def configuration():
    return jsonify({'registrationPossible': registration_possible})

@app.route("/generate-registration-options")
def generate_registration():
    if registration_possible == False:
        return jsonify({"error": "Registration not allowed"})
    options = generate_registration_options(
        rp_id=rp_id,
        user_name=user_name,
        rp_name=rp_name,
        user_id=user_id,
    )
    session['challenge'] = options.challenge
    return options_to_json(options)
 
@app.route("/verify-registration", methods=["POST"])
def verify_registration():
    if registration_possible == False:
        return jsonify({"error": "Registration not allowed"})
    try:
        registration_verification = verify_registration_response(
            credential=RegistrationCredential.parse_raw(json.dumps(request.get_json())),
            expected_challenge=session.get('challenge'),
            expected_origin=expected_origin,
            expected_rp_id=rp_id,
            require_user_verification=require_user_verification,
        )
        # Write the credential public key to a file "authorized_keyfile" to a new line
        with open("authorized_keyfile", "a") as f:
            f.write(bytes_to_base64url(registration_verification.credential_public_key)+"\n")
        print (registration_verification.json(indent=2))
        return jsonify({"verified": True})
    except Exception as e:
        print("ERROR: ", e)
        return jsonify({"error": str(e)})

@app.route("/generate-authentication-options")
def generate_authentication():
    options = generate_authentication_options(
        rp_id="localhost",
    )
    session['challenge'] = options.challenge
    return options_to_json(options)

@app.route("/verify-authentication", methods=["POST"])
def verify_authentication():
    try:
        with open("authorized_keyfile", "r") as f:
            for line in f.readlines():
                 print(line)
                 try:
                    credential_public_key = base64url_to_bytes(line)
                    authentication_verification = verify_authentication_response(
                        credential=AuthenticationCredential.parse_raw(json.dumps(request.get_json())),
                        expected_challenge=session.get('challenge'),
                        expected_origin=expected_origin,
                        expected_rp_id=rp_id,
                        require_user_verification=require_user_verification,
                        credential_public_key=credential_public_key,
                        credential_current_sign_count=0,
                    )
                 except:
                    print("Key not valid, try next one")
        print (authentication_verification.json(indent=2)) # Don't delete this line, it's needed for the verification
        return jsonify({"verified": True})
    except Exception as e:
        print("ERROR: ", e)
        return jsonify({"error": "Not registered"})

# Change the server name for security reasons
@app.after_request
def changeserver(response):
    response.headers['server'] = "Apache"
    return response

if __name__ == '__main__':
    app.run(host="localhost", port=8085)
