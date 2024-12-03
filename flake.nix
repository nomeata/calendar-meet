{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-23.05";
  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
    in
    { devShell.${system} = pkgs.stdenv.mkDerivation rec {
      name = "env";
      buildInputs = with pkgs; [
        python3
        python3Packages.google-auth
        python3Packages.google-auth-oauthlib
        python3Packages.google-auth-httplib2
        python3Packages.google-api-python-client
      ];
   };};
}
