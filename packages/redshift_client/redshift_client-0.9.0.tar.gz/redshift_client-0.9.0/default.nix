{
  src,
  legacy_pkgs,
  others,
  _metadata ? null,
}: let
  supported = ["python38" "python39" "python310"];
  version = let
    file_str = builtins.readFile "${src}/redshift_client/__init__.py";
    match = builtins.match ".*__version__ *= *\"(.+?)\".*" file_str;
  in
    builtins.elemAt match 0;
  metadata =
    if _metadata == null
    then
      (
        (builtins.fromTOML (builtins.readFile ./pyproject.toml)).project
        // {
          inherit version;
        }
      )
    else _metadata;
  publish = import ./build/publish {
    nixpkgs = legacy_pkgs;
  };
  build_for = selected_python: let
    lib = {
      buildEnv = legacy_pkgs."${selected_python}".buildEnv.override;
      buildPythonPackage = legacy_pkgs."${selected_python}".pkgs.buildPythonPackage;
      fetchPypi = legacy_pkgs.python3Packages.fetchPypi;
    };
    python_pkgs = import ./build/deps lib (
      legacy_pkgs."${selected_python}Packages"
      // (builtins.mapAttrs (_: v: v."${selected_python}".pkg) others)
    );
    self_pkgs = import ./build/pkg {
      inherit src lib metadata python_pkgs;
    };
    checks = import ./ci/check.nix {self_pkg = self_pkgs.pkg;};
  in {
    check = checks;
    env = self_pkgs.env;
    pkg = self_pkgs.pkg;
  };
  pkgs = builtins.listToAttrs (map
    (name: {
      inherit name;
      value = build_for name;
    })
    supported);
in
  pkgs
  // {
    inherit publish;
  }
