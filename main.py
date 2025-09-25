import google.generativeai as genai
import pandas as pd
import json
import subprocess
from models.create import *
from flask import Flask, render_template, jsonify ,request,redirect
import json
from flask import session as sess

app = Flask(__name__)
app.secret_key="01714815624"

genai.configure(api_key="AIzaSyATln8rhGMZA0qvVqG6xDgEyfPBHD1VRgY")

pattern = """
Each day must strictly have tasks matching ONE of the following combinations:
- **Combination A:** 3 Easy
- **Combination B:** 2 Medium.
- **Combination C:** 1 Hard + 2 task Easy
- **Combination D:** 1 Medium + 1 Hard
"""

def upstat(name, status):
    with open('schedule.json', 'r+') as f:
        data = json.load(f)
        for day in data['study_schedule']:
            for task in day['tasks']:
                if task['name'] == name:
                    task['stat'] = status
        f.seek(0)
        json.dump(data, f, indent=4)


def generate():
    try:
        df = pd.read_csv("dataset.csv")
        csv_string = df.to_csv(index=False)
        df = pd.read_csv("easy.csv")
        easy_csv_string = df.to_csv(index=False)
        df = pd.read_csv("med.csv")
        medium_csv_string = df.to_csv(index=False)
        df = pd.read_csv("hard.csv")
        hard_csv_string = df.to_csv(index=False)
    except FileNotFoundError:
        result = subprocess.run(['python', 'webscrape/webscrape.py'])
        df = pd.read_csv("dataset.csv")
        csv_string = df.to_csv(index=False)
        df = pd.read_csv("easy.csv")
        easy_csv_string = df.to_csv(index=False)
        df = pd.read_csv("med.csv")
        medium_csv_string = df.to_csv(index=False)
        df = pd.read_csv("hard.csv")
        hard_csv_string = df.to_csv(index=False) 

    prompt = f"""
    Return a single valid JSON object for a 90-day study schedule.

    Datasets below contain every allowed task.  
    Each row already includes the correct difficulty.  
    **Never invent tasks or change the difficulty value.**  
    You must copy the `difficulty` column exactly as written.
    {pattern}
    **IMPORTANT:**  
    *Never mix tasks from more than one combination per day. 
    
    try to follow the above combination strictly if it is not possible to generate a 90 day schedule with the exact combinations then produce a 90 day schedule following the above combinations for as many days you can in short change the above combination if absolutely necessary and minimize the days you change the pattern for*

    Do not deviate from these combinations for any day.

    Each task object must contain:
        - "name"
        - "difficulty"
        - "link"
        - "stat" 

     Task uniqueness: each task from the CSVs can appear once only.

    Easy Tasks:
    {easy_csv_string}

    Medium Tasks:
    {medium_csv_string}

    Hard Tasks:
    {hard_csv_string}

    Output: a JSON object with a top-level key "study_schedule" (array of day objects).
    the json object must contain name,difficulty,link and stat 
    Return ONLY this JSON object—no code fences, no extra text.
    """

    model = genai.GenerativeModel('gemini-2.5-flash-lite')

    try:
        response = model.generate_content(prompt)
        #print(response)
        json_string = response.text.split("```json\n")[1].strip().rsplit("\n```", 1)[0].strip()
        schedule_json = json.loads(json_string)
        
        with open("schedule.json", "w") as f:
            json.dump(schedule_json, f, indent=2)
        
    except Exception as e:
        print(f"An error occurred: {e}")
generate()



@app.route('/schedule',methods=["GET","POST"])
def home():
    with open("schedule.json") as f:
        schedule = json.load(f)
    if request.method=="GET":
        return  render_template("schedule.html",schedule=schedule,username=sess["firstname"])
    

@app.route('/prompt',methods=["GET","POST"])
def promt():
    global pattern
    if request.method=="GET":
        return render_template("prompt.html",username=sess["firstname"])
    else:
        pattern = request.form["pro"]
        generate()
        return redirect("/schedule")
    

@app.route("/signup/",methods=["GET","POST"])
def signup():
    if request.method=="GET":
        return render_template("signup.html")
    else:
        email1 = request.form["emailid"]
        password1 = request.form["password"]
        fname1 = request.form["fname"]
        try:
            with Session(engine) as session:
                session.execute(insert(User).values(email=email1,password=password1,fname=fname1))
                session.commit()
        except:
            return render_template("signuperror.html")
        else:
            return redirect("/")

 
@app.route("/",methods=["GET","POST"])
def index():
    if request.method=="GET":
        return render_template("index.html")
    elif request.method=="POST":
        email = request.form["emailid"]
        password=request.form["password"]
        try:
            with Session(engine) as session:
                search = session.execute(select(User).where(User.email==email)).scalar_one()
            sess["userid"] = search.id
            sess["firstname"] = search.fname.split()[0]
            sess["email"] = search.email
            sess["pass"] = search.password
            sess["fname"]=search.fname
            
        except:
            return render_template("loginerror.html")
        else:
            if email==sess["email"] and password==sess["pass"]:
                return redirect("/schedule")
            else:
                return render_template("loginerror.html")

@app.route("/complete/<ques>",methods=["GET","POST"])
def comp(ques):
    status = 1
    upstat(ques,status)
    return redirect("/schedule")
@app.route("/incomplete/<ques>",methods=["GET","POST"])
def incomp(ques):
    status = 0
    upstat(ques,status)
    return redirect("/schedule")
if __name__ == '__main__':
    app.run(debug=True)
