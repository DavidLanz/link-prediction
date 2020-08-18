# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.5.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# # Train and test datasets 
#
# Now that we've decided we're going to use a machine learning approach, we need to come up with train and test datasets on which we can build, and then evaluate a model.
#
# ### Positive examples
#
# The tricky thing when working with graph data is that we can't just randomly split the data, as this could lead to data leakage.
#
# Data leakage can occur when data outside of your training data is inadvertently used to create your model. This can easily happen when working with graphs because pairs of nodes in our training set may be connected to those in the test set.
#
# When we compute link prediction measures over that training set the __measures computed contain information from the test set__ that we’ll later evaluate our model against.
#
# Instead we need to split our graph into training and test sub graphs. If our graph has a concept of time our life is easy — we can split the graph at a point in time and the training set will be from before the time, the test set after.
#
# This is still not a perfect solution and we’ll need to try and ensure that the general network structure in the training and test sub graphs is similar.
#
# Once we’ve done that we’ll have pairs of nodes in our train and test set that have relationships between them. They will be the __positive examples__ in our machine learning model.
#
# We are lucky that our citation graph contains a times. We can create train and test graphs by splitting the data on a particular year. Now we need to figure out what year that should be. Let's have a look at the distribution of the first year that co-authors collaborated:

# +
from neo4j import GraphDatabase

# tag::imports[]
import pandas as pd
import matplotlib 
import matplotlib.pyplot as plt

plt.style.use('fivethirtyeight')
pd.set_option('display.float_format', lambda x: '%.3f' % x)
# end::imports[]

# +
bolt_uri = "bolt://link-prediction-neo4j"
driver = GraphDatabase.driver(bolt_uri, auth=("neo4j", "admin"))

print(driver.address)
# -

# We can create the co-author graph by running the query below to do this:

# +
# tag::determine-split[]
query = """
MATCH p=()-[r:CO_AUTHOR]->() 
WITH r.year AS year, count(*) AS count
ORDER BY year
RETURN toString(year) AS year, count
"""

with driver.session(database="neo4j") as session:
    result = session.run(query)
    by_year = pd.DataFrame([dict(record) for record in result])

ax = by_year.plot(kind='bar', x='year', y='count', legend=None, figsize=(15,8))
ax.xaxis.set_label_text("")
plt.tight_layout()
plt.show()
# end::determine-split[]
# -

# Now that we've created our co-author graph, we want to come up with an approach that will allow us to predict future links (relationships) that will be created between people.