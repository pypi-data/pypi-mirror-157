import logging
import numpy as np
import pandas as pd
from typing import Union, List
from torch.utils.data import Dataset
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, StandardScaler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('Data')


class SimpleData(Dataset):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __len__(self):
        return len(self.y)

    def __getitem__(self, idx):
        return self.x[idx], self.y[idx]


class MILData():
    def __init__(self, dataframe: pd.DataFrame,
                 time_column: str = None, drop_time_col: bool = True) -> None:
        self.df = dataframe
        self.parameters_list = dataframe.columns.values.tolist()
        self.param_index_dict = {param: idx for idx, param in enumerate(self.parameters_list)}
        self.index_param_dict = {idx: param for idx, param in self.param_index_dict.items()}
        self.time_column = time_column
        self.data_is_scaled = False

        if drop_time_col:
            self.df.drop(columns=[time_column], inplace=True)

    def MIL_processing(self, dataframe: pd.DataFrame = None,
                       test_size: float = 0.3,
                       val_size: float = 0,
                       anonamly_column: str = 'Anomaly',
                       flight_id_column: str = 'flight_id',
                       different_length_method: str = 'pad',
                       pad_value: Union[int, str] = 'max',
                       anomalies: Union[int, List[int]] = 1) -> None:

        assert test_size >= 0
        assert val_size >= 0

        if dataframe is None:
            dataframe = self.df.copy()

        if isinstance(anomalies, int):
            anomalies = [anomalies]

        self.anomaly_column = anonamly_column
        self.flight_id_column = flight_id_column

        # Assumes that normal flights have an index of 0
        nom_flights_count = int(dataframe[dataframe[anonamly_column] == 0][flight_id_column].unique().shape[0])
        adverse_flights_count = 0
        for idx_anomaly in anomalies:
            adverse_flights_count += int(dataframe[dataframe[anonamly_column] == idx_anomaly][flight_id_column].
                                         unique().shape[0])
        n_flights = nom_flights_count + adverse_flights_count
        logger.info(f"There are: {n_flights}, {nom_flights_count} nominal and {adverse_flights_count} adverse")

        flight_class = np.ones((n_flights, 1)) * 10
        self.flights_lengths = np.zeros((n_flights, 1))
        self.fligths_indices = np.ones((n_flights, 1)) * -1
        split_index = np.arange(0, n_flights, 1).reshape(-1, 1)

        # Create a list of flights
        def append_dataframe_of_individual_flights(counter: int = 0, new_list: List[pd.DataFrame] = []):
            max_fl_length = 0
            min_fl_length = 1e6
            nom_anomalies = [0] + anomalies
            logger.debug(f"Labels to loop through: {nom_anomalies}")
            # Fill all the nominal flights and anomalies
            for idx in nom_anomalies:
                list_ids_of_flights = dataframe[dataframe[anonamly_column] == idx][flight_id_column].\
                                      unique().astype(int)
                for fl_id in list_ids_of_flights:
                    # L x D shape
                    fl = dataframe[(dataframe[flight_id_column] == fl_id) & (dataframe[anonamly_column] == idx)]
                    length_of_current_fl = len(fl)
                    logger.debug(f'Label: {idx}. Flight idx: {fl_id} has length: {length_of_current_fl}')
                    self.flights_lengths[counter] = length_of_current_fl

                    if length_of_current_fl > max_fl_length:
                        max_fl_length = length_of_current_fl
                    if length_of_current_fl < min_fl_length:
                        min_fl_length = length_of_current_fl

                    flight_class[counter] = idx
                    self.fligths_indices = fl_id
                    new_list.append(fl)
                    counter += 1

            return new_list, counter, max_fl_length

        temp, counter, self.max_flight_length = append_dataframe_of_individual_flights()

        # TODO: Make this work with variable flight lengths
        # Stacking flights together
        unique_flight_lengths = np.unique(self.flights_lengths.flatten())
        if len(unique_flight_lengths) == 1:
            try:
                data = np.stack(temp, axis=0)  # shape [# flights, sample per flight, n_features]
            except ValueError as err:
                if err == "all input arrays must have the same shape":
                    logger.error(err)
                raise
            except Exception as err:
                logger.error(err)
                raise
        else:
            assert different_length_method in ['pad', 'list'], "'different_length_method' can only be 'pad' or 'list'"
            # Apply padding so that all time-series have the same length
            if different_length_method == 'pad':
                logger.info(f'Will pad dataframes with length lower than {self.max_flight_length}')
                idx_flight_lenght_lower_than_max = np.where(self.flights_lengths.flatten() < self.max_flight_length)[0]
                for idx_lower in idx_flight_lenght_lower_than_max:
                    fl_with_diff_length = temp[idx_lower]
                    diff_in_length = self.max_flight_length - len(fl_with_diff_length)
                    padded_df = self.pad_pandas_dataframe(fl_with_diff_length,
                                                          number_of_pads=diff_in_length,
                                                          pad_value=pad_value)
                    temp[idx_lower] = padded_df
                data = np.stack(temp, axis=0)
            elif different_length_method == 'list':
                # Create list of np arrays of dims [L1, D], [L2, D], etc..
                data = []
                for fl in temp:
                    data.append(fl.values)

        self.flight_class = flight_class

        x_train_idx, x_test_idx, y_train, y_test = train_test_split(split_index, flight_class,
                                                                    test_size=test_size,
                                                                    stratify=flight_class)

        # Binary case
        if len(np.unique(y_train)) == 2:
            y_train[np.where(y_train != 0)] = 1
            y_test[np.where(y_test != 0)] = 1

        if not isinstance(data, list):
            self.trainX = data[x_train_idx].reshape(len(x_train_idx),
                                                    self.max_flight_length, -1)
        else:
            # Re-order list
            self.trainX = [data[int(i)] for i in x_train_idx]

        if val_size > 0:
            x_test_idx, x_val_idx, y_test, y_val = train_test_split(x_test_idx, y_test,
                                                                    test_size=val_size,
                                                                    stratify=y_test)
            self.valIndex = x_val_idx
            if not isinstance(data, list):
                self.valX = data[x_val_idx].reshape(len(x_val_idx), self.max_flight_length, -1)
            else:
                self.valX = [data[int(i)] for i in x_val_idx]
            self.valY = y_val
            self.using_val_data = True
        else:
            self.using_val_data = False

        self.trainIndex = x_train_idx
        if not isinstance(data, list):
            self.testX = data[x_test_idx].reshape(len(x_test_idx),
                                                  self.max_flight_length, -1)
        else:
            self.testX = [data[int(i)] for i in x_test_idx]

        self.trainY, self.testY = y_train, y_test
        self.testIndex = x_test_idx

    def normalize_data(self, method: str = 'zscore',
                       avoid_columns: list = []) -> None:

        assert method.lower() in ['zscore', 'minmax'], 'Only "minmax" and "zscore" are available methods'

        self.scaler = StandardScaler() if method == 'standard_scaler' else MinMaxScaler()
        self.data_is_scaled = True

        # Scale data
        if not isinstance(self.trainX, list):
            N_train, L, D = self.trainX.shape
            N_test, _, _ = self.testX.shape
            if self.using_val_data:
                N_val, _, _ = self.valX.shape

            indices_cols_avoid = [self.param_index_dict[param] for param in avoid_columns]
            if len(indices_cols_avoid) > 0:
                # N*L x D
                scaled_x_train = self.scaler.fit_transform(np.delete(self.trainX,
                                                                     indices_cols_avoid,
                                                                     axis=2).reshape(N_train * L,
                                                                                     D - len(indices_cols_avoid)))
                scaled_x_test = self.scaler.transform(np.delete(self.testX,
                                                                indices_cols_avoid,
                                                                axis=2).reshape(N_test * L,
                                                                                D - len(indices_cols_avoid)))
                if self.using_val_data:
                    scaled_x_val = self.scaler.transform(np.delete(self.testX,
                                                                   indices_cols_avoid,
                                                                   axis=2).reshape(N_val * L,
                                                                                   D - len(indices_cols_avoid)))
            else:
                scaled_x_train = self.scaler.fit_transform(self.trainX)
                scaled_x_test = self.scaler.transform(self.testX)
                if self.using_val_data:
                    scaled_x_val = self.scaler.transform(self.valX)

            # Reshape data
            self.scaled_x_train = scaled_x_train.reshape(N_train, L, -1)
            self.scaled_x_test = scaled_x_test.reshape(N_test, L, -1)
            if self.using_val_data:
                self.scaled_x_val = scaled_x_val.reshape(N_val, L, -1)
        else:
            x_train = np.concatenate(self.trainX)
            train_length_each_timeseries = [len(i) for i in self.trainX]
            x_test = np.concatenate(self.testX)
            test_length_each_timeseries = [len(i) for i in self.testX]
            if self.using_val_data:
                x_val = np.concatenate(self.valX)
                val_length_each_timeseries = [len(i) for i in self.valX]

            indices_cols_avoid = [self.param_index_dict[param] for param in avoid_columns]

            if len(indices_cols_avoid) > 0:
                scaled_x_train = self.scaler.fit_transform(np.delete(x_train,
                                                                     indices_cols_avoid,
                                                                     axis=1))
                scaled_x_test = self.scaler.transform(np.delete(x_test,
                                                                indices_cols_avoid,
                                                                axis=1))
                if self.using_val_data:
                    scaled_x_val = self.scaler.transform(np.delete(x_val,
                                                                   indices_cols_avoid,
                                                                   axis=1))
            else:
                scaled_x_train = self.scaler.fit_transform(x_train)
                scaled_x_test = self.scaler.transform(x_test)
                self.scaled_x_test = np.array_split(scaled_x_test, np.cumsum(test_length_each_timeseries))
                if self.using_val_data:
                    scaled_x_val = self.scaler.transform(x_val)

            # Re-create the list of numpy arrays
            self.scaled_x_train = np.array_split(scaled_x_train, np.cumsum(train_length_each_timeseries))
            self.scaled_x_test = np.array_split(scaled_x_test, np.cumsum(test_length_each_timeseries))
            if self.using_val_data:
                self.scaled_x_val = np.array_split(scaled_x_val, np.cumsum(val_length_each_timeseries))

    def retrieve_flight_id_using_flight_idx(self, idx: int, data_set: str = 'train'):

        if not isinstance(self.trainX, list):
            if data_set == 'train':
                return int(self.trainX[idx, 0, self.param_index_dict[self.flight_id_column]])
            elif data_set == 'test':
                return int(self.testX[idx, 0, self.param_index_dict[self.flight_id_column]])
            else:
                return int(self.valX[idx, 0, self.param_index_dict[self.flight_id_column]])
        else:
            if data_set == 'train':
                return int(self.trainX[idx][0, self.param_index_dict[self.flight_id_column]])
            elif data_set == 'test':
                return int(self.testX[idx][0, self.param_index_dict[self.flight_id_column]])
            else:
                return int(self.valX[idx][0, self.param_index_dict[self.flight_id_column]])

    def retrieve_original_flight_data(self, idx: int, data_set: str = 'train',
                                      parameter: str = None):

        parameters_list = [parameter] if parameter is not None else self.parameters_list
        return self.df[self.df[self.flight_id_column] == self.retrieve_flight_id_using_flight_idx(idx,
                                                                                                  data_set)][parameters_list]

    def retrieve_flight_index_using_flight_id(self, flight_id: int,
                                              data_set: str = 'train'):

        if not isinstance(self.trainX, list):
            if data_set == 'train':
                return np.where(self.trainX[:, 0, self.param_index_dict[self.flight_id_column]] == flight_id)[0]
            elif data_set == 'test':
                return np.where(self.testX[:, 0, self.param_index_dict[self.flight_id_column]] == flight_id)[0]
            elif data_set == 'val':
                return np.where(self.valX[:, 0, self.param_index_dict[self.flight_id_column]] == flight_id)[0]
        else:
            if data_set == 'train':
                return [idx for idx in range(len(self.trainX)) if len(np.where(self.trainX[idx][0,
                                                                                                self.param_index_dict[self.flight_id_column]] == flight_id)[0]) > 0][0]
            elif data_set == 'test':
                return [idx for idx in range(len(self.testX)) if len(np.where(self.testX[idx][0,
                                                                                              self.param_index_dict[self.flight_id_column]] == flight_id)[0]) > 0][0]
            elif data_set == 'val':
                return [idx for idx in range(len(self.valX)) if len(np.where(self.valX[idx][0,
                                                                                            self.param_index_dict[self.flight_id_column]] == flight_id)[0]) > 0][0]

    @staticmethod
    def pad_pandas_dataframe(dataframe: pd.DataFrame,
                             pad_value: Union[int, str] = 'max',
                             number_of_pads: int = 1,
                             position: str = 'tailing'):

        if isinstance(pad_value, str):
            assert pad_value.lower() in ['min', 'max', 'mean', 'median'],\
                   '"pads_value" as a str can only be "min", "max", "mean", or "median"'
            if 'max' in pad_value:
                pad_value = dataframe.max().tolist()
                df_temp = pd.DataFrame([pad_value] * number_of_pads,
                                       columns=dataframe.columns)
            elif 'min' in pad_value:
                pad_value = dataframe.min().tolist()
                df_temp = pd.DataFrame([pad_value] * number_of_pads,
                                       columns=dataframe.columns)
            elif 'mean' in pad_value:
                pad_value = dataframe.mean().tolist()
                df_temp = pd.DataFrame([pad_value] * number_of_pads,
                                       columns=dataframe.columns)
            elif 'median' in pad_value:
                pad_value = dataframe.median().tolist()
                df_temp = pd.DataFrame([pad_value] * number_of_pads,
                                       columns=dataframe.columns)
        elif isinstance(pad_value, int):
            df_temp = pd.DataFrame([[pad_value] * dataframe.shape[1]] * number_of_pads,
                                   columns=dataframe.columns)

        if position == 'tailing':
            return dataframe.append(df_temp, ignore_index=True)
        else:
            return df_temp.append(dataframe, ignore_index=True)
