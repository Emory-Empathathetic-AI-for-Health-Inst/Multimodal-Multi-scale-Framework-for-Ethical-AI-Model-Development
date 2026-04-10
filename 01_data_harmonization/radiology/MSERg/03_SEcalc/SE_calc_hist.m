clear all
%%setup autoMSERg input
currentFolder = pwd;
parentFolder = fileparts(currentFolder);
addpath([currentFolder,'/feature_extraction']);
HISTURL = [parentFolder,'/example/processed/affine_hist.png'];  
HISTmask = [parentFolder,'/example/processed/affine_hist_mask.png'];   
RegOutputFolder = [parentFolder,'\example/processed/hist_rep'];
mkdir(RegOutputFolder);
scaleIndex =[1,2,3,4,5,6,7,8];% set the scale size that needed in the multiscale resolution
REP_calc_clinic(HISTURL, HISTmask,RegOutputFolder,scaleIndex)