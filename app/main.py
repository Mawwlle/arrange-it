from datetime import datetime, timedelta

import asyncpg
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from loguru import logger
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_database() -> asyncpg.connection.Connection:
    return await asyncpg.connect(
        user="postgres", password="abc", database="postgres", host="127.0.0.1"
    )


class User(BaseModel):
    id: int
    nickname: str
    password: str
    email: str
    role: int = 1
    name: str
    age: int = 20
    info: str
    interests: str
    rank: int = 1
    rating: int = 0


class UserRepresentation(BaseModel):
    nickname: str
    email: str
    name: str
    age: int = 20
    info: str
    interests: str
    rating: int = 0


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserRepresentation:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise credentials_exception

        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = await get_user_db(username=token_data.username)

    if user is None:
        raise credentials_exception

    return UserRepresentation(
        nickname=user.nickname,
        email=user.email,
        name=user.name,
        age=user.age,
        info=user.info,
        interests=user.interests,
        rating=user.rating,
    )


async def get_password_hash(password) -> str:
    return pwd_context.hash(password)


async def get_user_db(username: str) -> User:
    conn = await get_database()
    record = await conn.fetchrow(
        'SELECT * FROM "user" WHERE nickname = $1',
        username,
    )

    try:
        user = User(**record)
    except (TypeError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found!"
        )

    return user


async def get_user_repr(username: str) -> UserRepresentation:
    conn = await get_database()
    record = await conn.fetchrow(
        'SELECT nickname, email, name, age, info, interests, rating FROM "user" WHERE nickname = $1',
        username,
    )

    try:
        user = UserRepresentation(**record)
    except (TypeError, ValidationError):
        logger.ERROR("Im here")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found!"
        )

    return user


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


async def set_user_in_db(user: User) -> bool:
    conn = await get_database()
    hashed_pass = await get_password_hash(user.password)

    await conn.execute(
        'INSERT INTO "user" VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)',
        user.id,
        user.nickname,
        hashed_pass,
        user.email,
        user.role,
        user.name,
        user.age,
        user.info,
        user.interests,
        user.rank,
        user.rating,
    )
    return True


@app.get("/user")
async def user(
    username: str, current_user: str = Depends(get_current_user)
) -> UserRepresentation:
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return await get_user_repr(username)


class Token(BaseModel):
    access_token: str
    token_type: str


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def get_user_list():
    conn = await get_database()
    record = await conn.fetch(
        'SELECT nickname, email, name, age, info, interests, rating FROM "user"'
    )

    return list(record)


@app.get("/user_list")
async def get_list(current_user: str = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return await get_user_list()


class TokenData(BaseModel):
    username: str | None = None


async def create_access_token(
    data: dict, expires_delta: timedelta | None = None
) -> str:
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


async def authenticate_user(username: str, password: str) -> bool | UserRepresentation:
    user = await get_user_db(username)

    if not user:
        return False

    if not await verify_password(password, user.password):
        return False

    return UserRepresentation(
        nickname=user.nickname,
        email=user.email,
        name=user.name,
        age=user.age,
        info=user.info,
        interests=user.interests,
        rating=user.rating,
    )


@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data={"sub": user.nickname}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/role")
async def create_role(role: str, current_user: str = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    conn = await get_database()
    await conn.execute('INSERT INTO "role"(name) VALUES ($1)', role)


@app.post("/rank")
async def create_rank(rank: str, current_user: str = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    conn = await get_database()
    await conn.execute('INSERT INTO "rank"(designation) VALUES ($1)', rank)
