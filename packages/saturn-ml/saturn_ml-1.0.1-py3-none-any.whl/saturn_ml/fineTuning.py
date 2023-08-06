"""
DOCUMENTATION 

This script aims to tune your model with different settings which includes randomized search, grid search or optuna 

"""


from cv2 import grabCut
import numpy as np 
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from xgboost import XGBRegressor



class autoTuning: 
    
    
    def __init__(self, model) -> None:
        self.model = model


    def autoTuningRFr(self, train, labels):
        # n_jobs = -1 uses all the cores available 
        rf = RandomForestRegressor(random_state= 42, n_jobs= -1 , verbose = 1)
        
        # number of trees in random forests 
        n_estimators = [int(x) for x in np.linspace(start = 200 , stop = 2000, num = 10)]
        
        # number of features to consider at every split
        max_features = ['auto', 'sqrt']

        # maximum number of levels in tree
        max_depth = [int(x) for x in np.linspace(10, 110, num = 11)]
        max_depth.append(None)
        
        # min number of  samples required to split a node 
        min_samples_split = [2, 5, 10]

        # min number of samples required at each leaf node 
        min_samples_leaf = [1, 2, 4]

        # method of selecting samples for training each tree
        bootstrap = [True, False]

        # create a random grid 
        
        random_grid = {
            
            'n_estimators' : n_estimators,
            'max_features' : max_features,
            'max_depth' : max_depth, 
            'min_samples_split' : min_samples_split, 
            'min_samples_leaf' : min_samples_leaf,
            'bootstrap' : bootstrap
        }

        rf_random = RandomizedSearchCV(estimator= rf, param_distributions= random_grid,
                                       n_iter= 100, cv = 3, verbose = 2, random_state=42,
                                       n_jobs= -1)

        rf_random.fit(train, labels)

        return rf_random



    def autoTuningXGBr(self, train, labels): 
        """
        Fine tuning for XGBRegressor, you may increase your CV, if you have smaller 
        sized dataset
        """

        model = XGBRegressor()

        parameters = {
            'nthread' : [4],
            'objective' : ['reg:linear'],
            'learning_rate' : [0.3, 0.05, .07],
            'max_depth' : [5,6,7],
            'min_child_weight' : [4], 
            'silent' : [1],
            'subsample' : [0.7], 
            'colsample_bytree' : [0.7], 
            'n_estimators' : [350, 500, 700] 
        }
        
        
        
        grid = GridSearchCV(model, parameters, cv = 2, n_jobs=-1, verbose = True)
        grid.fit(train, labels)
        return grid