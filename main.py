import gzip
import numpy as np
import matplotlib.pyplot as plt
f = gzip.open('train-images-idx3-ubyte.gz','r')
image_size = 28
image_pixel=image_size*image_size
no_of_different_labels = 10
f.read(16)
buf = f.read(image_size * image_size * 60000)
train_images = np.frombuffer(buf, dtype=np.uint8).astype(np.float32)
train_images = train_images.reshape(60000, image_size, image_size, 1)
train_images = np.asarray(train_images).squeeze()


f = gzip.open('t10k-images-idx3-ubyte.gz','r')
buf2 = f.read(image_size * image_size * 10000)

test_images = np.frombuffer(buf2, dtype=np.uint8).astype(np.float32)
test_images = test_images.reshape(10000, image_size, image_size, 1)
test_images = np.asarray(test_images).squeeze()


f = gzip.open('train-labels-idx1-ubyte.gz','r')
magic_number = int.from_bytes(f.read(4), 'big')
label_count = int.from_bytes(f.read(4), 'big')
label_data = f.read()
labels_train = np.frombuffer(label_data, dtype=np.uint8)

f = gzip.open('t10k-labels-idx1-ubyte.gz','r')
magic_number = int.from_bytes(f.read(4), 'big')
label_count = int.from_bytes(f.read(4), 'big')
label_data = f.read()
labels_test= np.frombuffer(label_data, dtype=np.uint8)


#////////////////////////
fac = 0.99 / 255
train_images=train_images.reshape((60000,784))
test_images=test_images.reshape((10000,784))
train_imgs = np.asfarray(train_images) * fac + 0.01
test_imgs = np.asfarray(test_images) * fac + 0.01

labels_train=labels_train.reshape((60000,1))
labels_test=labels_test.reshape((10000,1))
train_labels  = np.asfarray(labels_train)
test_labels = np.asfarray(labels_test)



lr = np.arange(no_of_different_labels)
train_labels_one_hot = (lr==train_labels).astype(float)
test_labels_one_hot = (lr==test_labels).astype(float)
train_labels_one_hot[train_labels_one_hot==0] = 0.01
train_labels_one_hot[train_labels_one_hot==1] = 0.99
test_labels_one_hot[test_labels_one_hot==0] = 0.01
test_labels_one_hot[test_labels_one_hot==1] = 0.99

@np.vectorize
def sigmoid(x):
    return 1 / (1 + np.e ** -x)
activation_function = sigmoid

from scipy.stats import truncnorm

def truncated_normal(mean=0, sd=1, low=0, upp=10):
    return truncnorm((low - mean) / sd, 
                     (upp - mean) / sd, 
                     loc=mean, 
                     scale=sd)


class NeuralNetwork:
    
    def __init__(self, 
                 no_of_in_nodes, 
                 no_of_out_nodes, 
                 no_of_hidden_nodes,
                 learning_rate):
        self.no_of_in_nodes = no_of_in_nodes
        self.no_of_out_nodes = no_of_out_nodes
        self.no_of_hidden_nodes = no_of_hidden_nodes
        self.learning_rate = learning_rate 
        self.create_weight_matrices()
        
    def create_weight_matrices(self):
        """ 
        A method to initialize the weight 
        matrices of the neural network
        """
        rad = 1 / np.sqrt(self.no_of_in_nodes)
        X = truncated_normal(mean=0, 
                             sd=1, 
                             low=-rad, 
                             upp=rad)
        self.wih = X.rvs((self.no_of_hidden_nodes, 
                                       self.no_of_in_nodes))
        rad = 1 / np.sqrt(self.no_of_hidden_nodes)
        X = truncated_normal(mean=0, sd=1, low=-rad, upp=rad)
        self.who = X.rvs((self.no_of_out_nodes, 
                                         self.no_of_hidden_nodes))
        
    
    def train(self, input_vector, target_vector):
        """
        input_vector and target_vector can 
        be tuple, list or ndarray
        """
        
        input_vector = np.array(input_vector, ndmin=2).T
        target_vector = np.array(target_vector, ndmin=2).T
        
        output_vector1 = np.dot(self.wih, 
                                input_vector)
        output_hidden = activation_function(output_vector1)
        
        output_vector2 = np.dot(self.who, 
                                output_hidden)
        output_network = activation_function(output_vector2)
        
        output_errors = target_vector - output_network
        # update the weights:
        tmp = output_errors * output_network \
              * (1.0 - output_network)     
        tmp = self.learning_rate  * np.dot(tmp, 
                                           output_hidden.T)
        self.who += tmp


        # calculate hidden errors:
        hidden_errors = np.dot(self.who.T, 
                               output_errors)
        # update the weights:
        tmp = hidden_errors * output_hidden * \
              (1.0 - output_hidden)
        self.wih += self.learning_rate \
                          * np.dot(tmp, input_vector.T)
        

        
    
    def run(self, input_vector):
        # input_vector can be tuple, list or ndarray
        input_vector = np.array(input_vector, ndmin=2).T

        output_vector = np.dot(self.wih, 
                               input_vector)
        output_vector = activation_function(output_vector)
        
        output_vector = np.dot(self.who, 
                               output_vector)
        output_vector = activation_function(output_vector)
    
        return output_vector
            
    def confusion_matrix(self, data_array, labels):
        cm = np.zeros((10, 10), int)
        for i in range(len(data_array)):
            res = self.run(data_array[i])
            res_max = res.argmax()
            target = labels[i][0]
            cm[res_max, int(target)] += 1
        return cm    

    def precision(self, label, confusion_matrix):
        col = confusion_matrix[:, label]
        return confusion_matrix[label, label] / col.sum()
    
    def recall(self, label, confusion_matrix):
        row = confusion_matrix[label, :]
        return confusion_matrix[label, label] / row.sum()
        
    
    def evaluate(self, data, labels):
        corrects, wrongs = 0, 0
        for i in range(len(data)):
            res = self.run(data[i])
            res_max = res.argmax()
            if res_max == labels[i]:
                corrects += 1
            else:
                wrongs += 1
        return corrects, wrongs
ANN = NeuralNetwork(no_of_in_nodes = image_pixel,no_of_out_nodes = 10,no_of_hidden_nodes = 100,learning_rate = 0.1)
for i in range(10):
    img = test_imgs[i].reshape((28,28))
    plt.imshow(img, cmap="Greys")
    print(labels_test[i])
    plt.show()
exit()
for i in range(len(train_imgs)):
    ANN.train(train_imgs[i], train_labels_one_hot[i])

for i in range(20):
    res = ANN.run(test_imgs[i])
    print(test_labels[i], np.argmax(res), np.max(res))


corrects, wrongs = ANN.evaluate(train_imgs, train_labels)
print("accuracy train: ", corrects / ( corrects + wrongs))
corrects, wrongs = ANN.evaluate(test_imgs, test_labels)
print("accuracy: test", corrects / ( corrects + wrongs))

cm = ANN.confusion_matrix(train_imgs, train_labels)
print(cm)

for i in range(10):
    print("digit: ", i, "precision: ", ANN.precision(i, cm), "recall: ", ANN.recall(i, cm))