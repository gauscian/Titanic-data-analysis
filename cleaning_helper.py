import pandas as pd
import numpy as np
from random import shuffle

# this was a low hanging fruit. Replacing the None values with most frequent embarking station.
def fix_embarked(dataframe):
    dataframe.loc[61, "Embarked"] = 'S'
    dataframe.loc[829, "Embarked"] = 'S'


# cutting age variable
def cut_age_variable(dataframe, bins_, str_):
    cuts = pd.cut(dataframe[str_], bins=bins_)
    # categorizing the cuts variables
    hash_map = {}
    index_ = 0
    for e in cuts:
        if e not in hash_map:
            hash_map[e] = index_
            index_ += 1

    cat_variable = []
    for c,a in zip(cuts, dataframe[str_]):
        if np.isnan(a):
            cat_variable.append(np.nan)
        else:
            cat_variable.append(hash_map[c])

    return pd.Series(cat_variable)


def create_distribution_list(ans):
    v_c = ans.value_counts()
    distribution_list = []
    for i, freq in zip(v_c.index, v_c):
        distribution_list += ([int(i)] * freq)
    shuffle(distribution_list)
    return distribution_list


def fix_age(dataframe, distribution_list, ans, str_):
    dataframe['dis_'+str_] = ans
    for e in dataframe[dataframe['dis_'+str_].isnull()].index:
        dataframe.loc[e, 'dis_'+str_] = np.random.choice(distribution_list, replace=False)
    dataframe['dis_'+str_] = dataframe['dis_'+str_].astype(int)


def cont_discrete(dataframe, bins_, str_):
    # cutting the age_variable
    ans = cut_age_variable(dataframe, bins_, str_)
    # creating the distribution list
    dist_list = create_distribution_list(ans)
    # populating the Age NaNs
    fix_age(dataframe, dist_list, ans, str_)


def discretize_field(dataframe, str_):
    series = dataframe[str_]
    u_values = series.unique()
    h_map = {}
    counter = 0
    for u in u_values:
        if u not in h_map:
            h_map[u] = counter
            counter += 1
    new_list = list()
    for each in dataframe[str_]:
        new_list.append(h_map[each])

    dataframe['dis_'+str_] = pd.Series(new_list)


# using information from the names field.
def working_with_names(dataframe):
    ex_series = dataframe.Name.str.extract("([A-Za-z]*\.)")

    ls_ = []

    # based in the value counts obervations
    female_ = set(['Miss.', 'Mrs.', 'Ms.'])
    male_ = set(['Mr.'])
    child_ = set(['Master.'])
    imp_people = set(["Dr.", "Rev.", "Col.", "Mlle.", "Major.", "Jonkheer.", "Capt.", "Sir.", "Don.", "Countess.", "Lady.", "Mme."])

    for e in ex_series[0]:
        if e in female_:
            ls_.append(0)
        elif e in male_:
            ls_.append(1)
        elif e in child_:
            ls_.append(2)
        elif e in imp_people:
            ls_.append(3)

    print(dataframe)

    dataframe['dis_name'] = pd.Series(ls_)


# using information from the Siblings and Parch to create a single field
def have_siblings_not(dataframe):
    ls_ = []

    for s,p in zip(dataframe['SibSp'], dataframe['Parch']):
        if (s+p) > 0:
            ls_.append(1)
        else:
            ls_.append(0)

    dataframe['hasSomeOne'] = pd.Series(ls_)


def complete_pipeline(dataframe):
    dataframe.drop(labels=['Cabin', 'Ticket', 'PassengerId'], axis=1, inplace=True)

    cont_discrete(dataframe, 10, 'Age')
    cont_discrete(dataframe, 23, 'Fare')
    dataframe.drop(['Age', 'Fare'], inplace=True, axis=1)

    discretize_field(dataframe, 'Embarked')
    discretize_field(dataframe, 'Sex')
    dataframe.drop(['Embarked', 'Sex'], axis=1,inplace=True)

    working_with_names(dataframe)
    dataframe.loc[417, 'dis_name'] = 2
    dataframe['dis_name'] = dataframe['dis_name'].astype(int)
    dataframe.drop(['Name'], axis=1, inplace=True)

    have_siblings_not(dataframe)
    dataframe.drop(['SibSp','Parch'], axis=1, inplace=True)
    
    
# general methods for calculating the precision and recall
def calculate_precision(conf_matrix):
    conf_matrix = np.array(conf_matrix)
    prec_ = 0
    n = len(conf_matrix)
    for col in range(n):
        prec_ += (conf_matrix[col][col] / (np.sum(conf_matrix[:,col])))
    prec_ /= n
    return prec_

def calculate_recall(conf_matrix):
    conf_matrix = np.array(conf_matrix)
    rec_ = 0
    n = len(conf_matrix)
    for col in range(n):
        rec_ += (conf_matrix[col][col] / (np.sum(conf_matrix[col, :])))
    rec_ /= n
    return rec_

def calculate_f1_score(prec, recall):
    return ((2*prec*recall)/(prec+recall))
