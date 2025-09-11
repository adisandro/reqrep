% This script plot the 6 Pareto front for the different configurations of
% the tool.

clearvars
clearvars -global
clearvars figIdx
close("all")
clc

%% Load results

% Define location of results file
fileOutput = "ToolOutput" + filesep + "results.csv";

% Read file
resultsTable = readtable(fileOutput,"VariableNamingRule","preserve");

% Drop last four columns
resultsTable.f_sem_taut = [];
resultsTable.f_sem_var_type = [];
resultsTable.f_sat_vertical = [];
resultsTable.f_sat_horizontal = [];

% Remove all entries that do not have weight [1, 1, 1]
resultsTable = resultsTable(strcmp(resultsTable.weights,"[1.0, 1.0, 1.0]"),:);

%% Get model name and requirement for each run

% Get config id column
configTemp = string(resultsTable.config_id);

% Split config id
strTemp = split(configTemp,"_");

% Save model, and requirement
resultsTable.model = strTemp(:,1);
resultsTable.requirement = strTemp(:,2);

% Reorder columns of the table
resultsTable = movevars(resultsTable,"model","Before",1);
resultsTable = movevars(resultsTable,"requirement","After","model");
resultsTable = movevars(resultsTable,"aggregation_strategy","After","requirement");
resultsTable = movevars(resultsTable,"weights","After","aggregation_strategy");

% Delete temporary variables
clear("*Temp")

%% Plot all pareto fronts

% Get list of models
modelList = unique(string(resultsTable.model));

% Loop over models
for ii = 1:length(modelList)

    % Call function to save the plot
    plotPareto(resultsTable(strcmp(resultsTable.model,modelList(ii)),:),modelList(ii));
end
 
% Plot graph with all the results
plotPareto(resultsTable,"All");

%% Helper function

% This function returns the Pareto front
function [x_par, y_par] = pareto_front(x,y)
    
    % Check that x and y have the same length
    if length(x) ~= length(y)
        error("The arrays x and y should have the same length.")
    end

    % Check that x and y are not empty
    if isempty(x) || isempty(y)
        error("The arrays x and y must not be empty.")
    end
    
    % Initialize the pareto front as empty
    x_par = [];
    y_par = [];

    % Loop over points
    for ii = 1:length(x)

        % Temporary remove i-th point from array
        idxTemp = true(length(x),1);
        idxTemp(ii) = false;
        xTemp = x(idxTemp);
        yTemp = y(idxTemp);

        % Check if it satisfies Pareto condition
        checkPareto = ~any(xTemp < x(ii) & yTemp < y(ii));

        % Save points on the front
        if checkPareto
            x_par = [x_par, x(ii)];
            y_par = [y_par, y(ii)];
        end
    end

    % Sort points on the front
    xFake = x_par-1e-6*y_par;
    [~, idxTemp] = sort(xFake);
    x_par = x_par(idxTemp);
    y_par = y_par(idxTemp);

end

% This function plots the Pareto front
function plotPareto(resultsTable,modelStr)
    
    % Define figure index
    persistent figIdx;
    if isempty(figIdx)
        figIdx = 0;
    end

    % Define axes labels
    desirabilityList = ["f_des_semantic"; "f_des_syntactic"; "f_des_satisfaction"];
    desirabilityStr = ["$Semantic~Integrity$"; "$Syntactic~Similarity$"; "$Satisfaction~extent$"];
    titleStr = sprintf("$Model:~%s$",modelStr);

    % Define list of aggregation methods
    aggrList = unique(string(resultsTable.aggregation_strategy));
    aggrStr = ["$No~aggregation$","$Weighted~sum$"];

    % Define markers and color for each aggregation method
    colorList = {[0,0,1],[1,0,0]};
    markerList = ["x","o"];

    % Loop over desirability functions
    for ii = 1:length(desirabilityList)

        % Create figure
        figIdx = figIdx+1;
        figure(figIdx)
        clf
        hold("on")
        grid("on")

        % Define title and axes labels
        xlim([-0.1,1.1])
        ylim([-0.1,1.1])
        xlabel("$Correctness$","FontSize",16,"Interpreter","latex")
        ylabel(desirabilityStr(ii),"FontSize",16,"Interpreter","latex")
        title(titleStr,"FontSize",20,"Interpreter","latex")

        % Loop over aggregation methods
        for jj = 1:length(aggrList)

            % Filter out results from the other aggragation method
            resultsTableTemp = resultsTable(strcmp(resultsTable.aggregation_strategy,aggrList(jj)),:);
            correct = resultsTableTemp.f_correctness;
            desire = resultsTableTemp.(desirabilityList(ii));

            % Plot Pareto front
            [correctPar, desirePar] = pareto_front(correct, desire);
            plot(correctPar,desirePar,"Color",colorList{jj},"LineWidth",1)

            % Plot points
            scatter(correct,desire,100,"Marker",markerList(jj),"MarkerEdgeColor",colorList{jj},"LineWidth",2)

        end

        % Add legend
        legend(["",aggrStr(1),"",aggrStr(2)],"Location","northeast","Interpreter","latex","FontSize",12)

        % Save figure
        saveas(gcf,"Figures" + filesep + sprintf("Pareto_%s_%i.pdf",modelStr,ii),"pdf");
        saveas(gcf,"Figures" + filesep + sprintf("Pareto_%s_%i.eps",modelStr,ii),"epsc");
    end

    
end