let
  env = import ./env.nix;
in

{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  buildInputs = with pkgs; [
    python312
    python312Packages.flask
    python312Packages.flask-session
    python312Packages.python-ldap
    python312Packages.redis
    python312Packages.requests
  ];

  # Use system certificates for requests
  REQUESTS_CA_BUNDLE = "/etc/ssl/certs/ca-certificates.crt";
  TOEMURL = env.TOEMURL;
  TOEMUSER = env.TOEMUSER;
  TOEMPASS = env.TOEMPASS;

  shellHook = "fish";
}
