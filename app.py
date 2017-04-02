from flask import Flask
from flask import render_template
from pymongo import MongoClient
import json
from bson import json_util
from bson.json_util import dumps
import csv
import random
import pandas
import sklearn.cluster as clt
import matplotlib.pylab as plt

app = Flask(__name__)

MONGODB_HOST = "localhost"
MONGODB_PORT = 27017
DBS_NAME = "lab2"
COLLECTION_NAME = "produce"
FIELDS = {"state": True, "year": True, "pcap": True, "hwy": True, "water": True,"util": True,"emp": True,"unemp": True, "_id": False}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/lab2/sample")
def lab2_produce():
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
    collection = connection[DBS_NAME][COLLECTION_NAME]
    #projects = collection.find(projection=FIELDS, limit=1000)
    projects = collection.find(projection=FIELDS)
    json_projects = []
    f = open("static/data/random.csv", "w", newline="")
    k = ["","_id","state","year","region","pcap","hwy","water","util","pc","gsp","emp","unemp"]
    writer = csv.DictWriter(f, fieldnames=k)
    writer.writeheader()
    for project in projects:
        if(random.random() > 0.3):
            writer.writerow(project)
        json_projects.append(project)

    json_projects = json.dumps(json_projects, default=json_util.default)
    df = pandas.read_json(json_projects)
    numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
    dataset = df.select_dtypes(include=numerics)
    plotd = {}
    for i in range(1, 10):
        km = clt.KMeans(n_clusters=i).fit(dataset)
        iner = km.inertia_
        plotd[i] = iner

    lists = sorted(plotd.items())
    x, y = zip(*lists)

    plt.plot(x, y)
    plt.show()

    connection.close()
    return json_projects

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000,debug=True)
