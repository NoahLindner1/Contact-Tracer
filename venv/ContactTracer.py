import sqlite3
from sqlite3 import Error

from flask import Flask
from flask import abort
from flask import request

app = Flask(__name__) 

# get all people
@app.route("/people")
def getPeople():
	people = []
	conn = None

	try:
		conn = sqlite3.connect("./dbs/ContactTracer.db")
		conn.row_factory = sqlite3.Row
		sql = """
			SELECT Person.first, Person.Last
			FROM Person
			ORDER BY Person.Last
		"""
		cursor = conn.cursor()
		cursor.execute(sql)
		rows = cursor.fetchall()

		for row in rows:
			being = {"first": row["first"],"last": row["last"]}
			people.append(being)

	except Error as e:
		print(f"Error opening the database {e}")
	finally:
		if conn:
			conn.close()

	return {"People": people }

#Route that gets all the diseases in the DB
@app.route("/Disease")
def getDiseases():
	Diseases = []
	conn = None

	try:
		conn = sqlite3.connect("./dbs/ContactTracer.db")
		conn.row_factory = sqlite3.Row
		sql = """
			SELECT Disease.ID, Disease.Name
			FROM Disease
			ORDER BY Disease.ID
		"""
		cursor = conn.cursor()
		cursor.execute(sql)
		rows = cursor.fetchall()

		for row in rows:
			DiseaseType = {"ID": row["ID"], "Name": row["Name"]}
			Diseases.append(DiseaseType)
	except Error as e:
		print(f"Error opening the database {e}")
	finally:
		if conn:
			conn.close()
	return {"Disease": Diseases}

#Get who has had a specified disease and what their symptoms were
@app.route("/Disease/<int:DiseaseID>")
def getSpecificDiseaseInfo(DiseaseID):
	DiseaseInfo = {"First": "","Last": "", "Name": "","DatePositive": "","Type": "","Description": "", "DateGotten": ""}
	conn = None

	try:
		conn = sqlite3.connect("./dbs/ContactTracer.db")
		conn.row_factory = sqlite3.Row
		sql = """
			SELECT Person.First,person.Last, Disease.Name, PersonHasDisease.DatePositive,symptom.Type,symptom.Description,PersonHasSymptom.DateGotten
			FROM PersonHasDisease,Person,Disease, PersonHasSymptom, symptom
			WHERE PersonHasDisease.DiseaseID = ?
			AND PersonHasDisease.PersonID = Person.ID
			AND Disease.ID = PersonHasDisease.DiseaseID
			AND PersonHasSymptom.SymptomID = symptom.id
		"""
		cursor = conn.cursor()
		cursor.execute(sql, (DiseaseID,))
		rows = cursor.fetchall()

		if(len(rows) == 0):
			abort(404)
		else:
			firstRow = True
			for row in rows:
				if(firstRow):
					DiseaseInfo["First"] = row["First"]
					DiseaseInfo["Last"] = row["Last"]
					DiseaseInfo["Name"] = row["Name"]
					DiseaseInfo["DatePositive"] = row["DatePositive"]
					DiseaseInfo["Type"] = row["Type"]
					DiseaseInfo["Description"] = row["Description"]
					DiseaseInfo["DateGotten"] = row["DateGotten"]
	except Error as e:
		print(f"Error opening the databse {e}")
		abort(500)
	finally:
		if conn:
			conn.close()
	return DiseaseInfo

#Contacts in a timeframe
@app.route("/contacts/between/<firstDate>/and/<secondDate>")
def getContactsBetweenDates(firstDate, secondDate):
	contacts = []
	conn = None
	try:
		conn = sqlite3.connect("./dbs/ContactTracer.db")
		conn.row_factory = sqlite3.Row
		sql = """
			SELECT Person.First, Person.Last, ComesInContact.InitiatorID, ComesInContact.ExposedID, ComesInContact.Date
			FROM ComesInContact,Person, PersonHasDisease
			WHERE date(ComesInContact.date) >= date(?)
			AND date(ComesInContact.date) <= date(?)
			AND Person.ID = ComesInContact.initiatorID
		"""
		cursor = conn.cursor()
		cursor.execute(sql, (firstDate,secondDate))
		rows = cursor.fetchall()

		for row in rows:
			contacts.append({"First": row["First"],"Last": row["Last"],"InitiatorID": row["InitiatorID"],"ExposedID": row["ExposedID"],"Date": row["Date"]})
	except Error as e:
		print(f"Error opening the database {e}")
		abort(500)
	finally:
		if conn:
			conn.close()
	
	return{"contacts": contacts}
	




#add a new person
@app.route("/person/new", methods = ["POST"])
def addPerson():
	newPerson = {}
	conn = None
	try:
		jsonPostData = request.get_json() 
		First = jsonPostData["First"]
		Last = jsonPostData["Last"]
		DOB = jsonPostData["DOB"]
		Phone = jsonPostData["Phone"]

		conn = sqlite3.connect("./dbs/ContactTracer.db")
		conn.row_factory = sqlite3.Row
		sql = """
			INSERT INTO Person(First,Last,DOB,Phone) VALUES (?,?,?,?)
		"""
		cursor = conn.cursor()
		cursor.execute(sql,(First,Last,DOB,Phone))
		conn.commit()
		sql = """
			SELECT Person.id,Person.First, Person.Last, Person.DOB, Person.Phone
			FROM Person
			Where Person.id = ?
		"""
		cursor.execute(sql, (cursor.lastrowid,))
		row = cursor.fetchone()
		newPerson["id"] = row["id"]
		newPerson["First"] = row["First"]
		newPerson["Last"] = row["Last"]
		newPerson["DOB"] = row["DOB"]
		newPerson["Phone"] = row["Phone"]
	except Error as e:
		print(f"Error opening the database{e}")
		abort(500)
	finally:
		if conn:
			conn.close()
	
	return newPerson

#add a new disease
@app.route("/Disease/new", methods = ["POST"])
def addDisease():
	newDisease = {}
	conn = None
	try:
		jsonPostData = request.get_json()
		Name = jsonPostData["Name"]

		conn = sqlite3.connect("./dbs/ContactTracer.db")
		conn.row_factory = sqlite3.Row
		sql = """
			INSERT INTO Disease (Name) VALUES (?)
		"""
		cursor = conn.cursor()
		cursor.execute(sql,(Name,))
		conn.commit()
		sql = """
			SELECT Disease.ID, Disease.Name
			From Disease
			Where Disease.ID = ?
		"""
		cursor.execute(sql,(cursor.lastrowid,))
		row = cursor.fetchone()
		newDisease["ID"] = row["ID"]
		newDisease["Name"] = row["Name"]
	except Error as e:
		print(f"Error opening the database {e}")
		abort(500)
	finally:
		if conn:
			conn.close()

	return newDisease

#add a new symptom
@app.route("/Symptom/new", methods = ["POST"])
def addSymptom():
	newSymptom = {}
	conn = None
	try:
		jsonPostData = request.get_json()
		Type = jsonPostData["Type"]
		Description = jsonPostData["Description"]

		conn = sqlite3.connect("./dbs/ContactTracer.db")
		conn.row_factory = sqlite3.Row
		sql = """
			INSERT INTO symptom (Type, Description) VALUES (?,?)
		"""
		cursor = conn.cursor()
		cursor.execute(sql,(Type,Description))
		conn.commit()
		sql = """
			SELECT symptom.id, symptom.Type, symptom.Description
			FROM symptom
			WHERE symptom.id = ?
		"""
		cursor.execute(sql,(cursor.lastrowid,))
		row = cursor.fetchone()
		newSymptom["id"] = row["id"]
		newSymptom["Type"] = row["Type"]
		newSymptom["Description"] = row["Description"]
	except Error as e:
		print(f"Error opening the database {e}")
	finally:
		if conn:
			conn.close()

	return newSymptom

#new contact
@app.route("/Contact/new", methods = ["POST"])
def addContact():
	newContact = {}
	conn = None
	try:
		jsonPostData = request.get_json()
		Date = jsonPostData["Date"]
		InitiatorID = jsonPostData["InitiatorID"]
		ExposedID = jsonPostData["ExposedID"]

		conn = sqlite3.connect("./dbs/ContactTracer.db")
		conn.row_factory = sqlite3.Row
		sql = """
			INSERT INTO ComesInContact (Date, InitiatorID, ExposedID) VALUES (?,?,?)
		"""
		cursor = conn.cursor()
		cursor.execute(sql, (Date,InitiatorID,ExposedID))
		conn.commit()
		sql = """
			SELECT ComesInContact.ID, ComesInContact.Date, ComesInContact.InitiatorID, ComesInContact.ExposedID
			FROM ComesInContact
			WHERE ComesIncontact.ID = ?
		"""

		cursor.execute(sql,(cursor.lastrowid,))
		row = cursor.fetchone()
		newContact["ID"] = row["ID"]
		newContact["Date"] = row["Date"]
		newContact["InitiatorID"] = row["InitiatorID"]
		newContact["ExposedID"] = row["ExposedID"]
	except Error as e:
		print(f"Error opening the database {e}")
	finally:
		if conn:
			conn.close()

	return newContact


#add a new positive case
@app.route("/Positive", methods = ["POST"])
def addPositive():
	newPositive = {}
	conn = None
	try:
		jsonPostData = request.get_json()
		PersonID = jsonPostData["PersonID"]
		DiseaseID = jsonPostData["DiseaseID"]
		DatePositive = jsonPostData["DatePositive"]

		conn = sqlite3.connect("./dbs/ContactTracer.db")
		conn.row_factory = sqlite3.Row
		sql = """
			INSERT INTO PersonHasDisease (PersonID,DiseaseID,DatePositive) VALUES (?,?,?)
		""" 
		cursor = conn.cursor()
		cursor.execute(sql, (PersonID,DiseaseID,DatePositive))
		conn.commit()
		sql = """
			SELECT PersonHasDisease.PersonID, PersonHasDisease.DiseaseID, DatePositive
			FROM PersonHasDisease
			WHERE PersonHasDisease.PersonID = ?
		"""

		cursor.execute(sql,(cursor.lastrowid,))
		row = cursor.fetchone()
		newPositive["PersonID"] = row["PersonID"]
		newPositive["DiseaseID"] = row["DiseaseID"]
		newPositive["DatePositive"] = row["DatePositive"]
	except Error as e:
		print(f"Error opening the database {e}")
	finally:
		if conn:
			conn.close()

	return newPositive

#add a new symptom for a person
@app.route("/symptom/person/new", methods = ["POST"])
def addPersonsSymptom():
	newPersonsSymptom = {}
	conn = None
	try:
		jsonPostData = request.get_json()
		PersonID = jsonPostData["PersonID"]
		SymptomID = jsonPostData["SymptomID"]
		DateGotten = jsonPostData["DateGotten"]

		conn = sqlite3.connect("./dbs/ContactTracer.db")
		conn.row_factory = sqlite3.Row
		sql = """
			INSERT INTO PersonHasSymptom (PersonID,SymptomID,DateGotten) VALUES (?,?,?)
		"""
		cursor = conn.cursor()
		cursor.execute(sql, (PersonID,SymptomID,DateGotten))
		conn.commit()
		sql = """
			SELECT PersonHasSymptom.PersonID, PersonHasSymptom.SymptomID, PersonHasSymptom.DateGotten
			FROM PersonHasSymptom
			WHERE PersonHasSymptom.PersonID = ?
		"""

		cursor.execute(sql,(cursor.lastrowid,))
		row = cursor.fetchone()
		newPersonsSymptom["PersonID"] = row["PersonID"]
		newPersonsSymptom["SymptomID"] = row["SymptomID"]
		newPersonsSymptom["DateGotten"] = row["DateGotten"]

	except Error as e:
		print(f"Error opening the databse {e}")
	finally:
		if conn:
			conn.close()

	return newPersonsSymptom

	