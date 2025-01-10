%PHASEHISTOGRAM  Draw a polar histogram with mean arrow for phase data
%
%   Usage:
%   [theta_mean, rho_mean, h_phist, h_pax, h_ml] = phasehistogram(phases, amps, <phasehistogram inputs>)
% 
%   Input:
%   phases: 1xN vector of phase values
%   amps: 1xN vector of amplitudes (default: 1)
% 
%   Output:
%   theta_mean: mean angle
%   rho_mean: mean magnitude
%   h_phist: handle for phase histogram
%   h_pax: handle for polar axis
%   h_ml: handle for mean line
% 
%   Example:
%         % Generate some phases
%         phases = mod(randn(1,1000) + pi/2, 2*pi);
%
%         %Create the plot
%         figure;
%         phasehistogram(phases, 1,'NumBins',25,'FaceColor','blue','FaceAlpha',.3);
%
% Copyright 2024 Michael J. Prerau Laboratory. - http://www.sleepEEG.org
%**************************************************************************

function [theta_mean, rho_mean, h_phist, h_pax, h_ml] = phasehistogram(phases, amps, varargin)
if nargin==0
    error('Must input phases');
end

if nargin<2 || isempty(amps)
    amps = ones(size(phases));
end

%Compute the mean population vector
vect_mean = mean(amps.*exp(1i*phases));

%Get the mean magnitude and angle
rho_mean = abs(vect_mean);
theta_mean = angle(vect_mean);

%Set default to normalization
varargin = [{'Normalization'}, {'pdf'}, varargin(:)'];

%Plot histogram
h_phist = polarhistogram(phases,varargin{:});
h_pax = gca;
h_pax.ThetaAxisUnits = 'radians';
%h_pax.ThetaTick = 0:pi/4:2*pi;
%h_pax.ThetaTick = 0:pi/2:2*pi;
h_pax.ThetaTick = 0:pi:2*pi;
%h_pax.ThetaTickLabel = {'0','\pi/4','\pi/2','3\pi/4' '\pm\pi','-3\pi/4', '-\pi/2','-\pi/4'};
%h_pax.ThetaTickLabel = {'0','\pi/2', '\pm\pi', '-\pi/2'};
h_pax.ThetaTickLabel = {'0','\pm\pi'};
h_pax.FontSize = 12;

%Add mean arrow
hold on
h_ml = polarplot([theta_mean theta_mean],[0 rho_mean],'linestyle','-','color','r','linewidth',2);

