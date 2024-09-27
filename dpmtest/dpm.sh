#!/usr/bin/env fish

# Run dpm test
echo "Running DPM benchmark:"
./dpm_test.sh
echo "DPM region results:"
cat dpm_log.txt | tail -n40
python3 parse_regions.py dpm_out.txt

echo "Running DPM benchmark (split-all):"
# Run dpm test
./dpm_test_split_all.sh
echo "DPM region results (split-all):"
cat dpm_log_split_all.txt | tail -n40
python3 parse_regions.py dpm_out_split_all.txt
