#!/usr/local/bin/mksh-static-printf

mkdir -p out; find ./src -name "*.java" -exec javac -cp "/usr/local/javalibs/junit.jar:$( bshnicp  ):/usr/local/javalibs/commons-logging-1.2.jar:/usr/local/javalibs/commons-codec-1.10.jar:/usr/local/javalibs/httpcore-4.4.10.jar:/usr/local/javalibs/httpclient-4.5.6.jar:/usr/local/javalibs/joda-time-2.9.4.jar:/usr/local/javalibs/hamcrest-all-1.3.jar:/data/media/0/src/program_ab/stc/lib/sanmoku-feature-ex-0.0.1.jar" -d out/ "{}" + && rm -vf -- lib/Ab.jar && ( cd out; zip -Xy ../lib/Ab.jar -r . ; );

