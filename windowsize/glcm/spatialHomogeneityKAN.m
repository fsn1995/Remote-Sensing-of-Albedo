%% Image Homogeneity at KAN_M


%% new color map
blue_fluorite = {'291b32', '2a1b34', '2b1b34', '2d1c36', '2f1c38', '301c39', '301d3a', '321d3b', '331d3d', '351d3f', '351e40', '371e41', '381e43', '3a1e45', '3b1f45', '3c1f46', '3e1f48', '3f1f4a', '401f4c', '42204d', '43204e', '44204f', '462051', '472052', '482054', '4a2056', '4a2157', '4c2158', '4e215a', '4f215b', '50215d', '52215e', '532160', '552162', '552263', '562264', '582265', '592267', '5b2268', '5c226b', '5e226c', '5f226e', '60226f', '622271', '632272', '642274', '662276', '672277', '692278', '6a227a', '6c227b', '6e227d', '6e237e', '6f247f', '702480', '712581', '722681', '732683', '742783', '752884', '762985', '772987', '792a87', '792b88', '7a2c89', '7b2c8a', '7c2d8a', '7d2d8c', '7e2e8d', '7f2f8d', '80308e', '813190', '823191', '833292', '843292', '863393', '863494', '873595', '893596', '8a3697', '8b3798', '8b3899', '8c389a', '8e399b', '8e3a9c', '8f3b9c', '8f3d9d', '8f3e9e', '903f9e', '90419e', '90439f', '9044a0', '9046a0', '9047a1', '9049a1', '914aa2', '914ca2', '914ca3', '914ea3', '9150a4', '9151a5', '9153a5', '9154a6', '9156a6', '9157a7', '9258a7', '9259a8', '925aa8', '925ba9', '925da9', '925faa', '9260ab', '9260ab', '9263ac', '9264ac', '9265ad', '9266ae', '9268ae', '9269ae', '926aaf', '926bb0', '926cb0', '926eb1', '926fb1', '9270b2', '9271b2', '9273b3', '9274b3', '9275b4', '9277b5', '9277b5', '9278b6', '927ab6', '927bb7', '927cb7', '927eb8', '927fb8', '9280b9', '9281ba', '9282ba', '9284bb', '9285bb', '9285bc', '9187bc', '9188bd', '918abd', '918bbe', '918cbf', '918dbf', '918ec0', '918fc0', '9191c1', '9092c2', '9094c2', '9094c2', '9095c3', '9096c3', '8f99c4', '8f9ac5', '8f9ac5', '8f9bc6', '8f9cc6', '8f9dc7', '8e9fc8', '8ea0c8', '8ea2c9', '8ea3c9', '8da5ca', '8da5ca', '8da6cb', '8da7cb', '8ca9cc', '8caacc', '8caccd', '8bacce', '8badce', '8baecf', '8ab0d0', '8ab2d0', '8ab2d1', '8ab4d1', '89b4d1', '89b5d2', '89b7d2', '88b8d3', '88bad4', '87bad4', '87bbd5', '86bdd6', '86bed6', '86c0d7', '85c0d7', '85c1d8', '84c3d8', '84c4d9', '83c5d9', '83c6da', '82c8da', '82c8db', '81cadc', '81cbdc', '80ccdd', '81cddd', '84cfdd', '85cfdd', '87d0dd', '8ad0de', '8dd1de', '8fd2de', '90d2de', '92d4de', '95d5de', '97d5de', '98d6de', '9bd7de', '9dd7df', 'a0d8df', 'a1d9df', 'a2dadf', 'a5dadf', 'a7dbdf', 'aadcdf', 'abdddf', 'acdde0', 'afdfe0', 'b1dfe0', 'b3e0e0', 'b4e1e0', 'b7e2e0', 'bae2e1', 'bae3e1', 'bee3e2', 'c0e4e3', 'c1e5e3', 'c4e6e3', 'c6e6e4', 'c8e7e4', 'cbe7e5', 'cde8e5', 'cee9e6', 'd2e9e7', 'd3eae7', 'd5eae7', 'd8ebe8', 'd9ece8', 'dcece9', 'deedea', 'dfeeea', 'e2eeea', 'e5efeb', 'e6f0eb', 'e9f0ec', 'ebf1ed', 'ecf2ed', 'eff3ee', 'f1f3ee'};
dpcolor = zeros(length(blue_fluorite), 3); % Preallocate
for k = 1 : length(blue_fluorite)
	thisCell = blue_fluorite{k};
	r = hex2dec(thisCell(1:2));
	g = hex2dec(thisCell(3:4));
	b = hex2dec(thisCell(5:6));
	dpcolor(k, :) = [r, g, b];
end
dpcolor = dpcolor / 255;

%% display map
f = figure;
f.Position = [10 10 800 300];

t = tiledlayout(1,2);

ax1 = nexttile;
mapx = [592725, 592725, 599435-30];
mapy = [7442800, 7437980+30, 7437980+30];
[utmx, utmy] = ll2utm(67.067 , -48.8355);


[l8, xa, ya, Il8] = geoimread("l8albedoKANM.tif", mapx, mapy);
[Xa, Ya] = meshgrid(xa, ya);
% figure
mapshow(ax1, Xa, Ya, l8, DisplayType="surface");
colormap(ax1,dpcolor)
% c = colorbar(ax1, 'southoutside');
% c.Label.String = 'albedo';
caxis(ax1, [0, 1])
mapshow(ax1, utmx, utmy, DisplayType='point', Marker='^', DisplayName='KAN\_M');
text(ax1, utmx+10, utmy, '\leftarrow KAN\_M');
text(ax1, min(mapx)+100, max(mapy)-300, 'a) L8', 'FontSize',12);
xlim(ax1, [min(mapx), max(mapx)])
ylim(ax1, [min(mapy), max(mapy)])
set(gca,'TickDir','out');

ax2 = nexttile;
[s2, xb, yb, Is2] = geoimread("s2albedoKANM.tif", mapx, mapy);
[Xb, Yb] = meshgrid(xb, yb);
% figure
mapshow(ax2, s2, Is2.SpatialRef, DisplayType="surface");
colormap(ax2, dpcolor)
c = colorbar(ax2);
c.Label.String = 'albedo';
c.Label.FontSize = 12;
caxis(ax2, [0, 1])
mapshow(ax2, utmx, utmy, DisplayType='point', Marker='^', DisplayName='KAN\_M')
text(ax2, utmx+10, utmy, '\leftarrow KAN\_M');
text(ax2, min(mapx)+100, max(mapy)-300, 'b) S2', 'FontSize',12);
xlim(ax2, [min(mapx), max(mapx)])
ylim(ax2, [min(mapy), max(mapy)])
set(gca,'TickDir','out');


ax1.XAxis.Exponent = 0;
ax1.YAxis.Exponent = 0;
ax1.YAxis.TickLabelFormat = '%.0f';
% ax1.FontSize = 16;
ax2.XAxis.Exponent = 0;
ax2.YAxis.Exponent = 0;
ax2.YAxis.TickLabelFormat = '%.0f';
% ax2.FontSize = 16;

t.TileSpacing = 'compact';
t.Padding = 'compact';

exportgraphics(t, 'KANalbedo.jpg', 'Resolution',300);
% exportgraphics(t, 'KANalbedo.pdf', 'Resolution',300);

%% Derive statistics from GLCM and Plot
% l8offset = 3;
% s2offset = 9;
offsetsh = [zeros(27,1) (1:27)'];
offsetsv = [(1:27)' zeros(27,1)];

s2resample = imresize(s2, 1/3, "bilinear"); % default is bicubic but it will produce pixel values outside the original range.
% figure, imshow(l8), figure, imshow(s2resample);

%% GLCM Plot Homogeneity
% horizontal offset
glcml8 = graycomatrix(l8, 'Offset',offsetsh);
glcms2 = graycomatrix(s2, 'Offset',offsetsh);
glcms2resample = graycomatrix(s2resample, 'Offset', offsetsh);

statsl8 = graycoprops(glcml8, "all");
statss2 = graycoprops(glcms2, "all");
statss2resample = graycoprops(glcms2resample, "all");

statsl8.Homogeneity(10:end) = nan;
statss2resample.Homogeneity(10:end) = nan;


% GLCM Plot Homogeneity
f = figure;
f.Position = [50 50 800 400]; 

% index = 3:3:27;
t = tiledlayout(2,2);
nexttile
plot(statsl8.Homogeneity, LineWidth=2, Marker="*", DisplayName="L8");
hold on
plot(statss2resample.Homogeneity, LineWidth=2, Marker="*", DisplayName="S2 resampled");
% title('Homogeneity of L8','FontSize', 12);
xlabel('Horizontal Offset (number of pixels)','FontSize', 12)
ylabel('Homogeneity','FontSize', 12)
text(0.90,0.90,'a)','Units','normalized','FontSize',12)
xlim([1 9])
ylim([0.84 0.96])
legend('Location','southwest')
grid on

nexttile
plot(statss2.Homogeneity, LineWidth=2, Marker="*", Color='#4DBEEE', DisplayName="S2");
% title('Homogeneity of S2','FontSize', 12);
xlabel('Horizontal Offset (number of pixels)','FontSize', 12)
% ylabel('Homogeneity')
text(0.90,0.90,'c)','Units','normalized','FontSize',12)
xlim([1 27])
ylim([0.84 0.96])
legend('Location','southwest')
grid on

% vertical offset
glcml8 = graycomatrix(l8, 'Offset',offsetsv);
glcms2 = graycomatrix(s2, 'Offset',offsetsv);
glcms2resample = graycomatrix(s2resample, 'Offset', offsetsv);

statsl8 = graycoprops(glcml8, "all");
statss2 = graycoprops(glcms2, "all");
statss2resample = graycoprops(glcms2resample, "all");


statsl8.Homogeneity(10:end) = nan;
statss2resample.Homogeneity(10:end) = nan;



nexttile
plot(statsl8.Homogeneity, LineWidth=2, Marker="*", DisplayName='L8');
hold on
plot(statss2resample.Homogeneity, LineWidth=2, Marker="*", DisplayName="S2 resampled");
% title('Homogeneity as a function of offset l8');
xlabel('Vertical Offset (number of pixels)','FontSize', 12)
ylabel('Homogeneity','FontSize', 12)
text(0.90,0.90,'b)','Units','normalized','FontSize',12)
xlim([1 9])
ylim([0.84 0.96])
legend('Location','southwest')
grid on

nexttile
plot([statss2.Homogeneity], LineWidth=2, Marker="*", Color='#4DBEEE', DisplayName="S2");
% title('Homogeneity as a function of offset s2');
xlabel('Vertical Offset (number of pixels)','FontSize', 12)
% ylabel('Homogeneity')
text(0.90,0.90,'d)','Units','normalized','FontSize',12)
xlim([1 27])
ylim([0.84 0.96])
legend('Location','southwest')
grid on

t.TileSpacing = 'compact';
t.Padding = 'compact';

exportgraphics(t, 'KANglcms.jpg', 'Resolution',300);
% exportgraphics(t, 'KANglcms.pdf', 'Resolution',300);

%% statistics of the homogeneity 
statsl8.Homogeneity(10:end) = nan;
statss2resample.Homogeneity(10:end) = nan;
figure;
boxplot([statsl8.Homogeneity' statss2resample.Homogeneity' statss2.Homogeneity'], ["L8" "S2 resampled" "S2"])
[h,p,ci,stats] = ttest2(statsl8.Homogeneity, statss2resample.Homogeneity)
boxplot([l8(:) s2resample(:)], ["L8" "S2 resampled"])
[h,p,ci,stats] = ttest2(l8(:), s2resample(:))
