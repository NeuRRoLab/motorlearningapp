clc
clear all;
close all;
addpath('C:\Users\mouli\Desktop\Things to Add in Dropbox\Matlab course\Course Materials\Other Programs\myfunctions');
addpath('C:\Users\mouli\Desktop\Herokuapp');
ID = {'90QQFrVZfIAl6oLR'};
data = readtable('processed_experiment_5P6U (5).csv');
data.subjectid = categorical(data.subject_code);
data.correcttrial = categorical(data.correct_trial);
data2 = data(data.subjectid == ID,:);
%% remove outliers
T = rmoutliers(data2(:,9));
ix = ismember(data2(:,9),T(:,1));
data2 = data2(ix,:);
%% 
% figure; stackedplot(data2);;
% figure; stackedplot(data2(:,9),'.','markersize',20);
% data2 = data2(data2.correcttrial == {'True'},:);
data2left = data2(data2.block_id < 37,:);
data2left = data2left(data2left.correcttrial == {'True'},:);
data2right = data2(data2.block_id > 36,:);
data2right = data2right(data2right.correcttrial == {'True'},:);

figure; 
subplot(2,2,1); h1 = stackedplot(data2left(:,9),'.','markersize',20);
ax1 = findobj(h1.NodeChildren, 'Type','Axes');
set([ax1.YLabel],'Rotation',90,'HorizontalAlignment', 'Center', 'VerticalAlignment', 'Bottom');
title(ID);
subplot(2,2,2); h2 = stackedplot(data2right(:,9),'.','markersize',20);
ax2 = findobj(h2.NodeChildren, 'Type','Axes');
set([ax2.YLabel],'Rotation',90,'HorizontalAlignment', 'Center', 'VerticalAlignment', 'Bottom');
title(ID);
%% Computing mean of correct trials within each block

for i = 1:36
    blockvalueleft = data2left(data2left.block_id == i,:);
    blockmeanleft(i,:) = mean(blockvalueleft{:,9},1);
    blockvalueright = data2right(data2right.block_id == i+36,:);
    blockmeanright(i,:) = mean(blockvalueright{:,9},1);
end

subplot(2,2,3); plot(blockmeanleft,'b.','markersize',20);
axis([0,37,0,max(blockmeanleft)*1.2]);
title('Left');
subplot(2,2,4); plot(blockmeanright,'r.','markersize',20);
axis([0,37,0,max(blockmeanright)*1.2]);
title('Right');