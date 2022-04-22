
import re
import sqlite3 as sql
from flask import Flask, request, jsonify
import numpy as np
import json
import scipy as sp
from sklearn.metrics.pairwise import cosine_similarity
import operator
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
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
print(tfv_matrix.shape)

sig = sigmoid_kernel(tfv_matrix, tfv_matrix)
indices = pd.Series(products.index, index=products['title']).drop_duplicates()
print(indices)

# content based filtering


# collaborative fitering


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


# @app.route('/get_userrecommendation', methods=['POST', 'GET'])
# def makin_table():
#     product = request.form.get("product_name")
#     user = request.form.get("user_name")
#     rating = request.form.get("rating")

#     merged = ratings[['user', 'product', 'rating']]
#     piv = merged.pivot_table(index=['user_id'], columns=[
#         'name'], values='user_rating')
#     piv_norm = piv.apply(lambda x: (x-np.mean(x)) /
#                          (np.max(x)-np.min(x)), axis=1)
#     piv_norm.fillna(0, inplace=True)
#     piv_norm = piv_norm.T
#     piv_norm = piv_norm.loc[:, (piv_norm != 0).any(axis=0)]

#     piv_sparse = sp.sparse.csr_matrix(piv_norm.values)

#     item_similarity = cosine_similarity(piv_sparse)
#     user_similarity = cosine_similarity(piv_sparse.T)

#     item_sim_df = pd.DataFrame(
#         item_similarity, index=piv_norm.index, columns=piv_norm.index)
#     user_sim_df = pd.DataFrame(
#         user_similarity, index=piv_norm.columns, columns=piv_norm.columns)
#     return item_sim_df, user_sim_df, piv_norm, piv_sparse, piv

# # This function will return the top 10 shows with the highest cosine similarity value


# def top_products(product_name, item_sim_df):
#     product_name = request.form.get("product_name")
#     count = 1
#     print('Similar shows to {} include:\n'.format(product_name))
#     for item in item_sim_df.sort_values(by=product_name, ascending=False).index[1:11]:
#         print('No. {}: {}'.format(count, item))
#         count += 1

# # This function will return the top 5 users with the highest similarity value


# def top_users(user, piv_norm, user_sim_df):
#     user = request.form.get("user_name")

#     if user not in piv_norm.columns:
#         return('No data available on user {}'.format(user))

#     print('Most Similar Users:\n')
#     sim_values = user_sim_df.sort_values(
#         by=user, ascending=False).loc[:, user].tolist()[1:11]
#     sim_users = user_sim_df.sort_values(by=user, ascending=False).index[1:11]
#     zipped = zip(sim_users, sim_values,)
#     for user, sim in zipped:
#         print('User #{0}, Similarity value: {1:.2f}'.format(user, sim))


# # This function constructs a list of lists containing the highest rated shows per similar user
# # and returns the name of the show along with the frequency it appears in the list

# def similar_user_rec(user, piv_norm, user_sim_df):

#     if user not in piv_norm.columns:
#         return('No data available on user {}'.format(user))

#     sim_users = user_sim_df.sort_values(by=user, ascending=False).index[1:11]
#     best = []
#     most_common = {}

#     for i in sim_users:
#         max_score = piv_norm.loc[:, i].max()
#         best.append(piv_norm[piv_norm.loc[:, i] == max_score].index.tolist())
#     for i in range(len(best)):
#         for j in best[i]:
#             if j in most_common:
#                 most_common[j] += 1
#             else:
#                 most_common[j] = 1
#     sorted_list = sorted(most_common.items(),
#                          key=operator.itemgetter(1), reverse=True)
#     return sorted_list[:5]

# # This function calculates the weighted average of similar users
# # to determine a potential rating for an input user and show


# def predicted_rating(product_name, user, user_sim_df, piv):
#     sim_users = user_sim_df.sort_values(by=user, ascending=False).index[1:1000]
#     user_values = user_sim_df.sort_values(
#         by=user, ascending=False).loc[:, user].tolist()[1:1000]
#     rating_list = []
#     weight_list = []
#     for j, i in enumerate(sim_users):
#         rating = piv.loc[i, product_name]
#         similarity = user_values[j]
#         if np.isnan(rating):
#             continue
#         elif not np.isnan(rating):
#             rating_list.append(rating*similarity)
#             weight_list.append(similarity)
#     return sum(rating_list)/sum(weight_list)


# def get_recommendations_user(similar_user_rec):
#     similar_user_recs = similar_user_rec(4)
#     return jsonify(similar_user_recs), 201


@app.route('/')
def index():
    return "yolo"


if __name__ == "__main__":
    app.run(debug=True)
