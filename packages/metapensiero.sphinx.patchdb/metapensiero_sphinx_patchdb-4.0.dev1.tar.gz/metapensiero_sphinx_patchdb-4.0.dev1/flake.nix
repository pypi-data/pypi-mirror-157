# -*- coding: utf-8 -*-
# :Project:   PatchDB — Development environment
# :Created:   dom 26 giu 2022, 11:48:09
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2022 Lele Gaifax
#

{
  description = "metapensiero.sphinx.patchdb";

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

        mkTestShell = python:
          let
            cython3 = python.pkgs.buildPythonPackage rec {
              pname = "Cython";
              version = "3.0.0a10";
              src = python.pkgs.fetchPypi {
                inherit pname version;
                hash = "sha256:342e95121a3d1a67cbcf7b340391eb40cc5ce3d2a79d7873e005e8783353d89d";
              };
              nativeBuildInputs = [ pkgs.pkg-config ];
              buildInputs = [ pkgs.glibcLocales ];
              LC_ALL = "en_US.UTF_8";
              doCheck = false;
            };

            # Current nixpkgs carries Sphinx 4.5 and Docutils 0.18,
            # that are incompatible

            docutils0171 = python.pkgs.buildPythonPackage rec {
              pname = "docutils";
              version = "0.17.1";
              src = python.pkgs.fetchPypi {
                inherit pname version;
                hash = "sha256:686577d2e4c32380bb50cbb22f575ed742d58168cee37e99117a854bcd88f125";
              };
              doCheck = false;
            };

            patchdb = python.pkgs.buildPythonApplication rec {
              name = "patchdb";
              src = ./.;
              buildInputs = [
                python.pkgs.flitBuildHook
              ];
              propagatedBuildInputs = [
                #docutils0171
              ] ++ (with python.pkgs; [
                enlighten
                sqlparse
              ]);
              buildPhase = "flitBuildPhase";
              doCheck = false;
            };

            psycopgVersion = "3.0.15";
            psycopg-c = python.pkgs.buildPythonPackage rec {
              pname = "psycopg-c";
              version = psycopgVersion;
              src = python.pkgs.fetchPypi {
                inherit pname version;
                hash = "sha256:6de99cb85274135d5d34a40028f0c06f56af637026fbb85f7b38ce689e9a16e7";
              };
              nativeBuildInputs = [
                pkgs.postgresql
                cython3
              ];
              doCheck = false;
            };

            psycopg = python.pkgs.buildPythonPackage rec {
              pname = "psycopg";
              version = psycopgVersion;
              src = python.pkgs.fetchPypi {
                inherit pname version;
                hash = "sha256:1c5637f47e9a4d9b742a0b101f39189bebae0f625bfdfb0cf8a54dd5fe677610";
              };
              nativeBuildInputs = [
                pkgs.postgresql
              ];
              propagatedBuildInputs = [psycopg-c];
              doCheck = false;
            };
          in
            pkgs.mkShell {
              name = "Test Python ${python.version}";
              packages = [
                python
                docutils0171
                patchdb
                psycopg
              ] ++ (with python.pkgs; [
                pytest
                sphinx
                sqlparse
              ]);

              LANG="C";
            };
      in {
        devShells = {
          default = pkgs.mkShell {
            name = "Dev shell";

            packages = with pkgs; [
              bump2version
              gnumake
              python3
              twine
            ] ++ (with pkgs.python3Packages; [
              babel
              hatchling
              tomli
            ]);

            shellHook = ''
               export PYTHONPATH="$(pwd)/src''${PYTHONPATH:+:}$PYTHONPATH"
             '';
          };

          testPy39 = mkTestShell pkgs.python39;
          testPy310 = mkTestShell pkgs.python310;
        };
      });
}
