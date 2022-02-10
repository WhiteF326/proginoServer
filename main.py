from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from fastapi.responses import PlainTextResponse

import markdown

app = FastAPI()

session = {}

md = markdown.Markdown()


# main page
@app.get("/", response_class=HTMLResponse, status_code=200)
async def root():
    f = open("./static/front.html", "r", encoding="utf-8")
    return f.read()

# course page
@app.get("/course/{courseName}", response_class=HTMLResponse, status_code=200)
async def course(courseName: str):
    f = open("./static/course.html", "r", encoding="utf-8")
    session["courseName"] = courseName
    return f.read()

# get courses info
@app.get("/courses", response_class=JSONResponse, status_code=200)
async def getProblems():
    f = open("./problems/meta.json", "r", encoding="utf-8")
    return "".join(f.readlines())

# get problems info
@app.get("/problem/{problemId}", response_class=HTMLResponse, status_code=200)
async def getProblem(problemId: str):
    f = open("./static/problems.html", "r", encoding="utf-8")
    session["problemId"] = problemId
    return "".join(f.readlines())

# get course info that accessed
@app.get("/accessed/course", response_class=PlainTextResponse, status_code=200)
async def getAccessed():
    if "courseName" in session:
        return session["courseName"]
    else:
        return "null"

# get problem info that accessed
@app.get("/accessed/problem", response_class=PlainTextResponse, status_code=200)
async def getAccessed():
    if "problemId" in session:
        return session["problemId"]
    else:
        return "null"

# get problem info from id
@app.get("/problem/{problemId}/raw", response_class=JSONResponse, status_code=200)
async def getProblem(problemId: str):
    f = open("./problems/" + problemId + "/" + problemId + ".json", "r", encoding="utf-8")
    return "".join(f.readlines())

# get problems body
@app.get("/problem/{problemId}/body", response_class=PlainTextResponse, status_code=200)
async def getProblemBody(problemId: str):
    f = open("./problems/" + problemId + "/problem.md", "r", encoding="utf-8")
    return md.convert("".join(f.readlines()))

# get user's progress
@app.get("/progress", response_class=JSONResponse, status_code=200)
async def getProgress():
    f = open("./status/status.json", "r", encoding="utf-8")
    return "".join(f.readlines())
