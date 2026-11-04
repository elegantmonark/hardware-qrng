function report = analyse_ed1(inputFile, outputDir)
%ANALYSE_ED1 Analyse the April Arduino capture and check the saved results.
%   Run analyse_ed1 with no arguments to use the original capture.
%   Use analyse_ed1('qrng_bits.csv', 'output') to choose the paths.
%   Requires MATLAB R2020a or later, with no extra toolboxes.
%
%   The CSV has no timestamps, so frequency stays in cycles per sample.
%   These checks describe the signal and bit balance. They cannot identify
%   where the noise comes from or establish that the output is secure.

    here = fileparts(mfilename('fullpath'));
    projectRoot = fileparts(fileparts(here));
    if nargin < 1 || isempty(inputFile)
        inputFile = fullfile(here, 'qrng_bits.csv'); % The Online folder keeps the CSV here.
        if ~isfile(inputFile)
            inputFile = fullfile(projectRoot, 'data', 'ED-1', 'qrng_bits.csv');
        end
    end
    if nargin < 2 || isempty(outputDir)
        outputDir = fullfile(here, 'output');
    end

    capture = readtable(inputFile);
    assert(all(ismember({'raw', 'bit'}, capture.Properties.VariableNames)), ...
        'CSV must contain raw and bit columns.');
    raw = double(capture.raw(:));
    bits = double(capture.bit(:));
    sampleCount = numel(raw);
    assert(sampleCount >= 1000, 'At least 1000 samples are required.');
    assert(all(isfinite(raw) & raw == fix(raw) & raw >= 0 & raw <= 1023), ...
        'Expected integer 10-bit Arduino ADC codes from 0 to 1023.');
    assert(all(bits == 0 | bits == 1), 'Bits must be zero or one.');
    assert(all(bits == mod(raw, 2)), 'Stored bits must match each ADC LSB.');

    maxLag = 100;
    blockSize = 1000;
    rawAcf = sequence_acf(raw, maxLag);
    bitAcf = sequence_acf(bits, maxLag);

    % Each column holds one consecutive block of 1000 bits.
    blockCount = floor(sampleCount / blockSize);
    blocks = reshape(bits(1:blockCount * blockSize), blockSize, blockCount);
    blockP1 = mean(blocks, 1);
    blockH = binary_entropy(blockP1);
    p1 = mean(bits);

    % The Hann window reduces leakage from cutting off the recorded signal.
    window = 0.5 - 0.5 * cos(2 * pi * (0:sampleCount-1)' / (sampleCount-1));
    spectrum = fft((raw - mean(raw)) .* window);
    power = abs(spectrum(1:floor(sampleCount / 2) + 1)).^2;
    power(1) = 0; % Skip DC when looking for the strongest repeating component.
    assert(sum(power) > 0, 'A constant signal has no non-DC spectrum to analyse.');
    power = power / sum(power);
    frequency = (0:floor(sampleCount / 2))' / sampleCount;
    [~, peakIndex] = max(power);

    changes = find(diff(bits) ~= 0);
    runLengths = diff([0; changes; sampleCount]);
    transitions = accumarray([bits(1:end-1)+1, bits(2:end)+1], 1, [2, 2]);

    report.input = char(inputFile);
    report.engine = 'MATLAB';
    report.engine_version = version;
    report.generated_at = datestr(now, 30);
    report.samples = sampleCount;
    report.ones = sum(bits);
    report.zeros = sampleCount - report.ones;
    report.proportion_ones = p1;
    report.binary_shannon_entropy = binary_entropy(p1);
    report.longest_identical_bit_run = max(runLengths);
    report.raw_adc.minimum = min(raw);
    report.raw_adc.maximum = max(raw);
    report.raw_adc.mean = mean(raw);
    report.raw_adc.standard_deviation = std(raw, 1); % Match the population convention in the saved audit.
    report.raw_adc.lag_1_correlation = rawAcf(2);
    report.raw_adc.dominant_cycles_per_sample = frequency(peakIndex);
    report.raw_adc.dominant_period_samples = 1 / frequency(peakIndex);
    report.lsb_lag_1_correlation = bitAcf(2);
    report.transition_counts = transitions;
    report.block_size = blockSize;
    report.block_entropy_mean = mean(blockH);
    report.notes = { ...
        'Arduino ED-1 capture; not an ESP32 capture.', ...
        'Frequency is cycles/sample; sampling rate is not established by this CSV.', ...
        'Binary Shannon entropy describes the marginal bit balance, not entropy rate.', ...
        'Descriptive diagnostics do not establish quantum origin or security.'};

    % Check the MATLAB results against the earlier Python analysis.
    referenceFile = fullfile(here, 'ed1_reference.json');
    if ~isfile(referenceFile)
        referenceFile = fullfile(projectRoot, 'results', 'ED-1', ...
            'april_2026_dataset_audit.json');
    end
    report.reference_checked = false;
    if isfile(referenceFile)
        expected = jsondecode(fileread(referenceFile));
        assert(report.samples == expected.samples, 'Sample count differs from ED-1.');
        assert(report.ones == expected.ones, 'One count differs from ED-1.');
        assert(report.longest_identical_bit_run == expected.longest_identical_bit_run, ...
            'Longest run differs from ED-1.');
        actualValues = [p1, report.binary_shannon_entropy, rawAcf(2), bitAcf(2), ...
            frequency(peakIndex), report.block_entropy_mean];
        expectedValues = [expected.proportion_ones, expected.binary_shannon_entropy, ...
            expected.raw_adc.lag_1_correlation, expected.lsb_lag_1_correlation, ...
            expected.raw_adc.dominant_cycles_per_sample, expected.block_entropy_mean];
        assert(all(abs(actualValues - expectedValues) < 1e-8), ...
            'MATLAB results differ from the preserved Python audit.');
        assert(isequal(transitions, expected.transition_counts), ...
            'Transition counts differ from ED-1.');
        report.reference_checked = true;
    end

    if ~isfolder(outputDir)
        mkdir(outputDir);
    end
    fig = figure('Name', 'ED-1 signal diagnostics', 'Color', 'w', ...
        'Position', [80, 80, 1400, 780]);
    layout = tiledlayout(fig, 2, 3, 'TileSpacing', 'compact', 'Padding', 'compact');

    nexttile;
    count = min(1500, sampleCount);
    plot(0:count-1, raw(1:count), 'Color', [0.12, 0.34, 0.55]);
    title('Raw ADC signal'); xlabel('Sample index'); ylabel('ADC code'); grid on;

    nexttile;
    histogram(raw, -0.5:1023.5, 'FaceColor', [0.12, 0.34, 0.55], 'EdgeColor', 'none');
    title('ADC distribution'); xlabel('ADC code'); ylabel('Count'); grid on;

    nexttile;
    semilogy(frequency(2:end), max(power(2:end), realmin));
    title(sprintf('Raw spectrum: peak %.5f cycles/sample', frequency(peakIndex)));
    xlabel('Cycles per sample'); ylabel('Normalised bin power'); grid on;

    nexttile;
    plot(1:maxLag, rawAcf(2:end), 'Color', [0.85, 0.33, 0.10]);
    yline(0, ':'); title('Raw ADC autocorrelation');
    xlabel('Lag / samples'); ylabel('Correlation'); grid on;

    nexttile;
    plot(1:maxLag, bitAcf(2:end), 'Color', [0.12, 0.55, 0.35]);
    yline(0, ':'); title('Extracted LSB autocorrelation');
    xlabel('Lag / samples'); ylabel('Correlation'); grid on;

    nexttile;
    plot((0:blockCount-1) * blockSize, blockP1);
    yline(0.5, '--'); title(sprintf('Balance in %d-bit blocks', blockSize));
    xlabel('Starting sample index'); ylabel('Proportion of ones'); grid on;
    title(layout, sprintf('ED-1 Arduino capture: %s samples | descriptive diagnostics', ...
        num2str(sampleCount)));
    exportgraphics(fig, fullfile(outputDir, 'ed1_matlab_diagnostics.png'), 'Resolution', 180);
    savefig(fig, fullfile(outputDir, 'ed1_matlab_diagnostics.fig'));

    lags = (0:maxLag)';
    writetable(table(lags, rawAcf, bitAcf), fullfile(outputDir, 'autocorrelation.csv'));
    write_text(fullfile(outputDir, 'ed1_matlab_report.json'), jsonencode(report));
    summary = sprintf([ ...
        'Runtime: MATLAB %s\nSamples: %d\nOnes: %d\nZeros: %d\n' ...
        'Proportion of ones: %.9f\nMarginal binary Shannon entropy: %.12f bits/symbol\n' ...
        'Raw ADC lag-1 correlation: %.12f\nLSB lag-1 correlation: %.12f\n' ...
        'Dominant component: %.9f cycles/sample (%.6f samples/period)\n' ...
        'Preserved reference checked: %d\n' ...
        'Interpretation: near-balanced LSBs coexist with strong raw-signal structure.\n' ...
        'These are descriptive diagnostics, not proof of quantum or secure entropy.\n'], ...
        report.engine_version, sampleCount, report.ones, report.zeros, p1, ...
        report.binary_shannon_entropy, rawAcf(2), bitAcf(2), ...
        frequency(peakIndex), report.raw_adc.dominant_period_samples, report.reference_checked);
    write_text(fullfile(outputDir, 'summary.txt'), summary);
    fprintf('%s\nOutput folder: %s\n', summary, outputDir);
end

function acf = sequence_acf(values, maxLag)
% Padding keeps the end of the capture from wrapping into the start.
% Divide by the number of overlapping samples before normalising lag zero.
    centred = values(:) - mean(values);
    n = numel(centred);
    if ~any(centred)
        acf = nan(maxLag+1, 1);
        return;
    end
    transformLength = 2^nextpow2(2*n - 1);
    transformed = fft(centred, transformLength);
    correlation = real(ifft(transformed .* conj(transformed)));
    overlap = (n:-1:n-maxLag)';
    correlation = correlation(1:maxLag+1) ./ overlap;
    acf = correlation / correlation(1);
end

function entropy = binary_entropy(p)
% All zeros or all ones have zero marginal entropy; skip log2(0).
    entropy = zeros(size(p));
    interior = p > 0 & p < 1;
    q = p(interior);
    entropy(interior) = -q .* log2(q) - (1-q) .* log2(1-q);
end

function write_text(path, contents)
    file = fopen(path, 'w');
    assert(file ~= -1, 'Could not open output file: %s', path);
    cleanup = onCleanup(@() fclose(file)); %#ok<NASGU>
    fprintf(file, '%s', contents);
end
