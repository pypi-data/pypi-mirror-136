@echo off

cmake -S . -B build/debug -G Ninja -DCMAKE_BUILD_TYPE=Debug -DCMAKE_PREFIX_PATH=%cd%/../library/install
cmake -S . -B build/release -G Ninja -DCMAKE_BUILD_TYPE=DelWithDebInfo -DCMAKE_PREFIX_PATH=%cd%/../library/install
