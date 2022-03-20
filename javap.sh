#!/usr/local/bin/mksh-static-printf

classpath="${CLASSPATH}${CLASSPATH:+:}$( find "$( pwd )/lib" -name "*.jar" | tr '\n' ":" )$( pwd )/out:$( pwd  )"

javap -cp "$classpath" -constants "$@"

