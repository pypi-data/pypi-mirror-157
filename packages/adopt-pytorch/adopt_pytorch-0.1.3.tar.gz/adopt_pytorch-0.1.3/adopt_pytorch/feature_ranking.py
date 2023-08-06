import logging
import adopt_pytorch.config as config
import numpy as np
import pandas as pd
from typing import List, Union

import torch

from adopt_pytorch.models import ADOPT

logging.basicConfig(level=config.log['feature_ranking'])
logger = logging.getLogger('feature_ranking')


# TODO: Might need to benchmark using torch vs using np for the computations, especially when GPU is not used with torch
def disturb_parameters(clf: ADOPT, input_values: Union[torch.Tensor, np.ndarray] = None,
                       param_index_dict: dict = None, list_parameters: list = None,
                       standard_deviation_scale: List[int] = None,
                       precursor_score_list: list = None) -> list:
    """Perturb each paramters for one flight.

    Args:
        clf (ADOPT): _description_
        input_values (Union[torch.Tensor, np.ndarray], optional): _description_. Defaults to None.
        list_parameters (list, optional): _description_. Defaults to None.
        standard_deviation_scale (List[int], optional): _description_. Defaults to [2, -2].
        precursor_score_list (list, optional): _description_. Defaults to None.
    """

    if standard_deviation_scale is None:
        standard_deviation_scale = config.standard_deviation_scale

    assert standard_deviation_scale[0] > standard_deviation_scale[1], 'Make sure the first index of '\
           'standard_deviation_scale is the upper limit'

    device = clf.device
    if (param_index_dict is not None) and (list_parameters is not None):
        index_parameters = [idx for param, idx in param_index_dict.items() if param in list_parameters]
    elif (list_parameters is not None) and (param_index_dict is None):
        index_parameters = [idx for idx in range(len(clf.parameters_list))]
    else:
        # Perturb all parameters
        index_parameters = [idx for idx in range(len(clf.parameters_list))]
        list_parameters = clf.parameters_list

    # Construct param: modified_precursor_score dict
    feature_precursor_score_dict = {param: {'upper': None, 'lower': None} for param in list_parameters}

    # Time to pertub the parameter and evaluate the precursor score
    if input_values is None:
        # 3D Tensor of shape: N, L, D
        input_values = clf.input_values
    elif torch.is_tensor(input_values):
        input_values = input_values.view(1, input_values.size(0), input_values.size(1))
    else:
        if len(input_values.shape) == 2:
            input_values = input_values.reshape(1, input_values.shape[0], input_values.shape[1])
        input_values = torch.Tensor(input_values)

    # Perform forward pass for regular input
    feature_precursor_score_dict['prediction_likelihood'] = clf(input_values, save_input=False).detach().numpy()
    feature_precursor_score_dict['original_score'] = clf.proba_time.detach().numpy()

    input_values = input_values.to(device)

    # This can be used to combine precursor scores of variable lengths
    if precursor_score_list is None:
        precursor_score_list = []

    for idx_param, param in zip(index_parameters, list_parameters):
        for case_num, case in enumerate(['upper', 'lower']):
            logger.info(f"Case: {case}. Computing pertubation for {param}")
            modified_input_values = input_values.clone()
            feature_input_values = modified_input_values[:, :, idx_param]

            # Compute stardard deviation and apply scale
            standard_deviation_with_scale = torch.std(feature_input_values) * standard_deviation_scale[case_num]

            # Add the std to the input value
            feature_input_values += standard_deviation_with_scale

            # Replace the values in original tensor
            modified_input_values[:, :, idx_param] = feature_input_values

            # Perform forward passes
            _ = clf(modified_input_values, save_input=False).detach().numpy()
            precursor_score = clf.proba_time.detach().numpy()

            feature_precursor_score_dict[param][case] = precursor_score

    precursor_score_list.append(feature_precursor_score_dict)

    return precursor_score_list


def compute_features_precursor_scores(precursor_score_list: List[dict],
                                      standard_deviation_scale: List[int] = None):

    if standard_deviation_scale is None:
        standard_deviation_scale = config.standard_deviation_scale

    param_score_list_of_dict = []
    standard_deviation_scale = standard_deviation_scale + [None]
    param_score_dict = {}
    for precursor_score_dict in precursor_score_list:
        # Shape is N, L, D=1
        original_precursor_score: np.ndarray = precursor_score_dict['original_score'].flatten()
        start, end = identify_start_end_threshold(original_precursor_score)
        for param, value in precursor_score_dict.items():
            if param in ['original_score', 'prediction_likelihood']:
                # skip
                continue
            param_score_dict[param] = {'score': [], 'standard_deviation': []}
            for window_start, window_end in zip(*[start, end]):
                # Usually 1 loop but could be more sometimes...
                mean_original_precursor_score = original_precursor_score[window_start: window_end + 1]
                # Shape is N, L, D=1
                window_upper_precursor_score: np.ndarray = value['upper'].flatten()[window_start: window_end + 1]
                window_lower_precursor_score: np.ndarray = value['lower'].flatten()[window_start: window_end + 1]

                upper_p_diff = round((np.mean(mean_original_precursor_score) -
                                     (np.mean(window_upper_precursor_score))) /
                                     np.mean(mean_original_precursor_score) * 100, 3)
                lower_p_diff = round((np.mean(mean_original_precursor_score) -
                                     (np.mean(window_lower_precursor_score))) /
                                     np.mean(mean_original_precursor_score) * 100, 3)

                param_score_dict[param]['score'].append(min(upper_p_diff, lower_p_diff, 0))
                param_score_dict[param]['standard_deviation'].append(standard_deviation_scale[np.argmin([upper_p_diff,
                                                                                                         lower_p_diff,
                                                                                                         0])])
        param_score_list_of_dict.append(param_score_dict)
    return param_score_list_of_dict


def identify_start_end_threshold(precursor_score: np.ndarray, threshold=0.5):

    if len(precursor_score.shape) > 1:
        precursor_score = precursor_score.flatten()

    flagged_steps = np.where(precursor_score > threshold)[0]
    # Create pandas series
    df = pd.DataFrame(data={'Indices': flagged_steps})
    indices_diff = df.Indices.diff()
    df['window_groups'] = (indices_diff != 1).astype(int).cumsum().values
    windows = df.groupby('window_groups').agg({'Indices': ['min', 'max']}).values
    start = windows.flatten()[0::2]
    end = windows.flatten()[1::2]

    # remove single points
    start_final = []
    end_final = []

    for s, e in zip(*[start, end]):
        if s != e:
            start_final.append(s)
            end_final.append(e+1)
    start_final = np.asarray(start_final)
    end_final = np.asarray(end_final)

    return start_final, end_final

    # flagged_steps = np.asarray([p > threshold for p in precursor_score]).flatten()
    # # Find indices where arrays are not aligned i.e. where the flagging starts and ends
    # flag_steps_indices = np.flatnonzero(flagged_steps[1:] != flagged_steps[:-1])
    # # Start and End indices
    # start = flag_steps_indices[0::2]
    # end = flag_steps_indices[1::2]

    # # last end index would not appear if the score is higher than threshold all the way to the end
    # if len(start) != len(end):
    #     end = np.append(end, len(flagged_steps))

    # return start, end


def rank_features(features_score_list_of_dict: List[dict] = None,
                  precursor_score_list: List[dict] = None,
                  standard_deviation_scale: List[int] = [2, -2]):

    if standard_deviation_scale is None:
        standard_deviation_scale = config.standard_deviation_scale

    sorted_features_list = []
    sorted_scores_list = []
    if features_score_list_of_dict is None and precursor_score_list is None:
        raise '"features_score_list_of_dict" and "precursor_score_list" cannot both be None'

    if precursor_score_list is not None:
        features_score_list_of_dict = compute_features_precursor_scores(precursor_score_list, standard_deviation_scale)

    for features_score_dict in features_score_list_of_dict:
        sorted_parameters_list_of_dict = sorted(features_score_dict.items(),
                                                key=lambda x: min(x[1]['score']))
        sorted_features_list.append([param[0] for param in sorted_parameters_list_of_dict])
        sorted_scores_list.append([abs(min(param[1]['score'])) for param in sorted_parameters_list_of_dict])

    return sorted_features_list, sorted_scores_list
