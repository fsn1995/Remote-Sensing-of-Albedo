%% This is to improve the spatial resolution of Landsat data by CNMF

%% Landsat
l8folder = "/data/shunan/data/albedo/LC08_L2SP_007013_20200822_20200905_02_T1";
l8wavelength = [440 480 560 655 865 1610 2200];
subdir = dir(fullfile(l8folder, '*SR_B*.TIF'));

% for i = 1:length(subdir)
%     bands = fullfile(subdir(i).folder , subdir(i).name);
% %     band = double(readgeoraster(bands))*0.0000275 - 0.2;
% %     band(band<0) = 0;
%     band = readgeoraster(bands);
%     img(:,:,i) = band;
% end
% hcube = hypercube(img, l8wavelength);

impath = dir(fullfile(l8folder, '*B8.TIF'));
[l8pan, R] = readgeoraster(fullfile(impath.folder, impath.name));
figure;
imshow(l8pan);
latlim = [66.5 67.5];
lonlim = [-50.1 -49];
[xlim, ylim, zone] = ll2utm(latlim, lonlim);
xlim(2) = xlim(2) + 30000*2;
% mapshow(l8pan, R);
[l8pancrop, Rb] = mapcrop(l8pan, R, xlim, ylim);
figure;
imshow(l8pancrop);

% newhcube = sharpencnmf(hcube,l8pan);
% 
% lrData = colorize(hcube,'method','rgb','ContrastStretching',false);
% % hrData = colorize(eo1ali,'method','rgb','ContrastStretching',true);
% outputData = colorize(newhcube,'method','rgb','ContrastStretching',false);
% 
% figure
% montage({lrData;l8pan;outputData})
% title('Low Resolution MS Input | High Resolution Pan Input | High Resolution MS Output')
% 
% 
% enviwrite(newhcube, fullfile(l8folder, "newcube.dat"));
% geotiffwrite(fullfile(l8folder, "LC08_L2SP_007012_20200822_20200905_02_T1.tif"), ...
%     newhcube.DataCube, R,'CoordRefSysCode', 32622, 'TiffType','bigtiff');


% newhcube = sharpencnmf(l8cube,l8pan);
% enviwrite(newcube, fullfile(l8folder, "newcube.dat"));

% % l8bands = strings(8,1);
% for i = 1:length(subdir)
%     l8bands = [subdir(i).folder ,'\', subdir(i).name];
%     l8img(:,:,i) = readgeoraster(l8bands);
% % end
% l8cube = hypercube(readgeoraster("E:\AU\algae\img\unzip\LC08_L2SP_006013_20170722_20200903_02_T1\LC08_L1TP_006013_20170722_20200903_02_T1subset.tif"), ...
%     l8wavelength);
% enviwrite(l8cube,'l8cube.dat');
% [l8pan, l8panR] = readgeoraster("E:\AU\algae\img\unzip\LC08_L2SP_006013_20170722_20200903_02_T1\LC08_L1TP_006013_20170722_20200903_02_T1_B8subset.tif");
% newhcube = sharpencnmf(l8cube,l8pan);
% enviwrite(hypercube(l8pan, 800), 'l8pan.dat');
% lrData = colorize(l8cube,'method','rgb','ContrastStretching',false);
% % hrData = colorize(eo1ali,'method','rgb','ContrastStretching',true);
% outputData = colorize(newhcube,'method','rgb','ContrastStretching',false);
% 
% figure
% montage({lrData;l8pan;outputData})
% title('Low Resolution HS Input | High Resolution MS Input | High Resolution HS Output')
% 
% enviwrite(newhcube, "newhcube.dat");




