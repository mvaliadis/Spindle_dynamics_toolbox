function [] = plotcos()
%PLOTCOS plot a cosine reference plot
% Where cos(0) = 1, means slow oscillation (SO) upstate
% cos(pi or -pi) = -1, indicates SO downstate
% Last updated, SChen 010725
%******************************************************************************************************************************************

    xs = -pi:0.01:pi;
    ys = cos(xs);
    hold on;
    plot(xs,ys,'k');
    xlim([-pi pi])
    yline(0,'k--')
    set(gca,'YTick',[],'box','off','YColor','none')
    xticks(-pi:pi/2:pi);
    xticklabels({'-\pi','-\pi/2','0', '\pi/2','\pi'});
    xlabel('SO Phase (rad)','fontsize',10);

    % Add "SO Rising" label
    text(-pi/2-0.4, cos(-pi/2-0.4) + 0.5, 'SO Rising', ...
        'HorizontalAlignment', 'center', 'Rotation', 45, 'FontSize', 10);
    
    % Add "SO Falling" label
    text(pi/2+0.4, cos(pi/2+0.4) + 0.5, 'SO Falling', ...
        'HorizontalAlignment', 'center', 'Rotation', 315, 'FontSize', 10);
    ax1 = gca; 
    ax1.FontSize = 10;

end

