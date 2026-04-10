function MSERgFun_clinic(scaleSelectedParameter,inputdir,outputdir)
%scaleIndex needs to be a vector for multi-scale registration. for example
%[2,3,8]
%moving and anotation refer to image direction, e.g. c:/folder/hist.png
%outputdir: the output direction; inputdir: the direction where save the
%input moving represetations
%this function require to finish previous steps in the registration pipline

com1 = 'elastix ';
ind = 0;
for i = 1:length(scaleSelectedParameter)
    scaleID =  scaleSelectedParameter(i);
    inputTemp = sprintf('/Scale_rep/scale%d/',scaleID);
    inputFile = [inputdir,inputTemp];
    for seID = 1:3
        tempName_f = sprintf('mriSE_%d.png',seID);
        inputName_f = [inputFile,tempName_f];
        tempName_m = sprintf('histSE_%d.png',seID);
        inputName_m = [inputFile,tempName_m];
        tempNameF = sprintf('-f%d ',ind);
        tempNameM = sprintf('-m%d  ',ind);
        comF(ind+1) = {[tempNameF,inputName_f,' ']};
        comM(ind+1) = {[tempNameM,inputName_m,' ']};
        
        ind = ind+1;
        
    end
end
    
com4 = ['-out ',outputdir,' '];
filename = outputdir;% change to your output dictionary
mkdir(filename);
com5 = sprintf('-p MSERg%d_clinical.txt ',ind);
command = [com1,cell2mat(comF),cell2mat(comM),com4,com5];

system(command)
copyfile([inputdir,'/affine_hist.png'],outputdir);
copyfile([inputdir,'/affine_hist_landmark.png'],outputdir);
cd(outputdir);
% transformation
        com6 = 'transformix ';
        com7 = '-in affine_hist.png ';
        com7_2 = '-def all ';
        com7_3 = ['-in affine_hist_landmark.png '];
        com8 = '-tp TransformParameters.0.txt ';
        com9 = ['-out ',outputdir,'/image'];
        com9_2 = ['-out ',outputdir,'/marker'];
        mkdir([outputdir,'/image'])
        mkdir([outputdir,'/marker'])
        command_t = [com6,com7,com8,com9];
        system(command_t);
        command_def = [com6,com7_2,com8,com9];
        system(command_def)
        command_marker = [com6,com7_3,com8,com9_2];
        system(command_marker)
     
end
