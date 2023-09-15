import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

df1 = pd.read_csv('/Users/noah/Desktop/image-data-creation/created_attributes.csv')
df2 = pd.read_csv('/Users/noah/Desktop/image-data-creation/created_attributes_og.csv')

def graph_histogram(column_name):
	list1 = df1[column_name]
	list2 = df2[column_name]

	# Create a histogram for the data from the first file
	plt.hist(list1, bins=10, alpha=0.5, label='Newly Created Data')

	# Create a histogram for the data from the second file
	plt.hist(list2, bins=10, alpha=0.5, label='Gabe Original Data')

	# Set labels and title for the histogram
	plt.xlabel('Value')
	plt.xlim(0,1)
	plt.ylabel('Frequency')
	plt.title('Vessel Lumen Pixel ' + column_name)

	# Add a legend to differentiate between the data files
	plt.legend()

	# Display the histogram
	plt.show()

graph_histogram("eccentricity")