# -*- coding: utf-8 -*-
# :Project:   metapensiero.tool.tinject — Development shell
# :Created:   mer 29 giu 2022, 10:40:08
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2022 Lele Gaifax
#

{
  description = "metapensiero.tool.tinject";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };

        jinja2-time = pkgs.python3Packages.buildPythonPackage rec {
          pname = "jinja2-time";
          version = "0.2.0";
          src = pkgs.python3Packages.fetchPypi {
            inherit pname version;
            hash = "sha256:d14eaa4d315e7688daa4969f616f226614350c48730bfa1692d2caebd8c90d40";
          };
          propagatedBuildInputs = [
            pkgs.python3Packages.arrow
            pkgs.python3Packages.jinja2
          ];
          doCheck = false;
        };

        ruamel-yaml-clib = pkgs.python3Packages.buildPythonPackage rec {
          pname = "ruamel.yaml.clib";
          version = "0.2.6";
          src = pkgs.python3Packages.fetchPypi {
            inherit pname version;
            hash = "sha256:4ff604ce439abb20794f05613c374759ce10e3595d1867764dd1ae675b85acbd";
          };
          doCheck = false;
        };

        ruamel-yaml = pkgs.python3Packages.buildPythonPackage rec {
          pname = "ruamel.yaml";
          version = "0.17.21";
          src = pkgs.python3Packages.fetchPypi {
            inherit pname version;
            hash = "sha256:8b7ce697a2f212752a35c1ac414471dc16c424c9573be4926b56ff3f5d23b7af";
          };
          propagatedBuildInputs = [
            ruamel-yaml-clib
          ];
          doCheck = false;
        };
      in {
        devShells = {
          default = pkgs.mkShell {
            name = "Dev shell";

            packages = [
              jinja2-time
              ruamel-yaml
            ] ++ (with pkgs; [
              bump2version
              just
              python3
              twine
            ]) ++ (with pkgs.python3Packages; [
              hatchling
              questionary
              jinja2
              tomli
            ]);

            shellHook = ''
               export PYTHONPATH="$(pwd)/src''${PYTHONPATH:+:}$PYTHONPATH"
             '';
          };
        };
      });
}
