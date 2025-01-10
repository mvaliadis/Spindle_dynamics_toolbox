function [ks,ksT] = KSplot(CIF,y,ploton)
% KSPLOT runs Kolmogorov–Smirnov (KS) test and plot KS plot
%
% Input:
%       - CIF (double), conditional intensity function
%       - y (double), binary event train
%       - ploton (double), generate KS plot if ploton is 1 
% Output:
%       - A KS plot
%       - ks: KS statistic
%       - ksT: KS test result, 0 means pass the KS test
%                              1 means fail to pass the KS test
%
% Updated SC,123024, 123124
%***********************************************************************************

%%

spindleindex = find(y);
N = length(spindleindex);

Z(1) = sum(CIF(1:spindleindex(1)));	
for i = 2:N							
  Z(i) = sum(CIF(spindleindex(i-1)+1:spindleindex(i)));
end
[eCDF0, zvals0] = ecdf(Z);				% Empirical CDF.
mCDF0 = 1-exp(-zvals0);				    % Model CDF.
x = linspace(0.0001,1,length(eCDF0)); 
upp = x + 1.36/sqrt(N); upp = upp'; 
low = x - 1.36/sqrt(N); low = low'; 
low(low<0) = 0; upp(upp>1) = 1; 
ks = max(abs(mCDF0-eCDF0));

ksT = double(kstest(eCDF0, 'CDF', [eCDF0 mCDF0])); % KS test results: 0:pass; 1: reject

% Figure
if ploton == 1
    fill([x fliplr(x)],[low; flipud(upp)],[0.9,0.9,0.9],'FaceAlpha',.5)
    hold on;  
    plot(x, x,'--', 'Color', [0.6 0.6 0.6], 'LineWidth', 1)
    plot(mCDF0, eCDF0, 'k', 'linewidth', 2);
    
    %Highlight the parts of the curve outside the confidence bounds in red
    inds = find(eCDF0>mCDF0+1.36/sqrt(N) | eCDF0<mCDF0-1.36/sqrt(N));
    empplot=nan(1,N);
    modplot=nan(1,N);
    empplot(inds)=eCDF0(inds);
    modplot(inds)=mCDF0(inds);
    plot(modplot,empplot, 'r','linewidth',2');

    ax4 = gca; 
    ax4.YTick = [0 0.5 1];
    ax4.XTick = [0 0.5 1];    
    ax4.YAxis.FontSize = 12;
    ax4.XAxis.FontSize = 12;

    %title(['KS Statistic = ' num2str(round(ks,4))],'Fontsize',12)
    ylabel('Empirical CDF','Fontsize',12)
    xlabel('Theoretical CDF','Fontsize',12)

    yyaxis right
    ax4 = gca; 
    ax4.YTick = [];
    ax4.YColor = 'k';
    ylabel(['KS stats: ' num2str(round(ks,4))],'Fontsize',10,'Color','k','Rotation',270);

end

end