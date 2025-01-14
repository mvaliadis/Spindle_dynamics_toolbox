% nanzscore - Computes z-scores for data with NaN values
%
% Syntax:
%   [zscored, mu, sigma] = nanzscore(data, varargin)
%
% Inputs:
%   - data: Input data array with NaN values
%   - varargin: Additional arguments passed to the zscore function
%
% Outputs:
%   - zscored: Z-scored data array
%   - mu: Mean of the non-NaN values in data
%   - sigma: Standard deviation of the non-NaN values in data
%
% Example:
%   data = [1, 2, NaN, 4, 5];
%   [zscored, mu, sigma] = nanzscore(data);
%
%   Copyright 2024 Michael J. Prerau Laboratory - http://www.sleepEEG.org
%********************************************************************

function [zscored, mu, sigma] = nanzscore(data, varargin)
    % Find non-NaN indices in the data
    inds = ~isnan(data);
    
    % Compute z-scores for non-NaN values
    [zscored, mu, sigma] = zscore(data(inds), varargin{:});
end


