from jaqpotpy.models.base_classes import Model
from jaqpotpy.doa.doa import DOA
from jaqpotpy.descriptors.base_classes import MolecularFeaturizer
from typing import Any, Union
import pandas as pd
import pickle
from jaqpotpy.datasets import MolecularTabularDataset, Dataset, TorchGraphDataset, SmilesDataset, MolecularDataset, CompositionDataset, StructureDataset
from jaqpotpy.models import Evaluator, Preprocesses
import torch
from torch.utils.data import DataLoader
from jaqpotpy.models import MolecularModel, MaterialModel
import numpy as np
from jaqpotpy.cfg import config
import os
import jaqpotpy


class MolecularTorch(Model):

    def __init__(self, dataset: MolecularDataset, model_nn: torch.nn.Module
                 , doa: DOA = None
                 , eval: Evaluator = None, preprocess: Preprocesses = None
                 , dataLoaderParams: Any = None, epochs: int = None
                 , criterion: torch.nn.Module = None, optimizer: Any = None
                 , train_batch: int = 50, test_batch: int = 50, log_steps: int = 1, model_dir: str = "./"):
        # super(InMemMolModel, self).__init__(dataset=dataset, doa=doa, model=model)
        self.dataset: MolecularDataset = dataset
        self.model_nn = model_nn
        self.doa = doa
        self.doa_m = None
        self.external = None
        self.evaluator: Evaluator = eval
        self.preprocess: Preprocesses = preprocess
        self.train_batch = train_batch
        self.test_batch = test_batch
        self.trainDataLoaderParams = {'batch_size': self.train_batch, 'shuffle': False, 'num_workers': 0}
        self.testDataLoaderParams = {'batch_size': self.test_batch, 'shuffle': False, 'num_workers': 0}
        self.epochs = epochs
        self.criterion = criterion
        self.trained_model = None
        self.model_fitted: MolecularModel = None
        self.optimizer_local = optimizer
        self.train_loader = None
        self.test_loader = None
        self.log_steps = log_steps
        self.best_model = model_nn
        self.path = None
        self.model_dir = model_dir
        # torch.multiprocessing.freeze_support()

    def __call__(self, smiles):
        self

    def fit(self):
        steps = self.epochs * 0.1
        if self.doa:
            if self.doa:
                if self.doa.__name__ == 'SmilesLeverage':
                    self.doa_m = self.doa.fit(self.dataset.smiles)
                else:
                    self.doa_m = self.doa.fit(X=self.dataset.__get_X__())
        if self.dataset.df is not None:
            pass
        else:
            self.dataset.create()
        if self.evaluator is not None:
            if self.evaluator.dataset.df is not None:
                pass
            else:
                self.evaluator.dataset.create()
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_fitted = MolecularModel()
        self.model_nn.to(device)
        # self.train_loader = DataLoader(dataset=self.dataset.df, **self.trainDataLoaderParams)
        # self.test_loader = DataLoader(dataset=self.evaluator.dataset.df, **self.testDataLoaderParams)
        self.train_loader = DataLoader(dataset=self.dataset, **self.trainDataLoaderParams)
        self.test_loader = DataLoader(dataset=self.evaluator.dataset, **self.testDataLoaderParams)
        temp_loss = None
        for epoch in range(1, self.epochs):
            self.train()
            train_loss = self.test(self.train_loader)
            test_loss = self.test(self.test_loader)
            if self.dataset.task == "classification":
                los = test_loss[2]
                if temp_loss is None or temp_loss < los:
                # if temp_loss < los and steps > epoch:
                    temp_loss = los
                    temp_path = self.path
                    self.path = self.model_dir + "molecular_model_ep_" + str(epoch) + "_er_" + str(los) + ".pt"
                    torch.save({
                        'epoch': epoch,
                        'model_state_dict': self.model_nn.state_dict(),
                        'optimizer_state_dict': self.optimizer_local.state_dict(),
                        'loss': los,
                    }, self.path)
                    try:
                        os.remove(temp_path)
                    except TypeError as e:
                        continue
                if epoch % self.log_steps == 0:
                    print(f'Epoch: {epoch:03d}, Train Accuracy: {train_loss[2]}, Test Accuracy: {test_loss[2]}')
            else:
                los = test_loss[1].item()
                if temp_loss is None or temp_loss > los:
                    temp_loss = los
                    temp_path = self.path
                    self.path = self.model_dir + "molecular_model_ep_" + str(epoch) + "_er_" + str(los) + ".pt"
                    torch.save({
                        'epoch': epoch,
                        'model_state_dict': self.model_nn.state_dict(),
                        'optimizer_state_dict': self.optimizer_local.state_dict(),
                        'loss': los,
                    }, self.path)
                    try:
                        os.remove(temp_path)
                    except TypeError as e:
                        continue
                if epoch % self.log_steps == 0:
                    print(f'Epoch: {epoch:03d}, Train Loss: {train_loss[1]}, Test Loss: {test_loss[1]}')
        return self

    def train(self):
        self.model_nn.train()
        for data in self.train_loader:
            out = self.model_nn(data[0].float())
            if self.dataset.task == 'classification':
                truth = torch.squeeze(data[1].long())
                loss = self.criterion(out, truth)
            else:
                # truth = torch.squeeze(data[1].float())
                loss = self.criterion(out, data[1].float())
            # loss = self.criterion(out, data[1].float())
            # print(loss)
            loss.backward(retain_graph=True)
            self.optimizer_local.step()
            self.optimizer_local.zero_grad()

    def test(self, dataloader):
        self.model_nn.eval()
        if self.dataset.task == 'classification':
            correct = 0
            for data in dataloader:
                out = self.model_nn(data[0].float())
                pred = out.argmax(dim=1)
                truth = torch.squeeze(data[1].long())
                correct += int((pred == truth).sum())
                loss = self.criterion(out, truth)
            return out, pred.numpy(), correct / len(dataloader.dataset)
        else:
            self.model_nn.eval()
            for data in dataloader:
                out = self.model_nn(data[0].float())
                loss = self.criterion(out, data[1].float())
            return out, loss

    def eval(self):
        checkpoint = torch.load(self.path)
        self.best_model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer_local.load_state_dict(checkpoint['optimizer_state_dict'])
        self.best_model.eval()
        if self.evaluator.functions:
            eval_keys = self.evaluator.functions.keys()
            correct = 0
            truth = np.array([])
            preds = np.array([])
            for data in self.test_loader:
                out = self.best_model(data[0].float())
                pred = out.argmax(dim=1)
                correct += int((pred == data[1].float()).sum())
                truth = np.append(truth, data[1].float().numpy())
                preds = np.append(preds, pred.numpy())
            # return out, pred.numpy(), correct / len(dataloader.dataset)
            for eval_key in eval_keys:
                eval_function = self.evaluator.functions.get(eval_key)
                print(eval_key + ": " + str(eval_function(truth, preds)))
        else:
            print("No eval functions passed")

    def create_molecular_model(self):
        checkpoint = torch.load(self.path)
        self.best_model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer_local.load_state_dict(checkpoint['optimizer_state_dict'])
        model = MolecularModel()
        if type(self.dataset.featurizer).__name__ == "RDKitDescriptors":
            model.descriptors = "RDKitDescriptors"
        else:
            model.descriptors = self.dataset.featurizer
        model.doa = self.doa
        model.model = self.best_model
        model.optimizer = self.optimizer_local
        model.X = self.dataset.X
        model.Y = self.dataset.y
        model.library = ['torch']
        model.version = [torch.__version__]
        model.jaqpotpy_version = jaqpotpy.__version__
        model.jaqpotpy_docker = config.jaqpotpy_docker
        model.modeling_task = self.dataset.task
        # model.external_feats = self.dataset.external
        return model


class MaterialTorch(Model):

    def __init__(self, dataset: Union[CompositionDataset, StructureDataset], model_nn: torch.nn.Module
                 , doa: DOA = None
                 , eval: Evaluator = None, preprocess: Preprocesses = None
                 , dataLoaderParams: Any = None, epochs: int = None
                 , criterion: torch.nn.Module = None, optimizer: Any = None
                 , train_batch: int = 50, test_batch: int = 50, log_steps: int = 1):
        # super(InMemMolModel, self).__init__(dataset=dataset, doa=doa, model=model)
        self.dataset: MolecularDataset = dataset
        self.model_nn = model_nn
        self.doa = doa
        self.doa_m = None
        self.external = None
        self.evaluator: Evaluator = eval
        self.preprocess: Preprocesses = preprocess
        self.train_batch = train_batch
        self.test_batch = test_batch
        self.trainDataLoaderParams = {'batch_size': self.train_batch, 'shuffle': False, 'num_workers': 0}
        self.testDataLoaderParams = {'batch_size': self.test_batch, 'shuffle': False, 'num_workers': 0}
        self.epochs = epochs
        self.criterion = criterion
        self.trained_model = None
        self.model_fitted: MolecularModel = None
        self.optimizer_local = optimizer
        self.train_loader = None
        self.test_loader = None
        self.log_steps = log_steps
        self.best_model = None
        # torch.multiprocessing.freeze_support()

    def __call__(self, smiles):
        self

    def fit(self):
        steps = self.epochs * 0.1
        if self.doa:
            if self.doa:
                if self.doa.__name__ == 'SmilesLeverage':
                    self.doa_m = self.doa.fit(self.dataset.smiles_strings)
                else:
                    self.doa_m = self.doa.fit(X=self.dataset.__get_X__())
        if self.dataset.df is not None:
            pass
        else:
            self.dataset.create()
        if self.evaluator is not None:
            if self.evaluator.dataset.df is not None:
                pass
            else:
                self.evaluator.dataset.create()
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_fitted = MolecularModel()
        self.model_nn.to(device)
        # self.train_loader = DataLoader(dataset=self.dataset.df, **self.trainDataLoaderParams)
        # self.test_loader = DataLoader(dataset=self.evaluator.dataset.df, **self.testDataLoaderParams)
        self.train_loader = DataLoader(dataset=self.dataset, **self.trainDataLoaderParams)
        self.test_loader = DataLoader(dataset=self.evaluator.dataset, **self.testDataLoaderParams)
        temp_loss = None
        for epoch in range(1, self.epochs):
            self.train()
            train_loss = self.test(self.train_loader)
            test_loss = self.test(self.test_loader)
            if self.dataset.task == "classification":
                los = test_loss[2]
                # if temp_loss is None or temp_loss < los and steps > epoch:
                if temp_loss is None or temp_loss < los:
                    self.best_model = self.model_nn
                if epoch % self.log_steps == 0:
                    print(f'Epoch: {epoch:03d}, Train Accuracy: {train_loss[2]}, Test Accuracy: {test_loss[2]}')
            else:
                los = test_loss[1].item()
                # if temp_loss is None or temp_loss < los and steps > epoch:
                if temp_loss is None or temp_loss > los:
                    self.best_model = self.model_nn
                if epoch % self.log_steps == 0:
                    print(f'Epoch: {epoch:03d}, Train Loss: {train_loss[1]}, Test Loss: {test_loss[1]}')
        return self

    def train(self):
        self.model_nn.train()
        for data in self.train_loader:
            out = self.model_nn(data[0].float())
            if self.dataset.task == 'classification':
                truth = torch.squeeze(data[1].long())
                loss = self.criterion(out, truth)
            else:
                # truth = torch.squeeze(data[1].float())
                loss = self.criterion(out, data[1].float())
            # loss = self.criterion(out, data[1].float())
            # print(loss)
            loss.backward(retain_graph=True)
            self.optimizer_local.step()
            self.optimizer_local.zero_grad()

    def test(self, dataloader):
        self.model_nn.eval()
        if self.dataset.task == 'classification':
            correct = 0
            for data in dataloader:
                out = self.model_nn(data[0].float())
                pred = out.argmax(dim=1)
                truth = torch.squeeze(data[1].long())
                correct += int((pred == truth).sum())
                loss = self.criterion(out, truth)
            return out, pred.numpy(), correct / len(dataloader.dataset)
        else:
            self.model_nn.eval()
            for data in dataloader:
                if self.best_model:
                    self.best_model.eval()
                out = self.model_nn(data[0].float())
                # truth = torch.squeeze(data[1].float())
                loss = self.criterion(out, data[1].float())
            return out, loss

    def eval(self):
        self.best_model.eval()
        if self.evaluator.functions:
            eval_keys = self.evaluator.functions.keys()
            correct = 0
            truth = np.array([])
            preds = np.array([])
            for data in self.test_loader:
                if self.dataset.task == 'classification':
                    out = self.best_model(data[0].float())
                    pred = out.argmax(dim=1)
                    correct += int((pred == data[1].float()).sum())
                    truth = np.append(truth, data[1].numpy())
                    preds = np.append(preds, pred.numpy())
                else:
                    out = self.best_model(data[0].float())
                    truth = np.append(truth, data[1].numpy())
                    preds = np.append(preds, out.detach().numpy())
            # return out, pred.numpy(), correct / len(dataloader.dataset)
            for eval_key in eval_keys:
                eval_function = self.evaluator.functions.get(eval_key)
                print(eval_key + ": " + str(eval_function(truth, preds)))
        else:
            print("No eval functions passed")

    def create_molecular_model(self):
        model = MaterialModel()
        model.descriptors = self.dataset.featurizer
        model.doa = self.doa
        model.model = self.best_model
        model.X = self.dataset.X
        model.Y = self.dataset.y
        model.library = ['torch']
        model.version = [torch.__version__]
        model.jaqpotpy_version = config.version
        model.modeling_task = self.dataset.task
        model.external_feats = self.dataset.external
        return model
