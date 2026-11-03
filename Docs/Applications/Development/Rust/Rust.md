# Rust development environment and faster downloads

Use Rust's `rustup` toolchain manager for a user-owned development environment. AnduinOS still uses APT for the system compiler/linker dependencies. This keeps project toolchains separate from packages maintained by the operating system.

## Install and verify

Refresh package metadata:

```bash
sudo apt update
```

Install a C compiler, linker and the download prerequisites:

```bash
sudo apt install build-essential curl ca-certificates
```

Follow the [official rustup installer](https://rust-lang.org/tools/install/), running it as your normal user:

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

Read the installer prompts and choose the default stable toolchain unless your project specifies another. Do not run this command with `sudo`. Load the environment into this Bash session:

```bash
. "$HOME/.cargo/env"
```

Check the selected toolchain:

```bash
rustup show
```

Check the compiler:

```bash
rustc --version
```

Check the package/build tool:

```bash
cargo --version
```

If `cargo` is not found, reopen Terminal or load the environment again. If another installation is selected, inspect `command -v cargo` and `command -v rustc` before uninstalling anything. A repository's `rust-toolchain.toml` can select a different toolchain from your default.

## Build a first program

Choose a directory for your projects, then create a new project with a name that does not already exist:

```bash
cargo new hello-anduinos
```

Enter it:

```bash
cd hello-anduinos
```

Compile and run:

```bash
cargo run
```

Expect `Hello, world!`. This verifies the compiler, linker and executable together. Later, `cargo check` gives a quicker compile check without building the final executable. For editor support, install **rust-analyzer** in your editor; see [Visual Studio Code](../../Code-Editors/Visual-Studio-Code/Visual-Studio-Code.md).

Native-library projects may need additional APT development packages such as `pkg-config` or `libssl-dev`. Install the dependencies requested by that project's build documentation rather than changing the Rust toolchain at random.

## Separate toolchain downloads from crate downloads

`rustup` downloads compiler toolchains. Cargo downloads crate dependencies and their registry index. Changing the Ubuntu APT mirror changes neither service.

For current Cargo, crates.io normally uses the sparse index. If an old personal configuration forces the Git index, inspect `~/.cargo/config.toml` and the project's `.cargo/config.toml`. Where you intentionally want crates.io's sparse protocol, merge this setting into the existing configuration without duplicating the table:

```toml
[registries.crates-io]
protocol = "sparse"
```

See [Cargo configuration](https://doc.rust-lang.org/cargo/reference/config.html). A project configuration may override your personal one. Do not disable TLS certificate verification to work around a slow or failing connection.

For a company proxy or regional mirror, use an endpoint you trust and follow its current instructions. Cargo's [source replacement](https://doc.rust-lang.org/cargo/reference/source-replacement.html) is distinct from rustup's distribution server. Apply one change at a time, retain the original configuration, and remove the added replacement when returning to the official source. A crates mirror does not speed up arbitrary Git dependencies.

From a real project containing external dependencies, run `cargo fetch` to verify downloads before measuring build performance. The Hello World example has no external crates, so its success alone does not validate registry access. Cached dependencies can be reused; `--offline` succeeds only when the needed dependencies are already available.

## Maintain the environment

Update your rustup-managed stable toolchain when appropriate for your projects:

```bash
rustup update stable
```

Keep project lockfiles and toolchain requirements under the project's own policy. Build output lives under `target`; `cargo clean` in that project removes it and trades disk space for a slower next build. Keep source code in an [independent backup](../../../Install/Backup-And-Restore.md), even when Home snapshots are enabled.
