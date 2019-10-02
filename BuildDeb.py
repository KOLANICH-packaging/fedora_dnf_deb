#!/usr/bin/env python3
"""Builds packages"""
import sys
from pathlib import Path
from tqdm.auto import tqdm
from prebuilder import *
from prebuilder.systems import CMake, AutoTools
from prebuilder.systems.meson import Meson
from prebuilder.buildPipeline import BuildRecipy, BuildPipeline
from prebuilder.repoPipeline import RepoPipelineMeta
from ClassDictMeta import ClassDictMeta
from prebuilder.fetchers import GitRepoFetcher, DiscoverDownloadVerifyUnpackFetcher

from AnyVer import AnyVer

from prebuilder.core.Package import PackageMetadata, PackagingSpec, PackageRef, VersionedPackageRef
from prebuilder.core.RunConfig import RunConfig
from prebuilder.core.Action import IFSAction
from prebuilder.distros.debian import Debian
from prebuilder.tools.apt import installPackages
from prebuilder.importers.debhelper import parseDebhelperDebianDir
1
import shutil
import shlex
from collections import OrderedDict

thisDir = Path(".").absolute()


class build(metaclass=RepoPipelineMeta):
	"""Yo dawg! It's {maintainerName}'s repo for {repoKind} of package management tools for RPM-based distros."""
	
	DISTROS = (Debian,)

	def _ZChunk():
		name = "zchunk"
		repoURI = "https://github.com/zchunk/zchunk"
		
		class cfg(metaclass=ClassDictMeta):
			descriptionShort = "A file format designed for highly efficient deltas while maintaining good compression"
			descriptionLong = """zchunk is a compressed file format that splits the file into independent chunks. This allows you to only download changed chunks when downloading a new version of the file, and also makes zchunk files efficient over rsync.

		zchunk files are protected with strong checksums to verify that the file you downloaded is, in fact, the file you wanted.

		As of zchunk-1.0, the ABI and API have been marked stable, and the only changes allowed are backwards-compatible additions"""
			section = "devel"
			homepage = repoURI
			# "license": "BSD-2-Clause"
			provides = (name,)
		
		buildRecipy = BuildRecipy(Meson, GitRepoFetcher(repoURI, refspec="master"), buildOptions = {})
		metadata = PackageMetadata(name, **cfg)
		
		return BuildPipeline(buildRecipy, ((Debian, metadata),))

	def _moduleMd():
		repoURI = "https://github.com/fedora-modularity/libmodulemd"
		
		class cfg(metaclass=ClassDictMeta):
			descriptionShort = "C Library for manipulating module metadata files"
			#descriptionLong = """ """
			#license = "MIT"
			version = "CI",
			section = "devel"
			homepage = repoURI
		
		branch = 1
		
		if branch == 1:
			buildRecipy = BuildRecipy(Meson, GitRepoFetcher(repoURI, refspec="1.x-maint"), buildOptions = {"with_docs":False, "developer_build": False}, firejailCfg={"disable": True})
			metadata = PackageMetadata(VersionedPackageRef("modulemd", version=AnyVer("1.8.16"), incompatibleDigits=1), **cfg)
		else:
			buildRecipy = BuildRecipy(Meson, GitRepoFetcher(repoURI, refspec="master"), buildOptions = {"with_docs":False, "developer_build": False}, firejailCfg={"disable": True})
			metadata = PackageMetadata(PackageRef("modulemd", incompatibleDigits=1), **cfg)
		return BuildPipeline(buildRecipy, ((Debian, metadata),))

	def _comps():
		repoURI = "https://github.com/rpm-software-management/libcomps"
		class cfg(metaclass=ClassDictMeta):
			descriptionShort = "Libcomps is a pure C alternative for yum.comps library."
			descriptionLong = "And there are bindings for python2 and python3."
			# "license": "GPL-2.0+",
			section = "devel"
			homepage = repoURI
		
		buildRecipy = BuildRecipy(CMake, GitRepoFetcher(repoURI, refspec="master"), patches = [(thisDir / "patches" / "libcomps")], buildOptions = {
			"PYTHON_DESIRED": 3,
			"ENABLE_TESTS": False,
			"ENABLE_DOCS": False,
		}, subdir="libcomps")
		metadata = PackageMetadata("comps", **cfg)
		return BuildPipeline(buildRecipy, ((Debian, metadata),))

	def _solv():
		buildRecipy = BuildRecipy(CMake, GitRepoFetcher("https://github.com/KOLANICH/libsolv", refspec="packaging"), buildOptions = {
			"WITH_LIBXML2":True,
			"WITH_SYSTEM_ZCHUNK":True,
			"ENABLE_PYTHON":False,
			"ENABLE_PYTHON3":True,
			"ENABLE_RPMDB":True,
			"ENABLE_RPMPKG":True,
			"ENABLE_PUBKEY":True,
			"ENABLE_SUSEREPO":True,
			"ENABLE_RPMDB_BYRPMHEADER":True,
			"ENABLE_RPMDB_LIBRPM":True,
			"ENABLE_RPMPKG_LIBRPM":True,
			"ENABLE_RPMMD":True,
			"ENABLE_COMPS":True,
			"ENABLE_DEBIAN":True,
			"MULTI_SEMANTICS":True,
			"ENABLE_LZMA_COMPRESSION":True,
			"ENABLE_BZIP2_COMPRESSION":True,
			"ENABLE_ZSTD_COMPRESSION":True,
			"ENABLE_ZCHUNK_COMPRESSION":True,
			"ENABLE_COMPLEX_DEPS":True,
		})
		metadata = PackageMetadata(VersionedPackageRef("solv", version=AnyVer("0.7.10")))
		return BuildPipeline(buildRecipy, ((Debian, metadata),))

	def _rpm():
		"https://git.launchpad.net/ubuntu/+source/rpm" "ubuntu/devel"
		repoURI = "https://github.com/rpm-software-management/rpm"
		
		class cfg(metaclass=ClassDictMeta):
			descriptionShort = "RPM shared library"
			descriptionLong = "The RPM Package Manager (RPM) is a command-line driven package management system capable of installing, uninstalling, verifying, querying, and updating computer software packages. This library allows programs to make use of an RPM database or RPM packages without going through the program rpm."
			# "license": "MIT",
			#"provides": ("librpm8", "rpm", "librpmsign8", "librpmio8", "librpmbuild8", "librpm-dev", "rpm-common", "rpm2cpio"),
			section = "devel"
			homepage = repoURI
		
		buildRecipy = BuildRecipy(AutoTools, GitRepoFetcher(repoURI, refspec="master"), patches = [(thisDir / "patches" / "librpm")], useKati=True, buildOptions = {
			"with-selinux":True,
			"with-cap":True,
			"enable-python":True,
			"enable-shared":True,
			"with-debian":True,
			"with-lua":True,
			"with-external-db":True,
			"datadir":"/usr/share",
			#"with-vendor":"debian",
			
			# only for Linux
			"with-cap": True,
			"with-selinux": True,
		})
		
		metadata = PackageMetadata("rpm", **cfg)
		
		runConfig = RunConfig()
		debianCmakeDir = runConfig.downloadsTmp / "debian_rpm"
		fetcher = GitRepoFetcher("https://salsa.debian.org/pkg-rpm-team/rpm")
		fetcher(debianCmakeDir, runConfig)
		
		parsedDebhelperDescription = parseDebhelperDebianDir(debianCmakeDir / "debian")
		
		parsedPackagingSpecs = tuple(s for s in parsedDebhelperDescription["pkgs"] if s[0].ref.group not in {"python2"})
		packagingSpec = PackagingSpec(metadata, parsedPackagingSpecs)
		
		return BuildPipeline(buildRecipy, ((Debian, packagingSpec),))


	def _repo():
		repoURI = "https://github.com/rpm-software-management/librepo"

		class cfg(metaclass=ClassDictMeta):
			descriptionShort = "A library providing C and Python (libcURL like) API for downloading packages and linux repository metadata in rpm-md format"
			descriptionLong = "blah blah blah"
			# "license": "LGPL-2.1",
			section = "devel"
			homepage = repoURI
		
		buildRecipy = BuildRecipy(CMake, GitRepoFetcher(repoURI, refspec="master"), patches = [(thisDir / "patches" / "librepo")], buildOptions = {
			"PYTHON_DESIRED": 3,
			"ENABLE_TESTS": False,
			"ENABLE_DOCS": False,
			"WITH_ZCHUNK": True,
		})
		metadata = PackageMetadata("repo", **cfg)
		return BuildPipeline(buildRecipy, ((Debian, metadata),))

	def dnf():
		buildRecipy = BuildRecipy(CMake, GitRepoFetcher("https://github.com/rpm-software-management/libdnf", refspec="master"), buildOptions = {
			"PYTHON_DESIRED":3,
			"WITH_GTKDOC":False,
			"WITH_MAN":False,
			"WITH_TESTS":False,
			"WITH_HTML":False,
			"WITH_ZCHUNK":False,
		}, patches=[(thisDir / "patches" / "libdnf")])
		metadata = PackageMetadata("dnf")
		return BuildPipeline(buildRecipy, ((Debian, metadata),))


if __name__ == "__main__":
	build()
