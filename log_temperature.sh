#!/bin/bash

output_file="output.txt"
program_command="sudo powermetrics"

while true; do
  # Generate metrics with powermetrics and redirect output to text file
  nohup bash -c "$program_command" > "$output_file" &
  program_pid=$!

  # Sleep for 6 seconds
  # 10 readings per minute seems nice
  # It happens to take 5 seconds for the metrics to read so this is good
  sleep 6

  # Terminate powermetrics and wait for it to exit
  sudo kill $program_pid
  wait $program_pid

  # Clear the contents of the text file before looping so we don't write the same data twice
  : > "$output_file"
done
