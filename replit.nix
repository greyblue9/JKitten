{ pkgs }: {
    deps = [
        pkgs.graalvm17-ce
        pkgs.maven
        pkgs.replitPackages.jdt-language-server
        pkgs.replitPackages.java-debug
        pkgs.unzip
        pkgs.zip
        pkgs.python39Full
        pkgs.libxml2
        pkgs.zsh
    ];
}