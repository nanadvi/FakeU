import csv
import psycopg2
from os import listdir

mergeCounter = 1
nonMergeCounter = 0

studentDictionary = {}
count = 0

class Course:
    def __init__(self, CID,Term,Subject,CRSE,Section,Units,Instructors, Students, mergeNumber, mergeChar):
        self.CID = CID
        self.CRSE = CRSE
        self.Subject = Subject
        self.Term = Term
        self.Section = Section
        self.Units = Units
        self.mergeNumber = mergeNumber
        self.mergeChar = mergeChar
        self.Instructors = Instructors
        self.Students = Students

def list_files(path,suffix="csv"):
    filenames = listdir(path)
    return [ filename for filename in filenames if filename.endswith( suffix ) ] #http://stackoverflow.com/a/9251091

def main():
    conn = psycopg2.connect(database='postgres', user=os.environ['USER'], port="5432")
    cur = conn.cursor()
    create_tables(cur,conn)
    PossibleMergedClasses = []
    iStudents = "INSERT INTO STUDENTS(sid,term_id,surname,preferred,level,email,major,mergechar,mergenum) VALUES"
    iCourses = "INSERT INTO COURSE(crse,cid,term_id,name,low_unit,max_unit,mergenum,mergechar) VALUES"
    iSection = "INSERT INTO SECTION(instructor,type, section_no,cid,room,build,days,_time,term_id,subsection,mergenum,mergechar) VALUES"
    iMergedCourses = "INSERT INTO MERGEDCOURSE(cid,term_id,mergechar,mergenum) VALUES"
    iStudentsCourseInfo = "INSERT INTO STUDENTSCOURSEINFO(seat_no,sid,cid,term_id,units,class,grade,mergenum,mergechar,status) VALUES"
    insertStudents = []
    insertCourses = []
    insertSection = []
    insertMergedCourses = []
    insertStudentsCourseInfo = []
    files = list_files("//Users//navid//Desktop//Grades//", suffix=".csv")
    for f in files:
        PossibleMergedClasses = []
        opencsv("//Users//navid//Desktop//Grades//"+f, PossibleMergedClasses,insertStudents,insertCourses,insertSection,insertStudentsCourseInfo,iStudents,iCourses,iSection,insertMergedCourses, iMergedCourses)
    students = iStudents+' '+''.join(insertStudents)[:-1]+';'
    courses = iCourses + ' ' + ''.join(insertCourses)[:-1]+';'
    section = iSection + ' ' + ''.join(insertSection)[:-1]+';'
    if not ''.join(insertMergedCourses) == "":
        mergedcourses = iMergedCourses+' '+''.join(insertMergedCourses)[:-1]+';'
    else:
        mergedcourses = ""
    studentscourseinfo = iStudentsCourseInfo+' '+''.join(insertStudentsCourseInfo)[:-1]+';'
    commands = [students,courses,section,studentscourseinfo]
    insert_into_tables(commands,cur,conn)


def tryToInsertIntoDictionary(key):
    global count
    if key not in studentDictionary:
        studentDictionary[key] = True
        return True
    elif studentDictionary[key]:
        return False


def n(member,type): #type can either be 1 as string, or 0 as int
    if member == "null" or member == "":
        return "null"
    else:
        if type == 1:
            return "\'"+member+"\'"
        else:
            return str(member)


def checkForSameTimeInSpace(class1, class2):
    if (class1.Instructors[0][2] == class2.Instructors[0][2] and class1.Instructors[0][3] == class2.Instructors[0][3] and class1.Instructors[0][4] == class2.Instructors[0][4] and class1.Instructors[0][5] == class2.Instructors[0][5]) and (class1.Subject != class2.Subject and class1.CRSE != class2.CRSE) and (class1.Instructors[0][2] != "null" and class1.Instructors[0][3] != "null" and class1.Instructors[0][4] != "null" and class1.Instructors[0][5] != "null"):
        #if time, building, room, day is the same, then not same course.  If they match, no attribute must be unknown.
        return True
    else:
        return False

def checkForStudentPromotion(class1,class2):
    for i in class1.Students:
        for j in class2.Students:
            if i[1] == j[1] and (i[4] != j[4] or i[6] != j[6] or i[7] != j[7] or i[9] != j[9]):
                return True
    return False

def convertime(time):
    if time == "null":
        return "null"
    else:
        start = time.split("-")[0].strip().split(":")
        end = time.split("-")[1].strip().split(":")
        if start[1][2:].strip() == 'PM' and start[0] != '12':
            start[0] = str(12+int(start[0]))
        elif start[1][2:].strip() == 'AM' and int(start[0]) == 12:
            start[0] = '00'
        start[1] = start[1][:2]
        if end[1][2:].strip() == 'PM' and end[0] != '12':
            end[0] = str(12+int(end[0]))
        elif end[1][2:].strip() == 'AM' and int(end[0]) == 12:
            end[0] = '00'
        end[1] = end[1][:2]
        return ':'.join(start)+" - "+':'.join(end)

def namemodify(name):
    modified = []
    if name.find("'") != -1:
        modified.append(name.split("'")[0])
        modified.append("''")
        modified.append(name.split("'")[1])
        return ''.join(modified)
    else:
        return name


def insertIntoSQL(PossibleMergedClasses,insertStudents,inserSection,insertCourses,insertMergedCourses,insertStudentsCourseInfo,iStudents,iCourses,iSection,iMergedCourses,summer):
    global mergeCounter
    global nonMergeCounter
    p = PossibleMergedClasses
    if summer:
        for i in range(0,len(PossibleMergedClasses)):
            for j in range (i+1,len(PossibleMergedClasses)):
                if PossibleMergedClasses[i].CID == PossibleMergedClasses[j].CID:
                    PossibleMergedClasses[i].mergeNumber = mergeCounter
                    PossibleMergedClasses[i].mergeChar = 'A'
                    PossibleMergedClasses[j].mergeNumber = mergeCounter
                    PossibleMergedClasses[j].mergeChar = 'B'
                    insertMergedCourses.append("("+str(PossibleMergedClasses[i].CID)+","+str(PossibleMergedClasses[i].Term) + ",\'"+PossibleMergedClasses[i].mergeChar+"\',"+str(PossibleMergedClasses[i].mergeNumber)+"),")
                    insertMergedCourses.append(
                        "(" + str(PossibleMergedClasses[j].CID) + "," + str(PossibleMergedClasses[j].Term) + ",\'" +
                        PossibleMergedClasses[j].mergeChar + "\'," + str(PossibleMergedClasses[j].mergeNumber) + "),")
                    if PossibleMergedClasses[i].Units.find("-") != -1:
                        insertCourses.append(
                            "(" + str(p[i].CRSE) + "," + str(p[i].CID) + "," + str(p[i].Term) + ",\'" + p[
                                i].Subject + "\'," + str(p[i].Units.split("-")[0]) + "," + str(
                                p[i].Units.split("-")[1]) + "," + str(p[i].mergeNumber) + ",\'" + str(
                                p[i].mergeChar) + "\'),")
                    else:
                        insertCourses.append(
                            "(" + str(p[i].CRSE) + "," + str(p[i].CID) + "," + str(p[i].Term) + ",\'" + p[
                                i].Subject + "\'," + str(p[i].Units) + "," + str(p[i].Units) + "," + str(
                                p[i].mergeNumber) + ",\'" + str(p[i].mergeChar) + "\'),")
                    if PossibleMergedClasses[j].Units.find("-") != -1:
                        insertCourses.append(
                            "(" + str(p[j].CRSE) + "," + str(p[j].CID) + "," + str(p[j].Term) + ",\'" + p[
                                j].Subject + "\'," + str(p[j].Units.split("-")[0]) + "," + str(
                                p[j].Units.split("-")[1]) + "," + str(p[j].mergeNumber) + ",\'" + str(
                                p[j].mergeChar) + "\'),")
                    else:
                        insertCourses.append(
                            "(" + str(p[j].CRSE) + "," + str(p[j].CID) + "," + str(p[j].Term) + ",\'" + p[
                                j].Subject + "\'," + str(p[j].Units) + "," + str(p[j].Units) + "," + str(
                                p[j].mergeNumber) + ",\'" + str(p[j].mergeChar) + "\'),")
                    for m in range(0, len(PossibleMergedClasses[i].Instructors)):
                            inserSection.append(
                                "(" + n(namemodify(p[i].Instructors[m][0]), 1) + "," + n(p[i].Instructors[m][1],
                                                                                         1) + "," + n(p[i].Section,
                                                                                                      0) + "," + n(
                                    p[i].CID, 0) + "," + n(p[i].Instructors[m][5], 0) + "," + n(
                                    p[i].Instructors[m][4], 1) + "," + n(p[i].Instructors[m][2], 1) + "," + n(
                                    convertime(p[i].Instructors[m][3]), 1) + "," + n(p[i].Term, 0) + "," + n(m,
                                                                                                             0) + "," + str(
                                    p[i].mergeNumber) + ",\'" + str(p[i].mergeChar) + "\'),")
                    for m in range(0, len(PossibleMergedClasses[j].Instructors)):
                            inserSection.append(
                                "(" + n(namemodify(p[j].Instructors[m][0]), 1) + "," + n(p[j].Instructors[m][1],
                                                                                         1) + "," + n(p[j].Section,
                                                                                                      0) + "," + n(
                                    p[j].CID, 0) + "," + n(p[j].Instructors[m][5], 0) + "," + n(
                                    p[j].Instructors[m][4], 1) + "," + n(p[j].Instructors[m][2], 1) + "," + n(
                                    convertime(p[j].Instructors[m][3]), 1) + "," + n(p[j].Term, 0) + "," + n(m,
                                                                                                             0) + "," + str(
                                    p[j].mergeNumber) + ",\'" + str(p[j].mergeChar) + "\'),")
                    for m in range(0, len(PossibleMergedClasses[i].Students)):
                        insertStudentsCourseInfo.append(
                            "(" + p[i].Students[m][0] + "," + p[i].Students[m][1] + "," + str(p[i].CID) + "," + str(
                                p[i].Term) + "," + n(p[i].Students[m][5], 0) + "," + "\'" + p[i].Students[m][
                                6] + "\',\'" + p[i].Students[m][8] + "\'," + str(p[i].mergeNumber) + ",\'" + str(
                                p[i].mergeChar) + "\',\'"+str(p[i].Students[m][9])+"\'),")
                    for m in range(0, len(PossibleMergedClasses[j].Students)):
                        insertStudentsCourseInfo.append(
                            "(" + p[j].Students[m][0] + "," + p[j].Students[m][1] + "," + str(p[j].CID) + "," + str(
                                p[j].Term) + "," + n(p[j].Students[m][5], 0) + "," + "\'" + p[j].Students[m][
                                6] + "\',\'" + p[j].Students[m][8] + "\'," + str(p[j].mergeNumber) + ",\'" + str(
                                p[j].mergeChar) + "\',\'"+str(p[j].Students[m][9])+"\'),")
                    for m in range(0, len(PossibleMergedClasses[i].Students)):
                        if tryToInsertIntoDictionary("(" + p[i].Students[m][1] + "," + p[i].Term + ",\'" + namemodify(
                                p[i].Students[m][2]) + "\'," + "\'" + namemodify(p[i].Students[m][3]) + "\',\'" +
                                                             p[i].Students[m][4] + "\'" + ",\'" + namemodify(
                                p[i].Students[m][10]) + "\'" + ",\'" + p[i].Students[m][7] + "\',\'" + p[
                            i].mergeChar + "\'," + str(p[i].mergeNumber) + "),"):
                            insertStudents.append("(" + p[i].Students[m][1] + "," + p[i].Term + ",\'" + namemodify(
                                p[i].Students[m][2]) + "\'," + "\'" + namemodify(p[i].Students[m][3]) + "\',\'" +
                                                  p[i].Students[m][4] + "\'" + ",\'" + namemodify(
                                p[i].Students[m][10]) + "\'" + ",\'" + p[i].Students[m][7] + "\',\'" + p[
                                                      i].mergeChar + "\'," + str(p[i].mergeNumber) + "),")
                    for m in range(0, len(PossibleMergedClasses[j].Students)):
                        if tryToInsertIntoDictionary("(" + p[j].Students[m][1] + "," + p[j].Term + ",\'" + namemodify(
                                p[j].Students[m][2]) + "\'," + "\'" + namemodify(p[j].Students[m][3]) + "\',\'" +
                                                             p[j].Students[m][4] + "\'" + ",\'" + namemodify(
                                p[j].Students[m][10]) + "\'" + ",\'" + p[j].Students[m][7] + "\',\'" + p[
                            j].mergeChar + "\'," + str(p[j].mergeNumber) + "),"):
                            insertStudents.append("(" + p[j].Students[m][1] + "," + p[j].Term + ",\'" + namemodify(
                                p[j].Students[m][2]) + "\'," + "\'" + namemodify(p[j].Students[m][3]) + "\',\'" +
                                                  p[j].Students[m][4] + "\'" + ",\'" + namemodify(
                                p[j].Students[m][10]) + "\'" + ",\'" + p[j].Students[m][7] + "\',\'" + p[
                                                      j].mergeChar + "\'," + str(p[j].mergeNumber) + "),")
                    mergeCounter += 1
                elif checkForSameTimeInSpace(PossibleMergedClasses[i], PossibleMergedClasses[j]):
                    PossibleMergedClasses[i].mergeNumber = mergeCounter
                    PossibleMergedClasses[i].mergeChar = 'A'
                    PossibleMergedClasses[j].mergeNumber = mergeCounter
                    PossibleMergedClasses[j].mergeChar = 'B'
                    insertMergedCourses.append(
                        "(" + str(PossibleMergedClasses[i].CID) + "," + str(PossibleMergedClasses[i].Term) + ",\'" +
                        PossibleMergedClasses[i].mergeChar + "\'," + str(PossibleMergedClasses[i].mergeNumber) + "),")
                    insertMergedCourses.append(
                        "(" + str(PossibleMergedClasses[j].CID) + "," + str(PossibleMergedClasses[j].Term) + ",\'" +
                        PossibleMergedClasses[j].mergeChar + "\'," + str(PossibleMergedClasses[j].mergeNumber) + "),")

                    if PossibleMergedClasses[i].Units.find("-") != -1:
                        insertCourses.append(
                            "(" + str(p[i].CRSE) + "," + str(p[i].CID) + "," + str(p[i].Term) + ",\'" + p[
                                i].Subject + "\'," + str(p[i].Units.split("-")[0]) + "," + str(
                                p[i].Units.split("-")[1]) + "," + str(p[i].mergeNumber) + ",\'" + str(
                                p[i].mergeChar) + "\'),")
                    else:
                        insertCourses.append(
                            "(" + str(p[i].CRSE) + "," + str(p[i].CID) + "," + str(p[i].Term) + ",\'" + p[
                                i].Subject + "\'," + str(p[i].Units) + "," + str(p[i].Units) + "," + str(
                                p[i].mergeNumber) + ",\'" + str(p[i].mergeChar) + "\'),")
                    if PossibleMergedClasses[j].Units.find("-") != -1:
                        insertCourses.append(
                            "(" + str(p[j].CRSE) + "," + str(p[j].CID) + "," + str(p[j].Term) + ",\'" + p[
                                j].Subject + "\'," + str(p[j].Units.split("-")[0]) + "," + str(
                                p[j].Units.split("-")[1]) + "," + str(p[j].mergeNumber) + ",\'" + str(
                                p[j].mergeChar) + "\'),")
                    else:
                        insertCourses.append(
                            "(" + str(p[j].CRSE) + "," + str(p[j].CID) + "," + str(p[j].Term) + ",\'" + p[
                                j].Subject + "\'," + str(p[j].Units) + "," + str(p[j].Units) + "," + str(
                                p[j].mergeNumber) + ",\'" + str(p[j].mergeChar) + "\'),")
                    for m in range(0, len(PossibleMergedClasses[i].Instructors)):
                            inserSection.append(
                                "(" + n(namemodify(p[i].Instructors[m][0]), 1) + "," + n(p[i].Instructors[m][1],
                                                                                         1) + "," + n(p[i].Section,
                                                                                                      0) + "," + n(
                                    p[i].CID, 0) + "," + n(p[i].Instructors[m][5], 0) + "," + n(
                                    p[i].Instructors[m][4], 1) + "," + n(p[i].Instructors[m][2], 1) + "," + n(
                                    convertime(p[i].Instructors[m][3]), 1) + "," + n(p[i].Term, 0) + "," + n(m,
                                                                                                             0) + "," + str(
                                    p[i].mergeNumber) + ",\'" + str(p[i].mergeChar) + "\'),")
                    for m in range(0, len(PossibleMergedClasses[j].Instructors)):
                            inserSection.append(
                                "(" + n(namemodify(p[j].Instructors[m][0]), 1) + "," + n(p[j].Instructors[m][1],
                                                                                         1) + "," + n(p[j].Section,
                                                                                                      0) + "," + n(
                                    p[j].CID, 0) + "," + n(p[j].Instructors[m][5], 0) + "," + n(
                                    p[j].Instructors[m][4], 1) + "," + n(p[j].Instructors[m][2], 1) + "," + n(
                                    convertime(p[j].Instructors[m][3]), 1) + "," + n(p[j].Term, 0) + "," + n(m,
                                                                                                             0) + "," + str(
                                    p[j].mergeNumber) + ",\'" + str(p[j].mergeChar) + "\'),")
                    for m in range(0, len(PossibleMergedClasses[i].Students)):
                        insertStudentsCourseInfo.append(
                            "(" + p[i].Students[m][0] + "," + p[i].Students[m][1] + "," + str(p[i].CID) + "," + str(
                                p[i].Term) + "," + n(p[i].Students[m][5], 0) + "," + "\'" + p[i].Students[m][
                                6] + "\',\'" + p[i].Students[m][8] + "\'," + str(p[i].mergeNumber) + ",\'" + str(
                                p[i].mergeChar) + "\',\'"+str(p[i].Students[m][9])+"\'),")
                    for m in range(0, len(PossibleMergedClasses[j].Students)):
                        insertStudentsCourseInfo.append(
                            "(" + p[j].Students[m][0] + "," + p[j].Students[m][1] + "," + str(p[j].CID) + "," + str(
                                p[j].Term) + "," + n(p[j].Students[m][5], 0) + "," + "\'" + p[j].Students[m][
                                6] + "\',\'" + p[j].Students[m][8] + "\'," + str(p[j].mergeNumber) + ",\'" + str(
                                p[j].mergeChar) + "\',\'"+str(p[j].Students[m][9])+"\'),")
                    for m in range(0, len(PossibleMergedClasses[i].Students)):
                        if tryToInsertIntoDictionary("(" + p[i].Students[m][1] + "," + p[i].Term + ",\'" + namemodify(
                                p[i].Students[m][2]) + "\'," + "\'" + namemodify(p[i].Students[m][3]) + "\',\'" +
                                                             p[i].Students[m][4] + "\'" + ",\'" + namemodify(
                                p[i].Students[m][10]) + "\'" + ",\'" + p[i].Students[m][7] + "\',\'" + p[
                            i].mergeChar + "\'," + str(p[i].mergeNumber) + "),"):
                            insertStudents.append("(" + p[i].Students[m][1] + "," + p[i].Term + ",\'" + namemodify(
                                p[i].Students[m][2]) + "\'," + "\'" + namemodify(p[i].Students[m][3]) + "\',\'" +
                                                  p[i].Students[m][4] + "\'" + ",\'" + namemodify(
                                p[i].Students[m][10]) + "\'" + ",\'" + p[i].Students[m][7] + "\',\'" + p[
                                                      i].mergeChar + "\'," + str(p[i].mergeNumber) + "),")
                    for m in range(0, len(PossibleMergedClasses[j].Students)):
                        if tryToInsertIntoDictionary("(" + p[j].Students[m][1] + "," + p[j].Term + ",\'" + namemodify(
                                p[j].Students[m][2]) + "\'," + "\'" + namemodify(p[j].Students[m][3]) + "\',\'" +
                                                             p[j].Students[m][4] + "\'" + ",\'" + namemodify(
                                p[j].Students[m][10]) + "\'" + ",\'" + p[j].Students[m][7] + "\',\'" + p[
                            j].mergeChar + "\'," + str(p[j].mergeNumber) + "),"):
                            insertStudents.append("(" + p[j].Students[m][1] + "," + p[j].Term + ",\'" + namemodify(
                                p[j].Students[m][2]) + "\'," + "\'" + namemodify(p[j].Students[m][3]) + "\',\'" +
                                                  p[j].Students[m][4] + "\'" + ",\'" + namemodify(
                                p[j].Students[m][10]) + "\'" + ",\'" + p[j].Students[m][7] + "\',\'" + p[
                                                      j].mergeChar + "\'," + str(p[j].mergeNumber) + "),")
                    mergeCounter += 1

                elif checkForStudentPromotion(PossibleMergedClasses[i],PossibleMergedClasses[j]):
                    PossibleMergedClasses[i].mergeNumber = mergeCounter
                    PossibleMergedClasses[i].mergeChar = 'A'
                    PossibleMergedClasses[j].mergeNumber = mergeCounter
                    PossibleMergedClasses[j].mergeChar = 'B'
                    insertMergedCourses.append(
                        "(" + str(PossibleMergedClasses[i].CID) + "," + str(PossibleMergedClasses[i].Term) + ",\'" +
                        PossibleMergedClasses[i].mergeChar + "\'," + str(PossibleMergedClasses[i].mergeNumber) + "),")
                    insertMergedCourses.append(
                        "(" + str(PossibleMergedClasses[j].CID) + "," + str(PossibleMergedClasses[j].Term) + ",\'" +
                        PossibleMergedClasses[j].mergeChar + "\'," + str(PossibleMergedClasses[j].mergeNumber) + "),")

                    if PossibleMergedClasses[i].Units.find("-") != -1:
                        insertCourses.append(
                            "(" + str(p[i].CRSE) + "," + str(p[i].CID) + "," + str(p[i].Term) + ",\'" + p[
                                i].Subject + "\'," + str(p[i].Units.split("-")[0]) + "," + str(
                                p[i].Units.split("-")[1]) + "," + str(p[i].mergeNumber) + ",\'" + str(
                                p[i].mergeChar) + "\'),")
                    else:
                        insertCourses.append(
                            "(" + str(p[i].CRSE) + "," + str(p[i].CID) + "," + str(p[i].Term) + ",\'" + p[
                                i].Subject + "\'," + str(p[i].Units) + "," + str(p[i].Units) + "," + str(
                                p[i].mergeNumber) + ",\'" + str(p[i].mergeChar) + "\'),")
                    if PossibleMergedClasses[j].Units.find("-") != -1:
                        insertCourses.append(
                            "(" + str(p[j].CRSE) + "," + str(p[j].CID) + "," + str(p[j].Term) + ",\'" + p[
                                j].Subject + "\'," + str(p[j].Units.split("-")[0]) + "," + str(
                                p[j].Units.split("-")[1]) + "," + str(p[j].mergeNumber) + ",\'" + str(
                                p[j].mergeChar) + "\'),")
                    else:
                        insertCourses.append(
                            "(" + str(p[j].CRSE) + "," + str(p[j].CID) + "," + str(p[j].Term) + ",\'" + p[
                                j].Subject + "\'," + str(p[j].Units) + "," + str(p[j].Units) + "," + str(
                                p[j].mergeNumber) + ",\'" + str(p[j].mergeChar) + "\'),")
                    for m in range(0, len(PossibleMergedClasses[i].Instructors)):
                            inserSection.append(
                                "(" + n(namemodify(p[i].Instructors[m][0]), 1) + "," + n(p[i].Instructors[m][1],
                                                                                         1) + "," + n(p[i].Section,
                                                                                                      0) + "," + n(
                                    p[i].CID, 0) + "," + n(p[i].Instructors[m][5], 0) + "," + n(
                                    p[i].Instructors[m][4], 1) + "," + n(p[i].Instructors[m][2], 1) + "," + n(
                                    convertime(p[i].Instructors[m][3]), 1) + "," + n(p[i].Term, 0) + "," + n(m,
                                                                                                             0) + "," + str(
                                    p[i].mergeNumber) + ",\'" + str(p[i].mergeChar) + "\'),")
                    for m in range(0, len(PossibleMergedClasses[j].Instructors)):
                            inserSection.append(
                                "(" + n(namemodify(p[j].Instructors[m][0]), 1) + "," + n(p[j].Instructors[m][1],
                                                                                         1) + "," + n(p[j].Section,
                                                                                                      0) + "," + n(
                                    p[j].CID, 0) + "," + n(p[j].Instructors[m][5], 0) + "," + n(
                                    p[j].Instructors[m][4], 1) + "," + n(p[j].Instructors[m][2], 1) + "," + n(
                                    convertime(p[j].Instructors[m][3]), 1) + "," + n(p[j].Term, 0) + "," + n(m,
                                                                                                             0) + "," + str(
                                    p[j].mergeNumber) + ",\'" + str(p[j].mergeChar) + "\'),")
                    for m in range(0, len(PossibleMergedClasses[i].Students)):
                        insertStudentsCourseInfo.append(
                            "(" + p[i].Students[m][0] + "," + p[i].Students[m][1] + "," + str(p[i].CID) + "," + str(
                                p[i].Term) + "," + n(p[i].Students[m][5], 0) + "," + "\'" + p[i].Students[m][
                                6] + "\',\'" + p[i].Students[m][8] + "\'," + str(p[i].mergeNumber) + ",\'" + str(
                                p[i].mergeChar) + "\',\'"+str(p[i].Students[m][9])+"\'),")
                    for m in range(0, len(PossibleMergedClasses[j].Students)):
                        insertStudentsCourseInfo.append(
                            "(" + p[j].Students[m][0] + "," + p[j].Students[m][1] + "," + str(p[j].CID) + "," + str(
                                p[j].Term) + "," + n(p[j].Students[m][5], 0) + "," + "\'" + p[j].Students[m][
                                6] + "\',\'" + p[j].Students[m][8] + "\'," + str(p[j].mergeNumber) + ",\'" + str(
                                p[j].mergeChar) + "\',\'"+str(p[j].Students[m][9])+"\'),")
                    for m in range(0, len(PossibleMergedClasses[i].Students)):
                        if tryToInsertIntoDictionary("(" + p[i].Students[m][1] + "," + p[i].Term + ",\'" + namemodify(
                                p[i].Students[m][2]) + "\'," + "\'" + namemodify(p[i].Students[m][3]) + "\',\'" +
                                                             p[i].Students[m][4] + "\'" + ",\'" + namemodify(
                                p[i].Students[m][10]) + "\'" + ",\'" + p[i].Students[m][7] + "\',\'" + p[
                            i].mergeChar + "\'," + str(p[i].mergeNumber) + "),"):
                            insertStudents.append("(" + p[i].Students[m][1] + "," + p[i].Term + ",\'" + namemodify(
                                p[i].Students[m][2]) + "\'," + "\'" + namemodify(p[i].Students[m][3]) + "\',\'" +
                                                  p[i].Students[m][4] + "\'" + ",\'" + namemodify(
                                p[i].Students[m][10]) + "\'" + ",\'" + p[i].Students[m][7] + "\',\'" + p[
                                                      i].mergeChar + "\'," + str(p[i].mergeNumber) + "),")
                    for m in range(0, len(PossibleMergedClasses[j].Students)):
                        if tryToInsertIntoDictionary("(" + p[j].Students[m][1] + "," + p[j].Term + ",\'" + namemodify(
                                p[j].Students[m][2]) + "\'," + "\'" + namemodify(p[j].Students[m][3]) + "\',\'" +
                                                             p[j].Students[m][4] + "\'" + ",\'" + namemodify(
                                p[j].Students[m][10]) + "\'" + ",\'" + p[j].Students[m][7] + "\',\'" + p[
                            j].mergeChar + "\'," + str(p[j].mergeNumber) + "),"):
                            insertStudents.append("(" + p[j].Students[m][1] + "," + p[j].Term + ",\'" + namemodify(
                                p[j].Students[m][2]) + "\'," + "\'" + namemodify(p[j].Students[m][3]) + "\',\'" +
                                                  p[j].Students[m][4] + "\'" + ",\'" + namemodify(
                                p[j].Students[m][10]) + "\'" + ",\'" + p[j].Students[m][7] + "\',\'" + p[
                                                      j].mergeChar + "\'," + str(p[j].mergeNumber) + "),")
                    mergeCounter += 1

    p = PossibleMergedClasses
    # for i in range (0, len(PossibleMergedClasses)):
    #     if PossibleMergedClasses[i].mergeChar == 'C':
    #         PossibleMergedClasses[i].mergeNumber = nonMergeCounter;
    #         nonMergeCounter += 1
    for i in range(0,len(PossibleMergedClasses)):
        if PossibleMergedClasses[i].mergeChar == 'C':
            if PossibleMergedClasses[i].Units.find("-") != -1:
                insertCourses.append("(" + str(p[i].CRSE) + "," + str(p[i].CID) + "," + str(p[i].Term) + ",\'" + p[i].Subject + "\'," + str(p[i].Units.split("-")[0]) + "," + str(p[i].Units.split("-")[1])+","+str(p[i].mergeNumber)+",\'"+str(p[i].mergeChar)+"\'),")
            else:
                insertCourses.append("(" + str(p[i].CRSE) + "," + str(p[i].CID) + "," + str(p[i].Term) + ",\'" + p[i].Subject + "\'," + str(p[i].Units) + ","+ str(p[i].Units)+","+ str(p[i].mergeNumber)+",\'"+str(p[i].mergeChar)+"\'),")

    for i in range(0,len(PossibleMergedClasses)):
        for j in range(0, len(PossibleMergedClasses[i].Instructors)):
            if PossibleMergedClasses[i].mergeChar == 'C':
                inserSection.append("(" + n(namemodify(p[i].Instructors[j][0]),1) + ","+n(p[i].Instructors[j][1],1)+","+n(p[i].Section,0)+","+n(p[i].CID,0)+","+n(p[i].Instructors[j][5],0)+","+n(p[i].Instructors[j][4],1)+","+n(p[i].Instructors[j][2],1)+"," + n(convertime(p[i].Instructors[j][3]),1)+","+n(p[i].Term,0)+","+n(j,0)+","+str(p[i].mergeNumber)+",\'"+str(p[i].mergeChar)+"\'),")
    for i in range(0,len(PossibleMergedClasses)):
        for j in range(0,len(PossibleMergedClasses[i].Students)):
            if PossibleMergedClasses[i].mergeChar == 'C':
                insertStudentsCourseInfo.append("("+p[i].Students[j][0]+","+p[i].Students[j][1]+","+str(p[i].CID)+","+str(p[i].Term)+","+n(p[i].Students[j][5],0)+","+"\'"+p[i].Students[j][6]+"\',\'" + p[i].Students[j][8] +"\',"+str(p[i].mergeNumber)+",\'"+str(p[i].mergeChar)+"\',\'"+str(p[i].Students[j][9])+"\'),")
    for i in range(0,len(PossibleMergedClasses)):
        for j in range(0,len(PossibleMergedClasses[i].Students)):
            if PossibleMergedClasses[i].mergeChar == 'C':
                if tryToInsertIntoDictionary("(" + p[i].Students[j][1]+","+p[i].Term+",\'"+namemodify(p[i].Students[j][2])+"\',"+"\'"+namemodify(p[i].Students[j][3])+"\',\'"+p[i].Students[j][4]+"\'"+",\'"+namemodify(p[i].Students[j][10])+"\'"+",\'"+p[i].Students[j][7]+"\',\'"+p[i].mergeChar+"\',"+str(p[i].mergeNumber)+"),"):
                    insertStudents.append("(" + p[i].Students[j][1]+","+p[i].Term+",\'"+namemodify(p[i].Students[j][2])+"\',"+"\'"+namemodify(p[i].Students[j][3])+"\',\'"+p[i].Students[j][4]+"\'"+",\'"+namemodify(p[i].Students[j][10])+"\'"+",\'"+p[i].Students[j][7]+"\',\'"+p[i].mergeChar+"\',"+str(p[i].mergeNumber)+"),")
    return

def consolidate(info,instructorCount, PossibleMergedClasses, insertStudents,insertCourses,inserSection,insertStudentsCourseInfo):
    #def __init__(self, CID,Term,Subject,CRSE,Section,Units,Instructors, Students):
    students = []
    instructors = []
    for i in range(5,5+instructorCount):
        if info[i][0] == "":
            info[i][0] = info[5][0]
        instructors.append(info[i])
    for i in range(7+instructorCount,len(info)):
        students.append(info[i])
    for i in range(0,len(instructors)):
        for j in range(0, len(instructors[i])):
            if instructors[i][j] == '':
                instructors[i][j] = "null"

    aCourse = Course(info[2][0],info[2][1],info[2][2],info[2][3],info[2][4],info[2][5],instructors,students, 0, 'C')

    PossibleMergedClasses.append(aCourse)  #Will check for merged classes in this list, and dicussions that lack a professor may inherit lecture professor.

def opencsv(filename,PossibleMergedClasses,insertStudents,insertCourses,inserSection,insertStudentsCourseInfo,iStudents,iCourses,iSection,insertMergedCourses,iMergedCourses):
    information = []
    reachedSeats = False
    reachedInstructors = False
    readingStudents = False
    instructorCount = 0
    summer = False
    global _file
    if not filename.find("Q3") == -1:
        summer = True
    else:
        summer = False

    with open(filename) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            if reachedInstructors: #we've reached the row that could list one or more instructors.
                if ''.join(row) == "":
                    reachedInstructors = False
                else:
                    instructorCount += 1
            if reachedSeats: #we've reached the row that could list students, there may or may not be students.
                if ''.join(row) == ""  and readingStudents: #we're done reading students
                    consolidate(information,instructorCount, PossibleMergedClasses,insertStudents,insertCourses,inserSection,insertStudentsCourseInfo) #using the rows from information to insert into data collection
                    information.clear()
                    instructorCount = 0
                    reachedSeats = False
                    readingStudents = False
                elif ''.join(row) == "": #no students in class, we're not including this information in database
                    information.clear()
                    instructorCount = 0
                    reachedSeats = False
                    readingStudents = False
                else: #there's students to read
                    readingStudents = True

            information.append(row)
            if ''.join(row) == "INSTRUCTOR(S)TYPEDAYSTIMEBUILDROOM":
                reachedInstructors = True
            if ''.join(row) == "SEATSIDSURNAMEPREFNAMELEVELUNITSCLASSMAJORGRADESTATUSEMAIL":
                reachedSeats = True
    insertIntoSQL(PossibleMergedClasses,insertStudents,inserSection,insertCourses,insertMergedCourses,insertStudentsCourseInfo,iStudents,iCourses,iSection,iMergedCourses,summer)

def create_tables(cur,conn):
    commands = (
        """
        CREATE TABLE STUDENTS (
            sid INTEGER,
            term_id INTEGER,
            surname VARCHAR(255),
            preferred VARCHAR(255),
            level VARCHAR(255),
            email VARCHAR(255),
            major VARCHAR(255),
            mergechar CHAR,
            mergenum INTEGER,
            PRIMARY KEY (sid,term_id,mergenum,mergechar)
        )
        """,
        """
        CREATE TABLE COURSE (
            crse INTEGER,
            cid INTEGER,
            term_id INTEGER,
            name VARCHAR (255),
            low_unit INTEGER,
            max_unit INTEGER,
            mergenum INTEGER,
            mergechar CHAR,
            PRIMARY KEY(cid, term_id,mergenum,mergechar)
        )
        """,
        """
        CREATE TABLE SECTION (
            instructor VARCHAR(255),
            type VARCHAR(255),
            section_no INTEGER,
            cid INTEGER,
            room INTEGER,
            build VARCHAR(255),
            days VARCHAR(255),
            _time VARCHAR(255),
            term_id INTEGER,
            subsection INTEGER,
            mergenum INTEGER,
            mergechar CHAR,
            PRIMARY KEY (cid,term_id,subsection,mergenum,mergechar),
            FOREIGN KEY (cid, term_id, mergenum, mergechar) REFERENCES COURSE (cid, term_id, mergenum, mergechar)
        )
        """,

        """
        CREATE TABLE STUDENTSCOURSEINFO (
            seat_no INTEGER,
            sid INTEGER,
            cid INTEGER,
            term_id INTEGER,
            units INTEGER,
            class VARCHAR(255),
            grade VARCHAR(255),
            mergenum INTEGER,
            mergechar VARCHAR(255),
            status VARCHAR(255),
            PRIMARY KEY(sid,cid,term_id,mergenum,mergechar),
            FOREIGN KEY (cid, term_id, mergenum, mergechar) REFERENCES COURSE (cid, term_id, mergenum, mergechar),
            FOREIGN KEY (sid, term_id, mergenum, mergechar) REFERENCES STUDENTS(sid, term_id,mergenum, mergechar)
        )
        """
        )
    for c in commands:
        cur.execute(c)
    conn.commit()


def insert_into_tables(commands,cur,conn):

    for c in commands:
        if not c == "":
            cur.execute(c)
    conn.commit()

main()
