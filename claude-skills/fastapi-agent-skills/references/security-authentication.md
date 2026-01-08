# Security & Authentication

This guide covers OAuth2 password flow, JWT tokens, API keys, and CORS configuration.

## OAuth2 Password Flow

Implement token issuance using the OAuth2 password grant.

### Token Endpoint Implementation
Use `OAuth2PasswordRequestForm` to capture credentials and return a token:
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

@app.post("/token")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    if form.username != "expected_user" or form.password != "expected_password":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid credentials"
        )
    return {"access_token": "your_secure_token", "token_type": "bearer"}
```

## JWT Tokens

Issue and validate JSON Web Tokens (JWT) for stateless authentication.

### Token Issuance and Verification
Use a library like `PyJWT` to manage tokens:
```python
import jwt
from datetime import datetime, timedelta

SECRET = "your-secret-key"
ALGO = "HS256"

def issue_token(sub: str) -> str:
    now = datetime.utcnow()
    payload = {"sub": sub, "iat": now, "exp": now + timedelta(minutes=30)}
    return jwt.encode(payload, SECRET, algorithm=ALGO)

def verify_token(token: str) -> dict:
    return jwt.decode(token, SECRET, algorithms=[ALGO])
```

### Authentication Dependency
Protect routes by injecting the current user from the token:
```python
async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        data = verify_token(token)
        return {"sub": data["sub"]}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid token"
        )

@app.get("/me")
async def read_me(current_user: dict = Depends(get_current_user)):
    return current_user
```

## API Key Authentication

Protect endpoints using keys passed in headers, suitable for service-to-service calls.

### API Key Header
Parse keys from headers like `X-API-Key`:
```python
from fastapi import Header

async def require_api_key(x_api_key: str = Header(...)):
    if x_api_key != "your_valid_key":
        raise HTTPException(status_code=403, detail="Forbidden")
    return x_api_key
```

## CORS Configuration

Enable secure cross-origin requests from browser clients.

### CORS Middleware
Add `CORSMiddleware` with specific allowed origins:
```python
from starlette.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

## Critical Considerations
- Prefer federated identity (OIDC) for production over simple password flows.
- Always hash and salt passwords stored in your database.
- Rotate JWT secrets regularly and keep payloads minimal.
- Avoid using wildcard `*` for CORS origins when credentials are required.

## Integration with LLM Agents
- Provide helper functions for token lifecycle management (`issue`, `verify`).
- Show how to use `Depends` to secure route handlers.
- Document expected header names for API keys and auth tokens.
