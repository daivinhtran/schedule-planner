from flask import Flask
from flask import request
from flask import render_template
from flask import redirect, url_for
import json
import pickle
app = Flask(__name__)


def canTake(course, prereq, takenCourses):
  if course not in prereq:
    return True
  prereqArr = prereq[course]
  if len(prereqArr) == 0:
    return True
  return recursion_helper(prereqArr, takenCourses)

def courseTaken(course, takenCourses):
  return course in takenCourses

def recursion_helper(prereqArr, takenCourses):
  if len(prereqArr) == 0:
    return True
  if len(prereqArr) == 1:
    if type(prereqArr[0]) == type([]):
      return recursion_helper(prereqArr[0], takenCourses)
    else:
      return courseTaken(prereqArr[0], takenCourses)

  courseStack = []
  operatorStack = []

  for a in prereqArr:
    if type(a) == type([]):
      courseStack.append(recursion_helper(a, takenCourses))
    elif a != 'OR' and a != 'AND':
      courseStack.append(courseTaken(a, takenCourses))
    else:
      operatorStack.append(a)

  for ops in operatorStack:
    a = courseStack.pop()
    b = courseStack.pop()
    # ops = operatorStack.pop()    
    if ops == 'AND':
      courseStack.append(a & b)
    else:
      courseStack.append(a | b)

  return courseStack[0]


def generate(coursesToGraduate, takenCourses):
    import json
    with open('data/credithours.json') as json_data:
      creditHours = json.load(json_data)
      json_data.close()

    with open('data/prereq.json') as json_data:
      prereq = json.load(json_data)
      json_data.close()

    # takenCourses = ['CS1301', 'CS1331']
    nextSemesterCourses = []
    take1 = ['CoreA', 'SocialScience', 'CoreC', 'Wellness', 'CoreD', 'Stats_1', 'CoreE_1']
    for group in coursesToGraduate:
      for course in coursesToGraduate[group]:
        if canTake(course, prereq, takenCourses) and course not in takenCourses:
          nextSemesterCourses.append(course)
          if group in take1:
            break

    for course in nextSemesterCourses:
      print(course)
    return nextSemesterCourses

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
    coursesToGraduate = pickle.loads(request.args.get('courseToGraduate'))
    print('takenCourses: ', takenCourses)
    print('courseToGraduate: ', coursesToGraduate)
    nextSemesterCourses = generate(coursesToGraduate, takenCourses)
    return render_template('schedule.html', nextSemesterCourses=nextSemesterCourses)

if __name__ == "__main__":
    app.run()