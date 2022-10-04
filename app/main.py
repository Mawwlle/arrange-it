from fastapi import FastAPI
import pkg_resources

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/version")
async def version():
    return pkg_resources.get_distribution('arrange-it').version
