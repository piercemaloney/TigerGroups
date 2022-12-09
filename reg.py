'''
Webapp for browsing Princeton course registrar
Authors: Pierce Maloney and Antonio Knez
'''
from flask import Flask, request, make_response, render_template
import query


#-----------------------------------------------------------------------

app = Flask(__name__, template_folder='.')

#-----------------------------------------------------------------------

DB_FILE = './reg.sqlite'

#-----------------------------------------------------------------------

TABLE_HEADER = """
<table class="table table-striped" id="resultstable">
    <a id="changeClasses"></a>
    <thead>
        <tr>
            <th scope="col"><strong>ClassId</strong></th>
            <th scope="col"><strong>Dept</strong></th>
            <th scope="col"><strong>Num</strong></th>
            <th scope="col"><strong>Area</strong></th>
            <th scope="col"><strong>Title</strong></th>
        </tr>
    </thead>
"""

# order of strings: classid, classid, dept, num, area, title
TABLE_ROW = """
<tr>
    <td><a href= '/regdetails?classid=%s' >%s</td>
    <td>%s</td>
    <td>%s</td>
    <td>%s</td>
    <td>%s</td>
</tr>
"""

#-----------------------------------------------------------------------


def load_classes(dept, num, area, title):
    """
    Loads classes from the SQL db and displays with Flask
    Handles errors in loading and forwards to regerror.html
    """
    classes = None
    try:
        classes = query.get_classes(DB_FILE, dept, num, area, title)
    except Exception as ex:
        html_code = f'<p>{str(ex)}</p>'
        return make_response(html_code)
    # create table header
    html_code = TABLE_HEADER
    # create body of table
    html_code += "<tbody>"
    for row in classes:
        html_code += TABLE_ROW % (row.get_class_id(),
            row.get_class_id(), row.get_dept(), row.get_num(),
            row.get_area(), row.get_title())
    html_code += "</tbody>"
    # close table
    html_code += "</table>"
    # html_code = render_template("reg.html", classes=classes, dept=dept,
    #         num=num, area=area, title=title)
    return make_response(html_code)

@app.route('/', methods=['GET'])
@app.route('/reg', methods=['GET'])
def load_reg():
    """
    Fetches user's cookies for previous queries
    """
    prev_dept = request.cookies.get('prev_dept')
    prev_num = request.cookies.get('prev_num')
    prev_area = request.cookies.get('prev_area')
    prev_title = request.cookies.get('prev_title')
    if prev_dept is None:
        prev_dept = ''
    if prev_num is None:
        prev_num = ''
    if prev_area is None:
        prev_area = ''
    if prev_title is None:
        prev_title = ''

    # response = load_classes(dept=prev_dept, num=prev_num,
    #         area=prev_area, title=prev_title)
    classes = None
    try:
        classes = query.get_classes(DB_FILE, prev_dept, prev_num, prev_area, prev_title)
    except Exception as ex:
        html_code = render_template("regerror.html", error=str(ex))
        return make_response(html_code)
    html_code = render_template('reg.html', classes=classes)
    return make_response(html_code)
    # return response


@app.route('/search', methods=['GET'])
def load_results():
    """
    Displays the page if a search has been entered
    """
    dept = request.args.get('dept')
    num = request.args.get('coursenum')
    area = request.args.get('area')
    title = request.args.get('title')
    print("This line is reached 1")
    print(dept)
    print(num)
    print(area)
    print(title)
    if dept is None:
        dept = ''
    if num is None:
        num = ''
    if area is None:
        area = ''
    if title is None:
        title = ''

    response = load_classes(dept, num, area, title)

    # set cookies
    response.set_cookie('prev_dept', dept)
    response.set_cookie('prev_num', num)
    response.set_cookie('prev_area', area)
    response.set_cookie('prev_title', title)

    return response


@app.route('/regdetails', methods=['GET'])
def load_details():
    """
    Displays the reg details page when a class has been selected
    """
    class_id = request.args.get('classid')

    try:
        class_details, course_details = query.get_details(DB_FILE,
                                            class_id)
    except Exception as ex:
        html_code = render_template("regerror.html", error=str(ex))
        return make_response(html_code)

    html_code = render_template("regdetails.html",
            class_details=class_details, course_details=course_details)
    response = make_response(html_code)
    return response
