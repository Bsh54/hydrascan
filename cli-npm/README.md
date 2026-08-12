# hydrascan

Graph-native supply-chain blast-radius analysis for **npm** and **PyPI**, powered
by [HydraDB](https://github.com/hydra-db/hydradb).

Point it at any repository and see which of your projects a compromised package
can actually reach — and the exact command to fix each one.

## Usage

No install required:

```bash
npx hydrascan sindresorhus/got
npx hydrascan https://github.com/expressjs/express
npx hydrascan ./package-lock.json
```

Or install globally:

```bash
npm install -g hydrascan
hydrascan chalk/chalk
```

## Output

```
  my-web-app@1.0.0
  9 packages  |  npm  |  engine: hydradb

  Exposure score: 100/100  (Critical)

  Fixes (6 compromised dependencies):

    keyv@6.0.0        ->   npm uninstall keyv
    flat-cache@6.1.24 ->   npm uninstall flat-cache
    ...
```

## CI

Exit code is `1` when a compromised dependency is reachable, `0` when clean, so
you can gate a pipeline:

```bash
npx hydrascan "$REPO" || exit 1
```

Use `--json` for machine-readable output.

## Configuration

`HYDRASCAN_API_URL` points the CLI at your own HydraScan instance (defaults to
the hosted API).

## License

MIT
