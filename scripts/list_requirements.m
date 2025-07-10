function list_requirements(dirPath)
% List all requirements from requirement tables in .slx and .mdl files under dirPath

if nargin < 1
    error('You must specify the directory path as an input argument.');
end

% Configure MATLAB to suppress library warnings
warning('off', 'all'); % Suppress all warnings temporarily

% Find all .slx and .mdl files recursively
files_slx = dir(fullfile(dirPath, '**', '*.slx'));
files_mdl = dir(fullfile(dirPath, '**', '*.mdl'));
files = [files_slx; files_mdl];

if isempty(files)
    disp('No .slx or .mdl files found.');
    return;
end

for k = 1:length(files)
    filePath = fullfile(files(k).folder, files(k).name);
    [~, modelName, ~] = fileparts(filePath);
    fprintf('\nFile: %s\n', filePath);
    try

        load_system(filePath);
        % Use model name in find_system after loading

        tables_Temp = slreq.modeling.find(modelName);
        % TODO assert there is exactly one RT
        rt_path = tables_Temp.Path;

        Table = tables_Temp(1);

        % Read root requirements
        rows = getRequirementRows(Table);

        % Collect requirements into a struct array for merging later
        if ~exist('allData', 'var')
            allData = [];
        end
        for idx = 1:numel(rows)
            row = rows(idx);
            preconds = row.Preconditions;
            if iscell(preconds) && numel(preconds) > 1
            splitPreconds = cellfun(@char, preconds, 'UniformOutput', false);
            else
            splitPreconds = preconds;
            end

            postconds = row.Postconditions;
            if iscell(postconds) && numel(postconds) > 1
            splitPostconds = cellfun(@char, postconds, 'UniformOutput', false);
            else
            splitPostconds = postconds;
            end

            % Add data to struct array, include file/model info
            entry.Index = idx;
            entry.File = filePath;
            entry.Model = modelName;
            entry.Preconditions = splitPreconds;
            entry.Postconditions = splitPostconds;
            allData = [allData; entry];
        end

        % Only write CSV after all files processed
        if k == length(files)
            reqTable = struct2table(allData);

            % Ensure output directory exists
            parentDir = fileparts(dirPath);
            outputDir = fullfile(parentDir, 'output');
            if ~exist(outputDir, 'dir')
            mkdir(outputDir);
            end

            % Write merged CSV file
            outputFile = fullfile(outputDir, 'all_requirements.csv');
            writetable(reqTable, outputFile, 'WriteVariableNames', true);
            fprintf('Merged requirements written to: %s\n', outputFile);
        end

        close_system(modelName, 0);
    catch ME
        fprintf('  Error processing file: %s\n', ME.message);
    end
end

% Re-enable warnings
warning('on', 'all');
end