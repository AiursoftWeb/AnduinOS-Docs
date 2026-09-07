# Changing the distribution identity — retired instructions

The former instructions for turning AnduinOS into Ubuntu by reinstalling
identity packages are not supported on AnduinOS 2. AnduinOS supplies its own
`base-files` package; reinstalling it does not convert the distribution.

Changing `os-release` or `lsb-release` does not replace the installed package
set or establish a supported Ubuntu release-upgrade path. Do not follow the
old instructions to install Ubuntu upgrade components and run
`do-release-upgrade` as a conversion procedure.

For software compatibility, use the vendor's documented installation method
or an [isolated container](../Sandboxing/Using-Docker-As-Container.md).
For system maintenance, see [using APT](./Use-APT-to-manage-packages.md)
and [backup and recovery](../../Install/Backup-And-Restore.md).
This address remains to explain why the former tutorial was withdrawn.
