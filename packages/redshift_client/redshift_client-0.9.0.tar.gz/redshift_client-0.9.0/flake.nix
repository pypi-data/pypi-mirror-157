{
  description = "Redshift client-SDK";
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs";
    nix_filter.url = "github:numtide/nix-filter";
    purity.url = "gitlab:dmurciaatfluid/purity/v1.17.0";
    purity.inputs.nixpkgs.follows = "nixpkgs";
  };
  outputs = {
    self,
    nixpkgs,
    nix_filter,
    purity,
  }: let
    system = "x86_64-linux";
    path_filter = nix_filter.outputs.lib;
    src = path_filter {
      root = self;
      include = [
        "arch.cfg"
        "pyproject.toml"
        (path_filter.inDirectory "redshift_client")
        (path_filter.inDirectory "tests")
      ];
    };
    out = import ./default.nix {
      inherit src;
      legacy_pkgs = nixpkgs.legacyPackages."${system}";
      others = {
        fa-purity = purity.packages."${system}";
      };
    };
  in {
    packages."${system}" = out;
    defaultPackage."${system}" = self.packages."${system}".pkg;
  };
}
