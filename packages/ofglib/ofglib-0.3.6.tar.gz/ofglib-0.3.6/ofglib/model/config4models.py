import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error as mae, r2_score as r2
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV
import sklearn.decomposition as sk
from xgboost import XGBRegressor
from pygam import GAM, InvGaussGAM
from autofeat import AutoFeatRegressor
from copy import deepcopy

from .config4features import group2name, groups, to_target
# temperature_labels, mean_cols_without_temp, mean_cols_with_temp

#------------------------------------------------------
MAX_NUM_FEATURES_AUTOFEAT = 10
NUM_STEPS_AUTOFEAT = 2
AUTOFEAT_TRANSFORMATIONS = ("exp", "abs", "sqrt", "^2", "^3")
#------------------------------------------------------


#######################################
# Neural ODE
#######################################

from torchdyn.models import *
from torchdyn import *
import torch
import torch.nn as nn
import pytorch_lightning as pl
import torch.utils.data as data

class Learner(pl.LightningModule):
    def __init__(self, model:nn.Module, Xtr, Ytr, device):
        super().__init__()
        self.model = model
        self.Xtr = Xtr
        self.Ytr = Ytr
        self.learning_rate = 0.01
        self.learner_device = device

    def forward(self, x):
        return self.model(x)

    def training_step(self, batch, batch_idx):
        x, y = batch
        _, y_hat = self.model(x)
        y_hat = y_hat[-1]

        loss = nn.MSELoss()(y_hat[:, -1], y)
        logs = {'train_loss': loss}
        return {'loss': loss, 'log': logs}

    def configure_optimizers(self):
        return torch.optim.Adamax(self.model.parameters(), lr = self.learning_rate)

    def train_dataloader(self):
        X_train = torch.Tensor(self.Xtr.float()).to(self.learner_device)
        y_train = torch.Tensor(self.Ytr.float()).to(self.learner_device)
        train = data.TensorDataset(X_train, y_train)
        trainloader = data.DataLoader(train, batch_size=len(X_train), shuffle=True)
        return trainloader


class NODE:
    def __init__(self, n_epochs=200, inner_rate=0.5):
        self.n_epochs = n_epochs
        self.inner_rate = inner_rate
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    def fit(self, Xtr, Ytr):
        Xtr = np.hstack((Xtr, np.ones((Xtr.shape[0], 1))))
        X = torch.from_numpy(Xtr)
        yn = torch.from_numpy(Ytr)

        n_input = Xtr.shape[1]
        n_inner = int(n_input*self.inner_rate)
        f = nn.Sequential(nn.Linear(n_input, n_inner),
                          nn.Tanh(),
                          nn.Linear(n_inner, n_input),
                          ).to(self.device)
        model = NeuralODE(f, sensitivity='autograd', solver='rk4').to(self.device)

        learn = Learner(model, X, yn, self.device)
        trainer = pl.Trainer(min_epochs=self.n_epochs, max_epochs=self.n_epochs,
                             auto_lr_find=True)
        trainer.fit(learn)
        self.model = model
        return

    def predict(self, X):
        X = np.hstack((X, np.ones((X.shape[0], 1))))
        X = torch.from_numpy(X)
        X = torch.Tensor(X.float()).to(self.device)
        _, pred = self.model(X)
        return pred[-1].detach().cpu().numpy()[:, -1]


#######################################
# Models and grouping methods
#######################################

models = {# 'xgboost': XGBRegressor(),
          'xgboost': XGBRegressor(n_estimators=100,
                                  colsample_bytree=0.8,
                                  max_depth=4,
                                 ),
          'linear': LinearRegression(),
          'gam': GAM(),
          #'invgaussgam': InvGaussGAM()
          'node': NODE(n_epochs=500)
         }

class PCA(sk.PCA):
    def __init__(self):
        super().__init__(n_components=1)

    def predict(self, X):
        return self.transform(X)

    def gridsearch(self, X, Y):
        return self

def grouping(grouping_method):
    if grouping_method == 'pca':
        return  PCA()
    else:
        return GAM()


#######################################
# Main class
#######################################


class Model:
    '''A class to represent a model.

    ...

    Attributes
    ----------
    features : list
        list of column names
    target : str
        target name
    grouping_method : dict
        dictionary of PCA/GAM-transformers (default: None)
    verbose : int
        messages

    autofeat : bool
        if there is feature generator (default: False)
    afreg : autofeat.AutoFeatRegressor
        feature generator
    autofeat_inds : list
        indexes of the most important features
    autofeat_xmin, autofeat_xptp : float
        used in self.scale_autofeat

    NUM_SAMPLES : dict
        dictionary of metrics (default: empty dictionary)
    model : xgboost/linear/gam/node-regressor
        machine learning model (default: from 'models'-dict)

    Methods
    -------
    train_group_processors(df):
        Inserts into self.grouping fitted transformers
    generate_group_values(df):
        Inserts into df grouped columns
    train_autofeat(Xtr, Ytr):
        Trains self.afreg and returns Xtr, transromed by afreg

    scale(X, Y=None):
        Returns scaled between [xmin-0.2*np.abs(xmin)], 1] X /and Y
    scale_autofeat(X, train=False):
        Returns scaled between [0, 1] X
    rescale(Y):
        Returns rescaled Y

    tune(X, Y):
        Now: returns self.model
    status(message):
        Now: print(message)

    train(df):
        Returns True, if model fitted, else False

    predict(df, column_name=None):
        Returns predictions as pd.DataFrame with column_name

    Notes
    -----
    До обучения доходят только те модели, для которых были выбраны и таргеты,
    и признаки.

    '''

    def __init__(self, features, target,
                       model_name='xgboost',
                       grouping_method=None,
                       autofeat=False,
                       verbose=1):
        # model_name in ['xgboost', 'linear', 'gam', 'node']
        # grouping_method in [None, 'pca', 'gam']
        self.features = features
        self.target = target

        if not model_name:
            model_name = 'xgboost'
        if not autofeat:
            autofeat = False

        self.model_name = model_name
        self.model = deepcopy(models)[model_name]

        self.grouping = {}

        if grouping_method in ['pca', 'gam']:
            for group in groups:
                name = group2name(group, inverse=False)
                self.grouping[name] = grouping(grouping_method)
                self.features.append(name)

        self.autofeat = autofeat
        self.verbose = verbose
        self.NUM_SAMPLES = 0

    def train_group_processors(self, df):
        self.status(self.grouping)
        if len(self.grouping) > 0:
            self.status("[Grouping]: transform groups to a single column")

        keys_to_delete = []
        for name in self.grouping:
            self.status(f"{name[:21]}...{name[-21:]}")
            columns = group2name(name, inverse=True)
            df_sub = df.dropna(inplace=False, subset=columns+[self.target])

            # zero data for transforming
            if df_sub.empty:
                keys_to_delete.append(name)
                self.features.remove(name)
                continue

            X, Y = df_sub[columns].values, df_sub[self.target].values

            self.grouping[name] = self.grouping[name].gridsearch(X, Y)
            self.grouping[name].fit(X, Y)

        for key in keys_to_delete:
            self.grouping.pop(key, None)
        return

    def generate_group_values(self, df):
        for name in self.grouping:
            cols = group2name(name, inverse=True)
            X = df[cols].values
            Y = self.grouping[name].predict(X)
            df.insert(1, name, Y, False)
            #df[name] = Y # cause warning
        return

    def scale(self, X, Y=None):
        if Y is not None: # this call from train method
            self.xmin = X.min(axis=0)
            self.xmin = self.xmin - 0.2*np.abs(self.xmin)
            self.xptp = X.max(axis=0) - self.xmin
            self.xptp[self.xptp==0] = 1

            self.ymin = Y.min(0)
            self.yptp = Y.ptp(0) if Y.ptp()!=0 else 1

            return (X-self.xmin)/self.xptp, (Y-self.ymin)/self.yptp
        else:  # this call from predict method
            return (X-self.xmin)/self.xptp, None

    def scale_autofeat(self, X, train=False):
        if train:
            self.autofeat_xmin = X.min(axis=0)
            self.autofeat_xptp = X.ptp(axis=0)
        return (X - self.autofeat_xmin)/self.autofeat_xptp

    def rescale(self, Y):
        return Y*self.yptp + self.ymin

    def tune(self, X, Y):
        return self.model
        if self.model_name == "xgboost":
            self.status("[xgboost] Hyperparameters tuning")
            parameters = {'n_estimators': [80, 100, 120], # 100
                          'max_depth': [4, 6, 8],              # 4
                          'learning_rate': [0.05, 0.1, 0.3],   # 0.3
                          'colsample_bytree': [0.8, 1]}   # 0.8
            grid_search = GridSearchCV(estimator=self.model,
                                       param_grid=parameters,
                                       n_jobs = 1,
                                       cv = 5  ,
                                       verbose=self.verbose)
            grid_search.fit(X, Y)
            return grid_search.best_estimator_
        else:
            return self.model

    def status(self, message):
        if self.verbose>0:
            print(message)
        return

    def train_autofeat(self, Xtr, Ytr):
        X, Y = Xtr, Ytr
        if len(self.features) > MAX_NUM_FEATURES_AUTOFEAT:
            self.status(f"[RF Feature Selection]: selecting {MAX_NUM_FEATURES_AUTOFEAT} features out of {len(self.features)}")

            rf = RandomForestRegressor()
            rf.fit(Xtr, Ytr)
            inds = np.argsort(rf.feature_importances_)[::-1]
            self.autofeat_inds = inds[:MAX_NUM_FEATURES_AUTOFEAT]

            X = Xtr[:, self.autofeat_inds]

        self.afreg = AutoFeatRegressor(verbose=self.verbose,
                                       feateng_steps=NUM_STEPS_AUTOFEAT,
                                       transformations=AUTOFEAT_TRANSFORMATIONS,
                                       always_return_numpy=True)
        Xaf = self.afreg.fit_transform(X, Y)
        return Xaf

    def train(self, df):
        df = df.copy() # to avoid warning "A value is trying to be set on a copy of a slice from a DataFrame."

        # average for slab and experiment settings
        # df = df.merge(df.groupby(['ИД_СЛЯБА'],
        #                             as_index=False, sort=False,
        #                             dropna=True)[mean_cols_without_temp].mean(),
        #                 on='ИД_СЛЯБА',
        #                 suffixes=('_orig', ''))

        # for cols in mean_cols_with_temp:
        #     groupby_cols = ['ИД_СЛЯБА'] + cols[0]
        #     df   = df.merge(df.groupby(groupby_cols,
        #                                     as_index=False,
        #                                     sort=False,
        #                                     dropna=True)[cols[1]].mean(),
        #                         how='left',
        #                         on=groupby_cols,
        #                         suffixes=('_orig', ''))
        #     for col in cols[1]:
        #         ind = df[pd.isna(df[col])].index
        #         df.loc[ind, col] = df.loc[ind, col+'_orig']

        df[self.target] = to_target(df, self.target)

        # HOW TO PREDICT THEN?
        # if self.target in temperature_labels:
        #     temp_label = temperature_labels[self.target]
        #     if temp_label not in self.features:
        #         self.features.append(temp_label)

        self.train_group_processors(df)
        self.generate_group_values(df)

        self.END_DATE = df['НАЧ_ПРОКАТ'].max()

        df = df.dropna(inplace=False, subset=self.features + [self.target])
        Xtr, Ytr = df[self.features].values, df[self.target].values
        Xtr, Ytr = self.scale(Xtr, Ytr)

        if len(Ytr) <= self.NUM_SAMPLES: # if re-fit was requested and there are no new rows
            return False                 # then do not train and do not save

        self.NUM_SAMPLES = len(Ytr)

        if self.autofeat:
            Xaf = self.train_autofeat(Xtr, Ytr)
            Xaf = self.scale_autofeat(Xaf, train=True)
            Xtr = np.hstack((Xtr, Xaf))

        self.status(Xtr.shape)

        self.model = self.tune(Xtr, Ytr)
        self.model.fit(Xtr, Ytr)

        Ypr = self.model.predict(Xtr)
        Ypr = self.rescale(Ypr)
        Ytr = self.rescale(Ytr)

        self.r2 = r2(Ytr, Ypr)
        self.std = np.std(Ytr)
        self.delta = 1.96*np.std(Ytr)*np.sqrt(1-0.4**2)
        self.relative_error = np.round(100*np.mean(np.abs((Ytr - Ypr)/Ytr)), 0)
        self.status("[Completed] model training")
        self.status(f"    R2: {self.r2}")
        self.status(f"    STD: {self.std}")
        self.status(f"    Delta: {self.delta}")
        self.status(f"    𝛿: {self.relative_error}")
        self.status("----------------")
        return True

    def predict(self, df, column_name=None):
        self.generate_group_values(df)
        X = df[self.features].values
        sl = ~np.any(np.isnan(X), axis=1)

        Xpr, _ = self.scale(X[sl])
        #Xpr[Xpr<0] = 0 # if new data out of training range

        if self.autofeat:
            Xpr_af =  Xpr.copy()
            Xpr_af[Xpr_af<0] = 0 # if new data out of training range

            Xaf = self.afreg.transform(Xpr_af[:, self.autofeat_inds])
            Xaf = self.scale_autofeat(Xaf, train=False)
            Xpr = np.hstack((Xpr, Xaf))

        ypred = self.model.predict(Xpr)
        ypred = self.rescale(ypred)

        Y = np.empty(len(X))
        Y[:] = np.nan
        Y[sl] = ypred
        df_pred = pd.DataFrame(index=df.index)

        if column_name is None:
            column_name = self.target
        df_pred[column_name] = Y
        return df_pred
