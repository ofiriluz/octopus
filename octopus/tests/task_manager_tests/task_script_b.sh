# Echo some things to the console then write to file
echo Hello World
echo `pwd`
sleep 5

echo Now writing to file
echo {\"Test\":\"ABC\"} > 'octopus/tests/task_manager_tests/tmp_file.json'