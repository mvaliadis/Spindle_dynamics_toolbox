function [SOpower_norm, SOpower_times, SOpower_stages, norm_method, ptile] = compute_SOP(EEG, Fs, varargin)
% COMPUTE_SOP computes slow-oscillation power
% 
% Usage:
%   [SO_mat, freq_cbins, SO_cbins, time_in_bin, prop_in_bin, peak_SOpower_norm, peak_selection_inds] = ...
%                                 SOpowerHistogram(EEG, Fs, TFpeak_times, TFpeak_freqs, <options>)
%
%  Inputs:
%   REQUIRED:
%       EEG: 1xN double - timeseries EEG data --required
%       Fs: numerical - sampling frequency of EEG (Hz) --required
%                   OR
%       SOpower: 1xM double - timeseries SO power data --required
%       SOpower_times: 1xM double - timeseries SO power times --required
%
%       TFpeak_freqs: Px1 - frequency each TF peak occurs (Hz) --required
%       TFpeak_times: Px1 - times each TF peak occurs (s) --required
%
%   OPTIONAL:
%       TFpeak_stages: Px1 - sleep stage each TF peak occurs 5=W,4=R,3=N1,2=N2,1=N3
%       stage_vals:  1xS double - numeric stage values 5=W,4=R,3=N1,2=N2,1=N3
%       stage_times: 1xS double - stage times
%       freq_range: 1x2 double - min and max frequencies of TF peak to include in the histogram
%                   (Hz). Default = [0,40]
%       freq_binsizestep: 1x2 double - [size, step] frequency bin size and bin step for frequency
%                         axis of SO power histograms (Hz). Default = [1, 0.2]
%       SO_range: 1x2 double - min and max SO power values to consider in SO power analysis.
%                 Default calculated using min and max of SO power
%       SO_binsizestep: 1x2 double - [size, step] SO power bin size and step for SO power axis
%                            of histogram. Units are radians. Default
%                            size is (SO_range(2)-SOrange(1))/5, default step is
%                            (SO_range(2)-SOrange(1))/100
%       SO_freqrange: 1x2 double - min and max frequencies (Hz) considered to be "slow oscillation".
%                     Default = [0.3, 1.5]
%       SOPH_stages: stages in which to restrict the SOPH. Default: 1:3 (NREM only)
%                    W = 5, REM = 4, N1 = 3, N2 = 2, N3 = 1, Artifact = 6, Undefined = 0
%       norm_dim: double - histogram dimension to normalize, not related to norm_method (default: 0 = no normalization)
%       compute_rate: logical - histogram output in terms of TFpeaks/min instead of count. 
%                               Default = true.
%       min_time_in_bin: numerical - time (minutes) required in each SO power bin to include
%                                  in SOpower analysis. Otherwise all values in that SO power bin will
%                                  be NaN. Default = 1.
%       SOpower_outlier_threshold: double - cutoff threshold in standard deviation for excluding outlier SOpower values. 
%                                  Default = 3. 
%       norm_method: char - normalization method for SOpower. Options:'pNshiftS', 'percent', 'proportion', 'none'. Default: 'p2shift1234'
%                         For shift, it follows the format pNshiftS where N is the percentile and S is the list of stages (5=W,4=R,3=N1,2=N2,1=N3).
%                         (e.g. p2shift1234 = use the 2nd percentile of stages N3, N2, N1, and REM,
%                               p5shift123 = use the 5th percentile of stages N3, N2 and N1)
%       retain_Fs: logical - whether to upsample calculated SOpower to the sampling rate of EEG. Default = true
%       EEG_times: 1xN double - times for each EEG sample. Default = (0:length(EEG)-1)/Fs
%       time_range: 1x2 double - min and max times for which to include TFpeaks. Also used to normalize
%                   SOpower. Default = [EEG_times(1), EEG_times(end)]
%       isexcluded: 1xN logical - marks each timestep of EEG as artifact or non-artifact. Default = all false.
%
%       plot_on: logical - SO power histogram plots. Default = false
%       verbose: logical - Verbose output. Default = true
%
%  Outputs:
%       SO_mat: SO power histogram (SOpower x frequency)
%       freq_cbins: 1xF double - centers of the frequency bins
%       SO_cbins: 1xPO double - centers of the power SO bins
%       time_in_bin: 1xTx5 double - minutes spent in each power bin for each stage
%       prop_in_bin: 1xT double - proportion of total time (all stages) in each bin spent in
%                          the selected stages
%       peak_SOpower: 1xP double - normalized slow oscillation power at each TFpeak
%       peak_selection_inds: 1xP logical - which TFpeaks are counted in the histogram
%       SOpower: 1xM double - timeseries SO power data
%       SOpower_times: 1xM double - timeseries SO power times
%
% Copyright 2024 Michael J. Prerau Laboratory. - http://www.sleepEEG.org
% Code adapted from Prerau Lab, SChen
% **************************************************************

%% Parse input
%Input Error handling
p = inputParser;

%Stage info
addOptional(p, 'stage_vals', [], @(x) validateattributes(x, {'double', 'single'}, {'real'}));
addOptional(p, 'stage_times', [], @(x) validateattributes(x, {'numeric', 'vector'}, {'real'}));

%SOpower settings
addOptional(p, 'SO_freqrange', [0.3, 1.5], @(x) validateattributes(x, {'numeric', 'vector'}, {'real', 'finite', 'nonnan'}));
addOptional(p, 'SOpower_outlier_threshold', 3, @(x) validateattributes(x,{'numeric'}, {'scalar'}));
addOptional(p, 'norm_method', 'p2shift1234', @(x) validateattributes(x, {'char', 'numeric'},{}));
addOptional(p, 'retain_Fs', true, @(x) validateattributes(x,{'logical'},{}));
addOptional(p, 'tapers', [15 29], @(x) validateattributes(x,{'numeric', 'vector'}, {'numel',2}));
addOptional(p, 'window_params', [30 15], @(x) validateattributes(x,{'numeric', 'vector'}, {'numel',2}));

%EEG time settings
addOptional(p, 'EEG_times', [], @(x) validateattributes(x, {'numeric', 'vector'},{'real','finite','nonnan'}));
addOptional(p, 'time_range', [], @(x) validateattributes(x, {'numeric', 'vector'},{'real','finite','nonnan'}));
addOptional(p, 'isexcluded', [], @(x) validateattributes(x, {'logical', 'vector'},{}));

parse(p,varargin{:});
parser_results = struct2cell(p.Results); %#ok<NASGU>
field_names = fieldnames(p.Results);

eval(['[', sprintf('%s ', field_names{:}), '] = deal(parser_results{:});']);

if isempty(EEG_times) %#ok<*NODEF>
    EEG_times = (0:length(EEG)-1)/Fs;
else
    assert(length(EEG_times) == size(EEG,2), 'EEG_times must be the same length as EEG');
end

if isempty(time_range)
    time_range = [min(EEG_times), max(EEG_times)];
else
    assert( (time_range(1) >= min(EEG_times)) & (time_range(2) <= max(EEG_times)), 'time_range cannot be outside of the time range described by "EEG_times"');
end

if isempty(isexcluded)
    isexcluded = false(size(EEG,2),1);
else
    assert(length(isexcluded) == size(EEG,2),'isexcluded must be the same length as EEG');
end

%% Compute SO power
% Replace artifact timepoints with NaNs
nanEEG = EEG;
nanEEG(isexcluded) = nan;

% Now compute SOpower
[SOpower, SOpower_times] = compute_mtspect_power(nanEEG, Fs, 'freq_range', SO_freqrange,'tapers', tapers, 'window_params', window_params);

SOpower_times = SOpower_times + EEG_times(1); % adjust the time axis to EEG_times

% Compute SOpower stage
if ~isempty(stage_vals) && ~isempty(stage_times)
    SOpower_stages = interp1(stage_times, stage_vals, SOpower_times, 'previous');
else
    SOpower_stages = true;
end

% Exclude outlier SOpower that usually reflect isexcluded
SOpower(abs(nanzscore(SOpower)) >= SOpower_outlier_threshold) = nan;


%% Normalize SO power

%Handle shift inputs
if strcmpi(norm_method,'shift')
    shift_ptile = 2;
    shift_stages = 1:4;
elseif regexp(norm_method,'p*+shift*')
    shift_ptile = str2double(norm_method(2:strfind(norm_method,'shift')-1));
    shift_stages = unique((norm_method(strfind(norm_method,'shift')+5:end)) - '0');

    if isempty(shift_stages)
        shift_stages = 1:4;
    end

    norm_method = 'shift';
end

%Check shift
assert(shift_ptile >= 0 && shift_ptile <= 100, 'Shift percentile must be between 0 and 100');

switch norm_method
    case {'proportion', 'normalized'}
        [proppower, ~] = computeMTSpectPower(nanEEG, Fs, 'freq_range', [freq_range(1), freq_range(2)]);
        SOpower_norm = db2pow(SOpower)./db2pow(proppower);
        ptile = [];

    case {'percentile', 'percent', '%', '%SOP'}
        low_val =  1;
        high_val =  99;
        ptile = prctile(SOpower(SOpower_times>=time_range(1) & SOpower_times<=time_range(2)), [low_val, high_val]);
        SOpower_norm = SOpower-ptile(1);
        SOpower_norm = SOpower_norm/(ptile(2) - ptile(1));  % Note: is this computation correct? 

    case {'shift'}
        if islogical(SOpower_stages) && SOpower_stages
            SOpower_stages_valid = true(size(SOpower_stages));
        else
            SOpower_stages_valid = ismember(SOpower_stages, shift_stages);
        end
        ptile = prctile(SOpower(SOpower_times>=time_range(1) & SOpower_times<=time_range(2) & SOpower_stages_valid), shift_ptile);
        SOpower_norm = SOpower-ptile(1);

    case {'absolute', 'none'}
        SOpower_norm = SOpower;
        ptile = [];

    otherwise
        error(['Normalization method "', norm_method, '" not recognized']);
end

% Make the output SOpower_norm a row vector 
SOpower_norm = SOpower_norm';

%% (Optional) Upsample to EEG sampling rate 
if retain_Fs
    SOpower_norm_notnan = SOpower_norm(~isnan(SOpower_norm));
    SOpower_norm = interp1([EEG_times(1), SOpower_times(~isnan(SOpower_norm)), EEG_times(end)],...
       [SOpower_norm_notnan(1), SOpower_norm_notnan, SOpower_norm_notnan(end)], EEG_times);
    SOpower_norm(isexcluded) = nan;
    SOpower_times = EEG_times;
    if ~isempty(stage_vals) && ~isempty(stage_times)
        SOpower_stages = interp1(stage_times, stage_vals, SOpower_times, 'previous');
    else
        SOpower_stages = true;
    end
end

end
