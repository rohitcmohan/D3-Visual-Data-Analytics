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
import numpy as np
from sklearn.preprocessing import StandardScaler

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
    fs = open("static/data/stratified.csv", "w", newline="")
    # k = ["","_id","state","year","region","pcap","hwy","water","util","pc","gsp","emp","unemp"]
    # writer = csv.DictWriter(f, fieldnames=k)
    # writer.writeheader()
    for project in projects:
        # if(random.random() > 0.3):
        #     writer.writerow(project)
        json_projects.append(project)

    json_projects = json.dumps(json_projects, default=json_util.default)
    df = pandas.read_json(json_projects)
    del df['_id']
    rand_df = df.sample(frac=0.7)
    rand_df.to_csv(f)
    numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
    dataset = df.select_dtypes(include=numerics)
    plotd = {}
    # for i in range(1, 10):
    #     km = clt.KMeans(n_clusters=i).fit(dataset)
    #     iner = km.inertia_
    #     plotd[i] = iner
    # print(km.labels_)
    # lists = sorted(plotd.items())
    # x, y = zip(*lists)
    # plt.plot(x, y)
    # plt.show()
    km = clt.KMeans(n_clusters=3).fit(dataset)
    df['label'] = km.labels_
    strat_df = df.groupby('label', as_index=False, group_keys=False).apply(lambda x: x.sample(frac=.7))
    #del strat_df['label']
    strat_df.sort_index().to_csv(fs, index=False)

    #PCA
    dataset_strat = strat_df.select_dtypes(include=numerics)
    dataset_strat.apply(pandas.to_numeric, errors='coerce')
    std_data = StandardScaler().fit_transform(dataset_strat)
    mean_vec = np.mean(std_data, axis=0)
    cov_mat = (std_data - mean_vec).T.dot((std_data - mean_vec)) / (std_data.shape[0]-1)
    #print(std_data)
    cov_mat = np.cov(std_data.T)
    eigen_vals = np.linalg.eigvals(np.array(cov_mat))
    # print(eigen_vals)
    #plot eigen_vals
    # i = 1
    # for v in eigen_vals:
    #     plotd[i] = v
    #     i+=1
    # lists = sorted(plotd.items())
    # x, y = zip(*lists)
    # plt.plot(x, y)
    # plt.show()
    

    connection.close()
    return strat_df.transpose().to_json()

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000,debug=True)
