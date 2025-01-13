function [Sp_adj] = FinerModCardinalSpline(ord,c_pt_times_all,s,spline_resol)
%% Cardinal spline for non-uniform spacing
% modified cardinal spline in a finer resolution
% Input: 
%       -ord, (double): history order 
%       -c_pt_times_all, (double, vector): knot locations
%       -s, (double): tension parameter
%       -spline_resol, (double): this determines spline resolution in evaluation
% 
% Ouput: 
%       -Sp_adj(double,matrix), spline matrix in a finer resolution 
%                              (in spindle_resol*binsize resolution)
%
% Updated by Shuqiang Chen, 10/17/22
%************************************************************************************

%%

lastknot = ord;
numknots = length(c_pt_times_all);
Sp_adj = zeros(lastknot/spline_resol,numknots);

for i= 1:lastknot/spline_resol
   nearest_c_pt_index = max(find(c_pt_times_all<i*spline_resol));
   nearest_c_pt_time = c_pt_times_all(nearest_c_pt_index);
   next_c_pt_time = c_pt_times_all(nearest_c_pt_index+1);
   
   u = (i*spline_resol-nearest_c_pt_time)/(next_c_pt_time-nearest_c_pt_time);
   lb = (c_pt_times_all(3) - c_pt_times_all(1))/(c_pt_times_all(2)-c_pt_times_all(1));
   le = (c_pt_times_all(end) - c_pt_times_all(end-2))/(c_pt_times_all(end) - c_pt_times_all(end-1));   
   
   % Beginning knot 
   if nearest_c_pt_time == c_pt_times_all(1)  % Fixed Mehrad version
           p = [u^3 u^2 u 1]*[2-(s/lb) -2 s/lb;(s/lb)-3 3 -s/lb;0 0 0;1 0 0];
           Sp_adj(i,nearest_c_pt_index:nearest_c_pt_index+2) = p; 
   % End knot
   elseif nearest_c_pt_time==c_pt_times_all(end-1) % Fixed Mehrad version
           p=[u^3 u^2 u 1]*[-s/le 2 -2+(s/le);2*s/le -3 3-(2*s/le);-s/le 0 s/le;0 1 0];
           Sp_adj(i,nearest_c_pt_index-1:nearest_c_pt_index+1) = p;  
   % Interior knots
   else
           prev_c_pt_time = c_pt_times_all(nearest_c_pt_index-1);
           next2 = c_pt_times_all(nearest_c_pt_index+2);
           l1 = (next_c_pt_time-prev_c_pt_time)/(next_c_pt_time-nearest_c_pt_time); % scale factors for non-uniform spacing 
           l2 = (next2-nearest_c_pt_time)/(next_c_pt_time-nearest_c_pt_time); % scale factors for non-uniform spacing
           p=[u^3 u^2 u 1]*[-s/l1 2-s/l2 s/l1-2 s/l2;2*s/l1 s/l2-3 3-2*s/l1 -s/l2;-s/l1 0 s/l1 0;0 1 0 0];
           Sp_adj(i,nearest_c_pt_index-1:nearest_c_pt_index+2) = p;
    end
end


end