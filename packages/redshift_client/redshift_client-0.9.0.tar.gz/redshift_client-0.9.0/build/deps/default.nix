lib: pythonPkgs:
pythonPkgs
// {
  types-psycopg2 = import ./psycopg2/stubs.nix lib;
  import-linter = import ./import-linter {
    inherit lib;
    click = pythonPkgs.click;
    networkx = pythonPkgs.networkx;
  };
}
