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
import sklearn.decomposition as dec
import sklearn.manifold as man
import matplotlib.pylab as plt
import numpy as np
from sklearn.preprocessing import StandardScaler
import heapq
from operator import itemgetter
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

MONGODB_HOST = "localhost"
MONGODB_PORT = 27017
DBS_NAME = "lab2"
COLLECTION_NAME = "produce"
FIELDS = {"state": True, "year": True, "pcap": True, "hwy": True, "water": True,"util": True,"emp": True,"unemp": True, "_id": False}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/cluster")
def cluster():
    return render_template("cluster_plots.html")

@app.route("/scatter")
def scatter():
    return render_template("scatter_plot.html")

@app.route("/lab2/sample")
def lab2_sample():
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
    collection = connection[DBS_NAME][COLLECTION_NAME]
    #projects = collection.find(projection=FIELDS, limit=1000)
    projects = collection.find(projection=FIELDS)
    json_projects = []
    f = open("static/data/random.csv", "w", newline="")
    fs = open("static/data/stratified.csv", "w", newline="")

    for project in projects:
        json_projects.append(project)
    json_projects = json.dumps(json_projects, default=json_util.default)
    df = pandas.read_json(json_projects)
    del df['_id']
    rand_df = df.sample(frac=0.7)
    rand_df.to_csv(f)
    numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
    dataset = df.select_dtypes(include=numerics)
    plotd = {}
    for i in range(1, 10):
        km = clt.KMeans(n_clusters=i).fit(dataset)
        iner = km.inertia_
        plotd[i] = iner
    lists = sorted(plotd.items())
    x, y = zip(*lists)
    plt.title('kmeans_elbow')
    plt.plot(x, y)
    plt.show()

    km = clt.KMeans(n_clusters=3).fit(dataset)
    df['label'] = km.labels_
    strat_df = df.groupby('label', as_index=False, group_keys=False).apply(lambda x: x.sample(frac=.7))
    #del strat_df['label']
    strat_df.sort_index().to_csv(fs, index=False)
    f.close()
    fs.close()
    connection.close()
    return render_template("index.html")

@app.route("/lab2/cluster/pca")
def pca_cluster():
    fs = open("static/data/stratified.csv", "r")
    numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
    fig = plt.figure()
    plotd = {}
    strat_df = pandas.read_csv(fs)
    print(strat_df)
    #PCA
    dataset_strat = strat_df.select_dtypes(include=numerics)
    del dataset_strat['Unnamed: 0']
    cols = list(dataset_strat.columns.values)
    print(cols)
    #dataset_strat.apply(pandas.to_numeric, errors='coerce')
    std_data = StandardScaler().fit_transform(dataset_strat)
    mean_vec = np.mean(std_data, axis=0)
    cov_mat = (std_data - mean_vec).T.dot((std_data - mean_vec)) / (std_data.shape[0]-1)
    #print(dataset_strat)
    cov_mat = np.cov(std_data.T)
    eigen_vals = np.linalg.eigvals(np.array(cov_mat))
    #plot eigen_vals
    plotd.clear()
    i = 1
    for v in eigen_vals:
        plotd[i] = v
        i+=1

    lists = sorted(plotd.items())
    x, y = zip(*lists)
    plt.subplot(121)
    plt.title('eigen_vals')
    plt.plot(x, y)

    col_eigen = {}
    for i in range(len(cols)):
        col_eigen[cols[i]] = eigen_vals[i]

    pca = dec.PCA(n_components=2)
    pca_cor = pca.fit(std_data).components_
    pca_mat = pca.fit_transform(std_data)
    pca_dict = {}
    #plot pca_vals
    plotd.clear()
    for i in range(len(pca_cor[0])):
        plotd[i] = pca_cor[0][i] * pca_cor[0][i] + pca_cor[1][i] * pca_cor[1][i]

    lists = plotd.items()
    x, y = zip(*lists)
    plt.subplot(122)
    plt.title('pca_vals')
    plt.plot(x, y)

    pca_d = {}
    for i in range(len(pca_mat)):
        pca_d[i] = {'x':pca_mat[i][0], 'y':pca_mat[i][1], 'label':int(dataset_strat['label'].iloc[i])}
    #print(pca_d)
    pca_json = json.dumps(pca_d)

    fs.close()
    plt.show()
    return pca_json

@app.route("/lab2/cluster/mds")
def mds_cluster():
    fs = open("static/data/stratified.csv", "r")
    numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']

    strat_df = pandas.read_csv(fs)
    dataset_strat = strat_df.select_dtypes(include=numerics)
    del dataset_strat['Unnamed: 0']
    cols = list(dataset_strat.columns.values)
    print(cols)
    #dataset_strat.apply(pandas.to_numeric, errors='coerce')
    std_data = StandardScaler().fit_transform(dataset_strat)

    #MDS
    #correlattion
    # mds_corr = 1 - cosine_similarity(std_data)
    # mds = man.MDS(n_components=2, dissimilarity='precomputed')
    # mds_mat = mds.fit(mds_corr).embedding_

    #euclidean
    mds = man.MDS(n_components=2, dissimilarity='euclidean')
    mds_mat = mds.fit(std_data).embedding_

    mds_d = {}
    for i in range(len(mds_mat)):
        mds_d[i] = {'x':mds_mat[i][0], 'y':mds_mat[i][1], 'label':int(dataset_strat['label'].iloc[i])}
    #print(pca_d)
    mds_json = json.dumps(mds_d)

    fs.close()
    plt.show()
    return mds_json

@app.route("/lab2/scatter")
def lab2_scatter():
    connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
    collection = connection[DBS_NAME][COLLECTION_NAME]
    projects = collection.find(projection=FIELDS)
    json_projects = []
    ftop = open("static/data/top3.csv", "w", newline="")
    for project in projects:
        json_projects.append(project)
    json_projects = json.dumps(json_projects, default=json_util.default)
    df = pandas.read_json(json_projects)
    del df['_id']
    numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
    dataset = df.select_dtypes(include=numerics)

    km = clt.KMeans(n_clusters=3).fit(dataset)
    df['label'] = km.labels_

    #PCA
    dataset_strat = df.select_dtypes(include=numerics)
    del dataset_strat['']
    cols = list(dataset_strat.columns.values)
    print(cols)
    #dataset_strat.apply(pandas.to_numeric, errors='coerce')
    std_data = StandardScaler().fit_transform(dataset_strat)
    mean_vec = np.mean(std_data, axis=0)
    cov_mat = (std_data - mean_vec).T.dot((std_data - mean_vec)) / (std_data.shape[0]-1)
    #print(dataset_strat)
    cov_mat = np.cov(std_data.T)
    eigen_vals = np.linalg.eigvals(np.array(cov_mat))

    col_eigen = {}
    for i in range(len(cols)):
        col_eigen[cols[i]] = eigen_vals[i]

    pca = dec.PCA(n_components=2)
    pca_cor = pca.fit(std_data).components_
    pca_mat = pca.fit_transform(std_data)
    pca_dict = {}
    #plot pca_vals
    for i in range(len(pca_cor[0])):
        pca_dict[cols[i]] = pca_cor[0][i] * pca_cor[0][i] + pca_cor[1][i] * pca_cor[1][i]

    top_pca = dict(heapq.nlargest(3, pca_dict.items(), key=itemgetter(1)))
    print(top_pca)

    #top 3 to csv
    new_df = df.filter(list(top_pca.keys()))
    new_df['label'] = df['label']
    new_df.to_csv(ftop, index=False)
    connection.close()
    ftop.close()
    return new_df.T.to_json()

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000,debug=True)
