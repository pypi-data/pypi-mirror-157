import numpy as np
import pandas as pd


targets = {
           'FPT': ['FPT'],
           'FVS': ['FVS'],
           'FOYD': ['FOYD'],
           'FOS': ['FOS'],
           'FPTP': ['FPTP'],
           'FVSP': ['FVSP'],
           'FOYDP': ['FOYDP'],
           'FYDR': ['FYDR'],
           'FUV': ['FUV_1', 'FUV_2', 'FUV_3'],
           'FDV': ['FDV_1', 'FDV_2', 'FDV_3'],
           'DWTT': ['DWTT1', 'DWTT2'],
           'DVC': ['DVC1', 'DVC2', 'DVC3'],
           'NB_': ['NB1', 'NB2'],
           'FPT05': ['FPT05'],
           'FPTP05': ['FPTP05']
           }


temperature_labels = {'FUV': 'T_KCU',
                      'FDV': 'T_KCV',
                      'DWTT': 'T_KCD',
                      'DVC': 'T_KCDV'}

type_sample = {'FUV': 'TUV1', 'FDV': 'TUV2'}


# time_columns = ['ДЛИТ_ПЕЧЬ']
time_columns = ['ЗАГР_ПЕЧЬ', 'ВЫГР_ПЕЧЬ', 'НАЧ_ПРОКАТ', 'КОН_ПРОКАТ']

mean_cols_without_temp = ['FPT', 'FVS', 'FOYD', 'FOS', 'FPTP', 'FVSP',
        'FOYDP', 'FYDR', 'NB1', 'NB2', 'FPT05', 'FPTP05', ]

mean_cols_with_temp = [(['TUV1', 'T_KCU'], ['FUV_1', 'FUV_2', 'FUV_3']),
                    (['TUV2', 'T_KCV'], ['FDV_1', 'FDV_2', 'FDV_3']),
                    (['T_KCD'], [ 'DWTT1', 'DWTT2']),
                    (['T_KCDV'], [ 'DVC1', 'DVC2', 'DVC3'])]


label_encoders = {'ПР_ГП': ['HOT'],  # 5
                  'ТИПТЕХЭСПЦ': ['ДСП', 'ГМП'],  # 4
                  'ПР_УВС': ['УВС'],
                 }


error_codes = ['КОД_ОШИБКИ',  # 2
               'КОД_ЦЛК',  # 7
               'СТОППИР'  # 2
              ]


groups = [['ДУО_ОБЖ_01','ДУО_ОБЖ_02','ДУО_ОБЖ_03','ДУО_ОБЖ_04','ДУО_ОБЖ_05','ДУО_ОБЖ_06','ДУО_ОБЖ_07','ДУО_ОБЖ_08','ДУО_ОБЖ_09','ДУО_ОБЖ_10','ДУО_ОБЖ_11','ДУО_ОБЖ_12','ДУО_ОБЖ_13','ДУО_ОБЖ_14','ДУО_ОБЖ_15'],
          ['ДУО_УСС_01','ДУО_УСС_02','ДУО_УСС_03','ДУО_УСС_04','ДУО_УСС_05','ДУО_УСС_06','ДУО_УСС_07','ДУО_УСС_08','ДУО_УСС_09','ДУО_УСС_10','ДУО_УСС_11','ДУО_УСС_12','ДУО_УСС_13','ДУО_УСС_14','ДУО_УСС_15'],
          ['ДУО_УСП_01','ДУО_УСП_02','ДУО_УСП_03','ДУО_УСП_04','ДУО_УСП_05','ДУО_УСП_06','ДУО_УСП_07','ДУО_УСП_08','ДУО_УСП_09','ДУО_УСП_10','ДУО_УСП_11','ДУО_УСП_12','ДУО_УСП_13','ДУО_УСП_14','ДУО_УСП_15'],
          ['ДУО_СКР_01','ДУО_СКР_02','ДУО_СКР_03','ДУО_СКР_04','ДУО_СКР_05','ДУО_СКР_06','ДУО_СКР_07','ДУО_СКР_08','ДУО_СКР_09','ДУО_СКР_10','ДУО_СКР_11','ДУО_СКР_12','ДУО_СКР_13','ДУО_СКР_14','ДУО_СКР_15'],
          ['КВР_ОБЖ_01','КВР_ОБЖ_02','КВР_ОБЖ_03','КВР_ОБЖ_04','КВР_ОБЖ_05','КВР_ОБЖ_06','КВР_ОБЖ_07','КВР_ОБЖ_08','КВР_ОБЖ_09','КВР_ОБЖ_10','КВР_ОБЖ_11','КВР_ОБЖ_12','КВР_ОБЖ_13','КВР_ОБЖ_14','КВР_ОБЖ_15'],
          ['КВР_УСС_01','КВР_УСС_02','КВР_УСС_03','КВР_УСС_04','КВР_УСС_05','КВР_УСС_06','КВР_УСС_07','КВР_УСС_08','КВР_УСС_09','КВР_УСС_10','КВР_УСС_11','КВР_УСС_12','КВР_УСС_13','КВР_УСС_14','КВР_УСС_15'],
          ['КВР_УСП_01','КВР_УСП_02','КВР_УСП_03','КВР_УСП_04','КВР_УСП_05','КВР_УСП_06','КВР_УСП_07','КВР_УСП_08','КВР_УСП_09','КВР_УСП_10','КВР_УСП_11','КВР_УСП_12','КВР_УСП_13','КВР_УСП_14','КВР_УСП_15'],
          ['КВР_СКР_01','КВР_СКР_02','КВР_СКР_03','КВР_СКР_04','КВР_СКР_05','КВР_СКР_06','КВР_СКР_07','КВР_СКР_08','КВР_СКР_09','КВР_СКР_10','КВР_СКР_11','КВР_СКР_12','КВР_СКР_13','КВР_СКР_14','КВР_СКР_15'],
          ['DELTA1_2','DELTA2_3','DELTA3_4','DELTA4_5','DELTA5_6','DELTA6_7','DELTA7_8','DELTA8_9','DELTA9_10', 'DELTA10_11','DELTA11_12','DELTA12_13','DELTA13_14','DELTA14_15']
         ]


#-----------------------------------------------
# processing utils

def group2name(value, inverse):
    if inverse:
        return value.split(',')
    else:
        return ','.join(value)


def to_target(df, target_label):
    # to do: use DB for targets
    # or remove from db
    return df[targets[target_label]].mean(axis=1).copy()


def flatten(t):
    # ex: [1, 2, 2, [3], [4, 5]] => [1, 2, 2, 3, 4, 5]
    # ex: [1, 2, 2, [3], [4, [5, 6]]] => [1, 2, 2, 3, 4, 5, 6]
    if not isinstance(t, list):
        return [t]
    flat_list = []
    for sublist in t:
        if isinstance(sublist, list):
            for item in sublist:
                for it in flatten(item):
                    flat_list.append(it)
        else:
            flat_list.append(sublist)
    return flat_list


def filter_NOMP(df):
    filtered = set(df[df['NOMP'].str.contains('П')].index) | set(df[df['NOMP'].str.contains('У')].index) | set(df[df['NOMP'].str.startswith('9')].index)
    return df.drop(index=list(filtered), inplace=False)


def process_nonnegative_groups(df):
    for col in flatten(groups):
        if col in df:
            # x = df[col].values
            # x[np.logical_or(np.isnan(x), x<0)] = 0
            # df[col] = x
            ind = df[df[col]<0].index
            df.loc[ind, col] = 0
    return


def time2num(df, columns):
    for column in columns:
            df[column] = df[column].astype(str)
            df[column] = df[column].apply(lambda x: np.dot(np.array(x.split(':'), dtype=float), np.array([1.0, 1.0/60])))
    return


def encode(df, label_encoders):
    for column in label_encoders:  # for each column where label encoding is necessary
        for i, label in enumerate(label_encoders[column]):  # for each label in column
            df.loc[df[column]==label, column] = i
        df[column].fillna(i+1, inplace=True)
    return


def fillna_columns(df, columns):
    for column in columns:
            df[column].fillna(0, inplace=True)
    return

def temperature_to_int(df, columns):
    for column in columns:
        df.loc[:, column] = df[column].apply(lambda x: x.replace('--','-') if isinstance(x, str) else x)
        df.loc[:, column] = df[column].apply(lambda x: x.replace('++','+') if isinstance(x, str) else x)
        df.loc[:, column] = df[column].apply(lambda x: int(x) if not pd.isna(x) else None)


def to_numeric(df):
    process_nonnegative_groups(df)
    # time2num(df, time_columns)
    encode(df, label_encoders)
    fillna_columns(df, error_codes)
    fillna_columns(df, flatten(groups))
    # temperature_to_int(df, temperature_labels.values())
    return df.copy()


