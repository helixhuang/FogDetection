import argparse
import torch
import numpy as np
from torchvision import models
import sys
sys.path.insert(0,'..')

from helpers.data_loader import *
from models.model_utils import *
from train.train_utils import *
from train.test_utils import *

parser = argparse.ArgumentParser(description='Training models for fog detection')

# Learning
parser.add_argument('--lr', type=float, default=0.0001, help='initial learning rate [default: 0.0001]')
parser.add_argument('--epochs', type=int, default=2, help='default number of epochs for the training [default 2]')
parser.add_argument('--batch_size', type=int, default=164, help='batch size for training [default: 164]')
parser.add_argument('--from_conv_layer', type=int, default=False, help='train convolutional layers or only fc layer [default: False]')
parser.add_argument('--include_meteo', type=int, default=True, help='include meteo in model training or not [default: False]')

# Model
parser.add_argument('--model_name', type=str, default='merged_network', help='Form of model: resnet18, simple_CNN or merged_network')
parser.add_argument('--num_classes', type=int, default=3, help='number of classes to predict [default: 3]')
parser.add_argument('--meteo_inputs', type=int, default=4, help='number of meteorological variables included [default: 4]')
parser.add_argument('--meteo_hidden_size', type=int, default=15, help='size of hidden layer for meteo net [default: 15]')
parser.add_argument('--meteo_outputs', type=int, default=16, help='number of outputs for meteo NN [default: 16]')

#Device
parser.add_argument('--cuda', action='store_true', default=False, help='enable the gpu')
parser.add_argument('--model_save_path', default="../experiments/ex1/", help='directory to dump trained model')

# Directory/file locations model saving
parser.add_argument('--train_data_path', type=str, default="../data/processed/highway_train_IDW.npy", help='location of training numpy dictionary')
parser.add_argument('--val_data_path', type=str, default="../data/processed/highway_val_IDW.npy", help='location of validation numpy array dictionary')
parser.add_argument('--test_data_path', type=str, default="../data/processed/test_IDW.npy", help='location of test numpy array dictionary')

args = parser.parse_args()

if __name__ == '__main__':

	# Load dictionaries containing numpy arrays
	train_data, val_data = np.load(args.train_data_path)[()], np.load(args.val_data_path)[()]

	# Get loss weights
	loss_weights = calculate_loss_weights(train_data['targets'])

	# Create datasets
	train_dataset = FogDataset(train_data, custom_transforms['train'])
	validation_dataset = FogDataset(val_data, custom_transforms['eval'])

	# Create dataloaders and put in dictionary
	train_loader = create_loader(train_dataset, 'train', args.batch_size)
	validation_loader = create_loader(validation_dataset, 'validation', args.batch_size)

	# Loader dictionary
	loaders = {'train' : train_loader, 'validation': validation_loader}

	# Obtain and train model
	model = get_model(args)
	trained_model = train_model(model, loaders, loss_weights, args)

	# Test model
	test_data = np.load(args.test_data_path)[()]
	test_dataset = FogDataset(test_data, custom_transforms['eval'])
	test_loader = create_loader(test_dataset, 'test', len(test_data['targets']))
	cm = test_model(trained_model, test_loader, args)
