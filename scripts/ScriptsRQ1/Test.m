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

%% Plot syntactic similarity vs. satisfaction extent

% Remove requirements with correctness ~= 0
resultsTable = resultsTable(resultsTable.f_correctness == 0,:);

% Remove requirements with semantic integrity ~= 0
resultsTable = resultsTable(resultsTable.f_des_semantic == 0,:);

% Create plot
figure(1)
clf
hold on
grid on
xlabel("syntactic similarity")
ylabel("satisfaction extent")
title("All models")

% Plot points for no_aggregation
resultsTableTemp = resultsTable(strcmp(resultsTable.aggregation_strategy,"no_aggregation"),:);
syntactic = resultsTableTemp.f_des_syntactic;
satisfaction = resultsTableTemp.f_des_satisfaction;
[syn_par,sat_par] = pareto_front(syntactic,satisfaction);
plot(syn_par,sat_par,"b")
scatter(syn_par,sat_par,"bx")

% Plot points for weighted_sum
resultsTableTemp = resultsTable(strcmp(resultsTable.aggregation_strategy,"weighted_sum"),:);
syntactic = resultsTableTemp.f_des_syntactic;
satisfaction = resultsTableTemp.f_des_satisfaction;
[syn_par,sat_par] = pareto_front(syntactic,satisfaction);
plot(syn_par,sat_par,"r")
scatter(syn_par,sat_par,"ro")

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