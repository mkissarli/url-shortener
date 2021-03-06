from quart import Quart, request, abort, redirect
from uuid import uuid4
import sqlite3
from sqlite3 import Error

def create_connection(path):
   connection = None
   try:
      connection = sqlite3.connect(path)
      print("Connection to SQLite DB successful")
   except Error as e:
      print(f"The error '{e}' occurred")
   return connection

connection = create_connection("redirects.sqlite")
   
create_redirects_table = """
CREATE TABLE IF NOT EXISTS redirects (
  id   TEXT(255) UNIQUE,
  path TEXT(255) UNIQUE
);
"""

connection.execute(create_redirects_table)
connection.commit()

app = Quart(__name__)

@app.route('/')
async def hello():
    return 'hello'
 
@app.route('/register', methods=['POST'])
async def register():
   test_data = await request.get_json()
   
   path = ""
   try:
      path = test_data["path"]
   except KeyError:
      abort(400, "Invalid path parameter. Please include a path parameter.")

   try:
      path = str(path)
   except TypeError:
      abort(400, "Invalid Path type. Path parameter cannot be stringified.")
   
   # Don't necessarily need this? So what if the url doesn't reach anywhere.
   if path[:7] != "http://" and path[:8] != "https://":
      abort(400, "Invalid path address. Please insure path starts with http:// or https://")

   link = ""

   new_uuid = True
   while new_uuid:
      try:
         link = str(uuid4())
         connection.cursor().execute("INSERT INTO redirects VALUES (?, ?)", (link, str(path)))
         connection.commit()
         new_uuid = False
      except sqlite3.IntegrityError as e:
         if(str(e).endswith("path") != "path"):
            link = connection.cursor().execute("SELECT id FROM redirects where path=?", (path,)).fetchall()[0][0]
            new_uuid = False

   return {"tiny_url":("localhost:5000/" + link)}

@app.route('/<path>', methods=['GET'])
async def redirect_path(path):
   val = connection.cursor().execute("SELECT path FROM redirects where id=?", (path,)).fetchall()
   if len(val) > 0:
      return redirect(val[0][0])
   else:
      abort(404, "We have not made a tiny url for that yet.")
      return "404"

app.run()
