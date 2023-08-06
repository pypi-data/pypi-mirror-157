#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 29 16:45:58 2022

@author: Asish Kumar Swain

"""
import numpy as np 
import pandas as pd 
from sklearn.preprocessing import StandardScaler
Std = StandardScaler()



class simulate_2:
    def __init__(self,sc_df,sc_label):
        self.sc_df,self.sc_label = np.array(sc_df),np.array(sc_label)
        self.unique_cell_types = np.unique(sc_label)
        
    def create_spot(self,cell_type,cell_number):
        celltype_indexes = np.where(self.sc_label==cell_type)[0]
        selected_indexes = np.random.choice(celltype_indexes,cell_number)
        
        slice_sc_df = self.sc_df[selected_indexes,:]
        
        slice_sc_df_sum = np.array(slice_sc_df.sum(axis=0))
        
        return slice_sc_df_sum
    
    def simulate_st_data(self,cell_count_per_spot):
        n_cell,n_gene = self.sc_df.shape
        """Step1 intiate the matrix where
             i. 2x st spot having >80% one cell type
             ii.1x st spot having >40% two cell type
             iii.1x st spot having random mixture of all cells
         """ 
        simu_rows = int(2*n_cell+2*n_cell+int(2*n_cell)) 
        master_st_array = np.zeros([simu_rows,n_gene])  
        master_st_label = np.zeros([simu_rows,len(self.unique_cell_types)])
        count=0
    
    
    
        #Sub-step1 : 2x st spot having >80% one cell type 
        #Number of spots going to generate : 2X 
        new_spot_number = 2*n_cell
        
        for i in range(new_spot_number):
            label_dic ={}
            celltype1_prop = int(np.random.randint(80,100)*0.01*cell_count_per_spot)
            celltype2_prop = cell_count_per_spot-celltype1_prop
        
            #st_data_generation
            cell_tp1 = np.random.choice(self.unique_cell_types)
            cell_tp2 = np.random.choice(np.delete(self.unique_cell_types,cell_tp1))
            x1 = self.create_spot(cell_tp1,celltype1_prop)
            x2 = self.create_spot(cell_tp2,celltype2_prop)
            x = np.vstack((x1,x2))
            x = x.sum(axis =0)
            master_st_array[count,:] = x
            
            #label_data_generation
            label_dic[cell_tp1]=celltype1_prop
            label_dic[cell_tp2]=celltype2_prop
            for col in label_dic.keys():
                master_st_label[count,col]=label_dic[col] 
            
            
            count= count+1
            
        
        # #Sub-step2 - (40+40+20)
        new_spot_number = 2*n_cell

        for i in range(new_spot_number):
            label_dic = {}
            celltype1_prop = int(np.random.randint(40,52)*0.01*cell_count_per_spot)
            celltype2_prop = int(np.random.randint(30,50)*0.01*cell_count_per_spot)
            rest_prop = cell_count_per_spot - (celltype1_prop+celltype2_prop)
            
            #ST data generation
            cell_tp1 = np.random.choice(self.unique_cell_types)
            cell_tp2 = np.random.choice(np.delete(self.unique_cell_types,cell_tp1))
            x1 = self.create_spot(cell_tp1,celltype1_prop)
            x2 = self.create_spot(cell_tp2,celltype2_prop)
            x = np.vstack((x1,x2))
            label_dic[cell_tp1]=celltype1_prop
            label_dic[cell_tp2]=celltype2_prop
            for j in range(rest_prop):
                cell_tp_temp = np.random.choice(self.unique_cell_types)
                x3 = self.create_spot(cell_tp_temp,1)
                x = np.vstack((x,x3))
                if cell_tp_temp in label_dic.keys():
                    label_dic[cell_tp_temp] = label_dic[cell_tp_temp]+1
                else:
                    label_dic[cell_tp_temp] = 1
            x = x.sum(axis=0)
            
            #label and master dt gen
            master_st_array[count,:] = x
            for col in label_dic.keys():
                master_st_label[count,col]=label_dic[col]
            count=count+1
            
            
        #Sub-step-3 (all-random)
        new_spot_number = int(2*n_cell)

        for i in range(new_spot_number):
            index_selected = np.random.randint(0,n_cell,cell_count_per_spot)
            selected_labels = self.sc_label[index_selected]
            x = self.sc_df[index_selected,:]
            x = x.sum(axis=0)
            label = {}
            for i in self.unique_cell_types:
                label[i]= sum(selected_labels==i)
                
            #label and master dt gen
            master_st_array[count,:] = x
            for col in label.keys():
                master_st_label[count,col]=label[col]
            count=count+1

        master_st_label = master_st_label/cell_count_per_spot
          
    
        return master_st_array,master_st_label
def normalisation(df):
    df_with_noise_std = Std.fit_transform(df)
    
    
    return df_with_noise_std


        

