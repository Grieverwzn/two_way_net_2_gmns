# In[0] Package
import pandas as pd
import os
import numpy as np
import time

pd.options.display.max_columns = 20
from .setting import *


# In[0] Join name geometry on link.csv 
def _link_geometry(from_node_id, to_node_id, node_x_coord_dict, node_y_coord_dict):
    X1 = node_x_coord_dict[from_node_id]
    Y1 = node_y_coord_dict[from_node_id]

    X2 = node_x_coord_dict[to_node_id]
    Y2 = node_y_coord_dict[to_node_id]
    result = "LINESTRING (" + str(X1) + ' ' + str(Y1) + ", " + str(X2) + ' ' + str(Y2) + ")"
    return result


# Create the folder for further validation
def _mkdir(path):
    import os

    path = path.strip()
    path = path.rstrip("\\")

    isExists = os.path.exists(path)

    if not isExists:
        os.makedirs(path)
        print(path + ' create the folder sucessfully')
        return True
    else:
        print(path + ' the folder already exists')
        return False


# In[1] Join name geometry on link.csv 
def _conversion_AB(row):
    record = -1
    if row.Dir == 0:
        record = [str(int(row.ID)) + str('AB'), str(int(row.ID)) + str('BA'), str(row.ID), 1, 0, \
                  anode_dict[row.ID], bnode_dict[row.ID], anode_dict[row.ID], bnode_dict[row.ID], \
                  row['AB Length'], row['AB Lanes'], row['AB Speed'], \
                  int(row.link_type), int(row.FT), int(row.AT), \
                  100 * row.AT + row.FT]
        if len(ab_addtional_list) > 0:
            for name in ab_addtional_list:
                record.append(float(row[name]))
    elif row.Dir == 1:
        record = [str(int(row.ID)) + str('AB'), '', str(int(row.ID)), 1, 1, \
                  anode_dict[row.ID], bnode_dict[row.ID], anode_dict[row.ID], bnode_dict[row.ID], \
                  row['AB Length'], row['AB Lanes'], row['AB Speed'], \
                  int(row.link_type), int(row.FT), int(row.AT), \
                  100 * row.AT + row.FT]
        if len(ab_addtional_list) > 0:
            for name in ab_addtional_list:
                record.append(float(row[name]))
    return record


def _conversion_BA(row):
    record = -1
    if row.Dir == 0:
        record = [str(int(row.ID)) + str('BA'), str(int(row.ID)) + str('AB'), str(int(row.ID)), 1, 0, \
                  bnode_dict[row.ID], anode_dict[row.ID], anode_dict[row.ID], bnode_dict[row.ID], \
                  row['BA Length'], row['BA Lanes'], row['BA Speed'], \
                  int(row.link_type), int(row.FT), int(row.AT), \
                  100 * row.AT + row.FT]
        if len(ba_addtional_list) > 0:
            for name in ba_addtional_list:
                record.append(float(row[name]))
    elif row.Dir == -1:
        record = [str(int(row.ID)) + str('BA'), '', str(int(row.ID)), -1, -1, \
                  bnode_dict[row.ID], anode_dict[row.ID], anode_dict[row.ID], bnode_dict[row.ID], \
                  row['BA Length'], row['BA Lanes'], row['BA Speed'], \
                  int(row.link_type), int(row.FT), int(row.AT), \
                  100 * row.AT + row.FT]
        if len(ba_addtional_list) > 0:
            for name in ba_addtional_list:
                record.append(float(row[name]))

    return record


# In[2] convert two way network to gmns one way network
def convert_node_to_gmns(two_way_node_filename='input_node.csv', node_id='ID', x_coord='Longitude', y_coord='Latitude',
                         zone_id='TAZ',
                         output_folder='./'):
    node_df = pd.read_csv(two_way_node_filename, encoding='UTF-8')
    time_start = time.time()
    print('---Start converting', len(node_df), 'nodes to GMNS format---')
    node_df.rename(columns={node_id: 'node_id',
                            x_coord: 'x_coord',
                            y_coord: 'y_coord',
                            zone_id: 'zone_id'}, inplace=True)

    # generate geometry of nodes
    node_df['geometry'] = node_df.apply(lambda x: "POINT (" + str(x.x_coord) + ' ' + str(x.y_coord) + ')', axis=1)
    node_df.to_csv(os.path.join(output_folder, 'node.csv'), index=False)
    time_end = time.time()
    print('node.csv DONE, CPU time:', time_end - time_start, 's \n')


def convert_link_to_gmns(two_way_link_filename='input_link.csv', \
                         one_way_node_filename='node.csv', \
                         link_id='ID', from_node_id='From ID', to_node_id='To ID', dir_flag='Dir', \
                         ab_length='AB Length', ba_length='BA Length', ab_lanes='AB Lanes', ba_lanes='BA Lanes',
                         ab_speed='AB Speed', \
                         ba_speed='BA Speed', FT='FT', AT='AT', link_type='Link_type', ab_list=[], ba_list=[], \
                         output_folder='./', keep_original_attributes=False, opposite_link_id=False):
    global ab_addtional_list
    global ba_addtional_list
    ab_addtional_list = ab_list
    ba_addtional_list = ba_list
    if len(ab_addtional_list) != len(ba_addtional_list):
        print('WARNING:the ab_list and ba_list are not consistent')
        exit()

    node_df = pd.read_csv(one_way_node_filename, encoding='UTF-8')
    node_x_coord_dict = dict(zip(node_df['node_id'], node_df['x_coord']))
    node_y_coord_dict = dict(zip(node_df['node_id'], node_df['y_coord']))

    link_df = pd.read_csv(two_way_link_filename, encoding='UTF-8')
    link_df.rename(columns={link_id: 'ID',
                            from_node_id: 'From ID',
                            to_node_id: 'To ID',
                            dir_flag: 'Dir',
                            ab_length: 'AB Length',
                            ba_length: 'BA Length',
                            ab_lanes: 'AB Lanes',
                            ba_lanes: 'BA Lanes',
                            ab_speed: 'AB Speed',
                            ba_speed: 'BA Speed',
                            link_type: 'link_type',
                            FT: 'FT',
                            AT: 'AT'}, inplace=True)

    print('---Start converting', len(link_df), 'two-way links to GMNS format directional links---')
    time_start = time.time()
    global anode_dict
    global bnode_dict
    anode_dict = dict(zip(link_df['ID'], link_df['From ID']))
    bnode_dict = dict(zip(link_df['ID'], link_df['To ID']))

    input_list = []
    for __, row in link_df.iterrows():
        input_list.append(row)

    # ab direction
    one_way_link_ab = list(map(_conversion_AB, input_list))
    while -1 in one_way_link_ab:
        one_way_link_ab.remove(-1)
    print('convert ', len(one_way_link_ab), 'ab direction links sucessfully...')
    g_one_way_link_list = one_way_link_ab

    # ba direction
    one_way_link_ba = list(map(_conversion_BA, input_list))
    while -1 in one_way_link_ba:
        one_way_link_ba.remove(-1)
    print('convert ', len(one_way_link_ba), 'ba direction links sucessfully...')

    g_one_way_link_list.extend(one_way_link_ba)
    one_way_link_df = pd.DataFrame(g_one_way_link_list)
    name_dict = {0: 'link_id',
                 1: 'opposite_link_id',
                 2: 'ID',
                 3: 'dir_flag',
                 4: 'Dir',
                 5: 'from_node_id',
                 6: 'to_node_id',
                 7: 'From ID',
                 8: 'To ID',
                 9: 'length',
                 10: 'lanes',
                 11: 'free_speed',
                 12: 'link_type',
                 13: 'FT',
                 14: 'AT',
                 15: 'VDF'}

    one_way_link_df.rename(columns=name_dict, inplace=True)

    one_way_link_df['geometry'] = one_way_link_df.apply(
        lambda x: _link_geometry(x.from_node_id, x.to_node_id, node_x_coord_dict, node_y_coord_dict), axis=1)
    if not keep_original_attributes:
        # one_way_link_df=one_way_link_df[['link_id','from_node_id','to_node_id','length','dir_flag','lanes',
        # 'free_speed','link_type','FT','AT', 'VDF','geometry','opposite_link_id']]
        one_way_link_df.drop(['ID', 'From ID', 'To ID', 'Dir'], inplace=True, axis=1)
    elif keep_original_attributes:
        print('note: you keep some orginal attributes from the original two-way link file...')
        # one_way_link_df=one_way_link_df[['link_id','from_node_id','to_node_id','length','dir_flag','lanes',
        # 'free_speed','link_type','FT','AT', 'VDF','geometry','opposite_link_id','ID','From ID','To ID','Dir']]

    if not opposite_link_id:
        one_way_link_df.drop(['opposite_link_id'], inplace=True, axis=1)

    one_way_link_df.to_csv(os.path.join(output_folder, 'link.csv'), index=False)

    time_end = time.time()
    print('link.csv DONE, CPU time', time_end - time_start, 's \n')
