import numpy as np
import random
import scipy.io as sio


def sigmoid(z):
    """Evaluates the sigmoid function at the given input

    :param array-like z: Could be a number, list or Numpy array for
    which sigmoid is to be evaluated

    :return: numpy array"""

    z = np.asarray(z)
    return 1.0 / (1.0 + np.exp(-z))


def sigmoid_derivative(z):
    """Evaluates the derivative of the sigmoid function at the given input

    :param array-like z: Could be a number, list or Numpy array for which
    sigmoid derivative is to be evaluated

    :return: Numpy array"""

    return sigmoid(z) * (1 - sigmoid(z))


class NN_hwr(object):
    """A template class for a neural network to recognise handwritten text
    Initialise with a list with each element being the number of neurons in
    that layer
    For the init function, the parameters are

    :param list num_neurons_list: Create a neural network number
    of neuron per layer given by the list

    """

    def __init__(self, num_neurons_list):
        """Input must be a list of numbers

        :param list num_neurons_list: Create a neural network number of
        neuron per layer given by the list

        """
        for i in num_neurons_list:
            if type(i) not in [type(2)]:
                raise TypeError("Expected integer type")

        self.num_layers = len(num_neurons_list)
        self.num_neurons_list = num_neurons_list
        self.biases = [np.random.randn(y, 1) for y in num_neurons_list[1:]]
        self.weights = [np.random.randn(y, x)
                        for x, y in zip(num_neurons_list[:-1],
                        num_neurons_list[1:])]

    def forward_prop(self, x_train):
        """Computes the activations and weighted inputs of the neurons in
        the network for the given input data.

        :param ndarray x_train: The input for the first layer which needs
        to be forwards propogated

        :return: A tuple of lists containing activations and weighted inputs

        """

        activations = []
        z = []
        activations.append(x_train)

        for i in range(self.num_layers - 1):
            z.append(np.dot(self.weights[i], activations[-1]) + self.biases[i])
            activations.append(sigmoid(z[-1]))

        return activations[1:], z

    def back_prop(self, training_example):
        """Computes the partial derivatives of the cost function with respect to
        the weights and biases of the network
        training_example is a tuple with element fisrt element an np array and
        the second, an array of length 10 of zeros everywhere except at the
        image label where there is a 1

        :param tuple training_example: Tuple with first element as the input
        data and the second being its label

        :return: a tuple of numpy arrays containing the required derivatives"""

        if len(training_example) != 2:
            raise TypeError("Expected input of size 2")
        if isinstance(training_example[0], np.ndarray):
            if training_example[0].shape != (784, 1):
                raise TypeError("Expected list with 1st element\
                                 being a 784 x 1 numpy array")
        else:
            raise TypeError("Expected a numpy array for\
                            first element of input")

        x_train, y_train = training_example
        activations, z = self.forward_prop(x_train)

        delta_b = np.array(self.biases[:])
        delta_w = np.array(self.weights[:])

        delta_L = self.cost_derivative(activations[-1],
                                       y_train) * sigmoid_derivative(z[-1])

        delta_b[-1] = delta_L
        delta_w[-1] = np.outer(delta_L, activations[-2])
        delta = delta_L

        for i in range(2, self.num_layers):
            sd = sigmoid_derivative(z[-i])
            delta = np.dot(self.weights[-i + 1].transpose(), delta) * sd
            delta_b[-i] = delta
            if i == self.num_layers - 1:
                ac = x_train
            else:
                ac = activations[-i - 1]
            delta_w[-i] = np.outer(delta, ac)
        return (delta_b, delta_w)

    def train_batch(self, batch, learning_rate):
        """ Trains the network with one subset of the training data.
        Input is the subset of training data for witch the network is
        to be trained. Learning rate governs the rate at which the
        Weights and biases change in the gradient descent algorithm

        :param ndarray batch: An array of training examples with each
        being a tuple containing the input data and its label.

        :param fload learning_rate: The learning rate which determines
        the step size in gradient descent

        :return: None

        """

        delta_b_sum = [np.zeros(b.shape) for b in self.biases]
        delta_w_sum = [np.zeros(w.shape) for w in self.weights]
        for training_example in batch:
            delta_b, delta_w = self.back_prop(training_example)
            delta_b_sum += delta_b
            delta_w_sum += delta_w
        self.biases = self.biases - learning_rate * delta_b_sum
        self.weights = self.weights - learning_rate * delta_w_sum

    def train_nn(self, X_train, y_train, n_epochs, batch_size, learning_rate):
        """Trains the neural network with the test data. n_epochs is the number
        sweeps over the whole data. batch_size is the number of training
        example per batch in the stochastic gradient descent. X_train and
        y_train are the images and labels in the training data. X_train must
        be a 2-D array with only one row and y_train is an array of length 10
        of zeros everywhere except at the image label (where there is a 1)

        :param ndarray X_train: Numpy array containing the input training data
        :param ndarray y_train: Numpy array containing the labels for training.
        Formatted as an array of arrays with 1 at the label position and 0
        everywhere else

        :param int n_epochs: The number of sweeps over the data-set in the
        Stochastic Gradient Descent

        :param int batch_size: Number of training examples per batch in the
        Stochastic Gradient Descent

        :param fload learning_rate: The learning rate which determines the
        step size in gradient descent

        :return: None
        """

        m = len(y_train)
        train_data = list(zip(X_train, y_train))

        for i in range(n_epochs):
            random.shuffle(train_data)
            batches = [train_data[j:j + batch_size]
                       for j in range(0, m, batch_size)]
            for batch in batches:
                self.train_batch(batch, learning_rate)
            print("epoch no: %d" % i, self.cost_function(X_train, y_train))
        sio.savemat('../data/weights_biases', {'w': self.weights,
                    'b': self.biases})

    def cost_function(self, X_train, y_train):
        """Computes the quadratic cost function of the Neural Network

        :param ndarray X_train: Input data for training
        :param ndarray y_train: Labels corresponding to the inputs

        :return: Float value of the cost function of the Neural Network

        """
        J = 0
        for i in range(len(y_train)):
            J += 0.5 * np.sum((self.forward_prop(X_train[i])
                               [0][-1] - y_train[i])**2)
        return J

    def cost_derivative(self, activation, y):
        """Computes the derivative of the cost function given output activations and
        the labels

        :param ndarray activation: Activations of the neurons for a given input
        :param list y: The expected output for the input

        :return: Float value of the cost function of the Neural Network

        """
        return np.array(activation) - y