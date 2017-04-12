import psycopg2

conn = psycopg2.connect("dbname='postgres' user='navid' password=''")
cur = conn.cursor()
cur = conn.cursor()


def queryexecute_d(cur,command):
    avgcommand = """
    SELECT AVG(R1.gpa) as grade
    FROM
    (
      SELECT
        cid,
        term_id,
        CASE
        WHEN grade = 'A+'
          THEN 4.0 * units
        WHEN grade = 'A'
          THEN 4.0 * units
        WHEN grade = 'A-'
          THEN 3.7 * units
        WHEN grade = 'B+'
          THEN 3.3 * units
        WHEN grade = 'B'
          THEN 3.0 * units
        WHEN grade = 'B-'
          THEN 2.7 * units
        WHEN grade = 'C+'
          THEN 2.3 * units
        WHEN grade = 'C'
          THEN 2.0 * units
        WHEN grade = 'C-'
          THEN 1.7 * units
        WHEN grade = 'D+'
          THEN 1.3 * units
        WHEN grade = 'D'
          THEN 1.0 * units
        WHEN grade = 'D-'
          THEN 0.7 * units
        WHEN grade = 'F'
          THEN 0.0 * units
        END AS gpa
      FROM section
        NATURAL JOIN studentscourseinfo
      WHERE grade != 'P' AND grade != 'I' AND grade != 'NS'
            AND grade != '' AND grade != 'U' AND grade != 'NG'
            AND grade != 'S' AND grade != 'IP' AND grade != 'Y'
            AND grade != 'WN' AND grade != 'NP' AND grade != 'WD1'
            AND grade != 'WD2' AND grade != 'W10' AND grade != 'WI'
            AND grade != 'W04' AND grade != 'WD4' AND grade != 'XR'
            AND grade != 'WDC' AND section.instructor = %s
    ) AS R1
    """
    if command == 1: #easy
        maxcidtermid = []
        cur.execute(
            """
    SELECT cid, term_id, SUM(gpa)/SUM(units) AS totalgpa
    FROM (
      SELECT
        cid,
        term_id,
        mergechar,
        mergenum,
        units,
        CASE
        WHEN grade = 'A+'
          THEN 4.0 * units
        WHEN grade = 'A'
          THEN 4.0 * units
        WHEN grade = 'A-'
          THEN 3.7 * units
        WHEN grade = 'B+'
          THEN 3.3 * units
        WHEN grade = 'B'
          THEN 3.0 * units
        WHEN grade = 'B-'
          THEN 2.7 * units
        WHEN grade = 'C+'
          THEN 2.3 * units
        WHEN grade = 'C'
          THEN 2.0 * units
        WHEN grade = 'C-'
          THEN 1.7 * units
        WHEN grade = 'D+'
          THEN 1.3 * units
        WHEN grade = 'D'
          THEN 1.0 * units
        WHEN grade = 'D-'
          THEN 0.7 * units
        WHEN grade = 'F'
          THEN 0.0 * units
        END AS gpa
      FROM
        (
          SELECT
            cid,
            term_id,
            mergechar,
            mergenum,
            name,
            crse
          FROM course
          WHERE name = 'ABC' AND crse >= 100 AND crse <= 199
        ) AS R1 NATURAL JOIN studentscourseinfo
      WHERE grade != 'P' AND grade != 'I' AND grade != 'NS'
            AND grade != '' AND grade != 'U' AND grade != 'NG'
            AND grade != 'S' AND grade != 'IP' AND grade != 'Y'
            AND grade != 'WN' AND grade != 'NP' AND grade != 'WD1'
            AND grade != 'WD2' AND grade != 'W10' AND grade != 'WI'
            AND grade != 'W04' AND grade != 'WD4' AND grade != 'XR'
            AND grade != 'WDC'
    ) AS R1
    GROUP BY cid, term_id
            """
        )
        grades = []
        row = cur.fetchall()
        for r in row:
            grades.append(r[2])
        for l in row:
            if l[2] == max(grades):
                maxcidwithgpa = l[0]
                maxtermidwithgpa = l[1]
                maxcidtermid.append([maxcidwithgpa, maxtermidwithgpa])

        cur.execute(
            """
            SELECT cast(final.gradecount AS FLOAT)/cast(final.studentnum as FLOAT) as percentage, final.cid, final.term_id
  FROM
    (
      SELECT
        count        AS gradecount,
        totalstudent AS studentnum,
        cid,
        term_id
      FROM (
             SELECT
               passcount.count,
               passcount.cid,
               passcount.term_id
             FROM (
                    SELECT
                      studentscourseinfo.cid,
                      studentscourseinfo.term_id,
                      count(grade)
                    FROM course
                      INNER JOIN studentscourseinfo
                        ON course.cid = studentscourseinfo.cid AND course.term_id = studentscourseinfo.term_id AND
                           course.mergenum = studentscourseinfo.mergenum AND
                           course.mergechar = studentscourseinfo.mergechar
                    WHERE name = 'ABC' AND crse >= 100 AND crse <= 199 AND grade = 'P'
                    GROUP BY studentscourseinfo.cid, studentscourseinfo.term_id
                  ) AS passcount
           ) R1 NATURAL JOIN (

                               SELECT
                                 SUM(studentcount.count) AS totalstudent,
                                 studentcount.cid,
                                 studentcount.term_id
                               FROM (
                                      SELECT
                                        studentscourseinfo.cid,
                                        studentscourseinfo.term_id,
                                        count(sid)
                                      FROM course
                                        INNER JOIN studentscourseinfo
                                          ON course.cid = studentscourseinfo.cid AND
                                             course.term_id = studentscourseinfo.term_id AND
                                             course.mergenum = studentscourseinfo.mergenum AND
                                             course.mergechar = studentscourseinfo.mergechar
                                      WHERE name = 'ABC' AND crse >= 100 AND crse <= 199
                                      GROUP BY studentscourseinfo.cid, studentscourseinfo.term_id,
                                        studentscourseinfo.sid
                                    ) AS studentcount
                               GROUP BY studentcount.cid, studentcount.term_id
                             ) R2
    ) AS final
            """
        )
        percentages = []
        row2 = cur.fetchall()
        for i in row2:
            percentages.append(i[0])
        for j in row2:
            if j[0] == max(percentages):
                maxcid = j[1]
                maxtermid = j[2]
                maxcidtermid.append([maxcid, maxtermid])

        for i in maxcidtermid:
            cur.execute("SELECT instructor FROM section WHERE cid = %d AND term_id = %d" % (i[0],i[1]))
        instructors = cur.fetchall()

        for j in instructors:
            cur.execute(avgcommand, (j[0],))
            averagegrade = cur.fetchone()
            print("Easiest professor: " + str(j[0]) + "assigns %f on average" % averagegrade)
    if command == 0:  # hard
        maxcidtermid = []
        cur.execute(
            """
    SELECT cid, term_id, SUM(gpa)/SUM(units) AS totalgpa
    FROM (
      SELECT
        cid,
        term_id,
        mergechar,
        mergenum,
        units,
        CASE
        WHEN grade = 'A+'
          THEN 4.0 * units
        WHEN grade = 'A'
          THEN 4.0 * units
        WHEN grade = 'A-'
          THEN 3.7 * units
        WHEN grade = 'B+'
          THEN 3.3 * units
        WHEN grade = 'B'
          THEN 3.0 * units
        WHEN grade = 'B-'
          THEN 2.7 * units
        WHEN grade = 'C+'
          THEN 2.3 * units
        WHEN grade = 'C'
          THEN 2.0 * units
        WHEN grade = 'C-'
          THEN 1.7 * units
        WHEN grade = 'D+'
          THEN 1.3 * units
        WHEN grade = 'D'
          THEN 1.0 * units
        WHEN grade = 'D-'
          THEN 0.7 * units
        WHEN grade = 'F'
          THEN 0.0 * units
        END AS gpa
      FROM
        (
          SELECT
            cid,
            term_id,
            mergechar,
            mergenum,
            name,
            crse
          FROM course
          WHERE name = 'ABC' AND crse >= 100 AND crse <= 199
        ) AS R1 NATURAL JOIN studentscourseinfo
      WHERE grade != 'P' AND grade != 'I' AND grade != 'NS'
            AND grade != '' AND grade != 'U' AND grade != 'NG'
            AND grade != 'S' AND grade != 'IP' AND grade != 'Y'
            AND grade != 'WN' AND grade != 'NP' AND grade != 'WD1'
            AND grade != 'WD2' AND grade != 'W10' AND grade != 'WI'
            AND grade != 'W04' AND grade != 'WD4' AND grade != 'XR'
            AND grade != 'WDC'
    ) AS R1
    GROUP BY cid, term_id
            """
        )
        grades = []
        row = cur.fetchall()
        for r in row:
            grades.append(r[2])
        for l in row:
            if l[2] == min(grades):
                maxcidwithgpa = l[0]
                maxtermidwithgpa = l[1]
                maxcidtermid.append([maxcidwithgpa, maxtermidwithgpa])

        cur.execute(
            """
            SELECT cast(final.gradecount AS FLOAT)/cast(final.studentnum as FLOAT) as percentage, final.cid, final.term_id
  FROM
    (
      SELECT
        count        AS gradecount,
        totalstudent AS studentnum,
        cid,
        term_id
      FROM (
             SELECT
               passcount.count,
               passcount.cid,
               passcount.term_id
             FROM (
                    SELECT
                      studentscourseinfo.cid,
                      studentscourseinfo.term_id,
                      count(grade)
                    FROM course
                      INNER JOIN studentscourseinfo
                        ON course.cid = studentscourseinfo.cid AND course.term_id = studentscourseinfo.term_id AND
                           course.mergenum = studentscourseinfo.mergenum AND
                           course.mergechar = studentscourseinfo.mergechar
                    WHERE name = 'ABC' AND crse >= 100 AND crse <= 199 AND grade = 'P'
                    GROUP BY studentscourseinfo.cid, studentscourseinfo.term_id
                  ) AS passcount
           ) R1 NATURAL JOIN (

                               SELECT
                                 SUM(studentcount.count) AS totalstudent,
                                 studentcount.cid,
                                 studentcount.term_id
                               FROM (
                                      SELECT
                                        studentscourseinfo.cid,
                                        studentscourseinfo.term_id,
                                        count(sid)
                                      FROM course
                                        INNER JOIN studentscourseinfo
                                          ON course.cid = studentscourseinfo.cid AND
                                             course.term_id = studentscourseinfo.term_id AND
                                             course.mergenum = studentscourseinfo.mergenum AND
                                             course.mergechar = studentscourseinfo.mergechar
                                      WHERE name = 'ABC' AND crse >= 100 AND crse <= 199
                                      GROUP BY studentscourseinfo.cid, studentscourseinfo.term_id,
                                        studentscourseinfo.sid
                                    ) AS studentcount
                               GROUP BY studentcount.cid, studentcount.term_id
                             ) R2
    ) AS final
            """
        )
        percentages = []
        row2 = cur.fetchall()
        for i in row2:
            percentages.append(i[0])
        for j in row2:
            if j[0] == min(percentages):
                maxcid = j[1]
                maxtermid = j[2]
                maxcidtermid.append([maxcid, maxtermid])

        for i in maxcidtermid:
            cur.execute("SELECT instructor FROM section WHERE cid = %d AND term_id = %d" % (i[0], i[1]))
        instructors = cur.fetchall()

        for j in instructors:
            cur.execute(avgcommand, (j[0],))
            averagegrade = cur.fetchone()
            print("Hardest professor: " + str(j[0]) + "assigns %f on average" % averagegrade)


def queryexecute_c(cur, command):
    if(command == 1):
        cur.execute(
            """
        SELECT DISTINCT
          instructor
        FROM (
               SELECT
                 cid,
                 term_id,
                 SUM(gpa) / sum(units) AS totalgpa
               FROM (
                      SELECT
                        cid,
                        units,
                        term_id,
                        CASE
                        WHEN grade = 'A+'
                          THEN 4.0 * units
                        WHEN grade = 'A'
                          THEN 4.0 * units
                        WHEN grade = 'A-'
                          THEN 3.7 * units
                        WHEN grade = 'B+'
                          THEN 3.3 * units
                        WHEN grade = 'B'
                          THEN 3.0 * units
                        WHEN grade = 'B-'
                          THEN 2.7 * units
                        WHEN grade = 'C+'
                          THEN 2.3 * units
                        WHEN grade = 'C'
                          THEN 2.0 * units
                        WHEN grade = 'C-'
                          THEN 1.7 * units
                        WHEN grade = 'D+'
                          THEN 1.3 * units
                        WHEN grade = 'D'
                          THEN 1.0 * units
                        WHEN grade = 'D-'
                          THEN 0.7 * units
                        WHEN grade = 'F'
                          THEN 0.0 * units
                        END AS gpa
                      FROM studentscourseinfo
                      WHERE grade != 'P' AND grade != 'I' AND grade != 'NS'
                            AND grade != '' AND grade != 'U' AND grade != 'NG'
                            AND grade != 'S' AND grade != 'IP' AND grade != 'Y'
                            AND grade != 'WN' AND grade != 'NP' AND grade != 'WD1'
                            AND grade != 'WD2' AND grade != 'W10' AND grade != 'WI'
                            AND grade != 'W04' AND grade != 'WD4' AND grade != 'XR'
                            AND grade != 'WDC'
                    ) AS R1
               GROUP BY term_id, cid
             ) AS R2 NATURAL JOIN section
        WHERE totalgpa = (
          SELECT MAX(totalgpa)
          FROM (
                 SELECT
                   cid,
                   term_id,
                   SUM(gpa) / sum(units) AS totalgpa
                 FROM (
                        SELECT
                          cid,
                          units,
                          term_id,
                          CASE
                          WHEN grade = 'A+'
                            THEN 4.0 * units
                          WHEN grade = 'A'
                            THEN 4.0 * units
                          WHEN grade = 'A-'
                            THEN 3.7 * units
                          WHEN grade = 'B+'
                            THEN 3.3 * units
                          WHEN grade = 'B'
                            THEN 3.0 * units
                          WHEN grade = 'B-'
                            THEN 2.7 * units
                          WHEN grade = 'C+'
                            THEN 2.3 * units
                          WHEN grade = 'C'
                            THEN 2.0 * units
                          WHEN grade = 'C-'
                            THEN 1.7 * units
                          WHEN grade = 'D+'
                            THEN 1.3 * units
                          WHEN grade = 'D'
                            THEN 1.0 * units
                          WHEN grade = 'D-'
                            THEN 0.7 * units
                          WHEN grade = 'F'
                            THEN 0.0 * units
                          END AS gpa
                        FROM studentscourseinfo
                        WHERE grade != 'P' AND grade != 'I' AND grade != 'NS'
                              AND grade != '' AND grade != 'U' AND grade != 'NG'
                              AND grade != 'S' AND grade != 'IP' AND grade != 'Y'
                              AND grade != 'WN' AND grade != 'NP' AND grade != 'WD1'
                              AND grade != 'WD2' AND grade != 'W10' AND grade != 'WI'
                              AND grade != 'W04' AND grade != 'WD4' AND grade != 'XR'
                              AND grade != 'WDC'
                      ) AS R1
                 GROUP BY term_id, cid
               ) AS R2 NATURAL JOIN section
        ) AND instructor IS NOT NULL
            """
        )
        easy = cur.fetchall()
        avgcommand = """
        SELECT AVG(R1.gpa) as grade
        FROM
        (
          SELECT
            cid,
            term_id,
            CASE
            WHEN grade = 'A+'
              THEN 4.0 * units
            WHEN grade = 'A'
              THEN 4.0 * units
            WHEN grade = 'A-'
              THEN 3.7 * units
            WHEN grade = 'B+'
              THEN 3.3 * units
            WHEN grade = 'B'
              THEN 3.0 * units
            WHEN grade = 'B-'
              THEN 2.7 * units
            WHEN grade = 'C+'
              THEN 2.3 * units
            WHEN grade = 'C'
              THEN 2.0 * units
            WHEN grade = 'C-'
              THEN 1.7 * units
            WHEN grade = 'D+'
              THEN 1.3 * units
            WHEN grade = 'D'
              THEN 1.0 * units
            WHEN grade = 'D-'
              THEN 0.7 * units
            WHEN grade = 'F'
              THEN 0.0 * units
            END AS gpa
          FROM section
            NATURAL JOIN studentscourseinfo
          WHERE grade != 'P' AND grade != 'I' AND grade != 'NS'
                AND grade != '' AND grade != 'U' AND grade != 'NG'
                AND grade != 'S' AND grade != 'IP' AND grade != 'Y'
                AND grade != 'WN' AND grade != 'NP' AND grade != 'WD1'
                AND grade != 'WD2' AND grade != 'W10' AND grade != 'WI'
                AND grade != 'W04' AND grade != 'WD4' AND grade != 'XR'
                AND grade != 'WDC' AND section.instructor = %s
        ) AS R1
        """
        for n in easy:
            cur.execute(avgcommand, (n[0],))
            averagegrade = cur.fetchone()
            print("Easiest professor: " + str(n[0]) + "assigns %f on average" % averagegrade)
    if(command == 0):
        cur.execute(
            """
        SELECT DISTINCT
          instructor
        FROM (
               SELECT
                 cid,
                 term_id,
                 SUM(gpa) / sum(units) AS totalgpa
               FROM (
                      SELECT
                        cid,
                        units,
                        term_id,
                        CASE
                        WHEN grade = 'A+'
                          THEN 4.0 * units
                        WHEN grade = 'A'
                          THEN 4.0 * units
                        WHEN grade = 'A-'
                          THEN 3.7 * units
                        WHEN grade = 'B+'
                          THEN 3.3 * units
                        WHEN grade = 'B'
                          THEN 3.0 * units
                        WHEN grade = 'B-'
                          THEN 2.7 * units
                        WHEN grade = 'C+'
                          THEN 2.3 * units
                        WHEN grade = 'C'
                          THEN 2.0 * units
                        WHEN grade = 'C-'
                          THEN 1.7 * units
                        WHEN grade = 'D+'
                          THEN 1.3 * units
                        WHEN grade = 'D'
                          THEN 1.0 * units
                        WHEN grade = 'D-'
                          THEN 0.7 * units
                        WHEN grade = 'F'
                          THEN 0.0 * units
                        END AS gpa
                      FROM studentscourseinfo
                      WHERE grade != 'P' AND grade != 'I' AND grade != 'NS'
                            AND grade != '' AND grade != 'U' AND grade != 'NG'
                            AND grade != 'S' AND grade != 'IP' AND grade != 'Y'
                            AND grade != 'WN' AND grade != 'NP' AND grade != 'WD1'
                            AND grade != 'WD2' AND grade != 'W10' AND grade != 'WI'
                            AND grade != 'W04' AND grade != 'WD4' AND grade != 'XR'
                            AND grade != 'WDC'
                    ) AS R1
               GROUP BY term_id, cid
             ) AS R2 NATURAL JOIN section
        WHERE totalgpa = (
          SELECT MIN(totalgpa)
          FROM (
                 SELECT
                   cid,
                   term_id,
                   SUM(gpa) / sum(units) AS totalgpa
                 FROM (
                        SELECT
                          cid,
                          units,
                          term_id,
                          CASE
                          WHEN grade = 'A+'
                            THEN 4.0 * units
                          WHEN grade = 'A'
                            THEN 4.0 * units
                          WHEN grade = 'A-'
                            THEN 3.7 * units
                          WHEN grade = 'B+'
                            THEN 3.3 * units
                          WHEN grade = 'B'
                            THEN 3.0 * units
                          WHEN grade = 'B-'
                            THEN 2.7 * units
                          WHEN grade = 'C+'
                            THEN 2.3 * units
                          WHEN grade = 'C'
                            THEN 2.0 * units
                          WHEN grade = 'C-'
                            THEN 1.7 * units
                          WHEN grade = 'D+'
                            THEN 1.3 * units
                          WHEN grade = 'D'
                            THEN 1.0 * units
                          WHEN grade = 'D-'
                            THEN 0.7 * units
                          WHEN grade = 'F'
                            THEN 0.0 * units
                          END AS gpa
                        FROM studentscourseinfo
                        WHERE grade != 'P' AND grade != 'I' AND grade != 'NS'
                              AND grade != '' AND grade != 'U' AND grade != 'NG'
                              AND grade != 'S' AND grade != 'IP' AND grade != 'Y'
                              AND grade != 'WN' AND grade != 'NP' AND grade != 'WD1'
                              AND grade != 'WD2' AND grade != 'W10' AND grade != 'WI'
                              AND grade != 'W04' AND grade != 'WD4' AND grade != 'XR'
                              AND grade != 'WDC'
                      ) AS R1
                 GROUP BY term_id, cid
               ) AS R2 NATURAL JOIN section
        ) AND instructor IS NOT NULL
            """
        )
        hard = cur.fetchall()
        command = """
        SELECT AVG(R1.gpa) as grade
        FROM
        (
          SELECT
            cid,
            term_id,
            CASE
            WHEN grade = 'A+'
              THEN 4.0 * units
            WHEN grade = 'A'
              THEN 4.0 * units
            WHEN grade = 'A-'
              THEN 3.7 * units
            WHEN grade = 'B+'
              THEN 3.3 * units
            WHEN grade = 'B'
              THEN 3.0 * units
            WHEN grade = 'B-'
              THEN 2.7 * units
            WHEN grade = 'C+'
              THEN 2.3 * units
            WHEN grade = 'C'
              THEN 2.0 * units
            WHEN grade = 'C-'
              THEN 1.7 * units
            WHEN grade = 'D+'
              THEN 1.3 * units
            WHEN grade = 'D'
              THEN 1.0 * units
            WHEN grade = 'D-'
              THEN 0.7 * units
            WHEN grade = 'F'
              THEN 0.0 * units
            END AS gpa
          FROM section
            NATURAL JOIN studentscourseinfo
          WHERE grade != 'P' AND grade != 'I' AND grade != 'NS'
                AND grade != '' AND grade != 'U' AND grade != 'NG'
                AND grade != 'S' AND grade != 'IP' AND grade != 'Y'
                AND grade != 'WN' AND grade != 'NP' AND grade != 'WD1'
                AND grade != 'WD2' AND grade != 'W10' AND grade != 'WI'
                AND grade != 'W04' AND grade != 'WD4' AND grade != 'XR'
                AND grade != 'WDC' AND section.instructor = %s
        ) AS R1
        """
        for m in hard:
            cur.execute(avgcommand, (m[0],))
            averagegrade = cur.fetchone()
            print("Hardest professor: " + str(m[0]) + "assigns %f on average" % averagegrade)
#queryexecute_c(cur,1)
#queryexecute_c(cur, 0)

#queryexecute_d(cur, 0)
#queryexecute_d(cur, 1)

def queryexecute_e(cur):
    cur.execute(
        """
        SELECT DISTINCT c1.name, c1.crse, c2.name, c2.crse
        FROM course c1 INNER JOIN course c2
        ON c1.mergenum = c2.mergenum AND c1.mergechar = 'A' and c2.mergechar = 'B'
        """
    )
    courses = cur.fetchall()
    for c in courses:
        print(str(c[0])+str(c[1])+ " merges with "+str(c[2])+str(c[3]))

def queryexecute_f(cur):
    cur.execute(
        """
    SELECT cast(SUM(R1.gpa)/SUM(R1.units) AS FLOAT) AS averagem, R1.major
FROM
  (
    SELECT *
    FROM
      (
        SELECT
          major,
          units,
          cid,
          studentscourseinfo.term_id,
          CASE
          WHEN grade = 'A+'
            THEN 4.0 * units
          WHEN grade = 'A'
            THEN 4.0 * units
          WHEN grade = 'A-'
            THEN 3.7 * units
          WHEN grade = 'B+'
            THEN 3.3 * units
          WHEN grade = 'B'
            THEN 3.0 * units
          WHEN grade = 'B-'
            THEN 2.7 * units
          WHEN grade = 'C+'
            THEN 2.3 * units
          WHEN grade = 'C'
            THEN 2.0 * units
          WHEN grade = 'C-'
            THEN 1.7 * units
          WHEN grade = 'D+'
            THEN 1.3 * units
          WHEN grade = 'D'
            THEN 1.0 * units
          WHEN grade = 'D-'
            THEN 0.7 * units
          WHEN grade = 'F'
            THEN 0.0 * units
          END AS gpa
        FROM studentscourseinfo
          INNER JOIN students ON studentscourseinfo.sid = students.sid
        WHERE grade != 'P' AND grade != 'I' AND grade != 'NS'
              AND grade != '' AND grade != 'U' AND grade != 'NG'
              AND grade != 'S' AND grade != 'IP' AND grade != 'Y'
              AND grade != 'WN' AND grade != 'NP' AND grade != 'WD1'
              AND grade != 'WD2' AND grade != 'W10' AND grade != 'WI'
              AND grade != 'W04' AND grade != 'WD4' AND grade != 'XR'
              AND grade != 'WDC'
      ) AS R2 INNER JOIN course ON course.term_id = R2.term_id AND course.cid = R2.cid
    WHERE course.name = 'ABC'
  ) R1
GROUP BY R1.major
ORDER BY averagem
        """
    )
    grades = []
    row = cur.fetchall()
    for r in row:
        print(r)
        grades.append(r[0])
    maxavg = max(grades)
    minavg = min(grades)
    for l in row:
        if row[0] == maxavg:
            print("Best majors: "+ str(row[0]))
        elif row[0] == minavg:
            print("Worst majors: "+ str(row[0]))

def queryexecute_a(cur):
    cur.execute = (
        """
        SELECT
  units,
  AVG(percentage) AS avg
FROM (
       SELECT
         units,
         (r1.sid * 100) / r2.sid AS percentage,
         r1.term_id              AS term
       FROM (
              SELECT
                units,
                term_id,
                count(*) sid
              FROM studentscourseinfo
              GROUP BY units,term_id
            ) r1
         JOIN (
                SELECT
                  term_id,
                  count(*) sid
                FROM studentscourseinfo
                GROUP BY term_id
              ) r2
           ON r1.term_id = r2.term_id
     ) AS answer
GROUP BY units;
        """
    )
def queryexecute_b(cur):
    cur.execute = (
        """
        SELECT
  units,
  AVG(percentage) AS avg
FROM (
       SELECT
         units,
         (r1.sid * 100) / r2.sid AS percentage,
         r1.term_id              AS term
       FROM (
              SELECT
                units,
                term_id,
                count(*) sid
              FROM studentscourseinfo
              GROUP BY units,term_id
            ) r1
         JOIN (
                SELECT
                  term_id,
                  count(*) sid
                FROM studentscourseinfo
                GROUP BY term_id
              ) r2
           ON r1.term_id = r2.term_id
     ) AS answer
GROUP BY units;
        """
    )

#queryexecute_f(cur)