import os

os.environ["JWT_SECRET_KEY"] = (
    "testonly_secret_key-for-appointments-123445555@#"
)

os.environ["JWT-ALGORITHMS"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"