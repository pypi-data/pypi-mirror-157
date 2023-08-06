import adopt_pytorch.config as config
import torch
import logging
import warnings
import numpy as np
from torch import nn
from tqdm import tqdm
from sklearn.metrics import f1_score, balanced_accuracy_score
from torch.utils.data import DataLoader, WeightedRandomSampler

from adopt_pytorch.data import SimpleData

logging.basicConfig(level=config.log['models'])
logger = logging.getLogger('models')
torch.manual_seed(config.pytorch_seed)
np.random.seed(config.numpy_seed)


class ADOPT(nn.Module):
    '''Pytorch version of ADOPT. This version is able to use variable flight lengths'''
    def __init__(self, n_features, parameters_list,
                 hidden_size=5, device='cpu',
                 max_seq_len=None):
        nn.Module.__init__(self)

        self.n_features = n_features
        self.parameters_list = parameters_list
        self.hidden_size = hidden_size
        self.device = device
        self.max_seq_len = max_seq_len
        self.input_values = None

        self.gru = nn.GRU(input_size=self.n_features,
                          hidden_size=self.hidden_size,
                          batch_first=True)

        self.tanh_ = nn.Tanh()

        self.dense1 = nn.Sequential(nn.Linear(in_features=self.hidden_size,
                                    out_features=500),
                                    nn.Tanh())

        self.dense2 = nn.Sequential(nn.Linear(in_features=500,
                                    out_features=1),
                                    nn.Sigmoid())

    def forward(self, x, save_input=True):
        if not torch.is_tensor(x):
            x = torch.Tensor(x).to(self.device)
        else:
            x = x.to(self.device)

        if len(x.size()) == 2:
            x = x.view(1, x.size(0), x.size(1))

        # Save the passed input
        if save_input:
            self.input_values = x.detach().clone()
        # Make sure that the precursor probability over time is specific to current batch
        batch_size = x.size(0)
        n_timesteps = x.size(1)
        self.precursor_proba = torch.zeros((batch_size,
                                            n_timesteps,
                                            self.n_features)).to(self.device)

        self.proba_time = torch.zeros((batch_size,
                                       n_timesteps)).to(self.device)

        # Stateless
        h_0 = torch.zeros(1, batch_size, self.hidden_size).to(self.device)
        gru_out, h_out = self.gru(x, h_0)
        out1 = self.dense1(self.tanh_(gru_out))
        self.proba_time = self.dense2(out1)
        # Take the max proba across time
        final_out = torch.max(self.proba_time, axis=1)[0]

        return final_out.view(-1)


def train_binary_model(clf, X_train, y_train,
                       X_val=None, y_val=None, model_out_cpu: bool = True,
                       threshold: float = 0.5, batch_size: int = None, weight=None, optimizer: str = 'adam',
                       l2: float = 0, learning_rate: float = 0.01, n_epochs: int = 100,
                       use_stratified_batch_size: bool = True, print_every_epochs: int = 10,
                       verbose: int = 0, ignore_warnings=False):

    if ignore_warnings:
        warnings.filterwarnings('ignore')

    # Set the model to the relevant device
    clf.to(clf.device)

    # Add weight to each example, kinda useful for imbalanced dataset at times
    if weight is not None:
        weight = torch.Tensor(weight).to(clf.device)
    if len(np.unique(y_train)) == 2:
        criterion = nn.BCELoss(weight=weight)
    else:
        raise NotImplementedError

    # Setup optimizer
    if optimizer == "adam":
        optimizer = torch.optim.Adam(clf.parameters(),
                                     lr=learning_rate, weight_decay=l2)
    else:
        optimizer = torch.optim.SGD(clf.parameters(),
                                    lr=learning_rate, weight_decay=l2)

    # Init loss history and balanced accuracy
    hist = np.zeros(n_epochs)
    val_hist = np.zeros(n_epochs)
    b_acc = np.zeros(n_epochs)
    val_b_acc = np.zeros(n_epochs)
    f1 = np.zeros(n_epochs)
    val_f1 = np.zeros(n_epochs)

    # Conversion to tensors
    if not torch.is_tensor(X_train):
        if isinstance(X_train, list):
            X_train = [torch.Tensor(x) for x in X_train]
        else:
            X_train = torch.Tensor(X_train)
    if not torch.is_tensor(y_train):
        y_train = torch.Tensor(y_train.flatten())

    if X_val is not None and y_val is not None:
        if not torch.is_tensor(X_val):
            if isinstance(X_val, list):
                X_val = [torch.Tensor(x) for x in X_val]
            else:
                X_val = torch.Tensor(X_val)
        if not torch.is_tensor(y_val):
            y_val = torch.Tensor(y_val)
        data_val = SimpleData(X_val, y_val)

    if batch_size is None:
        batch_size = X_train.size(0)
        logger.warn("Setting the batch size = full training set could overwhelm GPU memory")
    if isinstance(X_train, list):
        batch_size = 1
        logger.warn('Beware, changing the batch size to 1 and training may be slow!')

    data_train = SimpleData(X_train, y_train)
    if use_stratified_batch_size is False:
        logger.info("Mini-batch strategy: Random sampling")
        dataloader_train = DataLoader(data_train, batch_size=batch_size, shuffle=True)
    else:
        logger.info("Mini-batch strategy: Stratified")
        # get class counts
        weights = []
        for label in torch.unique(y_train):
            count = len(torch.where(y_train == label)[0])
            weights.append(1 / count)
        weights = torch.tensor(weights).to(clf.device)
        samples_weights = weights[y_train.type(torch.LongTensor).to(clf.device)]
        sampler = WeightedRandomSampler(samples_weights, len(samples_weights), replacement=True)
        dataloader_train = DataLoader(data_train, batch_size=batch_size, sampler=sampler)

    if X_val is not None:
        dataloader_val = DataLoader(data_val, batch_size=batch_size, shuffle=False)

    # Train the model
    try:
        for epoch in tqdm(range(n_epochs)):
            batch_acc = []
            batch_val_acc = []
            batch_f1 = []
            batch_val_f1 = []

            for iteration, (batch_x, batch_y) in enumerate(dataloader_train):
                # Get batch
                batch_x, batch_y = batch_x.to(clf.device), batch_y.to(clf.device)
                # Reset gradient to zero
                optimizer.zero_grad()
                if (epoch == 0) and iteration == 0:
                    # TODO: Change this
                    for c in torch.unique(y_train):
                        logger.info(f"Proportion Class {c}: {batch_y[batch_y==c].shape[0]/len(batch_y)}")

                # Forward pass
                outputs = clf(batch_x)
                # Show info
                logger.debug(f"Epoch-Iteration:{epoch}-{iteration}")
                logger.debug(f"outputs: {outputs.flatten()}")
                logger.debug(f"targets: {batch_y.view(-1).flatten()}")
                # Get the loss
                loss = criterion(outputs.flatten(), batch_y.view(-1).flatten())

                hist[epoch] = loss.item()

                if "cuda" in clf.device:
                    temp_outpouts = (outputs.cpu().detach().numpy() > threshold).astype(int)
                    y_batch = batch_y.view(-1).cpu().detach().numpy()
                    b_acc[epoch] = balanced_accuracy_score(y_batch, temp_outpouts)
                else:
                    temp_outpouts = (outputs.detach().numpy() > threshold).astype(int)
                    y_batch = batch_y.view(-1).detach().numpy()
                    b_acc[epoch] = balanced_accuracy_score(y_batch, temp_outpouts)

                batch_acc.append(b_acc[epoch])
                batch_f1.append(f1_score(y_batch, temp_outpouts, average='binary'))

                # Backprop and perform optimisation
                loss.backward()
                optimizer.step()

                if X_val is not None and y_val is not None:
                    # Do not compute gradient on validation
                    with torch.no_grad():
                        mini_loss = []
                        for batch_X_val, batch_y_val in dataloader_val:
                            batch_X_val, batch_y_val = batch_X_val.to(clf.device), batch_y_val.to(clf.device)
                            valYhat = clf(batch_X_val)

                            val_loss = criterion(valYhat, batch_y_val.flatten())

                            mini_loss.append(val_loss.item())

                            if "cuda" in clf.device:
                                temp_out_y = (valYhat.cpu().detach().numpy() > threshold).astype(int)
                                y_val_batch = batch_y_val.view(-1).cpu().detach().numpy()
                                val_b_acc[epoch] = balanced_accuracy_score(y_val_batch,
                                                                           temp_out_y)
                            else:
                                temp_out_y = (valYhat.detach().numpy() > threshold).astype(int)
                                y_val_batch = batch_y_val.view(-1).detach().numpy()
                                val_b_acc[epoch] = balanced_accuracy_score(y_val_batch,
                                                                           temp_out_y)
                            batch_val_acc.append(val_b_acc[epoch])
                            batch_val_f1.append(f1_score(y_val_batch, temp_out_y, average='binary'))
                        val_hist[epoch] = np.mean(mini_loss)

                if verbose == 1:
                    if epoch % print_every_epochs == 0:
                        logger.info("\nEpoch: %d, loss: %1.5f" % (epoch, loss.item()))
                        logger.info("Epoch: %d, b_acc: %1.5f" % (epoch, b_acc[epoch]))
                        logger.info("Epoch: %d, f1 (binary): %1.5f" % (epoch, f1_score(y_batch,
                                                                                       temp_outpouts,
                                                                                       average='binary')))
                        if X_val is not None:
                            logger.info("Epoch: %d, val_loss: %1.5f" % (epoch, val_hist[epoch]))
                            logger.info("Epoch: %d, val_b_acc: %1.5f" % (epoch, val_b_acc[epoch]))
                            logger.info("Epoch: %d, val_f1 (binary): %1.5f\n" % (epoch, f1_score(y_val_batch,
                                                                                                 temp_out_y,
                                                                                                 average='binary')))

            b_acc[epoch] = np.mean(batch_acc)
            val_b_acc[epoch] = np.mean(batch_val_acc)
            f1[epoch] = np.mean(batch_f1)
            val_f1[epoch] = np.mean(batch_val_f1)
    except KeyboardInterrupt:
        logger.info("Training was interuppted!")
        if model_out_cpu and clf.device != "cpu":
            # Puts back model on cpu
            clf.cpu()
            clf.device = "cpu"

        # Eval/testing mode
        clf.eval()

        # Keep training data inside of model class
        clf.x_train = X_train
        clf.x_test = X_val

        return clf, hist, val_hist, (b_acc, val_b_acc, f1, val_f1)

    except Exception as E:
        logger.warn(E)
        logger.info(f"Fail safe on {iteration} for epoch {epoch}")

    if model_out_cpu and clf.device != "cpu":
        # Puts back model on cpu
        clf.cpu()
        clf.device = "cpu"

    # Eval/testing mode
    clf.eval()

    clf.x_train = X_train
    clf.x_test = X_val

    return clf, hist, val_hist, (b_acc, val_b_acc, f1, val_f1)
