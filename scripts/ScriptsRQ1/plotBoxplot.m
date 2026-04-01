% This script plots the boxplot for the Syntactic Similarity and
% Satisfaction Extent for all the case studies.

clearvars
clearvars -global
clearvars figIdx
close("all")
clc

% Remove warning for adding rows to the temporary table
warning off MATLAB:table:RowsAddedExistingVars

% Get path to root folder
pathTemp = string(mfilename("fullpath"));
if contains(pathTemp,'LiveEditorEvaluationHelper')
    pathTemp = string(matlab.desktop.editor.getActiveFilename);
end
pathTemp = split(pathTemp,filesep);
rootPath = join(pathTemp(1:end-3),filesep);

% Change current active directory to root folder
origPath = cd(rootPath);
addpath("scripts" + filesep + "ScriptsRQ1")

%% Define results instances

% Define location of results file
fileList = struct("Folder",[],"FileName",[],"Aggregation",[],"Config",[],...
    "Weights",[],"TautologyZ3",[],"Label",[]);

fileList(1).Folder = "output";
fileList(1).FileName = "results_V1_V3.csv";
fileList(1).Aggregation = "no_aggregation";
fileList(1).Config = "default";
fileList(1).Weights = "[1.0, 1.0, 1.0]";
fileList(1).TautologyZ3 = true;
fileList(1).Label = "V1";

fileList(2).Folder = "output";
fileList(2).FileName = "results_V2_V4.csv";
fileList(2).Aggregation = "no_aggregation";
fileList(2).Config = "default";
fileList(2).Weights = "[1.0, 1.0, 1.0]";
fileList(2).TautologyZ3 = false;
fileList(2).Label = "V2";

fileList(3).Folder = "output";
fileList(3).FileName = "results_V1_V3.csv";
fileList(3).Aggregation = "weighted_sum";
fileList(3).Config = "default";
fileList(3).Weights = "[1.0, 1.0, 1.0]";
fileList(3).TautologyZ3 = true;
fileList(3).Label = "V3";

fileList(4).Folder = "output";
fileList(4).FileName = "results_V2_V4.csv";
fileList(4).Aggregation = "weighted_sum";
fileList(4).Config = "default";
fileList(4).Weights = "[1.0, 1.0, 1.0]";
fileList(4).TautologyZ3 = false;
fileList(4).Label = "V4";

fileList(5).Folder = "output";
fileList(5).FileName = "results_V5.csv";
fileList(5).Aggregation = "no_aggregation";
fileList(5).Config = "default";
fileList(5).Weights = "[1.0, 3.0, 5.0]";
fileList(5).TautologyZ3 = true;
fileList(5).Label = "V5";

fileList(6).Folder = "output";
fileList(6).FileName = "results_V6_V7.csv";
fileList(6).Aggregation = "no_aggregation";
fileList(6).Config = "hp_increase_tree_depth";
fileList(6).Weights = "[1.0, 1.0, 1.0]";
fileList(6).TautologyZ3 = true;
fileList(6).Label = "V6";

fileList(7).Folder = "output";
fileList(7).FileName = "results_V6_V7.csv";
fileList(7).Aggregation = "no_aggregation";
fileList(7).Config = "hp_increase_num_offsprings";
fileList(7).Weights = "[1.0, 1.0, 1.0]";
fileList(7).TautologyZ3 = true;
fileList(7).Label = "V7";

% Get list of face and line colors
colorFace = {[204, 227, 242]/255;
    [248, 221, 210/255];
    [252, 239, 210]/255;
    [229, 214, 233]/255;
    [229, 239, 214]/255;
    [219, 242, 253]/255;
    [236, 208, 213]/255};

colorLine = {[  0, 114, 189]/255;
    [217,  83,  25]/255;
    [238, 177,  32]/255;
    [126,  47, 142]/255;
    [118, 173,  47]/255;
    [ 70, 173, 216]/255;
    [163,  19,  46]/255};

colorFace = repmat(colorFace,ceil(length(fileList)/length(colorFace)),1);
colorLine = repmat(colorLine,ceil(length(fileList)/length(colorLine)),1);

% Delete temporary variables
clear("*Temp")

%% Loop over results instance

% Define model and requirement lists
modelList = ["AFC", "AT", "CC", "EU", "NNP", "TUI"]';
reqList = ["AFC29", "AFC33", "AT1", "AT2", "CC1", "CCX", "EU3", "NNP3a", "NNP3b", "NNP4", "TU1", "TU2"]';

% Define empty desirability metrics' table
desTableTemplate = table('size', [0 5+7], ...
        'VariableTypes', [repmat("string",1,5),repmat("double",1,7)], ...
        'VariableNames', ["label","aggregation","model","weight","config","tautologyZ3","repairs_number","average","median","min","max","stddev"]);
desirabilityList = ["f_des_syntactic"; "f_des_satisfaction"];
desirabilityStr = ["Syntactic Similarity"; "Satisfaction extent"];
desirabilityShort = ["Synt", "Satis"];
syntTable = desTableTemplate;
satisTable = desTableTemplate;

% Define repairs table
repairsTable = table('size', [length(fileList), 5+5], ...
    'VariableTypes', [repmat("string",1,5),repmat("double",1,5)], ...
    'VariableNames', ["label","aggregation","model","weight","config","tautologyZ3","total","correct","sound","correct_sound"]);
repairsTable.label = [fileList.Label]';
repairsTable.aggregation = [fileList.Aggregation]';
repairsTable.model(:) = "All";
repairsTable.weight = [fileList.Weights]';
repairsTable.config = [fileList.Config]';
repairsTable.tautologyZ3 = [fileList.TautologyZ3]';

% Define empty global results table
resultsGlobal = [];

% Loop over results instances
for ii = 1:length(fileList)
    %% Read and filter results from raw data

    % Read file
    resultsTable = readtable(fileList(ii).Folder + filesep + fileList(ii).FileName, ...
        "VariableNamingRule","preserve");

    % Drop last four columns
    resultsTable.f_sem_taut = [];
    resultsTable.f_sem_var_type = [];
    resultsTable.f_sat_vertical = [];
    resultsTable.f_sat_horizontal = [];

    % Remove all entries that do not have the correct weights
    resultsTable = resultsTable(strcmp(resultsTable.weights,fileList(ii).Weights),:);

    % Remove all entries that do not have the correct aggregation method
    resultsTable = resultsTable(strcmp(resultsTable.aggregation_strategy,fileList(ii).Aggregation),:);

    % Remove all entries that do not have the correct config file
    if any(strcmp(resultsTable.Properties.VariableNames,"config"))
        resultsTable = resultsTable(strcmp(resultsTable.config,fileList(ii).Config),:);
        resultsTable.config = string(resultsTable.config);
    end
    
    % Count repairs
    repairsTable.total(ii) = height(resultsTable);
    repairsTable.correct(ii) = height(resultsTable(resultsTable.f_correctness == 0,:));
    repairsTable.sound(ii) = height(resultsTable(resultsTable.f_des_semantic == 0,:));
    repairsTable.correct_sound(ii) = height(resultsTable(resultsTable.f_correctness == 0 & resultsTable.f_des_semantic == 0,:));

    % Remove requirements with Correctness > 0
    resultsTable = resultsTable(resultsTable.f_correctness == 0,:);

    % Remove requirements with Semantic Integrity > 0
    resultsTable = resultsTable(resultsTable.f_des_semantic == 0,:);

    % Split config id column
    configTemp = string(resultsTable.config_id);
    strTemp = split(configTemp,"_");

    % Save model and requirement
    resultsTable.model = strTemp(:,1);
    resultsTable.requirement = strTemp(:,2);

    % Save label and z3-tautology flag
    resultsTable.label(:) = fileList(ii).Label;
    resultsTable.config(:) = fileList(ii).Config;
    resultsTable.tautologyZ3(:) = fileList(ii).TautologyZ3;

    % Reorder columns of the table
    resultsTable = movevars(resultsTable,"label","Before",1);
    resultsTable = movevars(resultsTable,"model","After","label");
    resultsTable = movevars(resultsTable,"requirement","After","model");
    resultsTable = movevars(resultsTable,"aggregation_strategy","After","requirement");
    resultsTable = movevars(resultsTable,"config","After","aggregation_strategy");
    resultsTable = movevars(resultsTable,"weights","After","config");
    resultsTable = movevars(resultsTable,"tautologyZ3","After","weights");

    %% Extract summary parameters
    
    % Get list of models and requirements
    modelListTemp = unique(string(resultsTable.model));
    modelListTemp = sort(modelListTemp);
    reqListTemp = unique(string(resultsTable.requirement));
    reqListTemp = sort(reqListTemp);
    
    % Check that model and requirement are on list
    if length(modelListTemp) ~= length(modelList)
        warning("The instance %s is considering a different number of models than expected!\n" + ...
            "It is possible that either the results for the model were not included, or all the proposed repairs for the model are incorrect or semantic unsound.",fileList(ii).Label)
    end
    if length(reqListTemp) ~= length(reqList)
        warning("The instance %s is considering a different number of requirements than expected!\n" + ...
            "It is possible that either the results for the requirement were not included, or all the proposed repairs for the requirement are incorrect or semantic unsound.",fileList(ii).Label)
    end
    for jj = 1:length(modelList)
        if ~any(strcmp(modelList(jj),modelListTemp))
            warning("The data for model %s was not included in instance %s!\n" + ...
                "Check if all the repairs for the model were filtered out due to being incorrect or semantically unsound.",modelList(jj),fileList(ii).Label)
        end
    end
    for jj = 1:length(reqList)
        if ~any(strcmp(reqList(jj),reqListTemp))
            warning("The data for requirement %s was not included in instance %s!\n" + ...
                "Check if all the repairs for the requirement were filtered out due to being incorrect or semantically unsound.",reqList(jj),fileList(ii).Label)
        end
    end

    % Loop over desirability metrics
    for jj = 1:length(desirabilityList)

        % Make empty table
        desTableTemp = desTableTemplate;

        % Add aggregation, weights, models, and labels to the table
        desTableTemp.label(1:length(modelListTemp)+1) = fileList(ii).Label;
        desTableTemp.aggregation(:) = fileList(ii).Aggregation;
        desTableTemp.model = [modelListTemp; "All"];
        desTableTemp.weight(:) = fileList(ii).Weights;
        desTableTemp.config(:) = fileList(ii).Config;
        desTableTemp.tautologyZ3(:) = fileList(ii).TautologyZ3;

        % Loop over rows of desirability table
        for kk = 1:height(desTableTemp)
    
            % Filter out result table
            if ~strcmp(desTableTemp.model(kk),"All")
                resultsTableTemp = resultsTable(strcmp(resultsTable.model,desTableTemp.model(kk)), :);
            else
                resultsTableTemp = resultsTable;
            end
    
            % Compute statistical description of data
            desTableTemp.repairs_number(kk) = height(resultsTableTemp);
            desTableTemp.average(kk) = mean(resultsTableTemp.(desirabilityList(jj)));
            desTableTemp.median(kk) = median(resultsTableTemp.(desirabilityList(jj)));
            desTableTemp.min(kk) = min(resultsTableTemp.(desirabilityList(jj)));
            desTableTemp.max(kk) = max(resultsTableTemp.(desirabilityList(jj)));
            desTableTemp.stddev(kk) = std(resultsTableTemp.(desirabilityList(jj)));
    
            % Delete temporary results table
            clear("resultsTableTemp")
        end

        % Append table to the proper global table
        if jj == 1
            syntTable = [syntTable; desTableTemp];
        else
            satisTable = [satisTable; desTableTemp];
        end

        % Print out table
        fprintf("\t%s - %s\n\n",fileList(ii).Label,desirabilityStr(jj))
        disp(desTableTemp)

        % Delete desirability metrics table
        clear("desTableTemp")

    end

    % Save results table in Global table

    if isempty(resultsGlobal)
        resultsGlobal = resultsTable;
    else
        resultsGlobal = [resultsGlobal; resultsTable];
    end

    % Delete temporary variables
    clear("*Temp","resultsTable")

end

% Save global tables
writetable(syntTable,sprintf("scripts"+filesep+"ScriptsRQ1"+filesep+"Table_%s.csv",desirabilityShort(1)))
writetable(satisTable,sprintf("scripts"+filesep+"ScriptsRQ1"+filesep+"Table_%s.csv",desirabilityShort(2)))

% Print number of repairs table
fprintf("\n\tNumber of repaired requirements:\n\n")
disp(repairsTable)
writetable(repairsTable,"scripts"+filesep+"ScriptsRQ1"+filesep+"repairNumber.csv")

%% Make boxplot for all models

% Get labels in the desired order
labelFiles = [fileList.Label]';

for ii = 1:length(desirabilityList)

    % Create figure
    figure(ii)
    clf
    hold("on")
    grid("on")
    orient(gcf,"landscape")

    % Add label for y axis
    ylabel(desirabilityStr(ii),"FontSize",20)
    % title("All models","FontSize",20)
    set(gca,"TickLabelInterpreter","none")
    set(gca,"FontSize",20)

    % Create boxchart
    boxc = boxchart(resultsGlobal.(desirabilityList(ii)),"GroupByColor",resultsGlobal.label,"ColorGroupWidth",0.9);
    legend("AutoUpdate","off","Location","eastoutside")
    legend("boxoff")
    xticks([])
    set(gcf,"Position",[0   80   800   400])

    % Reorder columns
    labelPlot = string(get(boxc,"DisplayName"));
    XDataBackup = get(boxc,"XData");
    YDataBackup = get(boxc,"YData");
    for jj = 1:length(labelFiles)
        idxTemp = find(strcmp(labelFiles(jj),labelPlot));
        assert(isscalar(idxTemp),"Two or more labels are identical.")
        set(boxc(jj),"XData",XDataBackup{idxTemp}, ...
            "YData",YDataBackup{idxTemp}, ...
            "DisplayName", labelPlot(idxTemp))
    end

    % Save plot
    exportgraphics(gcf,"scripts"+filesep+"ScriptsRQ1"+filesep+"Figures"+filesep+sprintf("Boxplot_%s.pdf",desirabilityShort(ii)),"BackgroundColor","none","ContentType","vector");
end

%% Make plot of requirements

figure(1+length(desirabilityList))
clf
hold("on")
grid("on")
orient(gcf,"landscape")

scatter(0, 0, 100, "+", "MarkerEdgeColor", [0 0 0], "LineWidth", 2)
scatter(0, 0, 100, "o", "MarkerEdgeColor", [0 0 0], "LineWidth", 2)
scatter(0, 0, 100, "^", "MarkerEdgeColor", [0 0 0], "LineWidth", 2)

for ii = 1:height(repairsTable)
    scatter(ii,repairsTable.total(ii),100,"+","MarkerEdgeColor",colorLine{ii},"LineWidth",2)
    scatter(ii,repairsTable.correct(ii),100,"o","MarkerEdgeColor",colorLine{ii},"LineWidth",2)
    scatter(ii,repairsTable.correct_sound(ii),100,"^","MarkerEdgeColor",colorLine{ii},"LineWidth",2)
end

set(gca,"FontSize",12)
xlabel("Configurations","FontSize",20)
xticks(1:length(fileList))
xlim([0.5,height(repairsTable)+0.5])
xticklabels([fileList.Label])
ylabel("Repaired requirements","FontSize",20)
legend("Total","Correct","Correct & Sound","Location","eastoutside","Fontsize",20)
set(gcf,"Position",[0   80   800   600])
exportgraphics(gcf,"scripts"+filesep+"ScriptsRQ1"+filesep+"Figures"+filesep+"Repairs.pdf","BackgroundColor","none","ContentType","vector");

% Change active directory back to initial one
cd(origPath)

