import sklearn
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction import DictVectorizer
import math



def classify():

	# read in the data set written by the server
	res = pd.read_csv("domains.csv")

	# data for my stuff
	# organize data this is y
	labels = np.asarray(res['one time'])
	
	res_selected = res.drop(['url','one time', 'format fields'], axis=1) # 'longest subdomain', 'domain length'
	#print(res_selected)
	res_features = res_selected.to_dict(orient='records')
	vec = DictVectorizer()
	features = vec.fit_transform(res_features).toarray()
	
	
	# this is X
	print(features)	
	
	# testing and training
	features_train, features_test, labels_train, labels_test = train_test_split(
	features, labels, 
	test_size=0.33, random_state=42)
	
	# choose a classifier
	# init
	clf = RandomForestClassifier(n_estimators =100) # min_samples_split=4
	# train using training data
	clf.fit(features_train, labels_train)
	y_pred = clf.predict(features_test)
	
	print("Accuracy: ", (labels_test, y_pred))
	
	# compute accuracy
	accuracy_test = clf.score(features_test,labels_test)
	accuracy_train = clf.score(features_train, labels_train)
	print("Testing accuracy:", accuracy_test)
	print("Training accuracy:", accuracy_train)
	
	# finding important features
	
	feature_names = ['entropy','domain length','longest subdomain','unusual length']
	
	feature_imp = pd.Series(clf.feature_importances_, index=feature_names).sort_values(ascending=False)
	print("features")
	print(feature_imp)
	
	# plot the important features

	sns.barplot(x=feature_imp,y=feature_imp.index)	
	plt.gcf().set_size_inches(6,3.5)
	plt.xlabel("Feature Importance Score", fontsize=8)
	plt.ylabel("Features", fontsize=8)
	plt.title("Distinguishing One Time Features", fontsize=10)
	plt.legend()
	plt.show()
	



# will only run if script run from command line, not if imported
if __name__ == "__main__":
	classify()
