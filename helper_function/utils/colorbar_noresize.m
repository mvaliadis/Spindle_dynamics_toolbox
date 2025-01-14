function c = colorbar_noresize(varargin)
% COLORBAR_NORESIZE creates a colorbar that does not resize the axis.
%
% Syntax:
%   c = colorbar_noresize
%   c = colorbar_noresize(ax, <colorbar arguments>)
%
% Description:
%   COLORBAR_NORESIZE creates a colorbar associated with the current axis
%   (gca) or the specified axis (ax). By default, the colorbar will retain
%   the same size as the axis and will not cause any resizing. Additional
%   colorbar arguments can be provided.
%
% Input Arguments:
%   - ax (optional): Handle to the axis for which the colorbar will be
%     created. Default is the current axis (gca).
%   - <colorbar arguments>: Additional arguments to customize the colorbar.
%
% Output Argument:
%   - c: Handle to the created colorbar.
%
% Copyright 2024 Michael J. Prerau Laboratory. - http://www.sleepEEG.org
%**************************************************************************

if nargin == 0 || ~isa(varargin{1},'matlab.graphics.axis.Axes')
    ax = gca;   % Use the current axis if no input argument is provided
else
    ax = varargin{1};
end

pos = ax.Position;  % Save the current position of the axis
c = colorbar(ax, varargin{2:end});  % Create the colorbar
ax.Position = pos;  % Restore the original position of the axis

end
