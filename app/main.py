from fastapi import FastAPI

app = FastAPI()


@app.get("/hello")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}
