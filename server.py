from flask import Flask
from flask import request
from flask import render_template
from flask import redirect, url_for
import json
import pickle
app = Flask(__name__)
 
# @app.route("/")
# def index():
#     return render_template('index.html')
 
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        selectedValue = request.form['option']
        return redirect(url_for('threadRequirements', selectedValue=selectedValue))
    return render_template('index.html')


@app.route('/<selectedValue>', methods=['GET','POST'])
def threadRequirements(selectedValue):
    with open('Data/' + selectedValue + '.json') as json_data:
      courseToGraduate = json.load(json_data)
      json_data.close()

    requiredCourses = []
    for group in courseToGraduate:
      for course in courseToGraduate[group]:
        if course not in requiredCourses:
          requiredCourses.append(course)

    if request.method == 'POST':
        if request.form.getlist('takenCourse'):
            takenCourses = request.form.getlist('takenCourse')
            return redirect(url_for('generateSchedule', takenCourses=pickle.dumps(takenCourses), courseToGraduate=pickle.dumps(courseToGraduate)))

    return render_template('thread_requirement.html', requiredCourses=requiredCourses)

@app.route('/generateSchedule')
def generateSchedule():
    takenCourses = pickle.loads(request.args.get('takenCourses'))
    courseToGraduate = pickle.loads(request.args.get('courseToGraduate'))
    print('takenCourses: ', takenCourses)
    print('courseToGraduate: ', courseToGraduate)
    return render_template('schedule.html')

if __name__ == "__main__":
    app.run()