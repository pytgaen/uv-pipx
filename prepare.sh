#!/usr/bin/env bash

function log_info() {
  echo >&2 -e "[\\e[1;94mINFO\\e[0m] $*"
}

function log_warn() {
  echo >&2 -e "[\\e[1;93mWARN\\e[0m] $*"
}

function log_error() {
  echo >&2 -e "[\\e[1;91mERROR\\e[0m] $*"
}

function pythonize_semver() {
  # https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/#choosing-a-versioning-scheme
  # for python convert 1.0.1-rc.1 from semver to 1.0.1rc1

  echo "$nextVer" | awk -F '-' '$2 ~ "rc[.].*" {nu=$2;sub("rc.", "", nu);printf($1"rc"nu)}  $2 ~ "alpha[.].*" {nu=$2;sub("alpha.", "", nu);printf($1"alpha"nu)}  $2 ~ "beta[.].*" {nu=$2;sub("beta.", "", nu);printf($1"beta"nu)}  $2=="" {print$0}'
}

function bump_python_file() {
  indent=$2
  log_info "${indent}Bump $1 to python version \\e[33;1m${nextPythonVer}\\e[0m..."
  sed -e "s/__version__[ ]*=[ ]*\".*\"[ ]*# to bump/__version__ = \"$nextVer\"  # to bump/" "$1" >"$1.next"
  mv -f "$1.next" "$1"
}

function bump_python_files() {
  log_info "Bump files in path $1 to python version \\e[33;1m${nextPythonVer}\\e[0m..."
  for pycode in $(grep -l -e '__version__.*# to bump' $1/*.py); do
    bump_python_file "$pycode" "  "
  done
}

function bump_pyproject_poetry() {
  log_info "Bump pyproject.toml to python version \\e[33;1m${nextPythonVer}\\e[0m..."
  # replace in pyproject.toml
  sed -e "s/version[ ]*=[ ]*\".*\"[ ]*# to bump/version = \"$nextPythonVer\" # to bump/" pyproject.toml >pyproject.toml.next
  mv -f pyproject.toml.next pyproject.toml
  head pyproject.toml
}

function bump_mkdocs() {
  local app_name=$1
  if [[ -d docs/ ]]; then
    log_info "Bump mkdoc for ${app_name} from \\e[33;1m${curVer}\\e[0m to \\e[33;1m${nextVer}\\e[0m..."
    # replace in mkdocs pages
    for doc in docs/*.md; do
      sed -e "s/$app_name $curVer/$app_name $nextVer/" "$doc" >"$doc.next"
      mv -f "$doc.next" "$doc"
    done
  fi
}

# check number of arguments
if [[ "$#" -le 2 ]]; then
  log_error "Missing arguments"
  log_error "Usage: $0 <current version> <next version> <release type>"
  exit 1
fi

curVer=$1
nextVer=$2
relType=$3

nextPythonVer=$(pythonize_semver)

if [[ "$curVer" ]]; then
  log_info "Bump version from \\e[33;1m${curVer}\\e[0m to \\e[33;1m${nextVer}\\e[0m..."

  bump_pyproject_poetry
  bump_python_files "uvpipx"
  bump_mkdocs "uvpipx"
else
  log_info "Bump version to \\e[33;1m${nextVer}\\e[0m (release type: $relType): this is the first release (skip)..."
fi
