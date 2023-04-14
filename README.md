# Simple Webauthn Server based on Flask, py_webauthn and simplewebauthn.js

This is a wsgi server that acts similar to a reverse proxy that requires authentication (e.g., nginx with mtls or nginx with 
oauth2-proxy). 

This is a minimal implementation of py_webauthn in flask with simplewebauthn.js to handle the interaction with the browser API. Tested with Chrome & Safari.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python3 server.py
```

## Configuration
Edit the `server.py` file to configure the server.

```python
registration_possible       = False # Set to True to allow registration
require_user_verification   = True # Set to True to require strong user verification
rp_id                       = "localhost" # Set to your domain name
rp_name                     = "WebAuthn Demo" # Set to your domain name
user_name                   = "Jonas" # Set to your name
user_id                     = "1" # Set to your user id
expected_origin             = "http://localhost:8085" # Set to your
```

## License
[MIT](https://choosealicense.com/licenses/mit/)
