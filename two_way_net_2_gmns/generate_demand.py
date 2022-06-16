
import pandas as pd
import numpy as np
import os 

def splitMultiColumnToSingleColumn(file_mapping_dict,output_folder='./'):	
    file_df=pd.DataFrame(file_mapping_dict)
    file_name_list=[]
    demand_period_list=[]
    agent_type_list=[]
    format_type_list=[]
    for f in range(len(file_df)):
        demand_filename=file_df.iloc[f].file_name
        period_name=file_df.iloc[f].period
        df=pd.read_csv(demand_filename,encoding='UTF-8')
        nb_column=df.shape[1]
        for i in range(2,nb_column):
            temp_df=df.iloc[:,[0,1,i]]
            agent_type_name=temp_df.iloc[:,2].name
            temp_df = temp_df.rename(columns = {temp_df.iloc[:,0].name: 'o_zone_id', temp_df.iloc[:,1].name: 'd_zone_id', temp_df.iloc[:,2].name: 'volume'}, inplace = False)
            temp_df.to_csv(os.path.join(output_folder,'demand_'+period_name+'_'+agent_type_name+'.csv'), index=False)
            print('generate demand_'+period_name+'_'+agent_type_name+'.csv...')
            file_name_list.append('demand_'+period_name+'_'+agent_type_name+'.csv')
            demand_period_list.append(period_name)
            format_type_list.append('column')
            agent_type_list.append(agent_type_name)
    
    setting_dict={'file_name':file_name_list,'format_type':format_type_list,'demand_period':demand_period_list,'agent_type':agent_type_list}
    setting_df=pd.DataFrame(setting_dict)
    setting_df.to_csv(os.path.join(output_folder,'file_settings.csv'), index=False)
    print('DONE')


def matrix2column(matrix_file_name='DA_GP.csv'):
    df=pd.read_csv(matrix_file_name,encoding='UTF-8') 
    df=df.drop(['Unnamed: 0'],axis=1)
    df_column=df.stack().reset_index().rename(columns={'level_0':'o_zone_id','level_1':'d_zone_id', 0:'volume'})
    df_column['o_zone_id']=df_column['o_zone_id']+1
    df_column.to_csv(matrix_file_name[:-4]+'_demand.csv', index=False)
    print('DONE')


def concatenateDemandFile(demand_folder,name,period,flag_truck=False):
	files =[file for file in os.listdir(demand_folder)]
	data_df=pd.DataFrame() # build up an empty dataframe using pandas
	df_list=[]
	for file in files :
		if period not in file: continue 
		if not flag_truck and ('ut' in file): continue
		df = pd.read_csv(demand_folder + file)
		df_list.append(df)
	
	data_df = pd.concat(df_list,sort=False) # Do not sort the field name of columns	
	data_df.to_csv(demand_folder+'demand_'+str(name)+'.csv', index=False)

	