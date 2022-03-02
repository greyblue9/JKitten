{ pkgs }: {
    deps = [
        pkgs.graalvm17-ce
        pkgs.maven
        pkgs.replitPackages.jdt-language-server
        pkgs.replitPackages.java-debug
        pkgs.unzip
        pkgs.zip
        pkgs.busybox
        pkgs.python39Full
    ];
}