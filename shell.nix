{ pkgs ? import <nixpkgs> { } }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    python311
    pdm
  ];
  shellHook = ''
    show_env
  '';
}
