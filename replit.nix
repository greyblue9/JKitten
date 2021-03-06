{ pkgs }: {
    deps = [
        pkgs.jdk8
        pkgs.maven
        pkgs.replitPackages.jdt-language-server
        pkgs.replitPackages.java-debug
        pkgs.unzip
        pkgs.zip
        #pkgs.python39Full
        pkgs.libxml2
        #pkgs.zsh
		pkgs.pigz
		pkgs.zlib
		(pkgs.python39.withPackages (p: [p.pandas p.numpy]))
    ];
}
