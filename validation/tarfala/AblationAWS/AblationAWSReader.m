%% AWS at upper ablation
clearvars
rawdata = readtable('AblationAWS.csv');
time = rawdata.TIMESTAMP;
RH = rawdata.RH_avg;
temp = rawdata.aT_fit;
clear rawdata
save('AblationAWS.mat');
%% AWS operates only in summer from 2013
clearvars
delete SgAWS_hourly_summer.csv
filepath = 'summer\';
subdir = dir(filepath);
for i = 3:length(subdir)
    rawdata = readtable([filepath,subdir(i).name]);
    time = rawdata.TIMESTAMP;
    data = table2array(rawdata(:,2:end));
    [yr,mo,da] = ymd(time);
    [hr,mi,se] = hms(time);
    dlmwrite('SgAWS_hourly_summer.csv',[yr,mo,da,hr,mi,se,data],'-append');
end
%     writetable(rawdata,'SgAWS_hourly_summer.csv')
clearvars
rawdata = readtable('SgAWS_hourly_summer.csv');
timeSummer = table2array(rawdata(:,1:6));
timeSummer = datetime(timeSummer);
RHSummer = table2array(rawdata(:,10:12));
tempSummer = table2array(rawdata(:,7:9));
RHSummer = nanmean(RHSummer,2);
tempSummer = nanmean(tempSummer,2);
precSummer = table2array(rawdata(:,end));
save('AblationAWSsummer.mat');
%% AWS data comparison
load('AblationAWS.mat');
subplot(2,1,1);
title('temperature');
plot(time,temp,'DisplayName','AWS');
hold on 
plot(timeSummer,tempSummer,'DisplayName','AWSsummer');
legend
subplot(2,1,2);
title('RH');
plot(time,RH,'DisplayName','AWS');
hold on 
plot(timeSummer,RHSummer,'DisplayName','AWSsummer');
legend

