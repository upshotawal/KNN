
import re
import sqlite3 as sql
from flask import Flask, request, jsonify
import numpy as np
import json
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

# fetching the data from product model from django's sqlite database
products = pd.read_sql_query("SELECT * from store_product", connect)


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


@app.route('/get_recommendation', methods=['POST', 'GET'])
def get_recommendations_product(sig=sig):
    # get the name of the product from django app
    query = request.form.get("product_name")

    # Get the index corresponding to product title
    idx = indices[query]
    # Get the pairwsie similarity scores
    sig_scores = list(enumerate(sig[idx]))
    # Sort the products
    sig_scores = sorted(sig_scores, key=lambda x: x[1].all(), reverse=True)
    # Scores of the 5 most similar products
    sig_scores = sig_scores[1:6]

    product_indices = [i[0] for i in sig_scores]

    value = products['title'].iloc[product_indices]
    print(value)
    items = dict(value)
    print(items)
    return jsonify(items), 201


@app.route('/')
def index():
    return "sheesh"


if __name__ == "__main__":
    app.run(debug=True)
