with import <nixpkgs> {};
stdenv.mkDerivation {
  name = "env";
  buildInputs = [
    bashInteractive
    python3Packages.wheel
    python3Packages.twine
  ];
  SOURCE_DATE_EPOCH="1523278946";
}
