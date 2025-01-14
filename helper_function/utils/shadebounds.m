function [line_handle, bounds_handle] = shadebounds(x, mid, hi, lo, mid_color, shade_color, bounds_color, shade_alpha)
% SHADEBOUNDS plots a curve with shaded bounds on a 2D plot.
%
% Syntax:
%   [line_handle, bounds_handle] = shadebounds(x, mid, hi, lo)
%   [line_handle, bounds_handle] = shadebounds(x, mid, hi, lo, mid_color)
%   [line_handle, bounds_handle] = shadebounds(x, mid, hi, lo, mid_color, shade_color)
%   [line_handle, bounds_handle] = shadebounds(x, mid, hi, lo, mid_color, shade_color, bounds_color)
%   [line_handle, bounds_handle] = shadebounds(x, mid, hi, lo, mid_color, shade_color, bounds_color, shade_alpha)
%
% Description:
%   SHADEBOUNDS plots a curve with shaded bounds on a 2D plot. The x-axis
%   represents the independent variable, and the mid, hi, and lo vectors
%   represent the corresponding dependent variables. The shaded bounds are
%   filled between the hi and lo curves.
%
% Input Arguments:
%   - x: Independent variable vector.
%   - mid: Dependent variable vector representing the curve to be plotted.
%   - hi: Dependent variable vector representing the upper bound of the
%     shaded region.
%   - lo: Dependent variable vector representing the lower bound of the
%     shaded region.
%   - mid_color (optional): Color of the curve. Default is [0 0 0] (black).
%   - shade_color (optional): Color of the shaded region. Default is [.5
%     .5 .5] (gray).
%   - bounds_color (optional): Color of the boundaries of the shaded
%     region. Default is [.9 .9 .9] (light gray).
%   - shade_alpha (optional): Transparency of the shaded region. Default is
%     0.1 (90% transparent).
%
% Output Arguments:
%   - line_handle: Handle to the plotted curve line.
%   - bounds_handle: Handle to the plotted shaded bounds region.
%
% Examples:
%   % Plot a curve with default shaded bounds
%   x = 1:10;
%   mid = x.^2;
%   hi = x.^2 + 6;
%   lo = x.^2 - 4;
%   [line_handle, bounds_handle] = shadebounds(x, mid, hi, lo)
%
%   % Plot a curve with custom colors and transparency
%   x = 1:10;
%   mid = x.^2;
%   hi = x.^2 + 6;
%   lo = x.^2 - 4;
%   mid_color = 'red';
%   shade_color = [1 0.8 0.8];  % Light pink
%   bounds_color = 'black';
%   shade_alpha = 0.3;
%   [line_handle, bounds_handle] = shadebounds(x, mid, hi, lo, mid_color, shade_color, bounds_color, shade_alpha)
%
% See also:
%   fill, plot
% 
% Copyright 2024 Michael J. Prerau Laboratory. - http://www.sleepEEG.org
%**************************************************************************

% Set defaults for optional input arguments
if nargin < 5
    mid_color = [0 0 0];              % Default curve color: black
end

if nargin < 6
    shade_color = [.2 .2 .2];      % Default shade color: dark gray
end

if nargin < 7
    bounds_color = [.9 .9 .9];        % Default bounds color: light gray
end

if nargin < 8
    shade_alpha = 0.1;                % Default shade transparency
end

% Make sure all vectors are pointing in the same direction
x = x(:)';
mid = mid(:)';
lo = lo(:)';
hi = hi(:)';

% Plot the curve and shaded bounds
hold on
bounds_handle = fill([x fliplr(x)], [lo fliplr(hi)], shade_color, 'EdgeColor', bounds_color, 'FaceAlpha', shade_alpha);
line_handle = plot(x, mid, 'LineWidth', 2, 'Color', mid_color);
end
