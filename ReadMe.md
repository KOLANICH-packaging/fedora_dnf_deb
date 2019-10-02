Scripts for building Debian/Ubuntu packages for CMake
=====================================================

Scripts in this repo are [Unlicensed ![](https://raw.githubusercontent.com/unlicense/unlicense.org/master/static/favicon.png)](https://unlicense.org/).

Third-party components have own licenses.

**DISCLAIMER: BADGES BELOW DO NOT REFLECT THE STATE OF THE DEPENDENCIES IN THE CONTAINER**

The software in this repo builds a set of packages from prebuilt binaries of Kitware (TM) CMake.
The licenses of the software is available by official links and are also included into the packages.

Artifacts of CI builds can be used as a repo for apt.

```bash
export ARTIFACTS_PATH=https://kolanich.gitlab.io/CMake_deb_packages_CI
export KEY_FINGERPRINT=0e94c991ee6dfe96affa14a8a059ada6ca7b4a3f
curl -o vanilla_CMake_KOLANICH.gpg $ARTIFACTS_PATH/public.gpg
apt-key add vanilla_CMake_KOLANICH.gpg
eval `apt-config shell TRUSTED_KEYS_DIR Dir::Etc::TrustedParts/d`
export KEY_PATH=$TRUSTED_KEYS_DIR/vanilla_CMake_KOLANICH.gpg
mv ./vanilla_CMake_KOLANICH.gpg $KEY_PATH
echo deb [arch=amd64,signed-by=$KEY_PATH] $ARTIFACTS_PATH/repo eoan contrib >> /etc/apt/sources.list.d/vanilla_CMake_KOLANICH.list
apt update
```

To install the packages, use `vanilla-` prefix:

```bash
apt-get -y install vanilla-cmake
```

Setting up an own repo
==================

1. generate a GPG private key (RSA 4096, signature only)

2. export it
```bash
gpg --no-default-keyring --keyring ./kr.gpg --export-secret-key $KEY_FINGERPRINT | base64 -w0 > ./private.gpg.b64
```
`-w0` is mandatory.

3. paste it into GitLab protected environment variable `GPG_KEY`
