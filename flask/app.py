
import re
import sqlite3 as sql
from flask import Flask, request, jsonify
import numpy as np
import json
import scipy as sp
from sklearn.metrics import recall_score
from sklearn.metrics.pairwise import cosine_similarity
import operator
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import sigmoid_kernel
import pandas as pd
import json
from config import DATABASE_PATH

app = Flask(__name__)

# connect to database from folder FYP project
connect = sql.connect(DATABASE_PATH)

database_table = pd.read_sql_query(
    "SELECT name FROM sqlite_master WHERE type='table'", connect)
print(database_table)

# fetching the data from models from django's sqlite database
products = pd.read_sql_query("SELECT * from store_product", connect)
users = pd.read_sql_query("SELECT * from auth_user", connect)
ratings = pd.read_sql_query("SELECT * from store_rating", connect)


# apply content based filtering
tfv = TfidfVectorizer(min_df=3,  max_features=None,
                      strip_accents='unicode', analyzer='word', token_pattern=r'\w{1,}',
                      ngram_range=(1, 3),
                      stop_words='english')

tfv_matrix = tfv.fit_transform(products['title'])
# print(tfv_matrix.shape)

sig = sigmoid_kernel(tfv_matrix, tfv_matrix)
indices = pd.Series(products.index, index=products['title']).drop_duplicates()
# print(indices)

# content based filtering


# applying KNN fitering
data_rating = pd.read_sql_query("SELECT * from store_rating", connect)
products = pd.read_sql_query("SELECT * from store_product", connect)
pivoted_data = data_rating.pivot_table(
    index='product_id', columns='user_id', values='rate').fillna(0)
features = csr_matrix(pivoted_data.values)


model = NearestNeighbors(metric='cosine', algorithm='brute')
model.fit(features)

# KNN filteringS


@app.route('/get_recommendation', methods=['POST', 'GET'])
def get_recommendations_product(sig=sig):
    # get the name of the product from django app
    query = request.form.get("product_name")

    # Get the index corresponding to product title
    idx = indices[query]
    # Get the pairwsie similarity scores
    sig_scores = list(enumerate(sig[idx]))

    # Sort the products
    sig_scores = sorted(sig_scores, key=lambda x: x[1], reverse=True)
    # sig_scores = sorted(sig_scores, key=lambda x: x[1].all(), reverse=True)

    # Scores of the 5 most similar products
    sig_scores = sig_scores[1:8]

    product_indices = [i[0] for i in sig_scores]

    value = products['title'].iloc[product_indices]
    print(value)
    items = dict(value)
    print(items)
    return jsonify(items), 201


# Applying Corelation Matrix ///////////
# collaborative filtering
product_df = pd.DataFrame(products)
product_df.rename(columns={'id': 'product_id'}, inplace=True)
product_df.head(2)
# print(product_df)

# merging the ratings and products column for getting the ratings and product title
merged = product_df.merge(ratings, left_on='product_id', right_on='product_id')

# only taking the required column
merged = merged[['user_id', 'title', 'rate']]
# print(merged)

piv = merged.pivot_table(index=['user_id'], columns=[
                         'title'], values='rate')
# print(piv)

# Note: As we are subtracting the mean from each rating to standardize
# all users with only one rating or who had rated everything the same will be dropped

# Normalize the values
piv_norm = piv.apply(lambda x: (x-np.mean(x))/(np.max(x)-np.min(x)), axis=1)


# Drop all columns containing only zeros representing users who did not rate
piv_norm.fillna(0, inplace=True)
piv_norm = piv_norm.T
piv_norm = piv_norm.loc[:, (piv_norm != 0).any(axis=0)]
print(piv_norm)

# Our data needs to be in a sparse matrix format to be read by the following functions

piv_sparse = sp.sparse.csr_matrix(piv_norm.values)
print(piv_sparse)

item_similarity = cosine_similarity(piv_sparse)
user_similarity = cosine_similarity(piv_sparse.T)

# Inserting the similarity matricies into dataframe objects

item_sim_df = pd.DataFrame(
    item_similarity, index=piv_norm.index, columns=piv_norm.index)
user_sim_df = pd.DataFrame(
    user_similarity, index=piv_norm.columns, columns=piv_norm.columns)


# Corelation Matrix////////////////////


@app.route('/get_user_recommendation', methods=['POST', 'GET'])
def similar_user_recs(user):
    if user not in piv_norm.columns:
        return('No data available on user {}'.format(user))

    sim_users = user_sim_df.sort_values(by=user, ascending=False).index[1:11]
    best = []
    most_common = {}

    for i in sim_users:
        max_score = piv_norm.loc[:, i].max()
        best.append(piv_norm[piv_norm.loc[:, i] == max_score].index.tolist())
    for i in range(len(best)):
        for j in best[i]:
            if j in most_common:
                most_common[j] += 1
            else:
                most_common[j] = 1
    sorted_list = sorted(most_common.items(),
                         key=operator.itemgetter(1), reverse=True)
    return sorted_list[:5]


@app.route('/user_recommendation', methods=['POST', 'GET'])
def user_recommendation(piv_norm=piv_norm, user_sim_df=user_sim_df,):
    rec = request.form.get('user_id')
    # got the user id from django, response 200, OK
    print(rec)

    return jsonify((similar_user_recs(rec))), 201


# @app.route('/recommend',methods=["POST","GET"])
# def hello_world():
#     users = request.form.get("user_id")
#     user_id = int(users)


#     distances,indices = model.kneighbors(pivoted_data.iloc[user_id,:].values.reshape(1,-1),n_neighbors=7)

#     recommended_items = set()
#     recommend_dict = dict()
#     newdic = dict()
#     for i in range(0,len(distances.flatten())):
#         if i == 0:
#             print('Recommendations for {0}:\n'.format(pivoted_data.index[user_id]))
#         else:
#             print('{0}: {1}, with distance of {2}:'.format(i, pivoted_data.index[indices.flatten()[i]],distances.flatten()[i]))
#             recommend_dict.update({i: pivoted_data.index[indices.flatten()[i]]})

#             recommended_items.add(pivoted_data.index[indices.flatten()[i]])
#     print(recommend_dict.items())
#     for k, v in recommend_dict.items():
#         newdic[str(k)]=str(v)

#     items = tuple(recommended_items)
#     recommended = '{}'.format(recommend_dict)
#     value = jsonify(newdic)

#     return value

@app.route('/')
def index():
    return "yolo"


if __name__ == "__main__":
    app.run(debug=True)
