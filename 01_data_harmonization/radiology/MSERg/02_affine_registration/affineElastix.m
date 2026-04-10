function affineElastix(fixed,moving,anotation,mask,outputdir)
com1 = 'elastix ';
mri = double(imread(fixed));
comF = ['-f0 ',fixed,' '];
comM = ['-m0 ',moving,' '];
com4 = ['-out ',outputdir,' '];
com5 =('-p affine1.txt ');
command = [com1,comF,comM,com4,com5];
system(command)
cd(outputdir);
% transformation
com6 = 'transformix ';
com7 = ['-in ',moving,' '];
com7_2 = '-def all ';
com7_3 = ['-in ',anotation,' '];
com7_4 = ['-in ',mask,' '];
com8 = '-tp TransformParameters.0.txt ';
com9 = ['-out ',outputdir,'/affine/image'];
com9_2 = ['-out ',outputdir,'/affine/marker'];
com9_3 = ['-out ',outputdir,'/affine/mask'];
mkdir([outputdir,'/affine/image'])
mkdir([outputdir,'/affine/marker'])
mkdir([outputdir,'/affine/mask'])
command_t = [com6,com7,com8,com9];
system(command_t);
command_def = [com6,com7_2,com8,com9];
system(command_def)
command_marker = [com6,com7_3,com8,com9_2];
system(command_marker)
command_mask = [com6,com7_4,com8,com9_3];
system(command_mask)

m = imread([outputdir,'/affine/image/result.tif']);
f = mri;

end