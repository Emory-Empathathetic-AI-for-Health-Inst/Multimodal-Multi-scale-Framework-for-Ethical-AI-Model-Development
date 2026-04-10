clear all
currentFolder = pwd;
parentFolder = fileparts(currentFolder);
addpath([currentFolder,'/feature_extraction']);
HISTURL = [parentFolder,'/example/mri.png'];  
HISTmask = [parentFolder,'/example/mri_mask.png'];   
RegOutputFolder = [parentFolder,'\example/processed/mri_rep'];
mkdir(RegOutputFolder);
scaleIndex =[1,2,3,4,5,6,7,8];
REP_calc_clinic(HISTURL, HISTmask,RegOutputFolder,scaleIndex)
