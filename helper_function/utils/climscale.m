%CLIMSCALE Rescale the color limits of an image to remove outliers with percentiles
%
%   Usage:
%       clims_new = climscale(hObj, ptiles, outliers)
%       climscale(hObj, outliers)
%       climscale(hObj, ptiles)
%       climscale(outliers)
%       climscale(ptiles)
%
%   Input:
%       hObj: handle to axis or image object -- (default: gca)
%       ptiles: 1x2 double - scaling percentiles (default: [5 98])
%       outliers: logical - remove outliers prior to scaling using isoutlier (default: true)
%
%   Output:
%       clims_new: 1x2 double - scaled caxis limits
%
%   Example:
%       %Create axes and image objects
%       ax = gca;
%       hImObj = imagesc(peaks(500));
%       
%       %Call with defaults
%       climscale;
%       pause(1)
%       
%       %Turn off outilers
%       climscale(false);
%       pause(1)
%       
%       %Set scaling percentiles
%       climscale([10 90]);
%       pause(1)
%       
%       %Set percentiles and outliers
%       climscale([5 95],true);
%       pause(1)
%       
%       %Select image objectß
%       climscale(hImObj, false);
%       pause(1)
%       
%       %Select axis
%       climscale(ax, true);
%       
% Copyright 2024 Michael J. Prerau Laboratory. - http://www.sleepEEG.org
%**************************************************************************

function clims_new = climscale(varargin)

hObj = [];
ptiles = [];
outliers = [];

%Handle a single input
if nargin == 1
    if ishandle(varargin{1})
        hObj = varargin{1};
    else
        if isvector(varargin{1}) && isnumeric(varargin{1})
            ptiles = varargin{1};
        elseif islogical(varargin{1})
            outliers = varargin{1};
        else
            error('Invalid single parameter call to climscale. Must be either handle, ptiles vector, or logical for outliers');
        end
    end
end

%Allow for all combinations of two inputs
if nargin == 2
    if ishandle(varargin{1})
        hObj = varargin{1};

        if isvector(varargin{2}) && isnumeric(varargin{1})
            ptiles = varargin{2};
        elseif islogical(varargin{2})
            outliers = varargin{2};
        else
            error('Invalid single parameter call to climscale. Must be either handle, ptiles vector, or logical for outliers');
        end
    else
        ptiles = varargin{1};
        outliers = varargin{2};
    end
end

%Case of 3 inputs
if nargin == 3
    hObj = varargin{1};
    ptiles = varargin{2};
    outliers = varargin{3};
end

%Set defaults
if isempty(hObj)
    hObj = gca;
end

if isempty(ptiles)
    ptiles = [5 98];
end

if isempty(outliers)
    outliers = true;
end

%Check inputs
assert(ishandle(hObj) || isa(hObj,'matlab.graphics.primitive.Image') || isa(hObj,'matlab.graphics.axis.Axes'),['First input must be axis or image handle. Input was ' class(hObj)])
assert(length(ptiles)==2 && issorted(ptiles) && isnumeric(ptiles), 'Percentiles must be a 1x2 vector that is monotically increasing and numeric');
assert(islogical(outliers), 'Outliers must be logical');


%Get color data
if isa(hObj,'matlab.graphics.primitive.Image')
    hIm = hObj;
    hAx = get(hIm, 'parent');
else
    hAx = hObj;
    hIm = findall(hAx,'type','image');
    assert(isscalar(hIm),'More than one image found in axis. Use specific image handle');
end

%Get color data
data = hIm.CData(:);

%Make sure it is not a flat image
assert(range(data)>0,'Image data are all equal');

%Handle massive images
N = length(data);
if N > 1e9
    warning('Data too large to efficiently compute percentile. Using random sampling.');
    data = data(randi(N, 1, min(100000, N)));
end

%Find poorly formed data
if ~outliers
    bad_inds = isnan(data) | isinf(data);
else %Remove outliers if selected
    bad_inds = isnan(data) | isinf(data) | isoutlier(data);
end

%Compute color limits
clims_new = prctile(data(~bad_inds), ptiles);

if clims_new(1) == clims_new(2)
    return;
end

%Update axis scale
set(hAx,'clim',clims_new);
end