# -*- coding: utf-8 -*-

from imp import new_module
import unittest

import numpy as np
import pandas as pd

from ultron.optimize.model.loader import load_model
from ultron.optimize.model.treemodel import RandomForestClassifier
from ultron.optimize.model.treemodel import RandomForestRegressor
from ultron.optimize.model.treemodel import ExtraTreesClassifier
from ultron.optimize.model.treemodel import ExtraTreesRegressor
from ultron.optimize.model.treemodel import BaggingClassifier
from ultron.optimize.model.treemodel import BaggingRegressor
from ultron.optimize.model.treemodel import AdaBoostClassifier
from ultron.optimize.model.treemodel import AdaBoostRegressor
from ultron.optimize.model.treemodel import GradientBoostingClassifier
from ultron.optimize.model.treemodel import GradientBoostingRegressor
from ultron.optimize.model.treemodel import XGBClassifier
from ultron.optimize.model.treemodel import XGBRegressor
from ultron.optimize.model.treemodel import XGBTrainer


class TreeModel(unittest.TestCase):

    def setUp(self):
        self.features = list('0123456789')
        self.x = pd.DataFrame(np.random.randn(1000, 10), columns=self.features)
        self.y = np.random.randn(1000)
        self.sample_x = pd.DataFrame(np.random.randn(100, 10), columns=self.features)


    def test_gradinet_boosting_regress_persistence(self):
        model = GradientBoostingRegressor(features=self.features)
        model.fit(self.x, self.y)

        desc = model.save()
        new_model = load_model(desc)
        self.assertEqual(model.features, new_model.features)

        np.testing.assert_array_almost_equal(model.predict(self.sample_x),
                                             new_model.predict(self.sample_x))
        np.testing.assert_array_almost_equal(model.importances, new_model.importances)


    def test_gradinet_boosting_classify_persistence(self):
        model = GradientBoostingClassifier(features=self.features)
        y = np.where(self.y > 0, 1, 0)
        model.fit(self.x, y)

        desc = model.save()
        new_model = load_model(desc)
        self.assertEqual(model.features, new_model.features)

        np.testing.assert_array_almost_equal(model.predict(self.sample_x),
                                             new_model.predict(self.sample_x))
        np.testing.assert_array_almost_equal(model.importances, new_model.importances)


    
    def test_ada_boost_regress_persistence(self):
        model = AdaBoostRegressor(features=self.features)
        model.fit(self.x, self.y)

        desc = model.save()
        new_model = load_model(desc)
        self.assertEqual(model.features, new_model.features)

        np.testing.assert_array_almost_equal(model.predict(self.sample_x),
                                             new_model.predict(self.sample_x))
        np.testing.assert_array_almost_equal(model.importances, new_model.importances)

    
    def test_ada_boost_classify_persistence(self):
        model = AdaBoostClassifier(features=self.features)
        y = np.where(self.y > 0, 1, 0)
        model.fit(self.x, y)

        desc = model.save()
        new_model = load_model(desc)
        self.assertEqual(model.features, new_model.features)

        np.testing.assert_array_almost_equal(model.predict(self.sample_x),
                                             new_model.predict(self.sample_x))
        np.testing.assert_array_almost_equal(model.importances, new_model.importances)

    
    def test_bagging_regress_persistence(self):
        model = BaggingRegressor(features=self.features)
        model.fit(self.x, self.y)

        desc = model.save()
        new_model = load_model(desc)
        self.assertEqual(model.features, new_model.features)

        np.testing.assert_array_almost_equal(model.predict(self.sample_x),
                                             new_model.predict(self.sample_x))
        np.testing.assert_array_almost_equal(model.importances, new_model.importances)

    
    def test_bagging_classify_persistence(self):
        model = BaggingClassifier(features=self.features)
        y = np.where(self.y > 0, 1, 0)
        model.fit(self.x, y)

        desc = model.save()
        new_model = load_model(desc)
        self.assertEqual(model.features, new_model.features)

        np.testing.assert_array_almost_equal(model.predict(self.sample_x),
                                             new_model.predict(self.sample_x))
        np.testing.assert_array_almost_equal(model.importances, new_model.importances)


    
    def test_extra_trees_regress_persistence(self):
        model = ExtraTreesRegressor(features=self.features)
        model.fit(self.x, self.y)

        desc = model.save()
        new_model = load_model(desc)
        self.assertEqual(model.features, new_model.features)

        np.testing.assert_array_almost_equal(model.predict(self.sample_x),
                                             new_model.predict(self.sample_x))
        np.testing.assert_array_almost_equal(model.importances, new_model.importances)


    def test_extra_trees_classify_persistence(self):
        model = ExtraTreesClassifier(features=self.features)
        y = np.where(self.y > 0, 1, 0)
        model.fit(self.x, y)

        desc = model.save()
        new_model = load_model(desc)
        self.assertEqual(model.features, new_model.features)

        np.testing.assert_array_almost_equal(model.predict(self.sample_x),
                                             new_model.predict(self.sample_x))
        np.testing.assert_array_almost_equal(model.importances, new_model.importances)
    
    def test_random_forest_regress_persistence(self):
        model = RandomForestRegressor(features=self.features)
        model.fit(self.x, self.y)

        desc = model.save()
        new_model = load_model(desc)
        self.assertEqual(model.features, new_model.features)

        np.testing.assert_array_almost_equal(model.predict(self.sample_x),
                                             new_model.predict(self.sample_x))
        np.testing.assert_array_almost_equal(model.importances, new_model.importances)

    def test_random_forest_classify_persistence(self):
        model = RandomForestClassifier(features=self.features)
        y = np.where(self.y > 0, 1, 0)
        model.fit(self.x, y)

        desc = model.save()
        new_model = load_model(desc)
        self.assertEqual(model.features, new_model.features)

        np.testing.assert_array_almost_equal(model.predict(self.sample_x),
                                             new_model.predict(self.sample_x))
        np.testing.assert_array_almost_equal(model.importances, new_model.importances)

    def test_xgb_regress_persistence(self):
        model = XGBRegressor(features=self.features)
        model.fit(self.x, self.y)

        desc = model.save()
        new_model = load_model(desc)
        self.assertEqual(model.features, new_model.features)

        np.testing.assert_array_almost_equal(model.predict(self.sample_x),
                                             new_model.predict(self.sample_x))
        np.testing.assert_array_almost_equal(model.importances, new_model.importances)

    def test_xgb_classify_persistence(self):
        model = XGBClassifier(features=self.features)
        y = np.where(self.y > 0, 1, 0)
        model.fit(self.x, y)

        desc = model.save()
        new_model = load_model(desc)
        self.assertEqual(model.features, new_model.features)

        np.testing.assert_array_almost_equal(model.predict(self.sample_x),
                                             new_model.predict(self.sample_x))
        np.testing.assert_array_almost_equal(model.importances, new_model.importances)

    def test_xgb_trainer_equal_classifier(self):
        model1 = XGBClassifier(n_estimators=100,
                               learning_rate=0.1,
                               max_depth=3,
                               features=self.features,
                               random_state=42)

        model2 = XGBTrainer(features=self.features,
                            objective='reg:logistic',
                            booster='gbtree',
                            tree_method='exact',
                            n_estimators=100,
                            learning_rate=0.1,
                            max_depth=3,
                            random_state=42)

        y = np.where(self.y > 0, 1, 0)
        model1.fit(self.x, y)
        model2.fit(self.x, y)

        predict1 = model1.predict(self.sample_x)
        predict2 = model2.predict(self.sample_x)
        predict2 = np.where(predict2 > 0.5, 1., 0.)
        np.testing.assert_array_almost_equal(predict1, predict2)

    def test_xgb_trainer_persistence(self):
        model = XGBTrainer(features=self.features,
                           objective='binary:logistic',
                           booster='gbtree',
                           tree_method='hist',
                           n_estimators=200)
        y = np.where(self.y > 0, 1, 0)
        model.fit(self.x, y)

        desc = model.save()
        new_model = load_model(desc)
        self.assertEqual(model.features, new_model.features)

        np.testing.assert_array_almost_equal(model.predict(self.sample_x),
                                             new_model.predict(self.sample_x))
        np.testing.assert_array_almost_equal(model.importances, new_model.importances)