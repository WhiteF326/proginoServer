import hashlib
import subprocess
from datetime import datetime
from glob import glob
import os
import uuid
from threading import Timer
from typing import Dict
from typing import Optional
from fastapi import BackgroundTasks, FastAPI
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from fastapi.responses import PlainTextResponse

import json

import markdown
from pydantic import BaseModel

app = FastAPI()

session = {}

md = markdown.Markdown()

class Submit(BaseModel):
    language: str
    code: str
    problem: str

class JudgeInfo():
    language: str
    problem: str
    submissionId: str
    testcaseNo: int
    testcaseName: str
    status: str
    memory: str
    process: subprocess.Popen
    runCommand: list[str]
    time: int
    timer: Timer
    UUID: str
    output: str
    error: str

class JudgeJob():
    UUID: str
    def __init__(self, UUID: str):
        self.UUID = UUID
    def __call__(self):
        # make process
        jobs[self.UUID].process = subprocess.run(
            jobs[self.UUID].runCommand,
            capture_output=True,
            text=True,
            stdin=open("./problems/" + jobs[self.UUID].problem + "/" + jobs[self.UUID].testcaseName["input"], "r", encoding="utf-8"),
        )
        # get status code
        statusCode = jobs[self.UUID].process.returncode
        if statusCode == 0:
            jobs[self.UUID].output = jobs[self.UUID].process.stdout
            jobs[self.UUID].error = jobs[self.UUID].process.stderr
            
            outputFile = open("./problems/" + jobs[self.UUID].problem + "/" + jobs[self.UUID].testcaseName["output"], "r", encoding="utf-8")
            if jobs[self.UUID].output == outputFile.read():
                jobs[self.UUID].status = "AC"
            else:
                jobs[self.UUID].status = "WA"
        else:
            jobs[self.UUID].status = "RE"

jobs: Dict[str, JudgeInfo] = {}

class User(BaseModel):
    username: Optional[str]
    password: Optional[str]
    salt: Optional[str]
    email: Optional[str]


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

# get submission page
@app.get(
    "/submission/{submissionId}",
    response_class=HTMLResponse,
    status_code=200
)
async def getSubmission(submissionId: str):
    f = open("./static/submission.html", "r", encoding="utf-8")
    session["submissionId"] = submissionId
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

# get submission info that accessed
@app.get(
    "/accessed/submission",
    response_class=PlainTextResponse,
    status_code=200
)
async def getAccessed():
    if "submissionId" in session:
        return session["submissionId"]
    else:
        return "null"

# get languages list
@app.get("/languages", response_class=JSONResponse, status_code=200)
async def getLanguages():
    f = open("./preferences/languages.json", "r", encoding="utf-8")
    return "".join(f.readlines())

# get problem info from id
@app.get(
    "/problem/{problemId}/raw",
    response_class=JSONResponse,
    status_code=200
)
async def getProblem(problemId: str):
    f = open("./problems/" + problemId + "/" + problemId + ".json", "r", encoding="utf-8")
    return "".join(f.readlines())

# get problems body
@app.get(
    "/problem/{problemId}/body",
    response_class=PlainTextResponse,
    status_code=200
)
async def getProblemBody(problemId: str):
    f = open("./problems/" + problemId + "/problem.md", "r", encoding="utf-8")
    return md.convert("".join(f.readlines()))

# get user's progress
@app.get("/progress", response_class=JSONResponse, status_code=200)
async def getProgress():
    f = open("./status/status.json", "r", encoding="utf-8")
    return "".join(f.readlines())

# submit code
@app.post("/submit", response_class=PlainTextResponse, status_code=200)
async def submit(submit: Submit):
    f = open("./submissions/submissions.json", "r", encoding="utf-8")
    # parse f as json
    submissions = json.loads("".join(f.readlines()))
    f.close()
    submissionId = len(submissions) + 1
    submissions[str(submissionId)] = {
        "language": submit.language,
        "code": submit.code,
        "problem": submit.problem,
        "verdict": "WJ",
        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "progress": "0",
        "judge": "judge"
    }
    f = open("./submissions/submissions.json", "w", encoding="utf-8")
    f.write(json.dumps(submissions))
    f.close()
    return str(submissionId)

# get submission info
@app.get(
    "/submission/{submissionId}/full",
    response_class=JSONResponse,
    status_code=200
)
async def getSubmission(submissionId: str):
    f = open("./submissions/submissions.json", "r", encoding="utf-8")
    # parse f as json
    submissions = json.loads("".join(f.readlines()))
    f.close()
    if submissionId in submissions:
        return submissions[submissionId]
    else:
        return "null"

# get full problems list
@app.get("/problems/list", response_class=JSONResponse, status_code=200)
async def getProblems():
    f = glob("./problems/*/*.json")
    problems = {}
    for problem in f:
        f = open(problem, "r", encoding="utf-8")
        problems[os.path.basename(problem).split(".")[0]] = json.loads(
            "".join(f.readlines())
        )
    return problems

# proceed judge
@app.get(
    "/judge/{submissionId}",
    response_class=JSONResponse,
    status_code=200
)
async def judge(submissionId: str, backgroundTasks: BackgroundTasks):
    f = open("./submissions/submissions.json", "r", encoding="utf-8")
    # parse f as json
    submissions = json.loads("".join(f.readlines()))
    f.close()
    # get submission info
    submission = submissions[submissionId]
    if submission["judge"] == "judge":
        # get problem info
        problem = json.loads(
            "".join(
                open("./problems/" + submission["problem"] + "/" + submission["problem"] + ".json", "r", encoding="utf-8")
                .readlines()
            )
        )
        # get language info
        language = json.loads(
            "".join(
                open("./preferences/languages.json", "r", encoding="utf-8")
            )
        )[submission["language"]]
        # make code file
        os.makedirs("./submissions/" + submissionId, exist_ok=True)
        f = open("./submissions/" + submissionId + "/Main." + language["extension"], "w", encoding="utf-8")
        f.write(submission["code"])
        f.close()

        # make judge info
        judgeUUIDs = []
        for testNo in range(len(problem["testcases"])):
            judgeInfo = JudgeInfo()
            judgeInfo.language = submission["language"]
            judgeInfo.memory = problem["limits"]["memory"]
            judgeInfo.time = problem["limits"]["time"]
            judgeInfo.timer = None
            judgeInfo.problem = submission["problem"]
            judgeInfo.status = "WJ"
            judgeInfo.testcaseNo = testNo
            judgeInfo.testcaseName = problem["testcases"][testNo]
            judgeInfo.submissionId = submissionId
            runCommand = [
                elm if elm != 0
                else "./submissions/" + submissionId + "/Main." + language["extension"]
                    for elm in language["command"]
            ]
            judgeInfo.runCommand = runCommand
            judgeInfo.process = None
            # generate uuid4
            judgeUUID = str(uuid.uuid4())
            judgeUUIDs.append(judgeUUID)
            judgeInfo.UUID = judgeUUID
            judgeInfo.output = ""
            judgeInfo.error = ""
            jobs[judgeUUID] = judgeInfo
            # add background task to judge
            backgroundTasks.add_task(
                # judgeProcess(judgeInfo)
                JudgeJob(UUID=judgeUUID)
            )
        submission["judge"] = "wait"
        submission["judgeUUIDs"] = judgeUUIDs
        f = open("./submissions/submissions.json", "w", encoding="utf-8")
        submissions[submissionId] = submission
        f.write(json.dumps(submissions))
        f.close()
        return json.dumps(
            {
                "status": "WJ",
                "doneTestCount": 0,
                "totalTestCount": len(problem["testcases"]),
            }
        )
    elif submission["judge"] == "wait":
        judges = []
        for judgeUUID in submission["judgeUUIDs"]:
            if judgeUUID in jobs:
                judges.append(jobs[judgeUUID].status)
            else:
                judges.append("IE")
        # if there is any judge such that has a verdict of "WJ", return "WJ"
        if "WJ" in judges:
            doneTestCount = len(judges) - judges.count("WJ")
            return json.dumps(
                {
                    "status": "WJ",
                    "doneTestCount": doneTestCount,
                    "totalTestCount": len(judges)
                }
            )
        # if there is any judge such that has a verdict of "RJ", return "RJ"
        elif "RJ" in judges:
            result = "RJ"
        else:
            # set judge status as "end"
            submission["judge"] = "end"
            f = open("./submissions/submissions.json", "w", encoding="utf-8")
            result = ""
            # if there is any judge such that has a verdict of "WA", return "WA"
            if "WA" in judges:
                result = "WA"
            # if there is any judge such that has a verdict of "IE", return "IE"
            elif "IE" in judges:
                result = "IE"
            # if there is any judge such that has a verdict of "RE", return "RE"
            elif "RE" in judges:
                result = "RE"
            # if there is any judge such that has a verdict of "TLE", return "TLE"
            elif "TLE" in judges:
                result = "TLE"
            # if there is any judge such that has a verdict of "MLE", return "MLE"
            elif "MLE" in judges:
                result = "MLE"
            # if there is any judge such that has a verdict of "OLE", return "OLE"
            elif "OLE" in judges:
                result = "OLE"
            # if there is any judge such that has a verdict of "CE", return "CE"
            elif "CE" in judges:
                result = "CE"
            # if there is any judge such that has a verdict of "AC", return "AC"
            elif "AC" in judges:
                result = "AC"
                # update user's status
                user = json.loads(
                    "".join(
                        open("./status/status.json", "r", encoding="utf-8")
                        .readlines()
                    )
                )
                # get course info
                course = json.loads(
                    "".join(
                        open("./problems/meta.json", "r", encoding="utf-8")
                        .readlines()
                    )
                )
                course = [elm["course"] for elm in course if int(submission["problem"]) in elm["problems"]][0]
                if not int(submission["problem"]) in user[course]:
                    user[course].append(int(submission["problem"]))
                g = open("./status/status.json", "w", encoding="utf-8")
                g.write(json.dumps(user))
                g.close()
            
            # set submission's verdict to result
            submission["verdict"] = result

            # update submissions.json
            submissions[submissionId] = submission
            f.write(json.dumps(submissions))
            f.close()

            return json.dumps({"status": result})

# search user
@app.post("/searchUser", status_code=200, response_class=JSONResponse)
def searchUser(user: User):
    users = json.loads(
        "".join(
            open("./status/status.json", "r", encoding="utf-8")
            .readlines()
        )
    )
    users = [elm for elm in users if elm["username"] == user["username"]]
    if len(user) == 0:
        return json.dumps({"status": "not found"})
    else:
        passAndSalt = user["password"] + users[0]["salt"]
        if users[0]["password"] == hashlib.sha256(user["password"].encode("utf-8")).hexdigest():
            return json.dumps({"status": "found", "user": users[0]})
        else:
            return json.dumps({"status": "invalid password"})
