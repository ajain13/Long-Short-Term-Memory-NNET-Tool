# LSTM for international airline passengers problem with regression framing
import numpy
import matplotlib.pyplot as plt
import pandas
import math
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error

parameters = {
	"input_filename": "",
	"n_layers": None,
	"n_dropout_layers": None,
	"optimizer": "",
	"learning_rate": None,
	"momentum": None,
	"err_metric": "mean_squared_error",
	"output_filename": None,
}

def run_nnet(input_filename, n_layers, n_dropout_layers, optimizer, learning_rate, momentum, err_metric, output_filename):
	parameters["input_filename"] = input_filename
	parameters["n_layers"] = n_layers
	parameters["n_dropout_layers"] = n_dropout_layers
	parameters["optimizer"] = optimizer
	parameters["learning_rate"] = learning_rate
	parameters["momentum"] = momentum
	if err_metric:
		parameters["err_metric"] = err_metric
	parameters["output_filename"] = output_filename
	run()

# create the inner layers
def add_layers(layer_dimensions, model):
		model.add(LSTM(input_dim=layer_dimensions[0], output_dim=layer_dimensions[1], return_sequences=True))
		i = 0
		for i in range(1, len(layer_dimensions)-2):
			model.add(LSTM(input_dim=layer_dimensions[i], output_dim=layer_dimensions[i+1], return_sequences=True))
		model.add(LSTM(input_dim=layer_dimensions[i], output_dim=layer_dimensions[i+1], return_sequences=False))
		model.add(Dense(output_dim=layer_dimensions[len(layer_dimensions)-1]))
		return model

# convert an array of values into a dataset matrix
def create_dataset(dataset, look_back=1):
	dataX, dataY = [], []
	for i in range(len(dataset)-look_back-1):
		a = dataset[i:(i+look_back), 0]
		dataX.append(a)
		dataY.append(dataset[i + look_back, 0])
	return numpy.array(dataX), numpy.array(dataY)

def run():
	# fix random seed for reproducibility
	numpy.random.seed(7)
	# load the dataset

	# changed this line to take in command line parameters
	# dataframe = pandas.read_csv('international-airline-passengers.csv', usecols=[1], engine='python', skipfooter=3)
	dataframe = pandas.read_csv(parameters["input_filename"], usecols=[1], engine='python', skipfooter=3)

	dataset = dataframe.values
	dataset = dataset.astype('float32')
	# normalize the dataset
	scaler = MinMaxScaler(feature_range=(0, 1))
	dataset = scaler.fit_transform(dataset)
	# split into train and test sets
	train_size = int(len(dataset) * 0.67)
	test_size = len(dataset) - train_size
	train, test = dataset[0:train_size,:], dataset[train_size:len(dataset),:]
	# reshape into X=t and Y=t+1
	look_back = 1
	trainX, trainY = create_dataset(train, look_back)
	testX, testY = create_dataset(test, look_back)
	# reshape input to be [samples, time steps, features]
	trainX = numpy.reshape(trainX, (trainX.shape[0], 1, trainX.shape[1]))
	testX = numpy.reshape(testX, (testX.shape[0], 1, testX.shape[1]))
	# create and fit the LSTM network
	model = Sequential()

	# changed this line to correspond to command line arguments.
	# model.add(LSTM(4, input_dim=look_back))
	# model.add(LSTM(parameters["n_layers"], input_dim=look_back))
	model = add_layers([1, 50, 100, 1], model) # Creates the inner layers

	# model.add(Dense(1))

	# changed this to take from command line
	# model.compile(loss='mean_squared_error', optimizer='adam')
	model.compile(loss=parameters["err_metric"], optimizer=parameters["optimizer"])

	model.fit(trainX, trainY, nb_epoch=100, batch_size=1, verbose=2)
	# make predictions
	trainPredict = model.predict(trainX)
	testPredict = model.predict(testX)
	# invert predictions
	trainPredict = scaler.inverse_transform(trainPredict)
	trainY = scaler.inverse_transform([trainY])
	testPredict = scaler.inverse_transform(testPredict)
	testY = scaler.inverse_transform([testY])
	# calculate root mean squared error
	trainScore = math.sqrt(mean_squared_error(trainY[0], trainPredict[:,0]))
	print('Train Score: %.2f RMSE' % (trainScore))
	testScore = math.sqrt(mean_squared_error(testY[0], testPredict[:,0]))
	print('Test Score: %.2f RMSE' % (testScore))
	# shift train predictions for plotting
	trainPredictPlot = numpy.empty_like(dataset)
	trainPredictPlot[:, :] = numpy.nan
	trainPredictPlot[look_back:len(trainPredict)+look_back, :] = trainPredict
	# shift test predictions for plotting
	testPredictPlot = numpy.empty_like(dataset)
	testPredictPlot[:, :] = numpy.nan
	testPredictPlot[len(trainPredict)+(look_back*2)+1:len(dataset)-1, :] = testPredict
	# plot baseline and predictions
	plt.plot(scaler.inverse_transform(dataset))
	plt.plot(trainPredictPlot)
	plt.plot(testPredictPlot)
	plt.show()
	plt.savefig(parameters["output_filename"]+".png")
