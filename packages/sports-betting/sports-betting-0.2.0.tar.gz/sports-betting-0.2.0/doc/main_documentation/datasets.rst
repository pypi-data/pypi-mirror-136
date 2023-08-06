########
Datasets
########

The `sports-betting` package provides a set of classes that help to download 
sports betting data.

***********
Dataloaders
***********

Each dataloader class corresponds to a data source or a combination 
of data sources. Their methods return datasets suitable for machine 
learning modelling. There various dataloaders available while all of 
them inherit from the same base class and provide the same public API.

A dataloader is initialized with the parameter ``param_grid`` that selects the training 
data to extract. You can get the available parameters and their values from the 
class method :meth:`get_all_params`. For example, the available parameters for the 
:class:`DummySoccerDataLoader` are the following::

   >>> from sportsbet.datasets import DummySoccerDataLoader
   >>> all_params = DummySoccerDataLoader.get_all_params()
   >>> list(all_params)
   [...{'division': 1, 'league': 'Spain', 'year': 1997}, {'division': 2, 'league': 'Spain', 'year': 1999}, {'division': 2, 'league': 'England', 'year': 1997}...]

The default value of ``param_grid`` is ``None`` and corresponds to the selection 
of all data. In the following example we select only the data of 
the Spanish end English leagues for all available divisions and years::

      >>> dataloader = DummySoccerDataLoader(param_grid={'league': ['Spain', 'England']})

Extracting the training data
============================

You can extract the training data using the method :meth:`extract_train_data` 
that accepts the parameters ``drop_na_thres`` and ``odds_type``. The training data 
is a tuple of the input matrix ``X_train``, the multi-output targets ``Y_train`` 
and the odds matrix ``Odds_train``.

Tha parameter ``drop_na_thres`` controls the proportion of the columns and rows with 
missing values that will be removed from the input matrix ``X_train``. It takes values in the range 
:math:`[0.0, 1.0]`.

The parameter ``odds_type`` selects the type of odds that will be used for the odds matrix ``Odds_train``. 
It also affects the columns of the multi-output targets ``Y_train`` since there is a correspondence between 
``Y_train`` and ``Odds_train``. You can get the available odds types from the class method :meth:`get_odds_types`:

   >>> DummySoccerDataLoader.get_odds_types()
   ['interwetten', 'williamhill']

Initially we extract the training data using the default values of ``drop_na_thres`` and ``odds_type``
which are ``None`` for both of them::
   
   >>> X_train, Y_train, O_train = dataloader.extract_train_data()

No columns are dropped from the input matrix ``X_train``::

   >>> X_train
               division   league  year    home_team    away_team ... williamhill__away_win__odds
   date                                                          ...
   1997-05-04         1    Spain  1997  Real Madrid    Barcelona ...                         NaN
   1998-03-04         3  England  1998    Liverpool      Arsenal ...                         NaN
   1999-03-04         2    Spain  1999    Barcelona  Real Madrid ...                         NaN

The multi-output targets matrix ``Y_train`` is the following::

   >>> Y_train
      away_win__full_time_goals ... under_2.5_goals__full_time_goals
   0                      False ...                            False
   1                       True ...                            False
   2                      False ...                            False

No odds matrix is returned:

   >>> O_train is None
   True

Instead if we extract the training data using specific values of ``drop_na_thres`` and ``odds_type`` then::
   
   >>> X_train, Y_train, O_train = dataloader.extract_train_data(drop_na_thres=1.0, odds_type='williamhill')

Columns that contain missing values are dropped from the input matrix ``X_train``::

   >>> X_train
               division   league  year ... williamhill__home_win__odds
   date                                ...                                                                                                                                         
   1997-05-04         1    Spain  1997 ...                         2.5
   1998-03-04         3  England  1998 ...                         2.0
   1999-03-04         2    Spain  1999 ...                         2.0

The multi-output targets ``Y_train`` is the following::

   >>> Y_train
      away_win__full_time_goals  ... home_win__full_time_goals
   0                      False  ...                      True
   1                       True  ...                     False
   2                      False  ...                     False

The corresponding odds matrix is the following:

   >>> O_train
      williamhill__away_win__odds ... williamhill__home_win__odds
   0                          NaN ...                         2.5
   1                          NaN ...                         2.0
   2                          NaN ...                         2.0
   

Extracting the fixtures data
============================

Once the training data are extracted, it is straightforward to extract 
the corresponding fixtures data using the method :meth:`extract_fixtures_data`:

   >>> X_fix, Y_fix, O_fix = dataloader.extract_fixtures_data()

The method accepts no parameters and the extracted fixtures input matrix has 
the same columns as the latest extracted input matrix for the training data::

   >>> X_fix
                               division  league ... williamhill__home_win__odds
   date                                                                                                                                                                                      
   ...         4     NaN ... 3.5
   ...         3  France ... 2.5

The odds matrix is the following::

   >>> O_fix
      williamhill__away_win__odds ... williamhill__home_win__odds
   0                          2.0 ...                         3.5
   1                          2.5 ...                         2.5

Since we are extracting the fixtures data, there is no target matrix::

   >>> Y_fix is None
   True
