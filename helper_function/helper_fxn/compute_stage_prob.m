function [stage_prop,timestamps] = compute_stage_prob(stagetrain,sop,sop_bin_divide)
%COMPUTE_STAGE_PROp Computes stage proportion
%
%   Usage:
%       stage_prop = compute_stage_prob(stage, sop, bin_divide)
%
%   Input:
%   stage: 1xN double - interpolated hypnogram at the resolution of the feature -- required
%   sop: 1xB double - feature bin centers -- required
%   bin_divide: 1xB cell array - indices for times corresponding to each bin
%
%   Output:
%   stage_prob: Bx5 double - time in stage probabilites for each stage  % N3,N2,N1,REM,Wake
%
%   Copyright 2020 Michael J. Prerau, Ph.D. - http://www.sleepEEG.org
%   This work is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
%   (http://creativecommons.org/licenses/by-nc-sa/4.0/)
%
%   Created, 10/27/2020 - MJP
%   Last modified, 02/28/2023, SC
%% ********************************************************************

%Compute the stage probability and components
%sop_bin_divide = (min(sop):0.5:max(sop))';
bin_size = sop_bin_divide(2) - sop_bin_divide(1);
num_bins = length(sop_bin_divide);
stage_prop = zeros(num_bins, 5);

%Loop through each bin and get the associated stages
for ii = 1:num_bins-1
    %inds = bin_indices(ii);
    inds = sop>sop_bin_divide(ii)&sop<sop_bin_divide(ii+1);
    hist_vals = histcounts(stagetrain(inds),.5:1:5.5)'; %Create histogram bin edges that include 1:5
    stage_prop(ii,:) = hist_vals/sum(hist_vals); % N3,N2,N1,REM,Wake
end

% The center of bin can be the timestamps to plot with SOP
timestamps = sop_bin_divide + 0.5*bin_size;
%timestamps = timestamps(1:end-1);
