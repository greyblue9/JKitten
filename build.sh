#!/usr/local/bin/mksh-static-printf

classpath="${CLASSPATH}${CLASSPATH:+:}$( find "$( pwd )/lib" -name "*.jar" | tr '\n' ":"
)$( pwd )/out:$( pwd  )"

rm -rf out && mkdir -p out
find ./src -name "*.java" -exec javac -g -implicit:none -proc:none -nowarn -verbose -cp "./lib/deps.jar:./lib/jackson-core-2.2.3.jar" -d out/ "{}" + && rm -vf -- lib/Ab.jar && ( cd out; zip -Xy ../lib/Ab.jar -r . ; );
[ $? -eq 0 ] || exit 1
dx=$( whence -p dx )
if [ -n "$dx" ]; then
  dx --dex --multi-dex --keep-classes --output=/tmp/classes.jar ./lib/Ab.jar && cp -pvf -- /tmp/classes.jar ./lib/Ab.jar
else
  ttue
fi


