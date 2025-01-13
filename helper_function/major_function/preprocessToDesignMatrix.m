function [X, BinData, res_table] = preprocessToDesignMatrix(EEG, Fs, stage_val, stage_time,ModelSpec)
%PREPROCESSTODESIGNMATRIX preprocesses raw EEG data to design matrix and binned data
% Input(All required):
%       - EEG: (double) raw EEG data              
%       - Fs: (double) sampling frequency in Hz   
%       - stage_val: (double) stage values 
%                   where 1,2,3,4,5 represent N3,N2,N1,REM and Wake
%       - stage_time:(double) corresponding time of the stage
%       - ModelSpec: A struct that contains all model specifications
%
% Output: 
%       - X (double, matrix): Design Matrix, the size depends on data length and ModelSpec
%       - BinData (struct): A struct that has all data saved in binsize 
%       - res_table: (table) All event info and signals to use. Key components include:
%           -- peak_ctimes: detected event central times (s)
%           -- peak_freqs: detected event frequency (Hz)
%           -- SOpow: Slow oscillation power
%           -- SOphase: Slow oscillation phase
%       
%       
% Please provide the following citation for all use:
%       Shuqiang Chen,Mingjian He,Ritchie E. Brown, Uri T. Eden, Michael J Prerau, 
%       "Individualized Temporal Patterns Drive Human Sleep Spindle Timing"
%       PNAS, 2025, https://doi.org/10.1073/pnas.2405276121
%
% Last updated, SChen 010725
%******************************************************************************************************************************************

%% Extract spindle events and their properties

binsize = ModelSpec.binsize;
hard_cutoffs = ModelSpec.hard_cutoffs; 
hist_choice = ModelSpec.hist_choice;

disp('May take minutes ... Extracting spindles ...');
[res_table] = eegToEventSignal(EEG, Fs, stage_val, stage_time);

%% Convert event data to binned data
[BinData] = rawToBinData(res_table, Fs, binsize, hard_cutoffs, hist_choice);

%% Build design matrix for the specified model
X = build_design_mt(ModelSpec, BinData);
    
end
