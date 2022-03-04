#!/usr/local/bin/mksh-static-printf

mkdir -p out; find ./src -name "*.java" -exec javac -cp "./lib/deps.jar:./lib/jackson-core-2.2.3.jar" -d out/ "{}" + && rm -vf -- lib/Ab.jar && ( cd out; zip -Xy ../lib/Ab.jar -r . ; );

