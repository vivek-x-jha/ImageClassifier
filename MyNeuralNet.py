import numpy as np
from scipy import optimize


class Neural_Network:
	def __init__(self):
		# Define Hyperparameters
		self.inputLayerSize = 2
		self.outputLayerSize = 1
		self.hiddenLayerSize = 3

		# Weights (parameters)
		self.W1 = np.random.randn(self.inputLayerSize, self.hiddenLayerSize)
		self.W2 = np.random.randn(self.hiddenLayerSize, self.outputLayerSize)

	def forward(self, X):
		# Propogate inputs though network
		self.z2 = np.dot(X, self.W1)
		self.a2 = self.sigmoid(self.z2)
		self.z3 = np.dot(self.a2, self.W2)
		yHat = self.sigmoid(self.z3)

		return yHat

	def sigmoid(self, z, derivative=False):
		# Apply sigmoid activation function to scalar, vector, or matrix
		if derivative:
			f = self.sigmoid(z) * (1 - self.sigmoid(z))
		else:
			f = 1 / (1 + np.exp(-z))

		return f

	def costFunc(self, X, y):
		# Compute cost for given X,y, use weights already stored in class.
		self.yHat = self.forward(X)
		J = 0.5 * sum((y - self.yHat) ** 2)

		return J

	def costFunctionPrime(self, X, y):
		# Compute derivative with respect to W1 and W2 for a given X and y:
		self.yHat = self.forward(X)

		delta3 = np.multiply(-(y - self.yHat), self.sigmoid(self.z3, derivative=True))
		dJdW2 = np.dot(self.a2.T, delta3)

		delta2 = np.dot(delta3, self.W2.T) * self.sigmoid(self.z2, derivative=True)
		dJdW1 = np.dot(X.T, delta2)

		return dJdW1, dJdW2

	# Helper Functions for interacting with other classes:
	def getParams(self):
		# Get W1 and W2 unrolled into vector:
		params = np.concatenate((self.W1.ravel(), self.W2.ravel()))

		return params

	def setParams(self, params):
		# Set W1 and W2 using single paramater vector.
		W1_start = 0
		W1_end = self.hiddenLayerSize * self.inputLayerSize
		self.W1 = np.reshape(params[W1_start:W1_end], (self.inputLayerSize, self.hiddenLayerSize))
		W2_end = W1_end + self.hiddenLayerSize * self.outputLayerSize
		self.W2 = np.reshape(params[W1_end:W2_end], (self.hiddenLayerSize, self.outputLayerSize))

	def computeGradients(self, X, y):
		dJdW1, dJdW2 = self.costFunctionPrime(X, y)

		return np.concatenate((dJdW1.ravel(), dJdW2.ravel()))


def computeNumericalGradient(N, X, y):
	paramsInitial = N.getParams()
	numgrad = np.zeros(paramsInitial.shape)
	perturb = np.zeros(paramsInitial.shape)
	e = 1e-4

	for p in range(len(paramsInitial)):
		# Set perturbation vector
		perturb[p] = e
		N.setParams(paramsInitial + perturb)
		loss2 = N.costFunc(X, y)

		N.setParams(paramsInitial - perturb)
		loss1 = N.costFunc(X, y)

		# Compute Numerical Gradient
		numgrad[p] = (loss2 - loss1) / (2 * e)

		# Return the value we changed to zero:
		perturb[p] = 0

	# Return Params to original value:
	N.setParams(paramsInitial)

	return numgrad


class trainer:
	def __init__(self, N):
		# Make Local reference to network:
		self.N = N

	def callbackF(self, params):
		self.N.setParams(params)
		self.J.append(self.N.costFunc(self.X, self.y))

	def costFunctionWrapper(self, params, X, y):
		self.N.setParams(params)
		cost = self.N.costFunc(X, y)
		grad = self.N.computeGradients(X, y)

		return cost, grad

	def train(self, X, y):
		# Make an internal variable for the callback function:
		self.X = X
		self.y = y

		# Make empty list to store costs:
		self.J = []

		params0 = self.N.getParams()

		options = {'maxiter': 200, 'disp': True}
		_res = optimize.minimize(self.costFunctionWrapper, params0, jac=True, method='BFGS',
		                         args=(X, y), options=options, callback=self.callbackF)

		self.N.setParams(_res.x)
		self.optimizationResults = _res


# X = (hours sleeping, hours studying)
X = np.array(([3, 5],
              [5, 1],
              [10, 2]), dtype=float)

# y = column vector containg test scores
y = np.array([[75, 82, 93]], dtype=float).T

# Normalize
X = X / np.amax(X, axis=0)
y = y / 100  # Max test score is 100

NN = Neural_Network()
yhat = NN.forward(X)
error = y - yhat

print(yhat * 100)
